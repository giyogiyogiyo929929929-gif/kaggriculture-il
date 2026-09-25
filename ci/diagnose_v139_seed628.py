from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from kaggle_environments import make
from scripts.eval import resolve_agent, evaluate

SEED = 628

V92_NEEDLE = '''        votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)\n        if votes < 1:\n            continue\n        ours = 0\n        for t in range(step + 1, min(len(tape), step + _V92_P_H + 1)):\n            ours += sum(min(100, int(o[2])) for o in (tape[t] or {}).get("market") or []\n                        if len(o) >= 3 and o[0] == "SELL" and o[1] == item)\n        qty = min(int(stock.get(item, 0)), ours)\n'''

V92_INSTRUMENTED = '''        votes_k1 = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= 1)\n        votes_k2 = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= 2)\n        votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)\n        ours_diag = 0\n        for t in range(step + 1, min(len(tape), step + _V92_P_H + 1)):\n            ours_diag += sum(min(100, int(o[2])) for o in (tape[t] or {}).get("market") or []\n                             if len(o) >= 3 and o[0] == "SELL" and o[1] == item)\n        _V139_DIAG_EVENTS.append({\n            "step": int(step),\n            "item": item,\n            "k": int(_V92_P_K),\n            "votes": int(votes),\n            "votes_k1": int(votes_k1),\n            "votes_k2": int(votes_k2),\n            "ours": int(ours_diag),\n            "stock": int(stock.get(item, 0)),\n            "qty_possible": int(min(int(stock.get(item, 0)), ours_diag)),\n            "market_before": [list(o) for o in market],\n            "already": sorted(already),\n            "top_score": float(st.get("top_score", -999.0)),\n        })\n        if votes < 1:\n            continue\n        ours = ours_diag\n        qty = min(int(stock.get(item, 0)), ours)\n'''


