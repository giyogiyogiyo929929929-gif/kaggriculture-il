from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V147_SHA256 = "8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923"

APPEND = r'''

# Diagnostic only: evaluate the existing v111 reorder without the v147
# CONFIRMED-clone gate, but never return the counterfactual action.
_V111_CF_PARENT = agent
_V111_CF_REPORT = {"calls": 0, "changes": 0, "errors": 0, "rows": []}
del agent

def agent(observation, configuration=None):
    action = _V111_CF_PARENT(observation, configuration)
    try:
        before = [list(o) for o in (action.get("market") or [])]
        _V111_CF_REPORT["calls"] += 1
        after = _v111_reorder(observation, before)
        after = [list(o) for o in (after or [])]
        if after != before:
            _V111_CF_REPORT["changes"] += 1
            stock = projected_shed(action, FarmView(observation))
            priorities = []
            for idx, order in enumerate(before):
                if order and order[0] == "SELL":
                    priorities.append({
                        "idx": idx,
                        "order": list(order),
                        "quote_priority": float(_r37_quote_priority(observation, order, stock)),
                    })
            if len(_V111_CF_REPORT["rows"]) < 128:
                _V111_CF_REPORT["rows"].append({
                    "step": int(observation.get("step", -1)),
                    "before": before,
                    "after": after,
                    "priorities": priorities,
                    "vote": str(globals().get("_V44Y_LAST", {}).get("vote", "")),
                })
    except Exception as exc:
        _V111_CF_REPORT["errors"] += 1
        if len(_V111_CF_REPORT["rows"]) < 128:
            _V111_CF_REPORT["rows"].append({"step": int(observation.get("step", -1)), "error": repr(exc)})
    return action

agent.telemetry = _V111_CF_REPORT
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()
    src = Path(args.source)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != V147_SHA256:
        raise SystemExit(f"v147 sha mismatch: {got}")
    for symbol in ("def _v111_reorder", "def _r37_quote_priority", "def projected_shed", "class FarmView"):
        if symbol not in text:
            raise SystemExit(f"required symbol missing: {symbol}")
    dst.write_text(text + APPEND, encoding="utf-8")
    print("diag_sha256=" + hashlib.sha256(dst.read_bytes()).hexdigest())
    print("mode=non-mutating action; ungated _v111_reorder counterfactual telemetry")


if __name__ == "__main__":
    main()
