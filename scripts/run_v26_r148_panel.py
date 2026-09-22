# -*- coding: utf-8 -*-
"""v26 R148をv25と同一seed・同一相手で順次評価し、発火量も記録する。

仕様: docs/experiments/EXP-20260922-51-v25-r148-overflow.md
"""
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.eval import _TimedAgent, health_metrics, resolve_agent  # noqa: E402

OUT = ROOT / "data/eval/v26_r148_panel"
STATUS = ROOT / "data/eval/v26_r148_panel.monitor.json"
CANDIDATE = "submissions/v26_r148_overflow/main.py"
BASELINE = "submissions/v25_e402_e410/main.py"
CANDIDATE_LABEL = "v26"
OPPONENTS = [
    ("jaxa", "opponents/jaxa_2802/main.py", 241),
    ("order_book", "opponents/order_book/main.py", 1501),
    ("pipe19", "opponents/pipe19/main.py", 1501),
    ("v49", "opponents/v49/main.py", 241),
    ("more_wheat", "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py", 1501),
]
PAIRS = 5


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def play(agent_path: str, opponent_path: str, seed: int, swap: bool) -> dict:
    from kaggle_environments import make

    raw_a = resolve_agent(agent_path)
    raw_b = resolve_agent(opponent_path)
    agent_a, agent_b = _TimedAgent(raw_a), _TimedAgent(raw_b)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([agent_b, agent_a] if swap else [agent_a, agent_b])
    seat_a = 1 if swap else 0
    rewards = [state["reward"] for state in env.state]
    telemetry = getattr(raw_a, "telemetry", {})
    return {
        "seed": seed,
        "swap": swap,
        "money": [rewards[seat_a], rewards[1 - seat_a]],
        "exceptions": {"a": agent_a.exceptions, "b": agent_b.exceptions},
        "animals_lost": health_metrics(env.steps, seat_a)["animals_lost"],
        "timing_max_ms": max(agent_a.timings, default=0) * 1000,
        "telemetry": dict(telemetry) if hasattr(telemetry, "items") else {},
    }


def run_set(agent_path: str, opponent_path: str, seed_start: int) -> tuple[dict, list[dict]]:
    matches = []
    begun = time.perf_counter()
    for seed in range(seed_start, seed_start + PAIRS):
        matches.append(play(agent_path, opponent_path, seed, False))
        matches.append(play(agent_path, opponent_path, seed, True))
    differences = [
        sum(match["money"][0] - match["money"][1] for match in matches[index:index + 2]) / 2
        for index in range(0, len(matches), 2)
    ]
    overflow_turns = sum(match["telemetry"].get("overflow_turns", 0) for match in matches)
    overflow_units = sum(match["telemetry"].get("overflow_units", 0) for match in matches)
    telemetry_sums = {}
    for match in matches:
        for key, value in match["telemetry"].items():
            if isinstance(value, (int, float)):
                telemetry_sums[key] = telemetry_sums.get(key, 0) + value
    row = {
        "wins": sum(value > 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
        "draws": sum(value == 0 for value in differences),
        "pair_diff_mean": statistics.mean(differences),
        "pair_diff_stderr": statistics.stdev(differences) / PAIRS ** 0.5,
        "exceptions_a": sum(match["exceptions"]["a"] for match in matches),
        "animals_lost": sum(match["animals_lost"] for match in matches),
        "timing_max_ms": max(match["timing_max_ms"] for match in matches),
        "overflow_turns": overflow_turns,
        "overflow_units": overflow_units,
        "telemetry_sums": telemetry_sums,
        "seconds": time.perf_counter() - begun,
    }
    return row, matches


def main() -> int:
    tasks = [(name, variant, path, opponent, seed)
             for name, opponent, seed in OPPONENTS
             for variant, path in (("v25", BASELINE), (CANDIDATE_LABEL, CANDIDATE))]
    rows = []
    status("running", total=len(tasks), completed=0, current=None, results=[])
    for index, (name, variant, path, opponent, seed) in enumerate(tasks, 1):
        label = f"{variant}_vs_{name}"
        status("running", total=len(tasks), completed=index - 1, current=label, results=rows)
        row, matches = run_set(path, opponent, seed)
        row.update(name=name, variant=variant)
        write(OUT / f"{label}.json", {"summary": row, "matches": matches})
        rows.append(row)
        status("running", total=len(tasks), completed=index, current=None, results=rows)
    comparisons = []
    for name, _opponent, _seed in OPPONENTS:
        base = next(row for row in rows if row["name"] == name and row["variant"] == "v25")
        candidate = next(row for row in rows if row["name"] == name and row["variant"] == CANDIDATE_LABEL)
        comparisons.append({
            "name": name,
            "win_delta": candidate["wins"] - base["wins"],
            "mean_delta": candidate["pair_diff_mean"] - base["pair_diff_mean"],
            "overflow_turns": candidate["overflow_turns"],
            "overflow_units": candidate["overflow_units"],
            "v25": base,
            "candidate_label": CANDIDATE_LABEL,
            "candidate": candidate,
        })
    passed = not any(item["win_delta"] < 0 or item["v26"]["exceptions_a"]
                     or item["v26"]["animals_lost"] > item["v25"]["animals_lost"]
                     for item in comparisons)
    summary = {"passed": passed, "comparisons": comparisons}
    write(OUT / "summary.json", summary)
    status("complete", total=len(tasks), completed=len(tasks), current=None,
           passed=passed, results=rows, summary=str(OUT / "summary.json"))
    return 0 if passed else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
