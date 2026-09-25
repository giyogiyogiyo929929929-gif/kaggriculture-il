from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V125C_SHA256 = "05b19ae901ee9f9d7078db55038ba931e72c7edd9eae8e97e562be82ea369793"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one replacement target, got {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    args = ap.parse_args()
    base = Path(args.base)
    out = Path(args.out)
    got = sha256(base)
    if got != V115_SHA256:
        raise SystemExit(f"v115 sha256 mismatch: {got} != {V115_SHA256}")

    s = base.read_text(encoding="utf-8")
    s = replace_once(s, "_ADV_BOOK=False", "_ADV_BOOK=True")
    s = replace_once(
        s,
        "                if _ADV_SUBTRACT_DEBTS:q-=debts.get(t,{}).get(o[1],0)   # already reserved by the sale-reservation layer\n                if q>0:plan.append((t,o[1],q))",
        "                if debts.get(t,{}).get(o[1],0)>0:\n                    continue\n                if q>0:plan.append((t,o[1],q))",
    )
    s = replace_once(
        s,
        "            take=min(q,avail);booked.append((t,item,take));n+=take;avail-=take",
        "            take=min(q,avail,max(0,1-added-n));booked.append((t,item,take));n+=take;avail-=take",
    )
    s += "\n# v125c candidate: conserved one-unit refinement of inherited EXP293 sale advance.\nkaggle_submission_agent_v125c = agent\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding="utf-8")
    got = sha256(out)
    if got != V125C_SHA256:
        raise SystemExit(f"v125c sha256 mismatch: {got} != {V125C_SHA256}")
    print(f"v125c_sha256={got}")
    print(f"v125c_bytes={out.stat().st_size}")


if __name__ == "__main__":
    main()
