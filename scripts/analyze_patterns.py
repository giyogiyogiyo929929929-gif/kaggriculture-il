"""上位勢のダイジェストを集計して、ルールベース・ベースラインのパラメータを決める材料を作る。

仕様: docs/04_model_design.md §2（パターン分析）
入力: data\\digest\\*.json.gz（docs/02_data_pipeline.md §4）

使い方:
    .venv\\Scripts\\python.exe scripts\\analyze_patterns.py
    .venv\\Scripts\\python.exe scripts\\analyze_patterns.py --digest-dir data\\digest --out data\\analysis
"""
from __future__ import annotations

import argparse
import collections
import csv
import statistics
import sys
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.digest_replay import load_digest  # noqa: E402

CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]
PRODUCTS = CROPS + ["EGG", "MILK", "WOOL", "FERTILIZER"]
STRUCTURES = ["COOP", "PASTURE"]
ORDER_KINDS = ["BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT", "SELL", "HIRE", "BUY_LAND"]
EARLY_DAYS = 3  # 序盤＝day 0〜2（doc 04 §2.3）


# ---------------------------------------------------------------- 読み込み


def iter_digests(digest_dir: Path) -> Iterator[dict]:
    for path in sorted(Path(digest_dir).glob("*.json.gz")):
        yield load_digest(path)


def _orders(digest: dict) -> Iterator[tuple[int, int, str, str, int]]:
    """(day, seat, kind, item, qty) を1注文ずつ返す。

    `HIRE` / `BUY_LAND` は引数なしなので item は空、qty は1（03 §3.3）。
    """
    for turn in digest.get("turns") or []:
        day = turn.get("day")
        for seat, action in enumerate(turn.get("a") or []):
            for order in action.get("m") or []:
                if not order:
                    continue
                kind = order[0]
                item = order[1] if len(order) > 1 and isinstance(order[1], str) else ""
                qty = order[2] if len(order) > 2 and isinstance(order[2], (int, float)) else 1
                yield day, seat, kind, item, int(qty)


# ---------------------------------------------------------------- 行の生成


def seat_rows(digest: dict) -> list[dict]:
    """エピソード×席の1行（doc 04 §2.3 seats.csv）。"""
    episode_id = digest.get("episode_id")
    seats = digest.get("seats") or []
    days = digest.get("days") or []

    totals: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    first_day: dict[tuple[int, str], int] = {}
    for day, seat, kind, item, qty in _orders(digest):
        key = f"{kind.lower()}_{item}" if item else kind.lower()
        totals[seat][key] += qty
        first_day.setdefault((seat, kind), day)

    rows = []
    for seat, info in enumerate(seats):
        row: dict = {
            "episode_id": episode_id,
            "seat": seat,
            "team_name": info.get("team_name"),
            "team_id": info.get("team_id"),
            "rank": info.get("rank"),
            "public_score": info.get("public_score"),
            "final_money": info.get("final_money"),
            "won": info.get("won"),
            "total_hires": totals[seat].get("hire", 0),
            "land_buys": totals[seat].get("buy_land", 0),
            "first_land_day": first_day.get((seat, "BUY_LAND")),
            "first_animal_day": first_day.get((seat, "BUY_ANIMAL")),
            "first_seed_day": first_day.get((seat, "BUY_SEED")),
        }
        for crop in CROPS:
            row[f"buy_seed_{crop}"] = totals[seat].get(f"buy_seed_{crop}", 0)
        for animal in ANIMALS:
            row[f"buy_animal_{animal}"] = totals[seat].get(f"buy_animal_{animal}", 0)
        for product in PRODUCTS:
            row[f"sell_{product}"] = totals[seat].get(f"sell_{product}", 0)
            row[f"buy_product_{product}"] = totals[seat].get(f"buy_product_{product}", 0)
        last = days[-1]["seats"][seat] if days else None
        if last:
            tiles = last.get("tiles") or {}
            for crop in CROPS:
                row[f"final_crop_{crop}"] = (tiles.get("crops") or {}).get(crop, 0)
            for animal in ANIMALS:
                row[f"final_animal_{animal}"] = (tiles.get("animals") or {}).get(animal, 0)
            row["final_quadrants"] = len(last.get("quadrants") or [])
        rows.append(row)
    return rows


