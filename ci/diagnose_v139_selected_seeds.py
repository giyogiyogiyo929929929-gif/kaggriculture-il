from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import ci.diagnose_v139_seed628 as diag

SEEDS = (621, 626, 628, 631)


def scalar_step_fields(value: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for k, v in value.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            if "step" in str(k).lower() and isinstance(v, (int, float, str, type(None))):
                out[p] = v
            elif isinstance(v, (dict, list)):
                out.update(scalar_step_fields(v, p))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            if isinstance(v, (dict, list)):
                out.update(scalar_step_fields(v, f"{prefix}[{i}]"))
    return out


def k1_only(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        e for e in events
        if int(e.get("votes_k1", 0)) > 0
        and int(e.get("votes_k2", 0)) == 0
        and int(e.get("qty_possible", 0)) > 0
    ]


def market(action: Any) -> list[list[Any]]:
    if not isinstance(action, dict):
        return []
    return [list(o) for o in (action.get("market") or [])]


def removed_orders(base_action: Any, cand_action: Any) -> list[list[Any]]:
    bc = Counter(tuple(o) for o in market(base_action))
    cc = Counter(tuple(o) for o in market(cand_action))
    return [list(o) for o, n in (bc - cc).items() for _ in range(n)]


def summarize(seed: int, seat: int, v115_diag: Path, v139_diag: Path, exact_v115: str) -> dict[str, Any]:
    diag.SEED = seed
    base = diag.run_focal(str(v115_diag), exact_v115, seat)
    cand = diag.run_focal(str(v139_diag), exact_v115, seat)
    div = diag.first_divergence(base, cand)
    i = div.get("first_action_mismatch_call")
    result: dict[str, Any] = {
        "seed": seed,
        "seat": seat,
        "baseline_reward": base["focal_reward"],
        "candidate_reward": cand["focal_reward"],
        "reward_delta_candidate_minus_baseline": float(cand["focal_reward"]) - float(base["focal_reward"]),
        "first_action_mismatch_call": i,
        "same_observation": div.get("same_observation_at_action_divergence"),
        "first_observation_mismatch_call": div.get("first_observation_mismatch_call"),
        "baseline_action": div.get("baseline_action"),
        "candidate_action": div.get("candidate_action"),
        "removed_orders": removed_orders(div.get("baseline_action"), div.get("candidate_action")),
        "step_fields_at_divergence": scalar_step_fields(div.get("baseline_observation")),
    }
    all_k1 = k1_only(base["diag_events"])
    result["baseline_k1_only_count"] = len(all_k1)
    result["baseline_k1_only_events"] = all_k1
    # The first divergent order should correspond to one of these events.  Emit
    # exact item/qty matches separately so the workflow log stays readable.
    matches = []
    for order in result["removed_orders"]:
        if len(order) < 3 or order[0] != "SELL":
            continue
        item, qty = order[1], int(order[2])
        matches.extend(e for e in all_k1 if e.get("item") == item and int(e.get("qty_possible", -1)) == qty)
    result["k1_only_matches_removed_order"] = matches
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v115", required=True)
    ap.add_argument("--v139", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    v115_diag = out.parent / "v115_diag_selected.py"
    v139_diag = out.parent / "v139_diag_selected.py"
    diag.instrument(Path(args.v115), v115_diag)
    diag.instrument(Path(args.v139), v139_diag)

    rows = [summarize(seed, 0, v115_diag, v139_diag, args.v115) for seed in SEEDS]
    report = {
        "purpose": "burned development contrast; not promotion evidence",
        "seeds": list(SEEDS),
        "seat": 0,
        "rows": rows,
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    compact = []
    for r in rows:
        compact.append({
            "seed": r["seed"],
            "reward_delta_candidate_minus_baseline": r["reward_delta_candidate_minus_baseline"],
            "first_action_mismatch_call": r["first_action_mismatch_call"],
            "same_observation": r["same_observation"],
            "baseline_market": market(r["baseline_action"]),
            "candidate_market": market(r["candidate_action"]),
            "removed_orders": r["removed_orders"],
            "step_fields_at_divergence": r["step_fields_at_divergence"],
            "baseline_k1_only_count": r["baseline_k1_only_count"],
            "k1_only_matches_removed_order": r["k1_only_matches_removed_order"],
            "k1_only_first10": r["baseline_k1_only_events"][:10],
        })
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
