# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "landscape", ROOT / "scripts/analysis/classify_v22_agent_landscape.py"
)
landscape = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(landscape)


def row(**updates):
    value = {
        "episode": 1, "created": "x", "opponent": "agent", "result": "win", "diff": 1,
        "first_physical_diff": 200, "first_market_action_diff": 1,
        "sells_op": {"WHEAT": 100}, "final_composition_op": {"SHEEP": 6, "COW": 6},
        "op_preempts_me_units_1_2": 10, "me_preempts_op_units_1_2": 5, "shops": [],
    }
    value.update(updates)
    return value


def test_late_clone_with_early_market_difference_is_orderbook_variant():
    assert landscape.market_layer(row()) == "same_farm_different_orderbook"


def test_early_physical_difference_is_independent_planner():
    target = row(first_physical_diff=3)
    assert landscape.farm_lineage(target) == "early_independent_0_24"
    assert landscape.market_layer(target) == "different_farm_planner"


def test_bulk_sell_and_sheep_focus():
    target = row(sells_op={"WHEAT": 50000}, final_composition_op={"SHEEP": 11})
    assert landscape.sell_style(target)[0] == "bulk_reservation_40kplus"
    assert landscape.farm_focus(target) == "sheep_wool_heavy"


def test_tomato_or_four_quadrants_marks_expansion():
    assert landscape.farm_focus(row(final_composition_op={"TOMATO": 4})) == "tomato_land_expansion"
    assert landscape.farm_focus(row(final_composition_op={"quadrants": 4})) == "tomato_land_expansion"
