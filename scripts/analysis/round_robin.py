"""Resumable, safety-gated local tournament of archived Kaggriculture agents."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"
if SITE_PACKAGES.is_dir():
    os.environ["PYTHONPATH"] = str(SITE_PACKAGES) + os.pathsep + os.environ.get("PYTHONPATH", "")
sys.path.insert(0, str(SCRIPT_DIR))
from recent_notebook_service import strict_static_audit  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from background_log import append_event  # noqa: E402

DEFAULT_DATA = ROOT / "data" / "automation" / "round_robin_20260923"
SUBMITTED = (
    "v16rc5", "thomas_v94_safe", "v6_preempt", "v7_relax", "v10_de",
    "v12_v51safe", "v22_antiv52_brunchguard", "v27_orderbook_layer_d",
)
OTHER_MONITORS = (
    ROOT / "data/automation/recent_notebooks/monitor.json",
    ROOT / "data/automation/v27_replay_service/monitor.json",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2)


def read_json(path: Path, default: object) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover() -> dict:
    candidates, excluded = [], []

    def add(label: str, category: str, path: Path, expected: str | None = None,
            audit: bool = False, evidence: Path | None = None) -> None:
        if not path.is_file():
            excluded.append({"name": label, "reason": "missing_agent"})
            return
        try:
            actual = digest(path)
            if expected and actual != expected:
                raise ValueError("SHA mismatch")
            if evidence is not None and not evidence.is_file():
                raise ValueError("missing successful evaluation evidence")
            if audit:
                problems = strict_static_audit(path)
                if problems:
                    raise ValueError(f"static audit warnings: {len(problems)}")
        except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
            excluded.append({"name": label, "reason": str(exc)})
            return
        candidates.append({"name": label, "category": category,
                           "path": str(path.relative_to(ROOT)), "sha256": actual})

    for name in SUBMITTED:
        add(f"submitted/{name}", "submitted", ROOT / "submissions" / name / "main.py")
    for directory in sorted((ROOT / "opponents").iterdir()):
        if directory.is_dir():
            add(f"opponent/{directory.name}", "opponent", directory / "main.py", audit=True)
    state = read_json(ROOT / "data/automation/recent_notebooks/state.json", {})
    for record in state.get("seen", {}).values():
        if record.get("status") != "evaluated":
            continue
        artifact = ROOT / record["artifact"]
        files = sorted((artifact / "extracted").glob("*.py"))
        label = f"automation/{record['ref']}@{record.get('lastRunTime', '')}"
        if len(files) != 1 or record.get("audit_warnings", 0) != 0:
            excluded.append({"name": label, "reason": "ambiguous extraction or audit warnings"})
            continue
        add(label, "automation", files[0], record.get("sha256"), audit=True,
            evidence=artifact / "results" / "vs_candidate.json")

    canonical: dict[str, dict] = {}
    for item in candidates:
        # A sidecar can change behaviour, so only identical self-contained agents deduplicate.
        parent = ROOT / item["path"]
        sidecars = sorted(p for p in parent.parent.glob("*.py") if p != parent)
        key = item["sha256"] if not sidecars else item["path"]
        if key in canonical:
            canonical[key]["aliases"].append(item["name"])
        else:
            canonical[key] = {**item, "aliases": [item["name"]]}
    agents = sorted(canonical.values(), key=lambda x: x["name"])
    return {"created_at": now(), "agents": agents, "excluded": excluded,
            "candidates": len(candidates), "unique_agents": len(agents),
            "pairs": len(agents) * (len(agents) - 1) // 2}


def schedule(agents: list[dict]) -> list[tuple[dict, dict]]:
    pairs = list(itertools.combinations(agents, 2))
    pairs.sort(key=lambda ab: (
        0 if any(x["category"] == "submitted" for x in ab) else 1,
        ab[0]["name"], ab[1]["name"],
    ))
    pilot = next((ab for ab in pairs if {x["name"] for x in ab} == {
        "submitted/v22_antiv52_brunchguard", "submitted/v27_orderbook_layer_d"}), None)
    if pilot:
        pairs.remove(pilot)
        pairs.insert(0, pilot)
    return pairs


def refresh_manifest(manifest: dict) -> tuple[dict, int]:
    """Enroll newly evaluated agents without changing established canonical IDs."""
    snapshot = discover()
    existing = manifest["agents"]

    def identity(item: dict) -> str:
        path = ROOT / item["path"]
        sidecars = sorted(p for p in path.parent.glob("*.py") if p != path)
        return item["sha256"] if not sidecars else item["path"]

    by_identity = {identity(item): item for item in existing}
    known_aliases = {alias for item in existing for alias in item["aliases"]}
    added = 0
    changed = False
    for item in snapshot["agents"]:
        new_aliases = [alias for alias in item["aliases"] if alias not in known_aliases]
        if not new_aliases:
            continue
        key = identity(item)
        if key in by_identity:
            by_identity[key]["aliases"].extend(new_aliases)
        else:
            new_item = {**item, "aliases": new_aliases}
            existing.append(new_item)
            by_identity[key] = new_item
            added += 1
        known_aliases.update(new_aliases)
        changed = True
    known_exclusions = {(x["name"], x["reason"]) for x in manifest["excluded"]}
    for item in snapshot["excluded"]:
        if (item["name"], item["reason"]) not in known_exclusions:
            manifest["excluded"].append(item)
            changed = True
    if changed:
        existing.sort(key=lambda x: x["name"])
        manifest.update(updated_at=now(), candidates=len(known_aliases),
                        unique_agents=len(existing), pairs=len(existing) * (len(existing) - 1) // 2)
    return manifest, added


def pair_key(a: dict, b: dict) -> str:
    return hashlib.sha256((a["name"] + "\0" + b["name"]).encode()).hexdigest()[:20]


def busy() -> bool:
    for path in OTHER_MONITORS:
        monitor = read_json(path, {})
        if monitor.get("state") in {"processing", "running", "evaluating"}:
            try:
                updated = datetime.fromisoformat(monitor["updated_at"].replace("Z", "+00:00"))
                if datetime.now(timezone.utc) - updated < timedelta(hours=2):
                    return True
            except (KeyError, ValueError, TypeError):
                pass
    return False


def standings(results: list[dict], agents: list[dict]) -> list[dict]:
    rows = {x["name"]: {"name": x["name"], "category": x["category"],
                         "aliases": x["aliases"], "wins": 0, "losses": 0,
                         "draws": 0, "pair_diff_total": 0.0} for x in agents}
    for result in results:
        if result["status"] != "complete":
            continue
        a, b = rows[result["a"]], rows[result["b"]]
        for row, win, loss in ((a, result["wins"], result["losses"]),
                               (b, result["losses"], result["wins"])):
            row["wins"] += win
            row["losses"] += loss
            row["draws"] += result["draws"]
        a["pair_diff_total"] += result["pair_diff_mean"]
        b["pair_diff_total"] -= result["pair_diff_mean"]
    return sorted(rows.values(), key=lambda x: (-x["wins"], x["losses"], -x["pair_diff_total"]))


def run(data: Path, max_pairs: int | None = None) -> int:
    data.mkdir(parents=True, exist_ok=True)
    manifest_path, results_path = data / "manifest.json", data / "results.jsonl"
    manifest = read_json(manifest_path, None)
    if manifest is None:
        manifest = discover()
        write_json(manifest_path, manifest)
    agents = manifest["agents"]
    if len(agents) < 2:
        raise RuntimeError("fewer than two eligible agents")
    results = []
    if results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                break
    done = {r["key"] for r in results}
    total = manifest["pairs"]

    def monitor(state: str, **extra: object) -> None:
        write_json(data / "monitor.json", {"state": state, "pid": os.getpid(),
                   "updated_at": now(), "completed": len(done), "total": total, **extra})

    monitor("running", eligible=len(agents), excluded=len(manifest["excluded"]))
    attempted = 0
    last_refresh = 0.0
    pending = schedule(agents)
    while True:
        if time.monotonic() - last_refresh >= 1800:
            manifest, added = refresh_manifest(manifest)
            last_refresh = time.monotonic()
            if added:
                write_json(manifest_path, manifest)
                agents = manifest["agents"]
                total = manifest["pairs"]
                pending = schedule(agents)
            elif manifest.get("updated_at"):
                write_json(manifest_path, manifest)
        next_pair = next(((x, y) for x, y in pending if pair_key(x, y) not in done), None)
        if next_pair is None:
            # Final ledger read catches a notebook that finished during the last matches.
            manifest, added = refresh_manifest(manifest)
            last_refresh = time.monotonic()
            if added:
                write_json(manifest_path, manifest)
                agents = manifest["agents"]
                total = manifest["pairs"]
                pending = schedule(agents)
                continue
            write_json(manifest_path, manifest)
            break
        a, b = next_pair
        key = pair_key(a, b)
        if max_pairs is not None and attempted >= max_pairs:
            break
        while busy():
            monitor("sleeping", reason="other_automation_busy",
                    next_poll_at=(datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat())
            time.sleep(60)
        monitor("processing", current=[a["name"], b["name"]])
        result = {"key": key, "a": a["name"], "b": b["name"], "finished_at": now()}
        try:
            for agent in (a, b):
                path = ROOT / agent["path"]
                if digest(path) != agent["sha256"]:
                    raise ValueError(f"changed agent: {agent['name']}")
            seed = int(key[:8], 16) % 1_000_000 + 1
            output = data / f"current_eval_{os.getpid()}.json"
            command = [sys.executable, str(ROOT / "scripts/eval.py"),
                       str(ROOT / a["path"]), str(ROOT / b["path"]),
                       "-n", "1", "-j", "1", "--seed-start", str(seed),
                       "--json", str(output)]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True,
                                       text=True, encoding="utf-8", errors="replace", timeout=600)
            if completed.returncode:
                raise RuntimeError((completed.stderr or completed.stdout)[-2000:])
            summary = read_json(output, {})
            result.update(status="complete", seed=seed, wins=summary["wins"],
                          losses=summary["losses"], draws=summary["draws"],
                          pair_diff_mean=summary["pair_diff_mean"],
                          exceptions=summary.get("exceptions"))
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, KeyError) as exc:
            result.update(status="failed", error=str(exc)[:2000])
        with results_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        results.append(result)
        done.add(key)
        attempted += 1
        if attempted == 1 and len(done) == 1 and result["status"] != "complete":
            monitor("fatal", error="pilot pairing failed", last_result=result)
            return 1
        if attempted % 10 == 0 or len(done) == total:
            write_json(data / "standings.json", standings(results, agents))
        monitor("running", last_result=result, eligible=len(agents), excluded=len(manifest["excluded"]))
    write_json(data / "standings.json", standings(results, agents))
    monitor("complete" if len(done) == total else "paused", failed=sum(r["status"] != "complete" for r in results))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--max-pairs", type=int)
    args = parser.parse_args()
    try:
        code = run(args.data_dir.resolve(), args.max_pairs)
    except Exception as exc:
        write_json(args.data_dir / "monitor.json", {"state": "fatal", "pid": os.getpid(),
                   "updated_at": now(), "error": repr(exc)})
        code = 1
    append_event("STOPPED" if code == 0 else "FAILED", "Kaggriculture round robin runner",
                 os.getpid(), f"exit={code}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
