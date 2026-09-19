"""ルールベース・ベースラインの受け入れ条件テスト。

仕様: docs/04_model_design.md §5.2（マクロ）, §5.3（実行層）, §5.5（受け入れ条件）
"""
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import execute, features, macro  # noqa: E402
import main as submission  # noqa: E402

BOARD = 10


def _tiles(entries=None, unlocked=("NW",)):
    """(x, y) → タイル。指定が無ければ NW だけ空き、他は LOCKED。"""
    grid = [[None] * BOARD for _ in range(BOARD)]
    for y in range(BOARD):
        for x in range(BOARD):
            quadrant = ("NW" if x < 5 else "NE") if y < 5 else ("SW" if x < 5 else "SE")
            if quadrant not in unlocked:
                grid[y][x] = "LOCKED"
    for (x, y), tile in (entries or {}).items():
        grid[y][x] = tile
    return grid


def _obs(day=0, hour=0, money=3000.0, tiles=None, shed=None, seeds=None,
         hands=(), inventories=None, seat=0, hires_today=0, unlocked=("NW",)):
    tiles = tiles if tiles is not None else _tiles(unlocked=unlocked)
    farm = {
        "money": money, "tiles": tiles, "farmer": [4, 4], "hands": [list(h) for h in hands],
        "unlocked_quadrants": list(unlocked), "hires_today": hires_today,
    }
    other = {
        "money": 3000.0, "tiles": _tiles(), "farmer": [4, 4], "hands": [],
        "unlocked_quadrants": ["NW"], "hires_today": 0,
    }
    return {
        "player": seat,
        "day": day,
        "hour": hour,
        "farms": [farm, other] if seat == 0 else [other, farm],
        "market": {"prices": {p: 25 for p in features.PRODUCTS},
                   "inventory": {p: 10000 for p in features.PRODUCTS}},
        "town": {"unlocked_shops": []},
        "private": {
            "shed": shed or {},
            "seeds": seeds or {},
            "inventories": inventories or [{} for _ in range(1 + len(hands))],
        },
    }


def _plant(crop, planted_day=0, watered=False, yield_units=0):
    return {"kind": "PLANT", "crop": crop, "planted_day": planted_day,
            "watered_today": watered, "consecutive_unwatered": 0, "yield_units": yield_units,
            "max_lifespan_step": -1, "fertilized_until_day": -1}


def _animal(kind="PASTURE", animal="COW", fed=False, yield_units=0, cared=False, fert=False):
    return {"kind": kind, "animal": animal, "placed_day": 0, "yield_units": yield_units,
            "fed_today": fed, "consecutive_unfed": 0, "cared_today": cared,
            "fertilizer_available": fert, "pending_care_bonus": 0}


# ---------------------------------------------------------------- features


def test_turn_index_without_step_key():
    """席1の観測には step が無いので day/hour から作る（doc 03 §3.2, 04 §5.4）。"""
    obs = _obs(day=3, hour=7, seat=1)
    assert "step" not in obs
    assert features.turn_index(obs) == 3 * 24 + 7


def test_shed_access_tiles():
    assert features.shed_access_tiles(BOARD) == [(4, 4), (5, 4), (4, 5), (5, 5)]
    assert features.is_shed_adjacent((5, 5), BOARD)
    assert not features.is_shed_adjacent((3, 3), BOARD)


# ---------------------------------------------------------------- マクロ


def test_day0_buys_seeds_and_animals():
    """day0 に MELON 12 / WHEAT 10 / COW 3 / SHEEP 2 を買う（doc 04 §5.2）。"""
    orders = macro.decide_market(_obs(day=0, hour=0))
    kinds = [(o[0], o[1] if len(o) > 1 else "", o[2] if len(o) > 2 else 1) for o in orders]
    assert ("BUY_SEED", "MELON", 12) in kinds or ("BUY_SEED", "MELON", 12.0) in kinds
    assert any(k[0] == "BUY_SEED" and k[1] == "WHEAT" for k in kinds)
    assert ["HIRE"] in orders


def test_orders_respect_limit():
    """1ターン最大10注文（doc 04 §5.2）。"""
    shed = {p: 30 for p in features.PRODUCTS}
    orders = macro.decide_market(_obs(day=12, hour=5, money=50000.0, shed=shed))
    assert len(orders) <= 10


