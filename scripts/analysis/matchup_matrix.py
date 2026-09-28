# -*- coding: utf-8 -*-
"""Evaluate an opponent-pool with one fixed matched-seed panel and build matchup matrices.

Each unordered pair is evaluated by scripts/eval.py. eval.py already swaps seats for every
seed, so every matrix cell uses the same seeds and both seats. Results are resumable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def parse_extra(values: list[str]) -> list[dict]:
    result = []
    for value in values:
        name, sep, path = value.partition("=")
        if not sep or not name or not path:
            raise ValueError(f"--extra-agent must be NAME=PATH: {value!r}")
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = ROOT / file_path
        if not file_path.is_file():
            raise FileNotFoundError(file_path)
        result.append({"name": name, "path": str(file_path.relative_to(ROOT))
                       if file_path.is_relative_to(ROOT) else str(file_path),
                       "sha256": sha256(file_path), "source": "extra"})
    return result


def load_agents(pool_path: Path, extras: list[str]) -> list[dict]:
    pool = read_json(pool_path, {})
    agents = []
    for row in pool.get("resolved", []):
        path = Path(row["path"])
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256(path)
        if row.get("sha256") and actual != row["sha256"]:
            raise ValueError(f"SHA mismatch: {row['name']}")
        agents.append({**row, "path": str(path.relative_to(ROOT))
                       if path.is_relative_to(ROOT) else str(path), "sha256": actual,
                       "source": "cluster"})
    agents.extend(parse_extra(extras))
    seen = set()
    unique = []
    for row in agents:
        if row["name"] in seen:
            raise ValueError(f"duplicate agent name: {row['name']}")
        seen.add(row["name"])
        unique.append(row)
    return sorted(unique, key=lambda row: row["name"])


def pair_key(a: dict, b: dict, seed_start: int, seeds: int) -> str:
    left, right = sorted((a["name"], b["name"]))
    payload = f"{left}\0{right}\0{seed_start}\0{seeds}"
    return hashlib.sha256(payload.encode()).hexdigest()[:20]


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            break
    return rows


def directed_cells(agents: list[dict], results: list[dict]) -> dict[str, dict[str, dict]]:
    cells = {a["name"]: {} for a in agents}
    for a in agents:
        cells[a["name"]][a["name"]] = {
            "wins": None, "losses": None, "draws": None,
            "win_rate": None, "pair_diff_mean": 0.0,
        }
    for row in results:
        if row.get("status") != "complete":
            continue
        a, b = row["a"], row["b"]
        total = row["wins"] + row["losses"] + row["draws"]
        rate_a = (row["wins"] + 0.5 * row["draws"]) / total if total else None
        rate_b = (row["losses"] + 0.5 * row["draws"]) / total if total else None
        cells[a][b] = {
            "wins": row["wins"], "losses": row["losses"], "draws": row["draws"],
            "win_rate": rate_a, "pair_diff_mean": row["pair_diff_mean"],
        }
        cells[b][a] = {
            "wins": row["losses"], "losses": row["wins"], "draws": row["draws"],
            "win_rate": rate_b, "pair_diff_mean": -row["pair_diff_mean"],
        }
    return cells


def weakness_summary(agents: list[dict], cells: dict[str, dict[str, dict]]) -> list[dict]:
    rows = []
    for agent in agents:
        name = agent["name"]
        opponents = [cell for other, cell in cells[name].items()
                     if other != name and cell.get("win_rate") is not None]
        if not opponents:
            mean_rate = None
            worst = None
        else:
            mean_rate = sum(cell["win_rate"] for cell in opponents) / len(opponents)
            worst = min(cell["win_rate"] for cell in opponents)
        rows.append({
            "name": name,
            "source": agent.get("source"),
            "cluster": agent.get("cluster"),
            "matchups": len(opponents),
            "mean_win_rate": mean_rate,
            "worst_win_rate": worst,
        })
    return rows


def write_matrix_csv(path: Path, agents: list[dict], cells: dict[str, dict[str, dict]],
                     field: str) -> None:
    names = [row["name"] for row in agents]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["agent", *names])
        for name in names:
            values = []
            for other in names:
                value = cells.get(name, {}).get(other, {}).get(field)
                values.append("" if value is None else value)
            writer.writerow([name, *values])


def evaluate_pair(a: dict, b: dict, seed_start: int, seeds: int, jobs: int,
                  temp_path: Path) -> dict:
    for agent in (a, b):
        path = Path(agent["path"])
        if not path.is_absolute():
            path = ROOT / path
        if sha256(path) != agent["sha256"]:
            raise ValueError(f"agent changed after manifest load: {agent['name']}")

    a_path = Path(a["path"])
    b_path = Path(b["path"])
    if not a_path.is_absolute():
        a_path = ROOT / a_path
    if not b_path.is_absolute():
        b_path = ROOT / b_path
    command = [
        sys.executable, str(ROOT / "scripts/eval.py"),
        str(a_path), str(b_path),
        "-n", str(seeds), "-j", str(jobs),
        "--seed-start", str(seed_start), "--json", str(temp_path),
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=max(600, seeds * 30))
    if completed.returncode:
        raise RuntimeError((completed.stderr or completed.stdout)[-3000:])
    summary = read_json(temp_path, {})
    return {
        "wins": int(summary["wins"]),
        "losses": int(summary["losses"]),
        "draws": int(summary["draws"]),
        "pair_diff_mean": float(summary["pair_diff_mean"]),
        "exceptions": summary.get("exceptions"),
    }


def run(pool_path: Path, out_dir: Path, seed_start: int, seeds: int, jobs: int,
        extras: list[str], max_pairs: int | None = None) -> dict:
    agents = load_agents(pool_path, extras)
    if len(agents) < 2:
        raise ValueError("need at least two resolved/extra agents")
    if seeds < 1:
        raise ValueError("--seeds must be >= 1")

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    ledger_path = out_dir / "results.jsonl"
    manifest = {
        "seed_start": seed_start,
        "seeds": seeds,
        "seat_swap": True,
        "agents": agents,
    }
    previous_manifest = read_json(manifest_path, None)
    if previous_manifest is not None and previous_manifest != manifest:
        raise ValueError("existing matrix manifest differs; use a new --out-dir")
    write_json(manifest_path, manifest)

    results = read_ledger(ledger_path)
    done = {row["key"] for row in results if row.get("status") == "complete"}
    attempted = 0
    for i, a in enumerate(agents):
        for b in agents[i + 1:]:
            key = pair_key(a, b, seed_start, seeds)
            if key in done:
                continue
            if max_pairs is not None and attempted >= max_pairs:
                break
            row = {"key": key, "a": a["name"], "b": b["name"],
                   "seed_start": seed_start, "seeds": seeds}
            try:
                temp_path = out_dir / f".current-{os.getpid()}.json"
                row.update(status="complete",
                           **evaluate_pair(a, b, seed_start, seeds, jobs, temp_path))
                done.add(key)
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, KeyError) as exc:
                row.update(status="failed", error=repr(exc))
            with ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            results.append(row)
            attempted += 1
        if max_pairs is not None and attempted >= max_pairs:
            break

    cells = directed_cells(agents, results)
    summary = {
        "seed_start": seed_start,
        "seeds": seeds,
        "seat_swap": True,
        "agents": [row["name"] for row in agents],
        "complete_pairs": sum(row.get("status") == "complete" for row in results),
        "failed_pairs": sum(row.get("status") == "failed" for row in results),
        "cells": cells,
        "agent_summary": weakness_summary(agents, cells),
    }
    write_json(out_dir / "matrix.json", summary)
    write_matrix_csv(out_dir / "win_rate.csv", agents, cells, "win_rate")
    write_matrix_csv(out_dir / "pair_diff.csv", agents, cells, "pair_diff_mean")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fixed-seed seat-swapped matchup matrix")
    parser.add_argument("--pool", type=Path,
                        default=ROOT / "data/analysis/strategy_pool/opponent_pool.json")
    parser.add_argument("--out-dir", type=Path,
                        default=ROOT / "data/analysis/strategy_pool/matchup_matrix")
    parser.add_argument("--seed-start", type=int, required=True,
                        help="Exploratory/burned seed panel start. Do not use reserved sealed seeds.")
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--extra-agent", action="append", default=[],
                        help="NAME=PATH; useful for champion/checkpoints")
    parser.add_argument("--max-pairs", type=int, help="smoke test / resumable partial run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(args.pool, args.out_dir, args.seed_start, args.seeds, args.jobs,
                  args.extra_agent, args.max_pairs)
    print(f"matrix: {len(summary['agents'])} agents, "
          f"{summary['complete_pairs']} complete, {summary['failed_pairs']} failed; "
          f"{args.seeds} matched seeds x both seats per pair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