def instrument(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    count = text.count(V92_NEEDLE)
    if count != 1:
        raise SystemExit(f"{src}: expected one V92 block, found {count}")
    text = text.replace(V92_NEEDLE, V92_INSTRUMENTED)
    text += "\n# diagnostic-only data sink; non-callable so Kaggle callable selection is unchanged\n_V139_DIAG_EVENTS = []\n"
    dst.write_text(text, encoding="utf-8")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def moneyish(value: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for k, v in value.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            lk = str(k).lower()
            if any(token in lk for token in ("money", "cash", "score", "balance")) and isinstance(v, (int, float, str, type(None))):
                out[p] = v
            elif isinstance(v, (dict, list)):
                out.update(moneyish(v, p))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            if isinstance(v, (dict, list)):
                out.update(moneyish(v, f"{prefix}[{i}]"))
    return out


class TraceAgent:
    def __init__(self, spec: str):
        self.agent = resolve_agent(spec)
        code = getattr(self.agent, "__code__", None)
        self.argcount = code.co_argcount if code is not None else 2
        self.trace: list[dict[str, Any]] = []
        self.exceptions: list[str] = []

    def __call__(self, obs, config=None):
        obs_copy = copy.deepcopy(obs)
        try:
            action = self.agent(*[obs, config][: self.argcount])
        except Exception as exc:
            self.exceptions.append(repr(exc))
            raise
        action_copy = copy.deepcopy(action)
        self.trace.append({
            "call": len(self.trace),
            "obs_hash": digest(obs_copy),
            "action_hash": digest(action_copy),
            "action": action_copy,
            "moneyish": moneyish(obs_copy),
            "observation": obs_copy,
        })
        return action

    @property
    def diag_events(self) -> list[dict[str, Any]]:
        g = getattr(self.agent, "__globals__", {})
        return copy.deepcopy(g.get("_V139_DIAG_EVENTS", []))


def run_focal(focal_spec: str, opponent_spec: str, seat: int) -> dict[str, Any]:
    focal = TraceAgent(focal_spec)
    opponent = resolve_agent(opponent_spec)
    env = make("kaggriculture", configuration={"seed": SEED})
    runners = [focal, opponent] if seat == 0 else [opponent, focal]
    env.run(runners)
    rewards = [state.get("reward") for state in env.state]
    return {
        "seat": seat,
        "focal_reward": rewards[seat],
        "opponent_reward": rewards[1 - seat],
        "trace": focal.trace,
        "diag_events": focal.diag_events,
        "exceptions": focal.exceptions,
        "steps": len(env.steps),
    }


def market_delta(a: Any, b: Any) -> dict[str, Any]:
    ma = (a or {}).get("market") or [] if isinstance(a, dict) else []
    mb = (b or {}).get("market") or [] if isinstance(b, dict) else []
    return {"baseline_market": ma, "candidate_market": mb}


def first_divergence(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, Any]:
    bt, ct = base["trace"], cand["trace"]
    limit = min(len(bt), len(ct))
    first_obs_mismatch = None
    first_action_mismatch = None
    for i in range(limit):
        if first_obs_mismatch is None and bt[i]["obs_hash"] != ct[i]["obs_hash"]:
            first_obs_mismatch = i
        if bt[i]["action_hash"] != ct[i]["action_hash"]:
            first_action_mismatch = i
            break
    if first_action_mismatch is None and len(bt) != len(ct):
        first_action_mismatch = limit
    out: dict[str, Any] = {
        "first_observation_mismatch_call": first_obs_mismatch,
        "first_action_mismatch_call": first_action_mismatch,
        "baseline_trace_len": len(bt),
        "candidate_trace_len": len(ct),
    }
    if first_action_mismatch is not None and first_action_mismatch < limit:
        i = first_action_mismatch
        out.update({
            "baseline_obs_hash": bt[i]["obs_hash"],
            "candidate_obs_hash": ct[i]["obs_hash"],
            "same_observation_at_action_divergence": bt[i]["obs_hash"] == ct[i]["obs_hash"],
            "baseline_action": bt[i]["action"],
            "candidate_action": ct[i]["action"],
            "market_delta": market_delta(bt[i]["action"], ct[i]["action"]),
            "baseline_moneyish": bt[i]["moneyish"],
            "candidate_moneyish": ct[i]["moneyish"],
            "baseline_observation": bt[i]["observation"],
            "candidate_observation": ct[i]["observation"],
        })
        # V92 events use the environment step index; preserve a generous neighborhood
        # around the focal call index because observation step numbering may be offset.
        lo, hi = max(0, i - 3), i + 4
        out["baseline_v92_events_near"] = [e for e in base["diag_events"] if lo <= int(e.get("step", -999)) <= hi]
        out["candidate_v92_events_near"] = [e for e in cand["diag_events"] if lo <= int(e.get("step", -999)) <= hi]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v115", required=True)
    ap.add_argument("--v139", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    work = out_path.parent
    v115_diag = work / "v115_diag.py"
    v139_diag = work / "v139_diag.py"
    instrument(Path(args.v115), v115_diag)
    instrument(Path(args.v139), v139_diag)

    report: dict[str, Any] = {
        "seed": SEED,
        "purpose": "diagnostic only; seed628 is burned development evidence and not promotion evidence",
        "seats": [],
    }

    for seat in (0, 1):
        # Counterfactual baseline: focal exact-v115 against exact-v115.
        base = run_focal(str(v115_diag), args.v115, seat)
        # Candidate world: focal v139 against exact-v115 in the same seat/seed.
        cand = run_focal(str(v139_diag), args.v115, seat)
        div = first_divergence(base, cand)
        report["seats"].append({
            "seat": seat,
            "baseline_rewards": [base["focal_reward"], base["opponent_reward"]],
            "candidate_rewards": [cand["focal_reward"], cand["opponent_reward"]],
            "baseline_diag_event_count": len(base["diag_events"]),
            "candidate_diag_event_count": len(cand["diag_events"]),
            "baseline_exceptions": base["exceptions"],
            "candidate_exceptions": cand["exceptions"],
            "divergence": div,
        })

    # Reproduce the official direct pair result in the same job as a guardrail.
    h2h = evaluate(args.v139, args.v115, pairs=1, jobs=1, seed_start=SEED)
    games = []
    for g in sorted(h2h["matches_detail"], key=lambda x: bool(x["swap"])):
        d = float(g["money"][0]) - float(g["money"][1])
        games.append({
            "swap": bool(g["swap"]),
            "candidate_money": g["money"][0],
            "champion_money": g["money"][1],
            "candidate_minus_champion": d,
        })
    report["official_direct_seed628"] = {
        "games": games,
        "pair_candidate_minus_champion": sum(g["candidate_minus_champion"] for g in games) / len(games),
        "candidate_exceptions": h2h["exceptions"]["a"],
        "champion_exceptions": h2h["exceptions"]["b"],
    }

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    compact = {
        "seed": SEED,
        "direct": report["official_direct_seed628"],
        "divergences": [
            {
                "seat": s["seat"],
                "call": s["divergence"].get("first_action_mismatch_call"),
                "same_obs": s["divergence"].get("same_observation_at_action_divergence"),
                "baseline_market": s["divergence"].get("market_delta", {}).get("baseline_market"),
                "candidate_market": s["divergence"].get("market_delta", {}).get("candidate_market"),
                "baseline_v92_events_near": s["divergence"].get("baseline_v92_events_near"),
                "candidate_v92_events_near": s["divergence"].get("candidate_v92_events_near"),
            }
            for s in report["seats"]
        ],
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
