# -*- coding: utf-8 -*-
"""v22直近戦の早期YARN試合を台帳再生する。

仕様: docs/experiments/EXP-20260922-49-v22-public-score-analysis.md
"""
import run_v12_recent_ledgers as analysis

analysis.MATCHES = analysis.ROOT / "data/analysis/v22_recent_opponents/matches.json"
analysis.RAW = analysis.ROOT / "data/raw/own_v22_recent"
analysis.OUT = analysis.ROOT / "data/analysis/v22_recent_ledgers"
analysis.MONITOR = analysis.ROOT / "data/analysis/v22_recent_ledgers.monitor.json"


if __name__ == "__main__":
    raise SystemExit(analysis.main())
