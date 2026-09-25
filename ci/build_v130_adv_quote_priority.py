from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V130_SHA256 = "6e673773e76eb0ebb0b561570da10c5125193ca30681f14aac63d83ae5a1f976"


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

    old = """    for item in sorted({it for _,it,_ in plan},key=lambda it:-int(prices.get(it,0))):\n"""
    new = """    # v130: the earlier R37 quote-priority layer runs before _adv_apply, so newly\n    # advanced SELLs would otherwise be ordered only by headline price. Rank just\n    # these candidate items by the same public-state quote-exposure model already\n    # used by v115, without changing quantities, horizon, or native route orders.\n    def _adv_priority(it):\n        avail=max(0,int(stock.get(it,0))-selling.get(it,0))\n        q=min(avail,sum(q for _,item,q in plan if item==it))\n        return _r37_quote_priority(obs,['SELL',it,q],stock)\n    for item in sorted({it for _,it,_ in plan},key=_adv_priority,reverse=True):\n"""
    source = replace_once(source, old, new, "advanced-sale ordering")

    got = sha256_text(source)
    if got != V130_SHA256:
        raise SystemExit(f"v130 sha256 mismatch: {got} != {V130_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v130_sha256={got}")
    print(f"v130_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
