# -*- coding: utf-8 -*-
"""v22リプレイの相手を行動特徴で分類する。仕様: EXP-20260922-54。"""
from __future__ import annotations

import collections
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/analysis/v22_recent_opponents/matches.json"
OUT = ROOT / "data/analysis/v22_agent_landscape"


def farm_lineage(row: dict[str, Any]) -> str:
    turn = row.get("first_physical_diff")
    if turn is None or turn > 167:
        return "late_clone_168plus"
    if turn <= 24:
        return "early_independent_0_24"
    return "mid_branch_25_167"


def market_layer(row: dict[str, Any]) -> str:
    lineage = farm_lineage(row)
    market_turn = row.get("first_market_action_diff")
    if lineage == "late_clone_168plus" and market_turn is not None and market_turn <= 3:
        return "same_farm_different_orderbook"
    if lineage == "late_clone_168plus":
        return "near_clone_market"
    return "different_farm_planner"


def sell_style(row: dict[str, Any]) -> tuple[str, int]:
    total = int(sum((row.get("sells_op") or {}).values()))
    if total >= 40_000:
        return "bulk_reservation_40kplus", total
    if total >= 10_000:
        return "aggressive_orders_10k_40k", total
    return "inventory_sized_under10k", total


def farm_focus(row: dict[str, Any]) -> str:
    final = row.get("final_composition_op") or {}
    sheep = int(final.get("SHEEP", 0))
    cows = int(final.get("COW", 0))
    geese = int(final.get("GOOSE", 0))
    coops = int(final.get("COOP", 0))
    tomatoes = int(final.get("TOMATO", 0))
    quadrants = int(final.get("quadrants", 0))
    if tomatoes or quadrants >= 4:
        return "tomato_land_expansion"
    if sheep >= 10 and geese == 0:
        return "sheep_wool_heavy"
    if geese >= 4 or coops >= 2:
        return "poultry_egg_mixed"
    if cows >= 8:
        return "cattle_milk_heavy"
    return "balanced_livestock"


def classify(row: dict[str, Any]) -> dict[str, Any]:
    style, sell_total = sell_style(row)
    op_preempts = int(row.get("op_preempts_me_units_1_2", 0))
    me_preempts = int(row.get("me_preempts_op_units_1_2", 0))
    return {
        "episode": row["episode"],
        "created": row.get("created"),
        "opponent": row["opponent"],
        "result": row.get("result"),
        "diff": row.get("diff"),
        "first_physical_diff": row.get("first_physical_diff"),
        "first_market_action_diff": row.get("first_market_action_diff"),
        "farm_lineage": farm_lineage(row),
        "market_layer": market_layer(row),
        "sell_style": style,
        "sell_order_units": sell_total,
        "farm_focus": farm_focus(row),
        "preemption_balance": op_preempts - me_preempts,
        "final_composition": row.get("final_composition_op") or {},
        "first_two_shops": (row.get("shops") or [])[:2],
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    classified = [classify(row) for row in rows]

    def distribution(key: str) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
        for row in classified:
            groups[str(row[key])].append(row)
        result = {}
        for label, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
            result[label] = {
                "count": len(group),
                "opponents": [item["opponent"] for item in group],
                "median_sell_order_units": statistics.median(item["sell_order_units"] for item in group),
                "median_preemption_balance": statistics.median(item["preemption_balance"] for item in group),
            }
        return result

    combinations = collections.Counter(
        (row["farm_lineage"], row["sell_style"], row["farm_focus"]) for row in classified
    )
    return {
        "games": len(classified),
        "window": {
            "newest": classified[0]["created"] if classified else None,
            "oldest": classified[-1]["created"] if classified else None,
        },
        "farm_lineage": distribution("farm_lineage"),
        "market_layer": distribution("market_layer"),
        "sell_style": distribution("sell_style"),
        "farm_focus": distribution("farm_focus"),
        "common_combinations": [
            {"farm_lineage": key[0], "sell_style": key[1], "farm_focus": key[2], "count": count}
            for key, count in combinations.most_common()
        ],
        "agents": classified,
    }


def markdown(summary: dict[str, Any]) -> str:
    labels = {
        "late_clone_168plus": "168 step以降まで同型",
        "mid_branch_25_167": "25〜167 stepで分岐",
        "early_independent_0_24": "24 step以内に独立",
        "same_farm_different_orderbook": "同じ農場＋別order book",
        "near_clone_market": "農場・市場とも近縁",
        "different_farm_planner": "別農場プランナー",
        "bulk_reservation_40kplus": "大量予約SELL（4万以上）",
        "aggressive_orders_10k_40k": "積極SELL（1万〜4万）",
        "inventory_sized_under10k": "在庫量相当SELL（1万未満）",
        "tomato_land_expansion": "TOMATO・土地拡張",
        "sheep_wool_heavy": "羊・WOOL偏重",
        "poultry_egg_mixed": "家禽・EGG混合",
        "cattle_milk_heavy": "牛・MILK偏重",
        "balanced_livestock": "家畜均衡",
    }
    lines = [
        "# v22対戦相手の行動分布", "",
        f"対象: {summary['games']}戦（{summary['window']['oldest']} 〜 {summary['window']['newest']} UTC）", "",
    ]
    for title, key in (("農場系統", "farm_lineage"), ("市場層", "market_layer"),
                       ("SELL方式", "sell_style"), ("農場重点", "farm_focus")):
        lines += [f"## {title}", "", "| 分類 | 件数 | 相手 |", "|---|---:|---|"]
        for label, item in summary[key].items():
            lines.append(f"| {labels.get(label, label)} | {item['count']} | {', '.join(item['opponents'])} |")
        lines.append("")
    lines += [
        "## 注意", "",
        "これは各seedの店舗構成を含む1試合の行動分類であり、コード同一性や固定戦略を断定するものではない。",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = summarize(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "landscape.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "summary.md").write_text(markdown(result), encoding="utf-8")
    print(f"classified {len(rows)} games -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
