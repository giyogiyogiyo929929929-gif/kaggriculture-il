from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parts = sorted(ROOT.glob("v91_h9.py.gz.b64.part*"))
if not parts:
    raise SystemExit("missing v91 h9 payload parts")

payload = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
source = gzip.decompress(base64.b64decode(payload)).decode("utf-8")
sha = hashlib.sha256(source.encode("utf-8")).hexdigest()
expected = "1c1c21f2038b5c756acdba9cc886955774c929c0cd716f4b584e157fc9726f81"
if sha != expected:
    raise SystemExit(f"v91 sha256 mismatch: {sha} != {expected}")

h9 = ROOT / "v91_chase_h9.py"
h9.write_text(source, encoding="utf-8")

old1 = 'lead["ceiling"] = min(9, previous + 1)'
new1 = 'lead["ceiling"] = min(13, previous + 1)'
old2 = 'ceiling = min(9, max(6, int(lead.get("ceiling", 7) or 7)))'
new2 = 'ceiling = min(13, max(6, int(lead.get("ceiling", 7) or 7)))'
if source.count(old1) != 1 or source.count(old2) != 1:
    raise SystemExit("unexpected h9 source: targeted ceiling lines not unique")
h13_source = source.replace(old1, new1).replace(old2, new2)
h13 = ROOT / "v92_chase_h13.py"
h13.write_text(h13_source, encoding="utf-8")

print(f"v91_sha256={sha}")
print(f"v91_bytes={len(source.encode('utf-8'))}")
print(f"v92_h13_sha256={hashlib.sha256(h13_source.encode('utf-8')).hexdigest()}")
