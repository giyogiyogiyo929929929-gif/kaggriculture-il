# -*- coding: utf-8 -*-
"""EXP-52のLayer Dをv25と同一seedで監視付き順次評価する。"""
import run_v26_r148_panel as panel

panel.OUT = panel.ROOT / "data/eval/v27_layerd_panel"
panel.STATUS = panel.ROOT / "data/eval/v27_layerd_panel.monitor.json"
panel.CANDIDATE = "submissions/v27_orderbook_layer_d/main.py"
panel.CANDIDATE_LABEL = "v27"


if __name__ == "__main__":
    raise SystemExit(panel.main())
