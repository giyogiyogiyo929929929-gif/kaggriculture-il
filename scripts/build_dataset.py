"""ダイジェストから、マクロ模倣モデルの学習テーブルを作る（タスク 1-1）。

仕様: docs/04_model_design.md §3.3（採用条件・ラベル・特徴量・重み）
入力: data\\digest\\*.json.gz（docs/02_data_pipeline.md §4）
出力: data\\dataset\\macro.csv

`data\\analysis\\*.csv`（0-5 の出力）は使わない。あれは人が読む集計で、
家畜の shed 列が無いなどラベルに必要な情報が落ちているため（doc 04 §3.3）。

使い方:
    .venv\\Scripts\\python.exe scripts\\build_dataset.py
    .venv\\Scripts\\python.exe scripts\\build_dataset.py --digest-dir data\\digest --out data\\dataset\\macro.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import features  # noqa: E402
from scripts.digest_replay import load_digest, load_teams  # noqa: E402

CROPS = features.CROP_ORDER
LAST_DAY = 28  # day29 の行動は換金だけで型にならない（doc 04 §3.3）
SKIP_KINDS = {"INVALID", "PASS", "NOOP"}  # 不正・no-op の注文（doc 03 §3.3）
RANK_FLOOR = 50  # 1位 = 2.0、50位以下 = 1.0 の線形（doc 04 §3.3）

LABEL_NAMES = [f"target_seed_{crop}" for crop in CROPS] + ["buy_land"]
EXTRA_NAMES = [f"buy_seed_{crop}" for crop in CROPS] + ["hires"]
KEY_NAMES = ["episode_id", "seat", "day", "team_id", "rank", "weight"]


# ---------------------------------------------------------------- 読み込み


def iter_digests(digest_dir: Path) -> Iterator[dict]:
    for path in sorted(Path(digest_dir).glob("*.json.gz")):
        yield load_digest(path)


def daily_orders(digest: dict) -> dict:
    """(seat, day) → {kind: {item: 数量}}。不正・no-op の注文は落とす（doc 04 §3.3）。"""
    totals: dict = {}
    for turn in digest.get("turns") or []:
        day = turn.get("day")
        for seat, action in enumerate(turn.get("a") or []):
            for order in action.get("m") or []:
                if not order or order[0] in SKIP_KINDS:
                    continue
                kind = order[0]
                item = order[1] if len(order) > 1 and isinstance(order[1], str) else ""
                qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                bucket = totals.setdefault((seat, day), {}).setdefault(kind, {})
                bucket[item] = bucket.get(item, 0) + int(qty)
    return totals


def day_state_from_digest(day_record: dict, seat: int) -> dict:
    """ダイジェストの days[] 1件から、`agent.features.day_state` と同じ形の状態を作る。

    実行時は観測から作る。両者が一致することを
    `tests/test_build_dataset.py::test_feature_vector_same_from_obs_and_digest` で見張る。
    """
    seats = day_record.get("seats") or []
    state = seats[seat] if seat < len(seats) else {}
    tiles = state.get("tiles") or {}
    return {
        "day": int(day_record.get("day", 0) or 0),
        "money": float(state.get("money", 0) or 0),
        "quadrants": len(state.get("quadrants") or ["NW"]),
        "weeds": tiles.get("weeds", 0) or 0,
        "empty": tiles.get("empty", 0) or 0,
        "locked": tiles.get("locked", 0) or 0,
        "yield_units": tiles.get("yield_units", 0) or 0,
        "crops": tiles.get("crops") or {},
        "animals": tiles.get("animals") or {},
        "structures": tiles.get("structures") or {},
        "shed": state.get("shed") or {},
        "seeds": state.get("seeds") or {},
        "prices": day_record.get("prices") or {},
        "inventory": day_record.get("inventory") or {},
    }


# ---------------------------------------------------------------- 行の生成


def rank_weight(rank) -> float:
    """1位 = 2.0、50位以下 = 1.0（doc 04 §3.3）。`public_score` は使わない。"""
    if rank is None:
        return 1.0
    position = max(1, min(int(rank), RANK_FLOOR))
    return 2.0 - (position - 1) / (RANK_FLOOR - 1)


def dataset_rows(digest: dict, teams: dict[str, dict]) -> list[dict]:
    """1エピソードぶんの行。リーダーボードに載った席 × day 0〜28（doc 04 §3.3）。

    `teams` は `digest_replay.load_teams` の戻り値（チーム名 → rank / team_id）。
    **ダイジェストの `seats[].rank` は使わない。** 作成時点のスナップショットで固定されていて、
    試し取得で作ったものは古い順位のまま残っている（doc 02 §4.2）。
    """
    episode_id = digest.get("episode_id")
    seats = digest.get("seats") or []
    orders = daily_orders(digest)

    rows: list[dict] = []
    for seat, info in enumerate(seats):
        team = teams.get(info.get("team_name"))
        if not team:  # リーダーボード圏外の相手は上位勢ではない
            continue
        weight = rank_weight(team["rank"])
        for day_record in digest.get("days") or []:
            day = day_record.get("day")
            if day is None or day > LAST_DAY:
                continue
            state = day_state_from_digest(day_record, seat)
            today = orders.get((seat, day), {})
            bought = today.get("BUY_SEED", {})
            row: dict = {
                "episode_id": episode_id,
                "seat": seat,
                "day": day,
                "team_id": team["team_id"],
                "rank": team["rank"],
                "weight": weight,
            }
            row.update(zip(features.FEATURE_NAMES, features.feature_vector(state)))
            row["day"] = day  # `day` は特徴量でもあるので、整数のまま上書きし直す
            for crop in CROPS:
                got = int(bought.get(crop, 0))
                held = int((state["crops"] or {}).get(crop, 0)) + int((state["seeds"] or {}).get(crop, 0))
                row[f"buy_seed_{crop}"] = got
                row[f"target_seed_{crop}"] = held + got
            row["buy_land"] = 1 if today.get("BUY_LAND") else 0
            row["hires"] = sum(today.get("HIRE", {}).values())
            rows.append(row)
    return rows


def balance_by_team(rows: list[dict]) -> list[dict]:
    """チームごとの重み合計をそろえる（doc 04 §3.3）。

    エピソード数が多いチームに引っ張られないようにする。`rank` による重み付けは残る。
    """
    totals: dict = {}
    for row in rows:
        totals[row["team_id"]] = totals.get(row["team_id"], 0.0) + row["weight"]
    if not totals:
        return rows
    target = sum(totals.values()) / len(totals)
    for row in rows:
        total = totals[row["team_id"]]
        if total:
            row["weight"] = row["weight"] * target / total
    return rows


def collect_rows(digest_dir: Path, meta_dir: Path) -> list[dict]:
    """ダイジェストを全部読んで、チーム均し済みの行を返す。

    rank は `meta_dir\\leaderboard.csv` から引き直す（doc 04 §3.3）。
    """
    teams = load_teams(meta_dir)
    rows: list[dict] = []
    for digest in iter_digests(digest_dir):
        rows.extend(dataset_rows(digest, teams))
    return balance_by_team(rows)


# ---------------------------------------------------------------- 出力


def build(digest_dir: Path, out_path: Path, meta_dir: Path) -> dict:
    rows = collect_rows(digest_dir, meta_dir)
    episodes = len({row["episode_id"] for row in rows})
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # `day` は KEY_NAMES と FEATURE_NAMES の両方にある。列を二重に出さない
    header = KEY_NAMES + [n for n in features.FEATURE_NAMES if n not in KEY_NAMES]
    header += LABEL_NAMES + EXTRA_NAMES
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    return {"episodes": episodes, "rows": len(rows), "path": out_path}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="マクロ模倣モデルの学習テーブルを作る（docs/04_model_design.md §3.3）"
    )
    parser.add_argument("--digest-dir", default=str(ROOT / "data" / "digest"))
    parser.add_argument("--meta-dir", default=str(ROOT / "data" / "meta"),
                        help="leaderboard.csv の場所。rank はここから引き直す")
    parser.add_argument("--out", default=str(ROOT / "data" / "dataset" / "macro.csv"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    digest_dir = Path(args.digest_dir)
    digests = sorted(digest_dir.glob("*.json.gz")) if digest_dir.exists() else []
    if not digests:
        print(f"ダイジェストが1本も無い（{digest_dir}）。先に scripts\\fetch_replays.py を実行する。")
        return 0

    meta_dir = Path(args.meta_dir)
    if not (meta_dir / "leaderboard.csv").exists():
        print(f"leaderboard.csv が無い（{meta_dir}）。rank を引けないので作らない。"
              "先に scripts\\fetch_replays.py を実行する。")
        return 0

    result = build(digest_dir, Path(args.out), meta_dir)
    if not result["rows"]:
        print(
            f"ダイジェスト {len(digests)} 本を読んだが、リーダーボードに載った席（rank）が1つも無かった。\n"
            f"{meta_dir / 'leaderboard.csv'} のチーム名とダイジェストの team_name を確認する（doc 02 §4.2）。"
        )
        return 0

    print(
        f"{result['rows']} 行（{result['episodes']} エピソード）を "
        f"{result['path']} に書いた。特徴量 {len(features.FEATURE_NAMES)} / "
        f"ラベル {len(LABEL_NAMES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
