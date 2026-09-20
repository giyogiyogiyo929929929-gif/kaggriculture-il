# -*- coding: utf-8 -*-
r"""submissions/v12_v51safe/main.py を作る：v51 の末尾に例外時フォールバックの包みを足す（ADR-0004 第1段）。

仕様: docs/adr/0004-switch-base-to-v51.md（第1段）、docs/01_requirements.md NFR-2

    .venv\Scripts\python.exe scripts\build_v12_v51safe.py

`opponents\v51\main.py`（取り込んだ原本）は1バイトも変えない。末尾に包みを足すだけ。
作りは v4（`submissions\thomas_v94_safe\main.py`）と同じ。
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYER = '''

# ---- kaggriculture-il による追加（2026-09-20、ADR-0004 第1段）。ここより上は opponents\\v51\\main.py と1バイトも違わない ----
# 目的：例外が出てもその試合を反則負けにしない（docs/01_requirements.md NFR-2）。
# Kaggle が使うのは「最後の callable」なので、元のファイルの最後の callable を包んだ関数を最後に置く。
# 出典：ahmedberatozer/kaggriculture-v51-lean-flock（Apache-2.0）。取り出しと監査は opponents\\v51\\SOURCE.md。
_KIL_INNER_AGENT = [value for value in list(globals().values()) if callable(value)][-1]


def _kil_safe_agent(observation, configuration=None):
    try:
        return _KIL_INNER_AGENT(observation, configuration)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
'''

if __name__ == "__main__":
    base = (ROOT / "opponents" / "v51" / "main.py").read_bytes()
    out_dir = ROOT / "submissions" / "v12_v51safe"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = base + LAYER.encode("utf-8")
    target = out_dir / "main.py"
    target.write_bytes(body)
    assert body[: len(base)] == base, "v51 の部分が変わっている"
    print(f"{target}: {len(body):,} bytes")
    print(f"  v51 原本と同じ先頭: {len(base):,} bytes  SHA-256 {hashlib.sha256(base).hexdigest()[:16]}…")
    print(f"  main.py           : SHA-256 {hashlib.sha256(body).hexdigest()}")
