# -*- coding: utf-8 -*-
"""共通ゲート実行器をv20候補へ向ける。"""
from pathlib import Path

import run_v19_gate as gate

gate.CANDIDATE = Path("submissions/v20_antiv52_cap2/main.py")
gate.OUT = gate.ROOT / "data" / "eval" / "v20_antiv52_cap2"
gate.REG = gate.ROOT / "data" / "eval" / "v20_antiv52_cap2_regression"

if __name__ == "__main__":
    raise SystemExit(gate.main())
