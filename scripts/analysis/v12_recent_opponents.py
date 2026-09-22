# -*- coding: utf-8 -*-
"""v12の直近公開リプレイを取得し、最近の相手の行動特徴を抽出する。

仕様: docs/experiments/EXP-20260922-46-v12-recent-opponents.md
"""
from __future__ import annotations

import collections
import csv
import io
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = "56398792"
LIMIT = 24
RAW = ROOT / "data/raw/own_v12_recent"
OUT = ROOT / "data/analysis/v12_recent_opponents"
MONITOR = ROOT / "data/analysis/v12_recent_opponents.monitor.json"
ME_NAMES = {
    "giyogoio hlrlqll",
    "giyogoioが相手の農地を燃やします",
    "giyogoioがすべてのエージェントを破壊します",
}


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(MONITOR, {"state": state, "updated": datetime.now().isoformat(), **extra})


def kaggle(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "kaggle", *args], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8",
    )


def episode_rows() -> list[dict[str, str]]:
    text = kaggle("competitions", "episodes", SUBMISSION, "-v").stdout
    lines = [line for line in text.splitlines() if line[:1].isdigit() or line.startswith("id,")]
    rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
    return [row for row in rows if "PUBLIC" in row.get("type", "")][:LIMIT]


def replay_path(episode: str) -> Path:
    found = list(RAW.glob(f"*{episode}*.json"))
    if not found:
        kaggle("competitions", "replay", episode, "-p", str(RAW))
        found = list(RAW.glob(f"*{episode}*.json"))
    if not found:
        raise FileNotFoundError(f"replay not found after download: {episode}")
    return found[0]


def strip_weeds(farm: dict) -> tuple:
    tiles = tuple(tuple(None if isinstance(tile, dict) and tile.get("kind") == "WEED"
                        else json.dumps(tile, sort_keys=True, ensure_ascii=False)
                        for tile in row) for row in farm.get("tiles", []))
    rest = tuple(sorted((key, json.dumps(value, sort_keys=True, ensure_ascii=False))
                        for key, value in farm.items() if key not in ("tiles", "money")))
    return tiles, rest


def action_at(step: dict, seat: int) -> dict:
    action = step[seat].get("action")
    return action if isinstance(action, dict) else {}


