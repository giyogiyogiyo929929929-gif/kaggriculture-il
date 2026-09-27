from pathlib import Path
import importlib.util
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
subprocess.check_call([sys.executable, str(ROOT / "build_sources.py")])
source = ROOT / "v112_wheat_lead3_lowdemand.py"
spec = importlib.util.spec_from_file_location("v112", source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

rows = []
for step in range(520, 720):
    action = mod._ACTIONS[step] if step < len(mod._ACTIONS) else {}
    orders = list((action or {}).get("market") or [])
    strawberry = []
    for i, order in enumerate(orders):
        if len(order) >= 3 and order[0] == "SELL" and order[1] == "STRAWBERRY":
            strawberry.append({"index": i, "qty": int(order[2])})
    if strawberry:
        rows.append({"step": step, "strawberry": strawberry, "market": orders})

print(json.dumps(rows, indent=2))
(ROOT / "v121_strawberry_schedule.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
