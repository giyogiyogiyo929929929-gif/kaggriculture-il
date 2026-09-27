from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
subprocess.check_call([sys.executable, str(ROOT / "build_sources.py")])
parent = (ROOT / "v112_wheat_lead3_lowdemand.py").read_text(encoding="utf-8")
suffix = (ROOT / "v119_suffix.pyfrag").read_text(encoding="utf-8")
out = ROOT / "v119_multi_premium_race_front.py"
out.write_bytes((parent + "\n" + suffix).encode("utf-8"))
print(out.name, hashlib.sha256(out.read_bytes()).hexdigest())
