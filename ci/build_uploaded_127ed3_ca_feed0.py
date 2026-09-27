from pathlib import Path
import hashlib
import sys

PARENT_SHA256 = "87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python ci/build_uploaded_127ed3_ca_feed0.py PARENT OUTPUT")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    b = src.read_bytes()
    got = hashlib.sha256(b).hexdigest()
    if got != PARENT_SHA256:
        raise SystemExit(f"parent sha mismatch: {got}")
    old = b"_CA_FEED_DAYS = 1"
    new = b"_CA_FEED_DAYS = 0"
    if b.count(old) != 1:
        raise SystemExit(f"expected exactly one feed-days setting, got {b.count(old)}")
    child = b.replace(old, new, 1)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(child)
    print(f"parent_sha256={got}")
    print(f"candidate_sha256={hashlib.sha256(child).hexdigest()}")
    print(f"candidate_bytes={len(child)}")


if __name__ == "__main__":
    main()
