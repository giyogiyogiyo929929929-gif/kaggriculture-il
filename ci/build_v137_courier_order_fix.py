from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V137_SHA256 = "9bf28ad9d9f8b405adfb2cc96e4c67912f0946205f40afab69179bb687343553"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("champion")
    parser.add_argument("out")
    args = parser.parse_args()

    source = Path(args.champion).read_text(encoding="utf-8")
    got = sha256_text(source)
    if got != V115_SHA256:
        raise SystemExit(f"v115 source sha256 mismatch: {got} != {V115_SHA256}")

    old = "for item, n in sorted(delivered.items(), key=lambda kv: -int(prices.get(kv[0], 0)) * kv[1]):"
    new = "for item, n in sorted(delivered.items(), key=lambda kv: int(prices.get(kv[0], 0)) * kv[1]):"
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"courier ordering: expected exactly one target, found {count}")
    source = source.replace(old, new)

    got = sha256_text(source)
    if got != V137_SHA256:
        raise SystemExit(f"v137 sha256 mismatch: {got} != {V137_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v137_sha256={got}")
    print(f"v137_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
