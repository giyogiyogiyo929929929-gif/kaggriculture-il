from pathlib import Path
import hashlib
import sys

PARENT_SHA256 = "cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44"
CANDIDATE_SHA256 = "d3cfbcbacb3530fc44e6db41fe7b336b00dcda6ae5823694869176de42711d9e"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python ci/build_uploaded_127ed3_ca_feed0_earlythin_v1.py PARENT OUTPUT")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    text = src.read_text(encoding="utf-8")
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != PARENT_SHA256:
        raise SystemExit(f"parent sha mismatch: {got}")
    old = "wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, _CA_FEED_DAYS)"
    new = (
        'early_thin = step < 300 and sum(1 for row in observation["farms"][seat]["tiles"] for tile in row '
        'if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "WHEAT") <= 5\n'
        '                    wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, 1 if early_thin else _CA_FEED_DAYS)'
    )
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one wheat_ok target, got {text.count(old)}")
    child = text.replace(old, new, 1).encode("utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(child)
    sha = hashlib.sha256(child).hexdigest()
    if sha != CANDIDATE_SHA256:
        raise SystemExit(f"candidate sha mismatch: {sha}")
    print(f"parent_sha256={got}")
    print(f"candidate_sha256={sha}")
    print(f"candidate_bytes={len(child)}")


if __name__ == "__main__":
    main()
