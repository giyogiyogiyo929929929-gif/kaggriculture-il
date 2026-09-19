"""模倣モデルの実行時統合（タスク 1-3）の受け入れ条件テスト。

仕様: docs/04_model_design.md §3.2（Plan）, §3.5（実行時・安全装置）, §3.6（受け入れ条件 1-3）
"""
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import features, macro, plan  # noqa: E402

BOARD = 10
LEARNED = ["WHEAT", "CARROT", "STRAWBERRY"]


def _tiles(entries=None, unlocked=("NW",)):
    grid = [[None] * BOARD for _ in range(BOARD)]
    for y in range(BOARD):
        for x in range(BOARD):
            quadrant = ("NW" if x < 5 else "NE") if y < 5 else ("SW" if x < 5 else "SE")
            if quadrant not in unlocked:
                grid[y][x] = "LOCKED"
    for (x, y), tile in (entries or {}).items():
        grid[y][x] = tile
    return grid


def _plant(crop):
    return {"kind": "PLANT", "crop": crop, "planted_day": 0, "watered_today": False,
            "consecutive_unwatered": 0, "yield_units": 0, "max_lifespan_step": -1,
            "fertilized_until_day": -1}


def _obs(day=5, hour=0, money=3000.0, seat=0, entries=None, seeds=None, unlocked=("NW",)):
    farm = {"money": money, "tiles": _tiles(entries, unlocked), "farmer": [4, 4], "hands": [],
            "unlocked_quadrants": list(unlocked), "hires_today": 0}
    other = {"money": 3000.0, "tiles": _tiles(), "farmer": [4, 4], "hands": [],
             "unlocked_quadrants": ["NW"], "hires_today": 0}
    return {
        "player": seat, "day": day, "hour": hour,
        "farms": [farm, other] if seat == 0 else [other, farm],
        "market": {"prices": {p: 25 for p in features.PRODUCTS},
                   "inventory": {p: 10000 for p in features.PRODUCTS}},
        "town": {"unlocked_shops": []},
        "private": {"shed": {}, "seeds": seeds or {}, "inventories": [{}]},
    }


def _constant_model(values: dict, land_raw: float = -10.0) -> dict:
    """木1本（葉だけ）で定数を返すモデル。`predict_heads` の形（agent/plan.py）。"""
    heads = {f"target_seed_{crop}": {"kind": "regression", "trees": [float(values.get(crop, 0.0))]}
             for crop in LEARNED}
    heads["buy_land"] = {"kind": "binary", "sigmoid": 1.0, "trees": [land_raw]}
    return {"format": plan.FORMAT_VERSION, "feature_names": list(features.FEATURE_NAMES), "heads": heads}


@pytest.fixture(autouse=True)
def _fresh_caches():
    plan.reset()
    yield
    plan.reset()


# ---------------------------------------------------------------- predict_plan


def test_default_model_path_is_next_to_agent_package():
    """本番では tar が展開された場所の models/macro.json を見る（doc 06）。main.py の __file__ は使わない。"""
    assert Path(plan.DEFAULT_MODEL_PATH) == ROOT / "models" / "macro.json"


def test_predict_plan_with_real_model_has_learned_crops_only():
    model = plan.get_model()
    assert model is not None, "models/macro.json が読めない（scripts\\train_macro.py を実行する）"
    result = plan.predict_plan(_obs(day=5), model)
    assert set(result["seed_targets"]) == set(LEARNED)  # TOMATO・MELON はルール表のまま（§3.2）
    assert all(isinstance(v, int) for v in result["seed_targets"].values())
    assert isinstance(result["want_land"], bool)
    assert isinstance(result["land_target"], int)


def test_predict_plan_rounds_and_clamps_to_holdings():
    """整数に丸め、保有（植え付け済み＋種在庫）以上にクランプする（§3.5 の訂正後の定義）。"""
    entries = {(0, 0): _plant("WHEAT"), (1, 0): _plant("WHEAT"), (2, 0): _plant("STRAWBERRY")}
    obs = _obs(entries=entries, seeds={"WHEAT": 3})
    model = _constant_model({"WHEAT": -100.0, "CARROT": 7.6, "STRAWBERRY": 0.4})
    targets = plan.predict_plan(obs, model)["seed_targets"]
    assert targets["WHEAT"] == 2 + 3          # 予測が保有より下 → 保有
    assert targets["CARROT"] == 8             # 丸め
    assert targets["STRAWBERRY"] == 1         # 丸めると 0 だが植え付け済みが1
    # 空きタイル数で上から抑えない（植え付け済みまで削ってしまうため。§3.5 の訂正）
    big = plan.predict_plan(obs, _constant_model({"WHEAT": 500.0}))["seed_targets"]
    assert big["WHEAT"] == 500


