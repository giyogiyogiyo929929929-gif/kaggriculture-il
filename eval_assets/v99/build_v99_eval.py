#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

V96_SHA256 = "dc0938fa82952e6599b04725f1e397ac1f317a0ddffaefbae204e265171b0a22"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v121", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    overlay = Path(__file__).with_name("v99_overlay.py").read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        subprocess.check_call([
            sys.executable,
            "eval_assets/v97/build_v97_eval.py",
            "--v121", args.v121,
            "--out-dir", str(tmp),
        ])
        v96 = tmp / "v96_champion_lead11_milkshops2.py"
        if sha256(v96) != V96_SHA256:
            raise SystemExit(f"unexpected v96 sha256: {sha256(v96)}")

        champion = out_dir / v96.name
        candidate = out_dir / "v99_candidate_main_farmer_weedlag_boundary.py"
        champion.write_bytes(v96.read_bytes())
        base = v96.read_text(encoding="utf-8")
        candidate.write_text(base.rstrip() + "\n\n" + overlay.rstrip() + "\n", encoding="utf-8")

        # Candidate must be append-only relative to exact v96.
        raw = candidate.read_bytes()
        prefix = v96.read_bytes()
        if not raw.startswith(prefix.rstrip()):
            raise SystemExit("v99 is not append-only from v96")

        print("v96", sha256(champion), champion)
        print("v99", sha256(candidate), candidate)


if __name__ == "__main__":
    main()
