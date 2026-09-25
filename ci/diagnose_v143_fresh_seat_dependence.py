from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from kaggle_environments import make
from scripts.eval import resolve_agent

EVENT_INSERT = '''        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n'''
EVENT_REPLACEMENT = '''        qty = min(int(stock.get(item, 0)), ours)\n        _v143_diag_preds = [int(ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0)) for ev in best]\n        _V143_FRESH_DIAG.append({\n            "step": int(step),\n            "item": item,\n            "preds": _v143_diag_preds,\n            "votes_active": int(votes),\n            "votes_ge1": int(sum(1 for x in _v143_diag_preds if x >= 1)),\n            "votes_ge2": int(sum(1 for x in _v143_diag_preds if x >= 2)),\n            "ours": int(ours),\n            "stock": int(stock.get(item, 0)),\n            "qty": int(qty),\n            "r37_quote_exposure": float(_r37_quote_priority(obs, ["SELL", item, qty], stock)) if qty > 0 else 0.0,\n            "market_before": [list(o) for o in market],\n            "already": sorted(already),\n            "top_score": float(st.get("top_score", -999.0)),\n            "market_price": int((obs.get("market") or {}).get("prices", {}).get(item, 0) or 0),\n            "market_inventory": int((obs.get("market") or {}).get("inventory", {}).get(item, 0) or 0),\n        })\n        if qty > 0:\n'''


def instrument_v115(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    if text.count(EVENT_INSERT) != 1:
        raise SystemExit(f"{src}: expected one primary V92 qty block, found {text.count(EVENT_INSERT)}")
    text = text.replace(EVENT_INSERT, EVENT_REPLACEMENT, 1)
    text += "\n# diagnostic-only non-callable data\n_V143_FRESH_DIAG = []\n"
    dst.write_text(text, encoding="utf-8")


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)


def digest(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


class TraceAgent:
    def __init__(self, spec: str):
        self.agent = resolve_agent(spec)
        code = getattr(self.agent, "__code__", None)
        self.argcount = code.co_argcount if code is not None else 2
        self.trace: list[dict[str, Any]] = []
        self.exceptions: list[str] = []

    def __call__(self, obs, config=None):
        before = copy.deepcopy(obs)
        try:
            action = self.agent(*[obs, config][: self.argcount])
        except Exception as exc:
            self.exceptions.append(repr(exc))
            raise
        action = copy.deepcopy(action)
        self.trace.append({
            "step": int(before.get("step", len(self.trace))),
            "obs_hash": digest(before),
            "action_hash": digest(action),
            "action": action,
        })
        return action

    def events(self) -> list[dict[str, Any]]:
        return copy.deepcopy(getattr(self.agent, "__globals__", {}).get("_V143_FRESH_DIAG", []))


def run(spec: str, opponent_spec: str, seed: int, seat: int) -> dict[str, Any]:
    focal = TraceAgent(spec)
    opponent = resolve_agent(opponent_spec)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([focal, opponent] if seat == 0 else [opponent, focal])
    rewards = [state.get("reward") for state in env.state]
    return {
        "reward": rewards[seat],
        "opponent_reward": rewards[1 - seat],
        "trace": focal.trace,
        "events": focal.events(),
        "exceptions": focal.exceptions,
    }


def order_delta(a: Any, b: Any) -> list[list[Any]]:
    am = [list(o) for o in (a or {}).get("market") or []] if isinstance(a, dict) else []
    bm = [list(o) for o in (b or {}).get("market") or []] if isinstance(b, dict) else []
    left = [list(o) for o in am]
    for o in bm:
        if o in left:
            left.remove(o)
    return left


def first_div(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, Any]:
    bt, ct = base["trace"], cand["trace"]
    n = min(len(bt), len(ct))
    idx = next((i for i in range(n) if bt[i]["action_hash"] != ct[i]["action_hash"]), None)
    if idx is None:
        return {"first_action_mismatch": None, "trace_len": [len(bt), len(ct)]}
    b, c = bt[idx], ct[idx]
    step = int(b["step"])
    return {
        "first_action_mismatch": idx,
        "step": step,
        "same_observation": b["obs_hash"] == c["obs_hash"],
        "v115_action": b["action"],
        "v143_action": c["action"],
        "removed_from_v115": order_delta(b["action"], c["action"]),
        "added_by_v143": order_delta(c["action"], b["action"]),
        "v115_primary_events_at_step": [e for e in base["events"] if int(e["step"]) == step],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v115", required=True)
    ap.add_argument("--v143", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    diag_v115 = out.parent / "v115_v143_fresh_diag.py"
    instrument_v115(Path(args.v115), diag_v115)

    # Seeds 663 and 669 are already-burned fresh-screen seeds where the two
    # seats moved in opposite directions (+50/-50 and +41/-41). Seed 651 is
    # the known positive burned control. No unused/sealed seed is consumed.
    cases = [(663, 0), (663, 1), (669, 0), (669, 1), (651, 0), (651, 1)]
    rows = []
    for seed, seat in cases:
        base = run(str(diag_v115), args.v115, seed, seat)
        cand = run(args.v143, args.v115, seed, seat)
        rows.append({
            "seed": seed,
            "seat": seat,
            "reward_delta_v143_minus_v115_counterfactual": float(cand["reward"]) - float(base["reward"]),
            "v115_reward": base["reward"],
            "v143_reward": cand["reward"],
            "v115_exceptions": base["exceptions"],
            "v143_exceptions": cand["exceptions"],
            "divergence": first_div(base, cand),
        })

    report = {
        "purpose": "burned v143 fresh-screen seat-dependence telemetry; not promotion evidence",
        "metric": "candidate_minus_champion = candidate - champion",
        "rows": rows,
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