def test_want_land_means_one_more_quadrant_than_this_morning():
    """want_land は「朝の区画数 + 1」まで（1日1枚。§3.5）。"""
    obs = _obs(unlocked=("NW", "NE"))
    yes = plan.predict_plan(obs, _constant_model({}, land_raw=10.0))
    assert yes["want_land"] is True and yes["land_target"] == 3
    no = plan.predict_plan(obs, _constant_model({}, land_raw=-10.0))
    assert no["want_land"] is False and no["land_target"] == 2


# ---------------------------------------------------------------- 安全装置（フォールバック）


def test_missing_model_falls_back_to_rules(tmp_path):
    assert plan.get_model(tmp_path / "none.json") is None
    assert plan.plan_for_turn(_obs(), model_path=tmp_path / "none.json") is None


def test_broken_model_falls_back_to_rules(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ not json", encoding="utf-8")
    assert plan.get_model(path) is None


def test_feature_order_mismatch_falls_back_to_rules(tmp_path):
    model = _constant_model({})
    model["feature_names"] = list(reversed(model["feature_names"]))
    path = tmp_path / "mismatch.json"
    path.write_text(json.dumps(model), encoding="utf-8")
    assert plan.get_model(path) is None


def test_prediction_error_falls_back_to_rules(tmp_path):
    """予測中の例外もルール表に落とす（試合を止めない。§3.5）。"""
    model = _constant_model({})
    model["heads"]["target_seed_WHEAT"]["trees"] = [[999, 0.0, 1.0, 2.0]]  # 範囲外の特徴量
    path = tmp_path / "bad_tree.json"
    path.write_text(json.dumps(model), encoding="utf-8")
    assert plan.plan_for_turn(_obs(), model_path=path) is None


def test_failed_load_is_not_retried_every_turn(tmp_path, monkeypatch):
    """読めなかったモデルを毎ターン読み直さない（時間の無駄。NFR-1）。"""
    calls = []
    real = plan.load_model
    monkeypatch.setattr(plan, "load_model", lambda p: calls.append(p) or real(p))
    missing = tmp_path / "none.json"
    for hour in range(5):
        plan.plan_for_turn(_obs(hour=hour), model_path=missing)
    assert len(calls) == 1


# ---------------------------------------------------------------- キャッシュ


def test_plan_is_cached_per_seat_and_day(monkeypatch):
    """(席, 日) ごとに1回。hour 0 では必ず作り直す（§3.5）。"""
    made = []
    monkeypatch.setattr(plan, "predict_plan",
                        lambda obs, model: made.append((obs["player"], obs["day"], obs["hour"])) or {"n": len(made)})
    monkeypatch.setattr(plan, "get_model", lambda path=None: {"fake": True})
    first = plan.plan_for_turn(_obs(day=3, hour=0, seat=0))
    assert plan.plan_for_turn(_obs(day=3, hour=5, seat=0)) is first      # 同じ日は使い回す
    other = plan.plan_for_turn(_obs(day=3, hour=5, seat=1))
    assert other is not first                                             # 席が違えば別
    plan.plan_for_turn(_obs(day=4, hour=0, seat=0))                       # 翌日
    plan.plan_for_turn(_obs(day=3, hour=0, seat=0))                       # 新しい試合の同じ日
    assert made == [(0, 3, 0), (1, 3, 5), (0, 4, 0), (0, 3, 0)]


def test_predict_plan_is_fast_with_real_model():
    """1回あたり最悪 < 10ms（§3.6 タスク1-3）。"""
    model = plan.get_model()
    obs = _obs(day=12, entries={(0, 0): _plant("WHEAT")}, seeds={"WHEAT": 4})
    timings = []
    for _ in range(200):
        start = time.perf_counter()
        plan.predict_plan(obs, model)
        timings.append(time.perf_counter() - start)
    assert max(timings) < 0.010, f"最悪 {max(timings) * 1000:.2f}ms"


# ---------------------------------------------------------------- decide_market への差し替え


def _seed_orders(orders):
    return {o[1]: o[2] for o in orders if o[0] == "BUY_SEED"}


def test_decide_market_without_plan_is_unchanged():
    obs = _obs(day=5, money=5000.0)
    assert macro.decide_market(obs) == macro.decide_market(obs, plan=None)


def test_plan_replaces_learned_crops_only():
    """WHEAT・CARROT・STRAWBERRY はプラン、TOMATO・MELON はルール表（§3.2）。"""
    obs = _obs(day=0, money=3000.0)
    rule = _seed_orders(macro.decide_market(obs))
    assert rule["MELON"] == macro.PARAMS["day0_seeds"]["MELON"]
    planned = {"seed_targets": {"WHEAT": 3, "CARROT": 0, "STRAWBERRY": 0},
               "want_land": False, "land_target": 1}
    got = _seed_orders(macro.decide_market(obs, plan=planned))
    assert got["WHEAT"] == 3                                  # プラン（ルール表は 10）
    assert got["MELON"] == macro.PARAMS["day0_seeds"]["MELON"]  # ルール表のまま
    assert "STRAWBERRY" not in got and "CARROT" not in got


def test_plan_mid_game_overrides_rule_table():
    obs = _obs(day=15, money=20000.0)
    planned = {"seed_targets": {"WHEAT": 0, "CARROT": 5, "STRAWBERRY": 0},
               "want_land": False, "land_target": 1}
    got = _seed_orders(macro.decide_market(obs, plan=planned))
    assert got == {"CARROT": 5}  # ルール表なら STRAWBERRY 33 / WHEAT 25 を買いに行く


def test_plan_does_not_buy_seeds_after_stop_planting_day():
    """実行層が植えない日には、プランがあっても種を買わない（死蔵するため。§3.5）。"""
    day = macro.PARAMS["stop_planting_day"]
    obs = _obs(day=day, money=20000.0)
    planned = {"seed_targets": {"WHEAT": 10, "CARROT": 10, "STRAWBERRY": 0},
               "want_land": False, "land_target": 1}
    assert _seed_orders(macro.decide_market(obs, plan=planned)) == {}


def test_want_land_buys_at_most_one_per_day():
    base = {"seed_targets": {c: 0 for c in LEARNED}}
    morning = _obs(day=3, money=5000.0)  # ルール表なら day 3 では買わない
    orders = macro.decide_market(morning, plan={**base, "want_land": True, "land_target": 2})
    assert ["BUY_LAND"] in orders
    # 同じ日に1枚買ったあと（区画 2 = land_target）は、もう買わない
    after = _obs(day=3, hour=4, money=5000.0, unlocked=("NW", "NE"))
    orders = macro.decide_market(after, plan={**base, "want_land": True, "land_target": 2})
    assert ["BUY_LAND"] not in orders


def test_want_land_false_overrides_rule_schedule():
    """ルール表なら day 6 に2枚目を買うが、プランが買わないと言えば買わない。"""
    obs = _obs(day=6, money=5000.0)
    assert ["BUY_LAND"] in macro.decide_market(obs)
    planned = {"seed_targets": {c: 0 for c in LEARNED}, "want_land": False, "land_target": 1}
    assert ["BUY_LAND"] not in macro.decide_market(obs, plan=planned)


# ---------------------------------------------------------------- main.py との統合


def _run_short_game(agent, steps=48, seed=3):
    from kaggle_environments import make

    env = make("kaggriculture", configuration={"seed": seed, "episodeSteps": steps}, debug=True)
    env.run([agent, "starter"])
    return env


def test_main_does_not_use_model(monkeypatch):
    """ADR-0002：main.py は模倣モデルを使わない（v2 に負けたため本線から外した）。"""
    import main as submission

    called = []
    monkeypatch.setattr(plan, "plan_for_turn", lambda *a, **kw: called.append(1))
    env = _run_short_game(submission.agent)
    assert env.steps[-1][0]["status"] == "DONE"
    assert not called


def test_main_matches_frozen_v2():
    """main.py は凍結した v2（現在の提出版）と同じ行動をとる（ADR-0002）。

    フェーズ1で agent/ に足したもの（features の特徴量、decide_market の plan 引数）が
    plan=None のときの挙動を変えていないことの回帰テスト。
    """
    import main as submission
    from scripts.eval import resolve_agent

    v2 = resolve_agent(str(ROOT / "baselines" / "v2_agent.py"))
    ours = _run_short_game(submission.agent, steps=96, seed=11)
    theirs = _run_short_game(v2, steps=96, seed=11)
    ours_actions = [step[0]["action"] for step in ours.steps]
    theirs_actions = [step[0]["action"] for step in theirs.steps]
    assert ours_actions == theirs_actions