def test_buys_land_on_schedule():
    """day6 に2枚目、day11 に3枚目（doc 04 §5.2）。"""
    orders = macro.decide_market(_obs(day=6, hour=0, money=5000.0))
    assert ["BUY_LAND"] in orders
    orders = macro.decide_market(_obs(day=11, hour=0, money=5000.0, unlocked=("NW", "NE")))
    assert ["BUY_LAND"] in orders
    # 予定日でなければ買わない
    orders = macro.decide_market(_obs(day=7, hour=0, money=5000.0, unlocked=("NW", "NE")))
    assert ["BUY_LAND"] not in orders


def test_land_not_bought_twice():
    orders = macro.decide_market(_obs(day=6, hour=0, money=5000.0, unlocked=("NW", "NE")))
    assert ["BUY_LAND"] not in orders


def test_sells_from_shed_but_keeps_wheat_for_feed():
    """WHEAT は餌の分を残して売る（doc 04 §5.1, §5.2）。"""
    tiles = _tiles({(0, 0): _animal(), (1, 0): _animal()})
    obs = _obs(day=12, hour=3, tiles=tiles, shed={"WHEAT": 20, "MILK": 5, "COW": 1})
    orders = macro.decide_market(obs)
    sells = {o[1]: o[2] for o in orders if o[0] == "SELL"}
    assert sells.get("MILK") == 5
    assert "COW" not in sells  # 家畜は売らない
    # 餌（家畜2頭 × feed_per_animal）＋予備を残して売る
    reserve = 2 * macro.PARAMS["feed_per_animal"] + macro.PARAMS["feed_buffer"]
    assert sells.get("WHEAT") == 20 - reserve


def test_buys_wheat_when_feed_is_short():
    tiles = _tiles({(0, 0): _animal(), (1, 0): _animal(), (2, 0): _animal()})
    obs = _obs(day=3, hour=0, tiles=tiles, shed={"WHEAT": 1})
    orders = macro.decide_market(obs)
    assert any(o[0] == "BUY_PRODUCT" and o[1] == "WHEAT" for o in orders)


def test_stops_planting_late():
    """stop_planting_day 以降は種を買わない（doc 04 §5.2）。"""
    orders = macro.decide_market(_obs(day=28, hour=0, money=50000.0))
    assert not any(o[0] == "BUY_SEED" for o in orders)


# ---------------------------------------------------------------- 実行層


def test_water_has_priority_over_harvest():
    """水やりが最優先（doc 04 §5.3）。"""
    tiles = _tiles({(4, 4): _plant("WHEAT", watered=False, yield_units=3)})
    actions = execute.assign(_obs(day=5, hour=5, tiles=tiles))
    assert actions["farmer"] == ["WATER"]


def test_feed_requires_wheat_in_inventory():
    """WHEAT を持っていなければ shed へ取りに行く（doc 04 §5.1）。"""
    tiles = _tiles({(4, 4): _animal(fed=False)})
    obs = _obs(day=5, hour=5, tiles=tiles, shed={"WHEAT": 10}, inventories=[{}])
    actions = execute.assign(obs)
    assert actions["farmer"][0] == "PICKUP" and actions["farmer"][1] == "WHEAT"

    obs = _obs(day=5, hour=5, tiles=tiles, shed={"WHEAT": 10}, inventories=[{"WHEAT": 5}])
    assert execute.assign(obs)["farmer"] == ["FEED"]


def test_moves_toward_task():
    tiles = _tiles({(0, 0): _plant("WHEAT")})
    actions = execute.assign(_obs(day=5, hour=5, tiles=tiles))
    assert actions["farmer"][0] in ("WEST", "NORTH")


def test_plants_on_empty_tile_with_seeds():
    obs = _obs(day=1, hour=5, seeds={"MELON": 3})
    actions = execute.assign(obs)
    assert actions["farmer"] == ["PLANT", "MELON"]


def test_late_game_plants_carrot():
    obs = _obs(day=26, hour=5, seeds={"CARROT": 2, "STRAWBERRY": 5})
    assert execute.assign(obs)["farmer"] == ["PLANT", "CARROT"]


