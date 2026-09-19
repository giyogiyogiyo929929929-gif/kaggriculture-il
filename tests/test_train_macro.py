"""モデル学習（タスク 1-2）の受け入れ条件テスト。

仕様: docs/04_model_design.md §3.4（モデルと検証）, §3.6（受け入れ条件 1-2）
"""
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import features, macro, plan  # noqa: E402
from scripts import build_dataset as bd  # noqa: E402
from scripts import train_macro as tm  # noqa: E402


def _row(episode_id, day, rng):
    """学習テーブル1行（doc 04 §3.3 の列）。ラベルは状態から決まる単純な規則にする。"""
    row = {name: 0.0 for name in features.FEATURE_NAMES}
    row.update({"episode_id": episode_id, "seat": 0, "day": day, "team_id": str(episode_id % 3),
                "rank": 1 + episode_id % 50, "weight": 1.0})
    row["money"] = float(rng.randint(0, 5000))
    row["empty"] = float(rng.randint(0, 30))
    row["quadrants"] = float(1 + (day >= 6) + (day >= 11))
    row["crop_WHEAT"] = float(rng.randint(0, 10))
    row["seeds_WHEAT"] = float(rng.randint(0, 3))
    for crop in bd.CROPS:
        hold = row[f"crop_{crop}"] + row[f"seeds_{crop}"]
        bought = (row["money"] // 1000) if crop == "WHEAT" else 0
        row[f"buy_seed_{crop}"] = int(bought)
        row[f"target_seed_{crop}"] = int(hold + bought)
    row["buy_land"] = int(day in (6, 11) and row["money"] > 1500)
    row["hires"] = 10
    return row


@pytest.fixture
def table_csv(tmp_path):
    rng = random.Random(0)
    rows = [_row(ep, day, rng) for ep in range(40) for day in range(29)]
    path = tmp_path / "macro.csv"
    header = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    return path


# ---------------------------------------------------------------- 比較対象


def test_heads_are_three_seeds_and_land():
    """学習するのは WHEAT・CARROT・STRAWBERRY・土地の4ヘッドだけ（doc 04 §3.0 の改訂）。

    TOMATO・MELON は EXP-20260919-08 で比較対象に負けたのでルール表のまま。
    """
    names = [name for name, _kind in tm.HEADS]
    assert names == ["target_seed_WHEAT", "target_seed_CARROT", "target_seed_STRAWBERRY", "buy_land"]
    assert dict(tm.HEADS)["buy_land"] == "binary"


def test_effective_target_is_rounded_and_at_least_holdings():
    """実行時に効く値 = max(保有, round(予測))（doc 04 §3.4）。上限（空き）は入れない。"""
    pred = np.array([3.4, 3.6, -2.0, 50.0])
    hold = np.array([5.0, 1.0, 0.0, 2.0])
    assert tm.effective_target(pred, hold).tolist() == [5.0, 4.0, 0.0, 50.0]


def test_regression_scores_judge_on_effective_value():
    """保有より下の予測は実行時に害が無いので、合否用の MAE では誤差に数えない（doc 04 §3.4）。"""
    y = np.array([5.0, 5.0])
    hold = np.array([5.0, 5.0])
    scores = tm.regression_scores(y, np.array([2.0, 5.2]), hold)
    assert scores["mae"] == pytest.approx(0.0)          # 実行時に効く値：どちらも 5
    assert scores["mae_raw"] == pytest.approx((3.0 + 0.2) / 2)


def test_rule_baseline_follows_macro_params():
    """ルール表は agent/macro.py の PARAMS（v2）から作る。値を写さない（doc 04 §3.4）。"""
    p = macro.PARAMS
    assert tm.rule_seed_target("MELON", day=0, empty=30) == p["day0_seeds"]["MELON"]
    assert tm.rule_seed_target("STRAWBERRY", day=15, empty=30) == p["mid_crops"]["STRAWBERRY"]
    assert tm.rule_seed_target("CARROT", day=p["late_switch_day"], empty=17) == 17
    assert tm.rule_seed_target("WHEAT", day=p["stop_planting_day"], empty=30) == 0
    # 土地：予定日「以降」で、欲しい枚数に足りなければ買う（§5.2）
    assert tm.rule_buy_land(day=5, quadrants=1) == 0
    assert tm.rule_buy_land(day=6, quadrants=1) == 1
    assert tm.rule_buy_land(day=8, quadrants=2) == 0
    assert tm.rule_buy_land(day=11, quadrants=2) == 1


def test_hold_baseline_is_current_holdings(table_csv):
    """「現状維持」＝植え付け済み＋種在庫。土地は「買わない」。"""
    table = tm.load_table(table_csv)
    hold = tm.baseline_hold(table, "target_seed_WHEAT")
    expected = table.frame["crop_WHEAT"] + table.frame["seeds_WHEAT"]
    assert np.allclose(hold, expected)
    assert not tm.baseline_hold(table, "buy_land").any()


# ---------------------------------------------------------------- 検証


def test_folds_split_by_episode(table_csv):
    """同じエピソードが学習と評価の両方に入らない（リーク防止。doc 04 §3.4）。"""
    table = tm.load_table(table_csv)
    for train, test, stop in tm.episode_folds(table, n_splits=5):
        episodes = table.frame["episode_id"].to_numpy()
        assert not set(episodes[train]) & set(episodes[test])
        # early stopping 用の検証も学習側から、エピソード単位で切り出す
        assert set(stop) <= set(train)
        fit = sorted(set(train) - set(stop))
        assert not set(episodes[fit]) & set(episodes[stop])


def test_cross_validate_reports_every_head_against_baselines(table_csv):
    report = tm.cross_validate(tm.load_table(table_csv), n_splits=3, max_rounds=40)
    for name, kind in tm.HEADS:
        head = report["heads"][name]
        assert set(head["scores"]) == {"model", "day_median", "hold", "rule"}
        if kind == "regression":
            assert all({"mae", "mae_raw"} <= set(s) for s in head["scores"].values())
        else:
            for s in head["scores"].values():
                assert {"accuracy", "precision", "recall", "f1"} <= set(s)
        assert isinstance(head["beats_best_baseline"], bool)
        assert head["rounds"] >= 1
    # WHEAT は状態（所持金）で決まるので、状態を見るモデルが比較対象を上回るはず
    assert report["heads"]["target_seed_WHEAT"]["beats_best_baseline"]


# ---------------------------------------------------------------- 書き出しと純 Python 推論


def test_exported_json_matches_lightgbm(table_csv, tmp_path):
    """純 Python で読んだ予測が LightGBM の predict と一致する（doc 04 §3.6）。"""
    table = tm.load_table(table_csv)
    boosters = tm.train_final(table, rounds={name: 30 for name, _ in tm.HEADS})
    out = tmp_path / "macro.json"
    tm.export_model(boosters, out)
    model = plan.load_model(out)
    X = table.X
    for name, kind in tm.HEADS:
        expected = boosters[name].predict(X[:50])
        got = [plan.predict_heads(model, list(x))[name] for x in X[:50]]
        assert np.allclose(got, expected, atol=1e-9), name
        if kind == "binary":
            assert all(0.0 <= g <= 1.0 for g in got)


def test_load_model_rejects_feature_order_mismatch(table_csv, tmp_path):
    """特徴量の並びが違うモデルは読まない（静かに間違った予測になるため。doc 04 §3.4）。"""
    table = tm.load_table(table_csv)
    out = tmp_path / "macro.json"
    tm.export_model(tm.train_final(table, rounds={name: 5 for name, _ in tm.HEADS}), out)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["feature_names"] = list(reversed(data["feature_names"]))
    out.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        plan.load_model(out)


def test_predict_heads_is_pure_python():
    """agent/plan.py は標準ライブラリだけ（提出環境の制約。doc 06）。"""
    source = (ROOT / "agent" / "plan.py").read_text(encoding="utf-8")
    for banned in ("import numpy", "import lightgbm", "import pandas", "from numpy", "from lightgbm"):
        assert banned not in source


# ---------------------------------------------------------------- CLI


def test_main_writes_model_and_report(table_csv, tmp_path, capsys):
    out = tmp_path / "models" / "macro.json"
    report = tmp_path / "models" / "macro_cv.json"
    code = tm.main(["--data", str(table_csv), "--out", str(out), "--report", str(report),
                    "--folds", "3", "--max-rounds", "30"])
    assert code == 0
    assert out.exists() and report.exists()
    text = capsys.readouterr().out
    assert "target_seed_WHEAT" in text and "buy_land" in text
    saved = json.loads(report.read_text(encoding="utf-8"))
    assert saved["model_bytes"] == out.stat().st_size


def test_main_without_data_does_not_crash(tmp_path, capsys):
    code = tm.main(["--data", str(tmp_path / "none.csv"), "--out", str(tmp_path / "m.json")])
    assert code == 0
    assert "build_dataset" in capsys.readouterr().out
