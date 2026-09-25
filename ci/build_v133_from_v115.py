from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V133_SHA256 = "6e673773e76eb0ebb0b561570da10c5125193ca30681f14aac63d83ae5a1f976"


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

    champion = Path(args.champion)
    source = champion.read_text(encoding="utf-8")
    got = sha256_text(source)
    if got != V115_SHA256:
        raise SystemExit(f"v115 source sha256 mismatch: {got} != {V115_SHA256}")

    old = "    for item in sorted({it for _,it,_ in plan},key=lambda it:-int(prices.get(it,0))):\n"
    new = """    # v133: newly advanced SELLs are created after R37's normal quote-order pass.\n    # Rank only these new sales with the same executable-quote priority so they do not\n    # bypass the champion's established market-order logic. Quantities/timing are unchanged.\n    def _adv_priority(it):\n        avail=max(0,int(stock.get(it,0))-selling.get(it,0))\n        q=min(avail,sum(q for _,item,q in plan if item==it))\n        return _r37_quote_priority(obs,['SELL',it,q],stock)\n    for item in sorted({it for _,it,_ in plan},key=_adv_priority,reverse=True):\n"""
    source = replace_once(source, old, new, "advanced-sale ordering")

    got = sha256_text(source)
    if got != V133_SHA256:
        raise SystemExit(f"v133 sha256 mismatch: {got} != {V133_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v133_sha256={got}")
    print(f"v133_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
