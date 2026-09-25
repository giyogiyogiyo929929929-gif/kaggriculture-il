from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V135_SHA256 = "90c91e19068e5b4324748f6eec61f54f93fd5af06f622d12ec8b5cf4b28896c1"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    return source.replace(old, new)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("champion")
    parser.add_argument("out")
    args = parser.parse_args()

    source = Path(args.champion).read_text(encoding="utf-8")
    got = sha256_text(source)
    if got != V115_SHA256:
        raise SystemExit(f"v115 source sha256 mismatch: {got} != {V115_SHA256}")

    old = """        if _v105_standard(configuration) and _v44y_clone_gate(observation):\n            action=_v111_reorder(observation,action)\n"""
    new = """        # v135: use the step-1 mirror latch rather than the behavior-dependent live clone gate.\n        # Keep the original late-game scope; non-mirror games stay on v115 behavior.\n        step=int(observation.get('step',0))\n        if (_v105_standard(configuration) and step>=216 and\n                int(_RACE_REPORT.get('race_mirror',0))==1):\n            action=_v111_reorder(observation,action)\n"""
    source = replace_once(source, old, new, "final Layer-D gate")

    got = sha256_text(source)
    if got != V135_SHA256:
        raise SystemExit(f"v135 sha256 mismatch: {got} != {V135_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v135_sha256={got}")
    print(f"v135_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
