#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated"
V94_SHA = "869b7e9fe727694ca52710716921856fea6511ccae71b0613be26f4e9236baa3"
V95_SHA = "ba21fe1dcf78113bb5c2531d015f318dbc0af290c608ea5925578b2485ee62cd"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    encoded = "".join((ROOT / f"payload_{i:02d}.txt").read_text(encoding="utf-8").strip() for i in range(6))
    v94 = zlib.decompress(base64.b64decode(encoded))
    if sha256(v94) != V94_SHA:
        raise SystemExit(f"v94 SHA mismatch: {sha256(v94)}")

    src = v94.decode("utf-8")
    replacements = {
        'lead["ceiling"] = min(14 if _adaptive_h14_allowed(obs) else 13, previous + 1)': 'lead["ceiling"] = min(15 if _adaptive_h14_allowed(obs) else 13, previous + 1)',
        'ceiling = min(14 if _adaptive_h14_allowed(obs) else 13, max(6, int(lead.get("ceiling", 7) or 7)))': 'ceiling = min(15 if _adaptive_h14_allowed(obs) else 13, max(6, int(lead.get("ceiling", 7) or 7)))',
        'if horizon == 14 and item == "MILK":': 'if horizon >= 14 and item == "MILK":',
        'agent.__version__ = "v94-adaptive-h14-yarn2-nomilk"': 'agent.__version__ = "v95-adaptive-h15-yarn2-nomilk"',
    }
    for old, new in replacements.items():
        if src.count(old) != 1:
            raise SystemExit(f"unexpected replacement count for: {old!r}: {src.count(old)}")
        src = src.replace(old, new)
    v95 = src.encode("utf-8")
    if sha256(v95) != V95_SHA:
        raise SystemExit(f"v95 SHA mismatch: {sha256(v95)}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v94_champion.py").write_bytes(v94)
    (OUT / "v95_candidate.py").write_bytes(v95)
    print("v94", V94_SHA)
    print("v95", V95_SHA)


if __name__ == "__main__":
    main()
