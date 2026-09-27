from pathlib import Path
import hashlib
import sys

PARENT_SHA256 = "cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44"
CANDIDATE_SHA256 = "e172cc82ff049766b9013a0a973817359d04349946544b1ba2091b552dc07c82"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python ci/build_uploaded_127ed3_ca_feed0_earlythin_v1.py PARENT OUTPUT")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    b = src.read_bytes()
    got = hashlib.sha256(b).hexdigest()
    if got != PARENT_SHA256:
        raise SystemExit(f"parent sha mismatch: {got}")

    old = b"wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, _CA_FEED_DAYS)"
    if b.count(old) != 1:
        raise SystemExit(f"expected exactly one wheat_ok target, got {b.count(old)}")
    idx = b.index(old)
    tail = b[idx + len(old):]
    eol = b"\r\n" if tail.startswith(b"\r\n") else b"\n"
    new = (
        b'early_thin = step < 300 and sum(1 for row in observation["farms"][seat]["tiles"] for tile in row '
        b'if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "WHEAT") <= 5'
        + eol
        + b'                    wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, 1 if early_thin else _CA_FEED_DAYS)'
    )
    child = b.replace(old, new, 1)
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
