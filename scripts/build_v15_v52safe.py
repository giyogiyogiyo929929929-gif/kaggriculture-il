# -*- coding: utf-8 -*-
r"""v52原本の末尾に例外時フォールバックだけを追加してv15候補を作る。

仕様: docs/adr/0006-switch-base-to-v52.md, docs/01_requirements.md NFR-2
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYER = r'''

# ---- kaggriculture-il による追加（2026-09-21、ADR-0006）。ここより上は opponents\v52\main.py と1バイトも違わない ----
# 目的：例外が出てもその試合を反則負けにしない（docs/01_requirements.md NFR-2）。
# Kaggle が使う「最後の callable」として、元の最後の callable を包む。
# 出典：ahmedberatozer/kaggriculture-v52-lean-flock-yarn-route（Apache-2.0）。詳細は opponents\v52\SOURCE.md。
_KIL_V52_INNER_AGENT = [value for value in list(globals().values()) if callable(value)][-1]


def _kil_v52_safe_agent(observation, configuration=None):
    try:
        return _KIL_V52_INNER_AGENT(observation, configuration)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
'''


if __name__ == "__main__":
    base = (ROOT / "opponents" / "v52" / "main.py").read_bytes()
    out_dir = ROOT / "submissions" / "v15_v52safe"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = base + LAYER.encode("utf-8")
    target = out_dir / "main.py"
    target.write_bytes(body)
    assert body[: len(base)] == base, "v52原本部分が変わっている"
    print(f"{target}: {len(body):,} bytes")
    print(f"  v52原本: SHA-256 {hashlib.sha256(base).hexdigest()}")
    print(f"  main.py: SHA-256 {hashlib.sha256(body).hexdigest()}")
