"""マクロ模倣モデルの学習・検証・書き出し（タスク 1-2）。

仕様: docs/04_model_design.md §3.4（モデルと検証）, §3.6（受け入れ条件 1-2）, §3.7（撤退条件）
入力: data\\dataset\\macro.csv（scripts\\build_dataset.py の出力。doc 04 §3.3）
出力: models\\macro.json（純 Python で読む。agent\\plan.py）/ models\\macro_cv.json（検証結果）

使い方:
    .venv\\Scripts\\python.exe scripts\\train_macro.py
    .venv\\Scripts\\python.exe scripts\\train_macro.py --data data\\dataset\\macro.csv --out models\\macro.json

検証はエピソード単位の5分割。early stopping は評価用 fold ではなく、
学習側の fold からさらにエピソード単位で切り出した検証用で行う（評価用で止めると CV が甘くなる）。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import features, macro  # noqa: E402
from agent.plan import FORMAT_VERSION  # noqa: E402

CROPS = features.CROP_ORDER
# TOMATO・MELON は比較対象に負けたのでルール表のまま（doc 04 §3.0 の改訂、EXP-20260919-08）
LEARNED_CROPS = ["WHEAT", "CARROT", "STRAWBERRY"]
HEADS = [(f"target_seed_{crop}", "regression") for crop in LEARNED_CROPS] + [("buy_land", "binary")]
BASELINES = ["day_median", "hold", "rule"]
BASELINE_LABELS = {"model": "状態モデル", "day_median": "日中央値", "hold": "現状維持", "rule": "ルール表(v2)"}

LGB_PARAMS = {  # doc 04 §3.4
    "num_leaves": 7,
    "learning_rate": 0.08,
    "min_data_in_leaf": 20,
    "seed": 0,
    "deterministic": True,
    "force_row_wise": True,
    "num_threads": 4,
    "verbose": -1,
}
MAX_ROUNDS = 200
EARLY_STOPPING = 30
STOP_FRACTION = 0.2  # 学習側 fold のうち early stopping に回すエピソードの割合


# ---------------------------------------------------------------- 読み込み


@dataclass
class Table:
    frame: pd.DataFrame

    @property
    def X(self) -> np.ndarray:
        return self.frame[list(features.FEATURE_NAMES)].to_numpy(dtype=float)

    @property
    def groups(self) -> np.ndarray:
        return self.frame["episode_id"].to_numpy()

    @property
    def weights(self) -> np.ndarray:
        return self.frame["weight"].to_numpy(dtype=float)

    def y(self, head: str) -> np.ndarray:
        return self.frame[head].to_numpy(dtype=float)


def load_table(path: Path) -> Table:
    frame = pd.read_csv(path)
    missing = [n for n in list(features.FEATURE_NAMES) + [h for h, _ in HEADS] if n not in frame.columns]
    if missing:
        raise ValueError(f"学習テーブルに列が無い: {missing[:5]}（build_dataset.py を作り直す）")
    return Table(frame.reset_index(drop=True))


# ---------------------------------------------------------------- 比較対象（doc 04 §3.4）


def rule_seed_target(crop: str, day: int, empty: float) -> float:
    """ルール表（v2）の種の目標。`agent/macro.py` の `_seed_targets` と同じ分岐で、値は PARAMS から読む。"""
    p = macro.PARAMS
    if day >= p["stop_planting_day"]:
        return 0.0
    if day <= 1:
        return float(p["day0_seeds"].get(crop, 0))
    if day >= p["late_switch_day"]:
        return float(empty) if crop == "CARROT" else 0.0
    return float(p["mid_crops"].get(crop, 0))


def rule_buy_land(day: int, quadrants: float) -> int:
    """ルール表（v2）の土地購入。予定日「以降」で、欲しい枚数に足りなければ買う（§5.2）。"""
    wanted = 1
    for scheduled_day, count in sorted(macro.PARAMS["land_buy_days"].items()):
        if day >= scheduled_day:
            wanted = max(wanted, count)
    return int(quadrants < wanted)


def baseline_rule(table: Table, head: str) -> np.ndarray:
    frame = table.frame
    if head == "buy_land":
        return np.array([rule_buy_land(int(d), q) for d, q in zip(frame["day"], frame["quadrants"])])
    crop = head.removeprefix("target_seed_")
    return np.array([rule_seed_target(crop, int(d), e) for d, e in zip(frame["day"], frame["empty"])])


def baseline_hold(table: Table, head: str) -> np.ndarray:
    """現状維持：いまの保有（植え付け済み＋種在庫）をそのまま目標にする。土地は買わない。"""
    if head == "buy_land":
        return np.zeros(len(table.frame), dtype=int)
    crop = head.removeprefix("target_seed_")
    return (table.frame[f"crop_{crop}"] + table.frame[f"seeds_{crop}"]).to_numpy(dtype=float)


def baseline_day_median(table: Table, head: str, kind: str, train, test) -> np.ndarray:
    """日中央値：学習側 fold の日ごとの中央値（二値は日ごとの陽性率 > 0.5）。状態は見ない。"""
    days = table.frame["day"].to_numpy()
    y = table.y(head)
    series = pd.Series(y[train])
    if kind == "binary":
        by_day = series.groupby(days[train]).mean()
        fallback = y[train].mean()
        return (pd.Series(days[test]).map(by_day).fillna(fallback).to_numpy() > 0.5).astype(int)
    by_day = series.groupby(days[train]).median()
    return pd.Series(days[test]).map(by_day).fillna(np.median(y[train])).to_numpy(dtype=float)


# ---------------------------------------------------------------- 評価指標


def effective_target(pred, hold) -> np.ndarray:
    """実行時に効く値 `max(保有, round(予測))`（doc 04 §3.4）。

    `decide_market` は目標が保有を超えたぶんしか買わず、予測は整数に丸めて渡す（§3.5）。
    空きタイル数による上限は入れない。実行時は毎ターン数え直すので hour 0 の値では再現できない。
    """
    return np.maximum(np.asarray(hold, dtype=float), np.round(np.asarray(pred, dtype=float)))


def regression_scores(y, pred, hold) -> dict:
    """`mae` が合否用（実行時に効く値）、`mae_raw` は参考（生の予測値）。"""
    y = np.asarray(y, dtype=float)
    return {
        "mae": float(np.mean(np.abs(y - effective_target(pred, hold)))),
        "mae_raw": float(np.mean(np.abs(y - np.asarray(pred, dtype=float)))),
    }


def binary_scores(y, pred) -> dict:
    y = np.asarray(y).astype(int)
    pred = np.asarray(pred).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"accuracy": float((pred == y).mean()), "precision": precision, "recall": recall, "f1": f1}


def _mean_scores(folds: list[dict]) -> dict:
    return {key: float(np.mean([f[key] for f in folds])) for key in folds[0]}


# ---------------------------------------------------------------- 学習


def episode_folds(table: Table, n_splits: int = 5, seed: int = 0):
    """(学習, 評価, 学習のうち early stopping 用) をエピソード単位で返す（doc 04 §3.4）。"""
    groups = table.groups
    for train, test in GroupKFold(n_splits=n_splits).split(table.X, groups=groups):
        inner = GroupShuffleSplit(n_splits=1, test_size=STOP_FRACTION, random_state=seed)
        _fit, stop = next(inner.split(train, groups=groups[train]))
        yield train, test, train[stop]


def _objective(kind: str) -> dict:
    return {"objective": "binary"} if kind == "binary" else {"objective": "regression"}


def _fit(table: Table, head: str, kind: str, rows, stop_rows=None, rounds: int = MAX_ROUNDS):
    params = {**LGB_PARAMS, **_objective(kind)}
    fit_rows = np.setdiff1d(rows, stop_rows) if stop_rows is not None else rows
    train_set = lgb.Dataset(table.X[fit_rows], table.y(head)[fit_rows],
                            weight=table.weights[fit_rows], feature_name=list(features.FEATURE_NAMES))
    if stop_rows is None:
        return lgb.train(params, train_set, num_boost_round=rounds)
    valid_set = lgb.Dataset(table.X[stop_rows], table.y(head)[stop_rows],
                            weight=table.weights[stop_rows], reference=train_set)
    return lgb.train(params, train_set, num_boost_round=rounds, valid_sets=[valid_set],
                     callbacks=[lgb.early_stopping(EARLY_STOPPING, verbose=False)])


def cross_validate(table: Table, n_splits: int = 5, max_rounds: int = MAX_ROUNDS) -> dict:
    """ヘッドごとにモデルと3つの比較対象を同じ fold で評価する。"""
    folds = list(episode_folds(table, n_splits=n_splits))
    report: dict = {"rows": len(table.frame), "episodes": int(len(set(table.groups))),
                    "folds": n_splits, "heads": {}}
    for head, kind in HEADS:
        y = table.y(head)
        per: dict[str, list] = {name: [] for name in ["model"] + BASELINES}
        best_rounds = []
        hold = baseline_hold(table, head)
        rule = baseline_rule(table, head)
        for train, test, stop in folds:
            if kind == "binary":
                def score(truth, pred):
                    return binary_scores(truth, pred)
            else:
                def score(truth, pred, _hold=hold[test]):
                    return regression_scores(truth, pred, _hold)
            booster = _fit(table, head, kind, train, stop, rounds=max_rounds)
            best_rounds.append(booster.best_iteration or booster.current_iteration())
            pred = booster.predict(table.X[test], num_iteration=booster.best_iteration or None)
            if kind == "binary":
                pred = (pred > 0.5).astype(int)
            per["model"].append(score(y[test], pred))
            per["day_median"].append(score(y[test], baseline_day_median(table, head, kind, train, test)))
            per["hold"].append(score(y[test], hold[test]))
            per["rule"].append(score(y[test], rule[test]))
        scores = {name: _mean_scores(values) for name, values in per.items()}
        if kind == "binary":
            best = max(BASELINES, key=lambda n: scores[n]["accuracy"])
            beats = scores["model"]["accuracy"] > scores[best]["accuracy"]
        else:
            best = min(BASELINES, key=lambda n: scores[n]["mae"])
            beats = scores["model"]["mae"] < scores[best]["mae"]
        report["heads"][head] = {
            "kind": kind,
            "scores": scores,
            "best_baseline": best,
            "beats_best_baseline": bool(beats),
            "rounds": max(1, int(np.median(best_rounds))),
            "fold_rounds": [int(r) for r in best_rounds],
        }
    return report


def train_final(table: Table, rounds: dict) -> dict:
    """全データで学習する。木の本数は CV の early stopping の中央値（`rounds`）。"""
    rows = np.arange(len(table.frame))
    return {head: _fit(table, head, kind, rows, rounds=int(rounds[head])) for head, kind in HEADS}


# ---------------------------------------------------------------- 書き出し


def _slim(node: dict):
    """LightGBM の木を `[特徴量index, 閾値, 左, 右]`（葉は数値）に削る（doc 04 §3.4）。"""
    if "split_index" not in node:
        return float(node["leaf_value"])
    if node.get("decision_type") != "<=":
        raise ValueError(f"想定外の分岐: {node.get('decision_type')}")
    return [int(node["split_feature"]), float(node["threshold"]),
            _slim(node["left_child"]), _slim(node["right_child"])]


def export_model(boosters: dict, path: Path) -> int:
    """`models/macro.json` を書き、バイト数を返す。閾値と葉は丸めない（丸めると予測がずれる）。"""
    heads = {}
    for head, kind in HEADS:
        dump = boosters[head].dump_model()
        if dump.get("feature_names") != list(features.FEATURE_NAMES):
            raise ValueError("学習時の特徴量の並びが FEATURE_NAMES と違う")
        entry = {"kind": kind, "trees": [_slim(t["tree_structure"]) for t in dump["tree_info"]]}
        if kind == "binary":
            objective = str(dump.get("objective", ""))
            sigmoid = 1.0
            for part in objective.split():
                if part.startswith("sigmoid:"):
                    sigmoid = float(part.split(":", 1)[1])
            entry["sigmoid"] = sigmoid
        heads[head] = entry
    model = {"format": FORMAT_VERSION, "feature_names": list(features.FEATURE_NAMES), "heads": heads}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model, separators=(",", ":")), encoding="utf-8")
    return path.stat().st_size


# ---------------------------------------------------------------- 表示


def format_report(report: dict) -> str:
    lines = [f"学習テーブル {report['rows']} 行 / {report['episodes']} エピソード / "
             f"エピソード単位 {report['folds']} 分割"]
    names = ["model"] + BASELINES
    header = "  ".join(f"{BASELINE_LABELS[n]:>10s}" for n in names)
    lines.append(f"\n{'ヘッド':24s}{header}   判定（最良の比較対象を上回るか）")
    for head, kind in HEADS:
        info = report["heads"][head]
        key = "accuracy" if kind == "binary" else "mae"
        cells = "  ".join(f"{info['scores'][n][key]:10.3f}" for n in names)
        mark = "上回る" if info["beats_best_baseline"] else "**下回る**"
        unit = "正答率" if kind == "binary" else "実効MAE"
        lines.append(f"{head:24s}{cells}   {mark}（{unit}、最良={BASELINE_LABELS[info['best_baseline']]}、"
                     f"木 {info['rounds']} 本）")
    lines.append("\n参考：生の予測値の MAE（保有より下の予測や端数も誤差に数える）")
    for head, kind in HEADS:
        if kind == "regression":
            cells = "  ".join(f"{report['heads'][head]['scores'][n]['mae_raw']:10.3f}" for n in names)
            lines.append(f"{head:24s}{cells}")
    land = report["heads"]["buy_land"]["scores"]
    lines.append("\nbuy_land の詳細（適合率 / 再現率 / F1）")
    for n in names:
        s = land[n]
        lines.append(f"  {BASELINE_LABELS[n]:10s} {s['precision']:.3f} / {s['recall']:.3f} / {s['f1']:.3f}")
    return "\n".join(lines)


# ---------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="マクロ模倣モデルを学習する（docs/04_model_design.md §3.4）")
    parser.add_argument("--data", default=str(ROOT / "data" / "dataset" / "macro.csv"))
    parser.add_argument("--out", default=str(ROOT / "models" / "macro.json"))
    parser.add_argument("--report", default=str(ROOT / "models" / "macro_cv.json"))
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data = Path(args.data)
    if not data.exists():
        print(f"学習テーブルが無い（{data}）。先に scripts\\build_dataset.py を実行する。")
        return 0

    table = load_table(data)
    report = cross_validate(table, n_splits=args.folds, max_rounds=args.max_rounds)
    boosters = train_final(table, {head: info["rounds"] for head, info in report["heads"].items()})
    report["model_bytes"] = export_model(boosters, Path(args.out))
    report["model_path"] = str(args.out)

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(format_report(report))
    print(f"\nモデル {args.out}（{report['model_bytes'] / 1024:.1f} KB）/ 検証結果 {args.report}")
    failed = [h for h, info in report["heads"].items() if not info["beats_best_baseline"]]
    if failed:
        print(f"比較対象の最良を上回らなかったヘッド: {', '.join(failed)}（doc 04 §3.6 / §3.7 を確認）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
