# -*- coding: utf-8 -*-
"""Report realized SELL execution order and unit prices from ledger_match.py pickles.

This is intentionally post-processing only: it does not run the environment or
modify an agent. Ledger rows are emitted in actual _commit_unit order, so the
per-player SELL sequence within a step is useful for diagnosing order-sensitive
market effects such as v153's dense self-exposure reorder.

Usage:
    python scripts/analysis/sell_sequence_report.py results/a.pkl [results/b.pkl ...]
    python scripts/analysis/sell_sequence_report.py results/a.pkl --from-step 288 --to-step 693 --min-distinct 2
"""
from __future__ import annotations

import argparse
import collections
import pickle
from pathlib import Path


def _rle(items: list[str]) -> str:
    if not items:
        return "-"
    out: list[str] = []
    cur = items[0]
    n = 1
    for item in items[1:]:
        if item == cur:
            n += 1
            continue
        out.append(f"{cur}x{n}" if n > 1 else cur)
        cur, n = item, 1
    out.append(f"{cur}x{n}" if n > 1 else cur)
    return " -> ".join(out)


def _step_stats(rows: list[tuple]) -> dict:
    seq = [str(r[3]) for r in rows]
    prices = [float(r[4]) for r in rows]
    by_item: dict[str, list[float]] = collections.defaultdict(list)
    for r in rows:
        by_item[str(r[3])].append(float(r[4]))
    items = {}
    for item, ps in by_item.items():
        items[item] = {
            "qty": len(ps),
            "gross": sum(ps),
            "avg": sum(ps) / len(ps),
            "first": ps[0],
            "last": ps[-1],
            "realized_drop": ps[0] - ps[-1],
            "min": min(ps),
            "max": max(ps),
        }
    return {
        "units": len(rows),
        "distinct": len(by_item),
        "gross": sum(prices),
        "sequence": seq,
        "items": items,
    }


def _fmt_num(v: float) -> str:
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pickles", nargs="+")
    ap.add_argument("--from-step", type=int, default=0)
    ap.add_argument("--to-step", type=int, default=10**9)
    ap.add_argument("--min-distinct", type=int, default=1)
    ap.add_argument(
        "--seat",
        choices=("a", "0", "1", "both"),
        default="a",
        help="a = the A/candidate seat stored by ledger_match.py",
    )
    args = ap.parse_args()

    for name in args.pickles:
        p = Path(name)
        with p.open("rb") as fh:
            game = pickle.load(fh)
        a_seat = int(game.get("a_seat", game.get("v5_seat", 0)))
        if args.seat == "a":
            seats = (a_seat,)
        elif args.seat == "both":
            seats = (0, 1)
        else:
            seats = (int(args.seat),)

        final = game.get("final")
        print(f"\n=== {p.name} seed={game.get('seed')} a_seat={a_seat} final={final}")
        grouped: dict[tuple[int, int], list[tuple]] = collections.defaultdict(list)
        for row in game.get("ledger", []):
            if len(row) < 5:
                continue
            step, player, op = int(row[0]), int(row[1]), row[2]
            if op != "SELL" or step < args.from_step or step > args.to_step:
                continue
            if player in seats:
                grouped[(step, player)].append(row)

        shown = 0
        total_gross = collections.Counter()
        total_units = collections.Counter()
        for (step, player), rows in sorted(grouped.items()):
            s = _step_stats(rows)
            if s["distinct"] < args.min_distinct:
                continue
            shown += 1
            total_gross[player] += s["gross"]
            total_units[player] += s["units"]
            print(
                f"step {step:3d} seat{player}: units={s['units']:3d} distinct={s['distinct']} "
                f"gross={_fmt_num(s['gross'])} seq={_rle(s['sequence'])}"
            )
            item_parts = []
            for item, x in s["items"].items():
                item_parts.append(
                    f"{item} q{x['qty']} gross={_fmt_num(x['gross'])} avg={_fmt_num(x['avg'])} "
                    f"first={_fmt_num(x['first'])} last={_fmt_num(x['last'])} "
                    f"drop={_fmt_num(x['realized_drop'])}"
                )
            print("  " + " | ".join(item_parts))

        if not shown:
            print("(no matching SELL steps)")
        else:
            for player in seats:
                if total_units[player]:
                    print(
                        f"TOTAL seat{player}: units={total_units[player]} "
                        f"gross={_fmt_num(total_gross[player])}"
                    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
