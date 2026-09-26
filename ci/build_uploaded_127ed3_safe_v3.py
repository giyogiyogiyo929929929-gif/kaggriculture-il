from pathlib import Path
import hashlib
import sys

RAW_SHA = "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"
SAFE_SHA = "87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df"
SUFFIX = b'''\n\n# Safety-only wrapper v3: delete/reinsert agent so Kaggle namespace-order loader selects it.\n_SAFE_V3_PARENT = ig_agent\ntry:\n    del agent\nexcept Exception:\n    pass\ndef agent(observation, configuration=None):\n    try:\n        return _SAFE_V3_PARENT(observation, configuration)\n    except Exception:\n        return {"farmer": ["PASS"], "hands": [], "market": []}\nagent.telemetry = _SAFE_V3_PARENT.telemetry\n'''

src = Path(sys.argv[1])
out = Path(sys.argv[2])
raw = src.read_bytes()
assert hashlib.sha256(raw).hexdigest() == RAW_SHA
safe = raw + SUFFIX
assert hashlib.sha256(safe).hexdigest() == SAFE_SHA
out.write_bytes(safe)
print(SAFE_SHA)
