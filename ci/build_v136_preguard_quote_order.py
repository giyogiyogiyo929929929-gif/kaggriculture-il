from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V136_SHA256 = "528104f691a53192904d59e491c5d9802f99cc99e2131890eee29dc2678a57f1"


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

    old = """    if not extra or len(orders)+len(extra)>10:return action\n    _PG_REPORT['preguard_turns']+=1;_PG_REPORT['preguard_units']+=sum(o[2] for o in extra)\n    return dict(action,market=orders+extra)\n"""
    new = """    if not extra or len(orders)+len(extra)>10:return action\n    # v136: keep the preguard's selected items and quantities unchanged; only\n    # rank the newly-added SELLs with v115's existing public quote-exposure model.\n    if len(extra)>1:\n        extra=sorted(extra,key=lambda o:_r37_quote_priority(obs,o,stock),reverse=True)\n    _PG_REPORT['preguard_turns']+=1;_PG_REPORT['preguard_units']+=sum(o[2] for o in extra)\n    return dict(action,market=orders+extra)\n"""
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"preguard block: expected exactly one target, found {count}")
    source = source.replace(old, new)

    got = sha256_text(source)
    if got != V136_SHA256:
        raise SystemExit(f"v136 sha256 mismatch: {got} != {V136_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v136_sha256={got}")
    print(f"v136_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
