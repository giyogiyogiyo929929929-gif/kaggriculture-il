from pathlib import Path
import base64
import hashlib
import sys

RAW_SHA256 = "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"
SAFE_V3_SHA256 = "87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df"
PART_DIR = Path(__file__).resolve().parent / "uploaded_127ed3"

WRAPPER = b'''\n\n# Safety-only wrapper v3: delete/reinsert agent so Kaggle namespace-order loader selects it.\n_SAFE_V3_PARENT = ig_agent\ntry:\n    del agent\nexcept Exception:\n    pass\ndef agent(observation, configuration=None):\n    try:\n        return _SAFE_V3_PARENT(observation, configuration)\n    except Exception:\n        return {"farmer": ["PASS"], "hands": [], "market": []}\nagent.telemetry = _SAFE_V3_PARENT.telemetry\n'''


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python ci/build_uploaded_127ed3_safety_v3.py OUTPUT")

    parts = sorted(PART_DIR.glob("part*.b64"))
    if not parts:
        raise SystemExit(f"no uploaded raw chunks found under {PART_DIR}")

    raw = b"".join(base64.b64decode(p.read_text(encoding="ascii")) for p in parts)
    raw_sha = hashlib.sha256(raw).hexdigest()
    if raw_sha != RAW_SHA256:
        raise SystemExit(f"raw parent sha mismatch: {raw_sha}")

    candidate = raw + WRAPPER
    candidate_sha = hashlib.sha256(candidate).hexdigest()
    if candidate_sha != SAFE_V3_SHA256:
        raise SystemExit(f"safety-v3 sha mismatch: {candidate_sha}")

    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(candidate)
    print(f"raw_sha256={raw_sha}")
    print(f"safety_v3_sha256={candidate_sha}")
    print(f"safety_v3_bytes={len(candidate)}")


if __name__ == "__main__":
    main()
