from pathlib import Path
import hashlib
import sys

SRC_SHA = "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"
OUT_SHA = "bad25166aa91712007af8a010f571dab5cf87873dc75f762f2e83b152849faad"

src = Path(sys.argv[1])
out = Path(sys.argv[2])
b = src.read_bytes()
assert hashlib.sha256(b).hexdigest() == SRC_SHA
nl = b"\r\n" if b"_CA_MARGIN = -20.0\r\n" in b else b"\n"
old = b"_CA_MARGIN = -20.0" + nl
assert b.count(old) == 1
b = b.replace(old, old + b"_CA_EARLY_MARGIN = 0.0" + nl + b"_CA_MARGIN_CUTOFF = 540" + nl, 1)
old = b"        pays_now = 3 * (p_c - _CA_DROP) - 20 > 4 * p_w - 10 + _CA_MARGIN" + nl
new = b"        ca_margin = _CA_EARLY_MARGIN if step < _CA_MARGIN_CUTOFF else _CA_MARGIN" + nl + b"        pays_now = 3 * (p_c - _CA_DROP) - 20 > 4 * p_w - 10 + ca_margin" + nl
assert b.count(old) == 1
b = b.replace(old, new, 1)
old = b"                if cu * (p_c - _CA_DROP) - 20 > wu * p_w - 10 + _CA_MARGIN:" + nl
new = b"                if cu * (p_c - _CA_DROP) - 20 > wu * p_w - 10 + ca_margin:" + nl
assert b.count(old) == 1
b = b.replace(old, new, 1)
assert hashlib.sha256(b).hexdigest() == OUT_SHA
out.write_bytes(b)
print(OUT_SHA)