def analyze(path: Path, created: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    names = data["info"]["TeamNames"]
    me = next((index for index, name in enumerate(names) if name in ME_NAMES), None)
    if me is None:
        raise ValueError(f"own team not found: {names}")
    op = 1 - me
    steps = data["steps"]
    rewards = data["rewards"]
    first_physical_diff = None
    for turn, step in enumerate(steps):
        farms = step[0]["observation"]["farms"]
        if strip_weeds(farms[me]) != strip_weeds(farms[op]):
            first_physical_diff = turn
            break

    unit_ops = [collections.Counter(), collections.Counter()]
    market_ops = [collections.Counter(), collections.Counter()]
    sells = [collections.Counter(), collections.Counter()]
    sale_steps = [collections.defaultdict(dict), collections.defaultdict(dict)]
    first_sale = [{}, {}]
    first_unit_action_diff = None
    first_market_action_diff = None
    unit_action_mismatch_turns = 0
    market_action_mismatch_turns = 0
    for turn in range(1, len(steps)):
        me_action = action_at(steps[turn], me)
        op_action = action_at(steps[turn], op)
        me_units = [me_action.get("farmer") or ["PASS"]] + list(me_action.get("hands") or [])
        op_units = [op_action.get("farmer") or ["PASS"]] + list(op_action.get("hands") or [])
        if me_units != op_units:
            unit_action_mismatch_turns += 1
            if first_unit_action_diff is None:
                first_unit_action_diff = turn
        if list(me_action.get("market") or []) != list(op_action.get("market") or []):
            market_action_mismatch_turns += 1
            if first_market_action_diff is None:
                first_market_action_diff = turn
        for seat in (me, op):
            action = action_at(steps[turn], seat)
            commands = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            for command in commands:
                if command:
                    unit_ops[seat][command[0]] += 1
            for order in action.get("market") or []:
                if not isinstance(order, list) or not order:
                    continue
                item = order[1] if len(order) > 1 else ""
                quantity = int(order[2]) if len(order) > 2 and isinstance(order[2], (int, float)) else 0
                market_ops[seat][f"{order[0]}:{item}"] += quantity if quantity else 1
                if order[0] == "SELL" and item:
                    sells[seat][item] += quantity
                    sale_steps[seat][item][turn] = sale_steps[seat][item].get(turn, 0) + quantity
                    first_sale[seat].setdefault(item, turn)

    simultaneous = 0
    op_preempts = 0
    me_preempts = 0
    collision_items = collections.Counter()
    items = set(sale_steps[me]) | set(sale_steps[op])
    for item in items:
        mine = sale_steps[me].get(item, {})
        theirs = sale_steps[op].get(item, {})
        for turn, quantity in theirs.items():
            if turn in mine:
                simultaneous += min(quantity, mine[turn])
                collision_items[item] += min(quantity, mine[turn])
            op_preempts += min(quantity, mine.get(turn + 1, 0) + mine.get(turn + 2, 0))
        for turn, quantity in mine.items():
            me_preempts += min(quantity, theirs.get(turn + 1, 0) + theirs.get(turn + 2, 0))

    daily = {}
    for turn, step in enumerate(steps):
        farms = step[0]["observation"]["farms"]
        daily[str(turn // 24)] = farms[me]["money"] - farms[op]["money"]

    final_farms = steps[-1][0]["observation"]["farms"]
    def composition(farm: dict) -> dict:
        result = collections.Counter()
        for row in farm.get("tiles", []):
            for tile in row:
                if not isinstance(tile, dict):
                    continue
                label = tile.get("animal") or tile.get("crop") or tile.get("kind")
                if label:
                    result[str(label)] += 1
        result["hands"] = len(farm.get("hands", []))
        result["quadrants"] = len(farm.get("unlocked_quadrants", []))
        return dict(result)

    diff = float(rewards[me] or 0) - float(rewards[op] or 0)
    shops = max(
        (list(step[0]["observation"].get("town", {}).get("unlocked_shops", [])) for step in steps),
        key=len,
        default=[],
    )
    return {
        "episode": int(data["info"]["EpisodeId"]), "created": created,
        "seed": data["info"].get("seed"), "opponent": names[op], "me_seat": me,
        "result": "win" if diff > 0 else ("loss" if diff < 0 else "draw"),
        "money": [rewards[me], rewards[op]], "diff": diff,
        "shops": shops,
        "first_physical_diff": first_physical_diff,
        "physical_copy_167": first_physical_diff is None or first_physical_diff > 167,
        "first_unit_action_diff": first_unit_action_diff,
        "first_market_action_diff": first_market_action_diff,
        "unit_action_mismatch_turns": unit_action_mismatch_turns,
        "market_action_mismatch_turns": market_action_mismatch_turns,
        "unit_ops_me": dict(unit_ops[me]), "unit_ops_op": dict(unit_ops[op]),
        "market_ops_me": dict(market_ops[me]), "market_ops_op": dict(market_ops[op]),
        "sells_me": dict(sells[me]), "sells_op": dict(sells[op]),
        "first_sale_me": first_sale[me], "first_sale_op": first_sale[op],
        "simultaneous_sell_units": simultaneous,
        "op_preempts_me_units_1_2": op_preempts,
        "me_preempts_op_units_1_2": me_preempts,
        "collision_items": dict(collision_items), "daily_money_diff": daily,
        "final_composition_me": composition(final_farms[me]),
        "final_composition_op": composition(final_farms[op]),
        "statuses": [entry.get("status") for entry in steps[-1]],
    }


def mean_counter(rows: list[dict], key: str) -> dict:
    names = sorted({name for row in rows for name in row[key]})
    return {name: round(statistics.mean(row[key].get(name, 0) for row in rows), 2) for name in names}


def summarize(rows: list[dict]) -> dict:
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["opponent"]].append(row)

    def group_summary(group: list[dict]) -> dict:
        divergences = [row["first_physical_diff"] for row in group if row["first_physical_diff"] is not None]
        return {
            "games": len(group),
            "wins": sum(row["result"] == "win" for row in group),
            "losses": sum(row["result"] == "loss" for row in group),
            "draws": sum(row["result"] == "draw" for row in group),
            "mean_diff": round(statistics.mean(row["diff"] for row in group), 2),
            "copy_167_games": sum(row["physical_copy_167"] for row in group),
            "median_first_physical_diff": statistics.median(divergences) if divergences else None,
            "mean_simultaneous_sell_units": round(statistics.mean(row["simultaneous_sell_units"] for row in group), 2),
            "mean_op_preempts_me_units_1_2": round(statistics.mean(row["op_preempts_me_units_1_2"] for row in group), 2),
            "mean_me_preempts_op_units_1_2": round(statistics.mean(row["me_preempts_op_units_1_2"] for row in group), 2),
            "mean_unit_ops_op": mean_counter(group, "unit_ops_op"),
            "mean_market_ops_op": mean_counter(group, "market_ops_op"),
            "mean_sells_op": mean_counter(group, "sells_op"),
            "mean_final_composition_op": mean_counter(group, "final_composition_op"),
            "episodes": [row["episode"] for row in group],
        }

    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
    return {
        "submission": SUBMISSION, "limit": LIMIT, "games": len(rows),
        "window": {"newest": rows[0]["created"], "oldest": rows[-1]["created"]},
        "overall": group_summary(rows),
        "opponents": {name: group_summary(group) for name, group in ordered},
    }


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    offline = "--offline" in sys.argv
    if offline:
        previous = json.loads((OUT / "matches.json").read_text(encoding="utf-8"))
        selected = [{"id": str(row["episode"]), "createTime": row["created"]} for row in previous]
    else:
        selected = episode_rows()
    status("running", stage="download", total=len(selected), completed=0,
           current=None, selected=[int(row["id"]) for row in selected])
    paths = []
    for index, row in enumerate(selected, 1):
        status("running", stage="download", total=len(selected), completed=index - 1,
               current=int(row["id"]), selected=[int(value["id"]) for value in selected])
        paths.append((replay_path(row["id"]), row["createTime"]))
    status("running", stage="analyze", total=len(selected), completed=0, current=None)
    rows = []
    for index, (path, created) in enumerate(paths, 1):
        status("running", stage="analyze", total=len(selected), completed=index - 1,
               current=path.name)
        rows.append(analyze(path, created))
        write(OUT / "matches.partial.json", rows)
    summary = summarize(rows)
    write(OUT / "matches.json", rows)
    write(OUT / "summary.json", summary)
    status("complete", stage="done", total=len(selected), completed=len(selected),
           current=None, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