def daily_state_rows(digest: dict) -> list[dict]:
    """エピソード×席×日の状態（doc 04 §2.3 daily_state.csv）。"""
    rows = []
    for day in digest.get("days") or []:
        for seat, state in enumerate(day.get("seats") or []):
            tiles = state.get("tiles") or {}
            row = {
                "episode_id": digest.get("episode_id"),
                "seat": seat,
                "day": day.get("day"),
                "money": state.get("money"),
                "quadrants": len(state.get("quadrants") or []),
                "hires_today": state.get("hires_today"),
                "weeds": tiles.get("weeds"),
                "empty": tiles.get("empty"),
                "locked": tiles.get("locked"),
                "yield_units": tiles.get("yield_units"),
            }
            for crop in CROPS:
                row[f"crop_{crop}"] = (tiles.get("crops") or {}).get(crop, 0)
            for animal in ANIMALS:
                row[f"animal_{animal}"] = (tiles.get("animals") or {}).get(animal, 0)
            for structure in STRUCTURES:
                row[f"structure_{structure}"] = (tiles.get("structures") or {}).get(structure, 0)
            for product in PRODUCTS:
                row[f"shed_{product}"] = (state.get("shed") or {}).get(product, 0)
            for crop in CROPS:
                row[f"seeds_{crop}"] = (state.get("seeds") or {}).get(crop, 0)
            rows.append(row)
    return rows


def daily_order_rows(digest: dict) -> list[dict]:
    """エピソード×席×日×種別×品目の注文集計（doc 04 §2.3 daily_orders.csv）。"""
    bucket: dict[tuple, dict] = {}
    for day, seat, kind, item, qty in _orders(digest):
        key = (day, seat, kind, item)
        entry = bucket.setdefault(
            key,
            {"episode_id": digest.get("episode_id"), "seat": seat, "day": day,
             "kind": kind, "item": item, "qty": 0, "orders": 0},
        )
        entry["qty"] += qty
        entry["orders"] += 1
    return [bucket[key] for key in sorted(bucket, key=lambda k: (k[0] or 0, k[1], k[2], k[3]))]


def price_rows(digest: dict) -> list[dict]:
    """エピソード×日×品目の価格と市場在庫（doc 04 §2.3 prices.csv）。"""
    rows = []
    for day in digest.get("days") or []:
        prices = day.get("prices") or {}
        inventory = day.get("inventory") or {}
        for item in sorted(prices):
            rows.append({
                "episode_id": digest.get("episode_id"),
                "day": day.get("day"),
                "item": item,
                "price": prices.get(item),
                "inventory": inventory.get(item),
                "shops": len(day.get("shops") or []),
            })
    return rows


def command_counts(digest: dict) -> collections.Counter:
    """(席, farmer/hands, コマンド) の出現回数（doc 04 §2.4：頻度だけ見る）。"""
    counts: collections.Counter = collections.Counter()
    for turn in digest.get("turns") or []:
        for seat, action in enumerate(turn.get("a") or []):
            farmer = action.get("f") or []
            if farmer:
                counts[(seat, "farmer", farmer[0])] += 1
            for hand in action.get("h") or []:
                if hand:
                    counts[(seat, "hands", hand[0])] += 1
    return counts


# ---------------------------------------------------------------- 要約


def _median(values: Iterable) -> float | None:
    values = [v for v in values if v is not None]
    return round(statistics.median(values), 1) if values else None


def _split_by_win(seats: list[dict]) -> tuple[list[dict], list[dict]]:
    return [s for s in seats if s.get("won")], [s for s in seats if not s.get("won")]


