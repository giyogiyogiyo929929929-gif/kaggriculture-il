from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V134_SHA256 = "be671048262de3269d30fb29357828015597e72be32718870147fe09ea325669"


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

    old = """        if standard:action=_adv_apply(observation,action)\n        if standard and _ADV_FRONT:action=_adv_frontload(observation,action)\n"""
    new = """        if standard:action=_adv_apply(observation,action)\n        if standard and _ADV_FRONT:action=_adv_frontload(observation,action)\n        # v134: R37 originally runs before EXP293 sale-advance/frontload. Reapply the\n        # champion's existing SELL-block quote-priority once to the combined post-advance\n        # market list. This changes order only; quantities, timing, routes and gates stay fixed.\n        if standard and int(observation['step'])>=288:action=_r37_reorder_sales(observation,action)\n"""
    source = replace_once(source, old, new, "post-advance R37 insertion")

    got = sha256_text(source)
    if got != V134_SHA256:
        raise SystemExit(f"v134 sha256 mismatch: {got} != {V134_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v134_sha256={got}")
    print(f"v134_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
