from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V139_SHA256 = "87209371be092a7587d08cd9bdf452d206d8a52d49fb9f7be0f069aa23602d2e"


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

    old = "_V92_P_K = 1"
    new = "_V92_P_K = 2"
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"V92 K target: expected one target, found {count}")
    source = source.replace(old, new)

    got = sha256_text(source)
    if got != V139_SHA256:
        raise SystemExit(f"v139 sha256 mismatch: {got} != {V139_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v139_sha256={got}")
    print(f"v139_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
