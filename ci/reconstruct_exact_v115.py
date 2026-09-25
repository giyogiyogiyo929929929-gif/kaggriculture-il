from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA256 = "cf2edf8b4a2ff13af0105f2360057ef9c55eece9ec6cb1d5d98046d95671d30a"
V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
PATCH_B64 = ROOT / "ci" / "v77_to_v115.patch.gz.b64"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base")
    parser.add_argument("out")
    args = parser.parse_args()
    base = Path(args.base).resolve()
    out = Path(args.out).resolve()

    got = sha256(base)
    if got != BASE_SHA256:
        raise SystemExit(f"v77 base sha256 mismatch: {got} != {BASE_SHA256}")

    payload = "".join(PATCH_B64.read_text(encoding="utf-8").split())
    patch = gzip.decompress(base64.b64decode(payload))
    with tempfile.TemporaryDirectory() as td_raw:
        td = Path(td_raw)
        work = td / "v77.py"
        shutil.copyfile(base, work)
        patch_path = td / "v77_to_v115.patch"
        patch_path.write_bytes(patch)
        subprocess.run(
            ["patch", "--batch", "-p0", "-i", str(patch_path)],
            cwd=td,
            check=True,
        )
        got = sha256(work)
        if got != V115_SHA256:
            raise SystemExit(f"v115 sha256 mismatch: {got} != {V115_SHA256}")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work, out)

    print(f"v115_sha256={sha256(out)}")
    print(f"v115_bytes={out.stat().st_size}")


if __name__ == "__main__":
    main()