def test_drops_inventory_when_full():
    """インベントリが溜まったら shed へ（doc 04 §5.3 優先度4）。"""
    obs = _obs(day=12, hour=5, inventories=[{"MILK": 12}])
    assert execute.assign(obs)["farmer"] == ["DROP"]


def test_places_animal_on_structure():
    tiles = _tiles({(4, 4): {"kind": "PASTURE"}})
    obs = _obs(day=2, hour=5, tiles=tiles, inventories=[{"COW": 1}])
    assert execute.assign(obs)["farmer"] == ["PLACE", "COW", 1]


def test_digs_weed():
    tiles = _tiles({(4, 4): {"kind": "WEED"}})
    obs = _obs(day=12, hour=5, tiles=tiles, seeds={})
    assert execute.assign(obs)["farmer"] == ["DIG"]


def test_hands_get_their_own_actions():
    """ハンドの数だけ行動を返し、同じタスクを重複割り当てしない（doc 04 §5.3）。"""
    tiles = _tiles({(4, 4): _plant("WHEAT"), (3, 4): _plant("WHEAT"), (2, 4): _plant("WHEAT")})
    obs = _obs(day=5, hour=5, tiles=tiles, hands=[(3, 4), (0, 0)],
               inventories=[{}, {}, {}])
    actions = execute.assign(obs)
    assert len(actions["hands"]) == 2
    assert actions["farmer"] == ["WATER"]
    assert actions["hands"][0] == ["WATER"]  # (3,4) の上に立っている
    assert actions["hands"][1][0] in ("NORTH", "SOUTH", "EAST", "WEST", "PASS")


def test_never_acts_on_locked_tile():
    """LOCKED の上ではタイル操作をしない（doc 04 §5.1）。"""
    obs = _obs(day=5, hour=5, hands=[(9, 9)], inventories=[{}, {}], seeds={"WHEAT": 5})
    actions = execute.assign(obs)
    assert actions["hands"][0][0] not in ("PLANT", "WATER", "BUILD_COOP", "BUILD_PASTURE", "DIG")


# ---------------------------------------------------------------- main.py


def test_agent_returns_valid_shape():
    result = submission.agent(_obs(day=0, hour=0))
    assert set(result) == {"farmer", "hands", "market"}
    assert isinstance(result["farmer"], list)
    assert isinstance(result["hands"], list)
    assert isinstance(result["market"], list)


def test_agent_never_raises():
    """壊れた観測でも例外を出さずフォールバックする（NFR-2 / doc 04 §5.4）。"""
    for broken in ({}, {"player": 0}, {"farms": []}, {"player": 5, "farms": [{}]}, None):
        result = submission.agent(broken)
        assert result["farmer"] == ["PASS"]
        assert result["market"] == []


def test_agent_is_last_callable():
    """提出仕様：最後に定義された callable が agent（doc 06）。"""
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    callables = [line for line in source.splitlines() if line.startswith("def ")]
    assert callables[-1].startswith("def agent(")


@pytest.mark.slow
def test_full_game_against_starter():
    """720ターン完走・例外ゼロ・推論50ms以内・家畜の逃走ゼロ（doc 04 §5.5）。"""
    from kaggle_environments import make

    timings: list[float] = []

    def timed_agent(obs, config=None):
        start = time.perf_counter()
        action = submission.agent(obs, config)
        timings.append(time.perf_counter() - start)
        return action

    env = make("kaggriculture", configuration={"seed": 7}, debug=True)
    env.run([timed_agent, "starter"])
    steps = env.steps
    assert len(steps) == 720
    assert steps[-1][0]["status"] == "DONE"
    assert all(not step[0].get("info") for step in steps), "エラー情報が記録されている"
    assert max(timings) < 0.05, f"最悪 {max(timings) * 1000:.1f}ms"

    final = steps[-1][0]["observation"]
    mine, theirs = env.state[0]["reward"], env.state[1]["reward"]
    assert mine > theirs, f"starter に負けた: {mine} vs {theirs}"

    farm = final["farms"][0]
    animals = sum(
        1 for row in farm["tiles"] for tile in row
        if isinstance(tile, dict) and tile.get("animal")
    )
    assert animals > 0, "家畜が全部いなくなっている"
    shed_total = sum(final["private"]["shed"].values()) if "private" in final else 0
    assert shed_total < 100, f"shed が溢れている: {shed_total}"