def build_summary(
    seats: list[dict],
    states: list[dict],
    orders: list[dict],
    prices: list[dict],
    commands: collections.Counter,
    episodes: int,
) -> str:
    """人が読む要約（doc 04 §2.3 の1〜7）。"""
    out: list[str] = []
    won, lost = _split_by_win(seats)
    out.append("# パターン分析の要約")
    out.append("")
    out.append(f"- エピソード数: {episodes}  席数: {len(seats)}（勝ち {len(won)} / 負け {len(lost)}）")
    ranks = [s["rank"] for s in seats if s.get("rank") is not None]
    out.append(f"- 順位が付いた席: {len(ranks)}（最上位 {min(ranks) if ranks else '-'}）")
    out.append("")

    # 1. 序盤の型
    out.append("## 1. 序盤の型（day 0〜2 の注文、席あたり中央値）")
    out.append("")
    out.append("| 種別 | 品目 | 勝ち席 | 負け席 |")
    out.append("|---|---|---|---|")
    early = [o for o in orders if (o["day"] or 0) < EARLY_DAYS]
    seat_keys = {(s["episode_id"], s["seat"]): bool(s.get("won")) for s in seats}
    combos = sorted({(o["kind"], o["item"]) for o in early})
    for kind, item in combos:
        per_seat_won, per_seat_lost = [], []
        for key, is_won in seat_keys.items():
            qty = sum(
                o["qty"] for o in early
                if (o["episode_id"], o["seat"]) == key and o["kind"] == kind and o["item"] == item
            )
            (per_seat_won if is_won else per_seat_lost).append(qty)
        out.append(f"| {kind} | {item or '-'} | {_median(per_seat_won)} | {_median(per_seat_lost)} |")
    out.append("")

    # 2-3. 作物・家畜構成の推移
    out.append("## 2-3. 作物・家畜構成の推移（全席の日別中央値）")
    out.append("")
    header = ["day", "money"] + [f"crop_{c}" for c in CROPS] + [f"animal_{a}" for a in ANIMALS]
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "---|" * len(header))
    by_day: dict[int, list[dict]] = collections.defaultdict(list)
    for state in states:
        by_day[state["day"]].append(state)
    for day in sorted(by_day):
        row = [str(day), str(_median(s["money"] for s in by_day[day]))]
        row += [str(_median(s[f"crop_{c}"] for s in by_day[day])) for c in CROPS]
        row += [str(_median(s[f"animal_{a}"] for s in by_day[day])) for a in ANIMALS]
        out.append("| " + " | ".join(row) + " |")
    out.append("")

    # 4. 雇用
    hires = [o for o in orders if o["kind"] == "HIRE"]
    per_day_hires: dict[int, list[int]] = collections.defaultdict(list)
    for order in hires:
        per_day_hires[order["day"]].append(order["qty"])
    out.append("## 4. 雇用（HIRE）")
    out.append("")
    out.append(f"- 席あたり総雇用数の中央値: 勝ち {_median(s['total_hires'] for s in won)} / "
               f"負け {_median(s['total_hires'] for s in lost)}")
    if per_day_hires:
        peak_day = max(per_day_hires, key=lambda d: sum(per_day_hires[d]))
        out.append(f"- 1日あたり雇用の中央値: {_median(v for vs in per_day_hires.values() for v in vs)}"
                   f"、最も雇う日: day {peak_day}")
    out.append("")

    # 5. 土地購入
    out.append("## 5. 土地購入（BUY_LAND）")
    out.append("")
    land_days: list[list[int]] = []
    for key in seat_keys:
        days_for_seat = sorted(
            o["day"] for o in orders
            if (o["episode_id"], o["seat"]) == key and o["kind"] == "BUY_LAND"
        )
        if days_for_seat:
            land_days.append(days_for_seat)
    for nth in range(3):
        values = [d[nth] for d in land_days if len(d) > nth]
        if values:
            out.append(f"- {nth + 2}枚目を買った日の中央値: {_median(values)}（{len(values)}席）")
    if not land_days:
        out.append("- 期間内に BUY_LAND なし")
    out.append("")

    # 6. 売却
    out.append("## 6. 売却（SELL）：品目別の総数量と、売った日の価格中央値")
    out.append("")
    out.append("| 品目 | 席あたり総数量(中央値) | 売却があった日の価格(中央値) | 最初に売った日(中央値) |")
    out.append("|---|---|---|---|")
    price_index = {(p["episode_id"], p["day"], p["item"]): p["price"] for p in prices}
    for product in PRODUCTS:
        totals, sell_prices, first_days = [], [], []
        for key in seat_keys:
            seat_orders = [
                o for o in orders
                if (o["episode_id"], o["seat"]) == key and o["kind"] == "SELL" and o["item"] == product
            ]
            totals.append(sum(o["qty"] for o in seat_orders))
            if seat_orders:
                first_days.append(min(o["day"] for o in seat_orders))
            for order in seat_orders:
                price = price_index.get((order["episode_id"], order["day"], product))
                if price is not None:
                    sell_prices.append(price)
        out.append(f"| {product} | {_median(totals)} | {_median(sell_prices)} | {_median(first_days)} |")
    out.append("")

    # 7. 勝敗との相関
    out.append("## 7. 最終所持金との関係（勝ち席 / 負け席の中央値）")
    out.append("")
    metrics = ["final_money", "total_hires", "land_buys", "final_quadrants"]
    metrics += [f"buy_animal_{a}" for a in ANIMALS]
    metrics += [f"sell_{p}" for p in PRODUCTS]
    out.append("| 指標 | 勝ち席 | 負け席 |")
    out.append("|---|---|---|")
    for metric in metrics:
        out.append(f"| {metric} | {_median(s.get(metric) for s in won)} | "
                   f"{_median(s.get(metric) for s in lost)} |")
    out.append("")

    # ミクロ行動の頻度（§2.4：頻度だけ）
    out.append("## 参考：farmer / hands のコマンド頻度（全席合計、上位15件）")
    out.append("")
    merged: collections.Counter = collections.Counter()
    for (_seat, who, command), count in commands.items():
        merged[(who, command)] += count
    out.append("| 対象 | コマンド | 回数 |")
    out.append("|---|---|---|")
    for (who, command), count in merged.most_common(15):
        out.append(f"| {who} | {command} | {count:,} |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------- 出力


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def analyze(digest_dir: Path, out_dir: Path) -> dict:
    """ダイジェストを全部読んで CSV と summary.md を書く（doc 04 §2.3）。"""
    out_dir = Path(out_dir)
    seats: list[dict] = []
    states: list[dict] = []
    orders: list[dict] = []
    prices: list[dict] = []
    commands: collections.Counter = collections.Counter()
    episodes = 0
    for digest in iter_digests(digest_dir):
        episodes += 1
        seats.extend(seat_rows(digest))
        states.extend(daily_state_rows(digest))
        orders.extend(daily_order_rows(digest))
        prices.extend(price_rows(digest))
        commands.update(command_counts(digest))

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "seats.csv", seats)
    write_csv(out_dir / "daily_state.csv", states)
    write_csv(out_dir / "daily_orders.csv", orders)
    write_csv(out_dir / "prices.csv", prices)
    summary = build_summary(seats, states, orders, prices, commands, episodes)
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    return {
        "episodes": episodes,
        "seats": len(seats),
        "daily_state": len(states),
        "daily_orders": len(orders),
        "prices": len(prices),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ダイジェストのパターン分析（docs/04_model_design.md §2）")
    parser.add_argument("--digest-dir", type=Path, default=ROOT / "data" / "digest")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "analysis")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    files = sorted(Path(args.digest_dir).glob("*.json.gz"))
    if not files:
        print(f"ダイジェストが1本も無い: {args.digest_dir}（先に fetch_replays.py を実行する）")
        return 0
    result = analyze(args.digest_dir, args.out)
    print(f"集計完了: {result}")
    print(f"出力先: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
