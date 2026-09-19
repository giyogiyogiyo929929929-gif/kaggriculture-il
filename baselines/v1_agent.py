"""比較用に凍結したエージェント（v1）。 submission 56333848

`scripts\\freeze_agent.py` が生成。手で編集しない。
"""
import os
import sys

if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from v1_pkg import execute, macro  # noqa: E402


def agent(obs, config=None):
    try:
        market = macro.decide_market(obs, config=config)
        units = execute.assign(obs, config=config)
        return {"farmer": units["farmer"], "hands": units["hands"], "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
