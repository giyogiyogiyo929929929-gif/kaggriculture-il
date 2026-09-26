from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V122_SHA256 = "ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1"
V124_SHA256 = "e5386b0708e7a5bde1b348a4942545a8e9ab453585fdd354ffaf9528c7cb9710"

V124_OVERLAY = """

# v124 candidate: when v122 fires at step649, keep WHEAT immediately after the last
# FERTILIZER SELL instead of forcing WHEAT behind unrelated trailing SELL orders.
# Preserve quantities, turn, BUY/HIRE barriers, and all non-WHEAT relative order.
_V124_PARENT = agent
_V124_REPORT = {'fires': 0, 'no_change': 0, 'errors': 0}

def _v124_adjust_market(action):
    market = [list(o) if isinstance(o, (list, tuple)) else o for o in (action.get('market') or [])]
    end = 0
    while end < len(market) and market[end] and market[end][0] == 'SELL':
        end += 1
    block = market[:end]
    wi = next((i for i,o in enumerate(block) if len(o)>=3 and o[:2]==['SELL','WHEAT']), None)
    ferts = [i for i,o in enumerate(block) if len(o)>=3 and o[:2]==['SELL','FERTILIZER']]
    if wi is None or not ferts:
        return action, False, True
    fi = ferts[-1]
    if wi == fi + 1:
        return action, False, False
    wheat = block.pop(wi)
    if wi < fi:
        fi -= 1
    block.insert(fi + 1, wheat)
    market[:end] = block
    out = dict(action); out['market'] = market
    return out, True, False

def agent(observation, configuration=None):
    before_fires = int(_V122_REPORT.get('fires', 0))
    action = _V124_PARENT(observation, configuration)
    try:
        step = int(observation.get('step', 0)); player = int(observation.get('player', 0))
        if step == 0 and player == 0:
            _V124_REPORT.update(fires=0, no_change=0, errors=0)
        if step != 649 or int(_V122_REPORT.get('fires', 0)) <= before_fires:
            return action
        out, changed, malformed = _v124_adjust_market(action)
        if malformed:
            _V124_REPORT['errors'] += 1
            return action
        if changed:
            _V124_REPORT['fires'] += 1
            return out
        _V124_REPORT['no_change'] += 1
        return action
    except Exception:
        _V124_REPORT['errors'] += 1
        return action
agent.telemetry = _V124_REPORT
kaggle_submission_agent_v124 = agent
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("v122")
    ap.add_argument("v124")
    args = ap.parse_args()

    parent = Path(args.v122).read_bytes()
    got_parent = sha256(parent)
    if got_parent != V122_SHA256:
        raise SystemExit(f"v122 sha mismatch: {got_parent}")

    candidate = parent + V124_OVERLAY.encode("utf-8")
    got_candidate = sha256(candidate)
    if got_candidate != V124_SHA256:
        raise SystemExit(f"v124 sha mismatch: {got_candidate}")

    Path(args.v124).write_bytes(candidate)
    compile(candidate.decode("utf-8"), args.v124, "exec")
    print(f"v124_sha256={got_candidate} bytes={len(candidate)}")


if __name__ == "__main__":
    main()
