"""マクロ模倣モデルの読み込みと推論（純 Python）。

仕様: docs/04_model_design.md §3.4（書き出し形式）, §3.5（実行時）
提出環境で動かすので標準ライブラリだけを使う（docs/06_submission.md）。

`models/macro.json` の形（`scripts/train_macro.py` の `export_model` が書く）:

    {"format": 1,
     "feature_names": [...49個...],
     "heads": {"target_seed_WHEAT": {"kind": "regression", "trees": [...]},
               "buy_land": {"kind": "binary", "sigmoid": 1.0, "trees": [...]}}}

木は `[特徴量index, 閾値, 左, 右]` の入れ子で、葉は数値。`x[index] <= 閾値` なら左。
"""
from __future__ import annotations

import json
import math
import os

from agent import features

FORMAT_VERSION = 1

# 本番では tar が /kaggle_simulations/agent/ に展開され、models/ は agent/ の隣に来る（doc 06）。
# `exec` される main.py と違い、import されたこのモジュールには __file__ がある。
DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "macro.json"
)

_MODELS: dict = {}  # パス → モデル（読めなかったら None。毎ターン読み直さない）
_PLANS: dict = {}   # (席, 日) → Plan（None はルール表に落ちたことを表す）


def load_model(path) -> dict:
    """モデルを読み、特徴量の並びが `features.FEATURE_NAMES` と一致するか確かめる。

    並びがずれたモデルは例外で止める。黙って読むと、間違った特徴量で予測することになる。
    """
    with open(path, encoding="utf-8") as handle:
        model = json.load(handle)
    if model.get("format") != FORMAT_VERSION:
        raise ValueError(f"モデル形式が違う: {model.get('format')!r}（期待 {FORMAT_VERSION}）")
    if list(model.get("feature_names") or []) != list(features.FEATURE_NAMES):
        raise ValueError("モデルの特徴量の並びが agent/features.py の FEATURE_NAMES と一致しない")
    return model


def _tree_value(node, x) -> float:
    while isinstance(node, list):
        index, threshold, left, right = node
        node = left if x[index] <= threshold else right
    return node


def predict_heads(model: dict, x) -> dict:
    """特徴量ベクトル1本からヘッドごとの予測値を返す。

    回帰は木の出力の合計、二値は合計をシグモイドに通した確率（LightGBM の `predict` と同じ）。
    """
    out = {}
    for name, head in model["heads"].items():
        raw = sum(_tree_value(tree, x) for tree in head["trees"])
        if head["kind"] == "binary":
            z = head.get("sigmoid", 1.0) * raw
            # 大きな負の値で exp が溢れないように分ける
            out[name] = 1.0 / (1.0 + math.exp(-z)) if z >= 0 else math.exp(z) / (1.0 + math.exp(z))
        else:
            out[name] = raw
    return out


# ------------------------------------------------- 実行時（doc 04 §3.5）


def get_model(path=None):
    """モデルを1回だけ読む。読めなければ None（＝ルール表に落ちる）。

    無い・壊れている・特徴量の並びが違う、のどれでも例外は出さない。試合を止めないため。
    ただし提出前に `scripts/preflight.py` が「読めてルール表に落ちていない」ことを確かめる（doc 06）。
    """
    key = str(path or DEFAULT_MODEL_PATH)
    if key not in _MODELS:
        try:
            _MODELS[key] = load_model(key)
        except Exception:
            _MODELS[key] = None
    return _MODELS[key]


def predict_plan(obs, model) -> dict:
    """その日の Plan（doc 04 §3.2）。

    - `seed_targets`：モデルが持つ作物（WHEAT・CARROT・STRAWBERRY）だけ。TOMATO・MELON はルール表のまま
    - 目標は整数に丸め、**保有（植え付け済み＋種在庫）以上**にクランプする。空きタイル数では抑えない
      （植え付け済みまで削ってしまう。上限は decide_market が毎ターン掛ける。§3.5 の訂正）
    - `want_land` は「朝の区画数 + 1」まで買う意味。`land_target` にその枚数を入れる（1日1枚。§3.5）
    """
    state = features.day_state(obs)
    raw = predict_heads(model, features.feature_vector(state))
    planted = state["crops"] or {}
    stock = state["seeds"] or {}
    targets = {}
    for head, value in raw.items():
        if not head.startswith("target_seed_"):
            continue
        crop = head[len("target_seed_"):]
        hold = int(planted.get(crop, 0) or 0) + int(stock.get(crop, 0) or 0)
        targets[crop] = max(hold, int(round(value)))
    want_land = raw.get("buy_land", 0.0) > 0.5
    quadrants = int(state["quadrants"])
    return {
        "seed_targets": targets,
        "want_land": bool(want_land),
        "land_target": quadrants + (1 if want_land else 0),
    }


def plan_for_turn(obs, model_path=None):
    """このターンに使う Plan。(席, 日) ごとに1回作り、hour 0 では必ず作り直す（§3.5）。

    モデルが無い・予測で例外が出たときは None を返す（`decide_market` はルール表で動く）。
    """
    try:
        key = (int(obs.get("player", 0) or 0), int(obs.get("day", 0) or 0))
        hour = int(obs.get("hour", 0) or 0)
    except Exception:
        return None
    if hour != 0 and key in _PLANS:
        return _PLANS[key]
    try:
        model = get_model(model_path)
        result = predict_plan(obs, model) if model is not None else None
    except Exception:
        result = None
    _PLANS[key] = result
    return result


def reset() -> None:
    """キャッシュを消す（テスト用）。"""
    _MODELS.clear()
    _PLANS.clear()
