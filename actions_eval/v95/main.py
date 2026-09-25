from pathlib import Path
import base64
import re
import zlib

wrapper = (Path(__file__).resolve().parents[1] / "v94" / "main.py").read_text(encoding="utf-8")
m = re.search(r"b85decode\('([^']+)'\)", wrapper)
if not m:
    raise RuntimeError("v94 payload not found")
src = zlib.decompress(base64.b85decode(m.group(1))).decode("utf-8")
src = src.replace("min(14 if _adaptive_h14_allowed(obs) else 13, previous + 1)", "min(15 if _adaptive_h14_allowed(obs) else 13, previous + 1)")
src = src.replace("min(14 if _adaptive_h14_allowed(obs) else 13, max(6, int(lead.get(\"ceiling\", 7) or 7)))", "min(15 if _adaptive_h14_allowed(obs) else 13, max(6, int(lead.get(\"ceiling\", 7) or 7)))")
src = src.replace('if horizon == 14 and item == "MILK":', 'if horizon >= 14 and item == "MILK":')
src = src.replace('agent.__version__ = "v94-adaptive-h14-yarn2-nomilk"', 'agent.__version__ = "v95-adaptive-h15-yarn2-nomilk"')
exec(compile(src, __file__, "exec"))
