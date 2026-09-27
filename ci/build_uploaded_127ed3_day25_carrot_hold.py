from pathlib import Path
import base64
import gzip
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ci.build_uploaded_127ed3_safety_v3 import (
    PART_DIR,
    PART_NAMES,
    RAW_SHA256,
    SAFE_V3_SHA256,
    WRAPPER,
)

PARENT_SHA256 = SAFE_V3_SHA256

SUFFIX = r'''

# Candidate: defer only CARROT market sales chosen from the day-25 hour-0 observation.
# The parent action is otherwise returned unchanged. Any retained CARROT remains in the
# shed and the unmodified parent can decide what to do with it on later observations.
_DAY25_CARROT_PARENT = agent

def agent(observation, configuration=None):
    action = _DAY25_CARROT_PARENT(observation, configuration)
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

agent.telemetry = getattr(_DAY25_CARROT_PARENT, "telemetry", None)
'''


def build(output: Path) -> str:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Keep reconstruction identical to the formal safety-v3 builder: only part00..part11.
    packed_b64 = "".join((PART_DIR / name).read_text(encoding="ascii") for name in PART_NAMES)
    raw = gzip.decompress(base64.b64decode(packed_b64))
    got_raw = hashlib.sha256(raw).hexdigest()
    assert got_raw == RAW_SHA256, got_raw

    parent = raw + WRAPPER
    got_parent = hashlib.sha256(parent).hexdigest()
    assert got_parent == PARENT_SHA256, got_parent

    child = parent + SUFFIX.encode("utf-8")
    output.write_bytes(child)
    return hashlib.sha256(child).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_uploaded_127ed3_day25_carrot_hold.py OUTPUT.py")
    out = Path(sys.argv[1])
    sha = build(out)
    print(f"wrote={out}")
    print(f"sha256={sha}")
