# -*- coding: utf-8 -*-
"""v22の直近24公開対戦を、v12と同一の集計器で解析する。

仕様: docs/experiments/EXP-20260922-49-v22-public-score-analysis.md
"""
from pathlib import Path

import v12_recent_opponents as analysis

analysis.SUBMISSION = "56439885"
analysis.LIMIT = 24
analysis.RAW = analysis.ROOT / "data/raw/own_v22_recent"
analysis.OUT = analysis.ROOT / "data/analysis/v22_recent_opponents"
analysis.MONITOR = analysis.ROOT / "data/analysis/v22_recent_opponents.monitor.json"


if __name__ == "__main__":
    raise SystemExit(analysis.main())
