from pathlib import Path
import hashlib
import sys

PARENT_SHA256 = "cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44"
CANDIDATE_SHA256 = "2aab62a693bd3a357ad87649b8ba90a79b512d383a7694b07bbcdbe0deef48c8"

SUFFIX = r'''

# Candidate: defer only CARROT market sales chosen from the day-25 hour-0 observation.
# Delete/reinsert agent so Kaggle's namespace-order loader selects this wrapper.
_D25_CARROT_PARENT = agent
try:
    del agent
except Exception:
    pass

def agent(observation, configuration=None):
    action = _D25_CARROT_PARENT(observation, configuration)
    try:
        if int(observation.get("step", -1)) == 600 and isinstance(action, dict):
            market = action.get("market")
            if isinstance(market, list):
                kept = [
                    order for order in market
                    if not (
                        isinstance(order, (list, tuple))
                        and len(order) >= 2
                        and order[0] == "SELL"
                        and order[1] == "CARROT"
                    )
                ]
                if len(kept) != len(market):
                    action = dict(action)
                    action["market"] = kept
    except Exception:
        pass
    return action

agent.telemetry = getattr(_D25_CARROT_PARENT, "telemetry", None)
'''


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python ci/build_uploaded_127ed3_ca_feed0_d25_carrot_hold_v1.py PARENT OUTPUT")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    parent = src.read_bytes()
    got = hashlib.sha256(parent).hexdigest()
    if got != PARENT_SHA256:
        raise SystemExit(f"parent sha mismatch: {got}")
    child = parent + SUFFIX.encode("utf-8")
    sha = hashlib.sha256(child).hexdigest()
    if sha != CANDIDATE_SHA256:
        raise SystemExit(f"candidate sha mismatch: {sha}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(child)
    print(f"parent_sha256={got}")
    print(f"candidate_sha256={sha}")
    print(f"candidate_bytes={len(child)}")


if __name__ == "__main__":
    main()
