from __future__ import annotations

import argparse
import json
from pathlib import Path

RANK = {"L": 0, "T": 1, "W": 2}


def outcome(margin: float) -> str:
    if margin > 0:
        return "W"
    if margin < 0:
        return "L"
    return "T"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    args = p.parse_args()

    src = json.loads(Path(args.input).read_text(encoding="utf-8"))
    counts = {
        "cells": 0,
        "improved_outcome": 0,
        "worsened_outcome": 0,
        "same_outcome": 0,
        "nonwin_to_win": 0,
        "loss_to_tie": 0,
        "win_to_nonwin": 0,
        "tie_to_loss": 0,
        "champion_wins": 0,
        "champion_ties": 0,
        "champion_losses": 0,
        "candidate_wins": 0,
        "candidate_ties": 0,
        "candidate_losses": 0,
    }
    cells = []
    for row in src.get("rows", []):
        seed = int(row["seed"])
        for seat in row.get("seats", []):
            c_margin = float(seat["candidate_margin"])
            h_margin = float(seat["champion_margin"])
            co = outcome(c_margin)
            ho = outcome(h_margin)
            counts["cells"] += 1
            counts[{"W": "champion_wins", "T": "champion_ties", "L": "champion_losses"}[ho]] += 1
            counts[{"W": "candidate_wins", "T": "candidate_ties", "L": "candidate_losses"}[co]] += 1
            if RANK[co] > RANK[ho]:
                counts["improved_outcome"] += 1
            elif RANK[co] < RANK[ho]:
                counts["worsened_outcome"] += 1
            else:
                counts["same_outcome"] += 1
            if ho != "W" and co == "W":
                counts["nonwin_to_win"] += 1
            if ho == "L" and co == "T":
                counts["loss_to_tie"] += 1
            if ho == "W" and co != "W":
                counts["win_to_nonwin"] += 1
            if ho == "T" and co == "L":
                counts["tie_to_loss"] += 1
            cells.append({
                "seed": seed,
                "swap": bool(seat["swap"]),
                "champion_outcome": ho,
                "candidate_outcome": co,
                "champion_margin": h_margin,
                "candidate_margin": c_margin,
                "candidate_minus_champion_money": float(seat["candidate_minus_champion_money"]),
                "candidate_minus_champion_margin": float(seat["candidate_minus_champion_margin"]),
            })

    out = {
        "opponent": src.get("opponent"),
        "seed_start": src.get("seed_start"),
        "seed_count": src.get("seed_count"),
        "candidate_minus_champion_mean": src.get("candidate_minus_champion_mean"),
        "worst_pair_cash_delta": src.get("worst"),
        "best_pair_cash_delta": src.get("best"),
        "candidate_exceptions": src.get("candidate_exceptions"),
        "champion_exceptions": src.get("champion_exceptions"),
        **counts,
        "cells_detail": cells,
    }
    dst = Path(args.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "cells_detail"}, indent=2))


if __name__ == "__main__":
    main()
