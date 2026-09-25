from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V132_SHA256 = "99b5c3ce0ddd4e4a7acd96441b71ed88f08a2cbc5d0a2635583e75818a11c21b"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("champion")
    parser.add_argument("out")
    args = parser.parse_args()

    champion = Path(args.champion)
    source = champion.read_text(encoding="utf-8")
    got = sha256_text(source)
    if got != V115_SHA256:
        raise SystemExit(f"v115 source sha256 mismatch: {got} != {V115_SHA256}")

    old = "_OPEN_ATTACK=30\n"
    if source.count(old) != 1:
        raise SystemExit(f"expected one _OPEN_ATTACK=30 assignment, found {source.count(old)}")
    source = source.replace(old, "_OPEN_ATTACK=15\n")

    got = sha256_text(source)
    if got != V132_SHA256:
        raise SystemExit(f"v132 sha256 mismatch: {got} != {V132_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v132_sha256={got}")
    print(f"v132_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
