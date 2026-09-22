# -*- coding: utf-8 -*-
"""共通ゲート実行器をv22候補へ向け、終了状態も記録する。"""
import json
from datetime import datetime
from pathlib import Path

import run_v19_gate as gate

gate.CANDIDATE = Path("submissions/v22_antiv52_brunchguard/main.py")
gate.OUT = gate.ROOT / "data" / "eval" / "v22_antiv52_brunchguard"
gate.REG = gate.ROOT / "data" / "eval" / "v22_antiv52_brunchguard_regression"
STATUS = gate.ROOT / "data" / "eval" / "v22_antiv52_brunchguard.monitor.json"


def write_status(state, **extra):
    STATUS.write_text(json.dumps({"state": state, "updated": datetime.now().isoformat(), **extra},
                                 ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    write_status("running")
    try:
        code = gate.main()
    except Exception as error:
        write_status("failed", error=repr(error))
        raise
    write_status("complete", exit_code=code)
    raise SystemExit(code)
