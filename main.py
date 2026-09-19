"""Kaggriculture 提出用エージェント。

仕様: docs/04_model_design.md §5.4（構造とフォールバック）, docs/06_submission.md
マクロ（買う・売る・雇う）は agent/macro.py、ミクロ（誰がどこで何をする）は agent/execute.py。
模倣モデル（agent/plan.py）は使わない。v2 に負けたため本線から外した（ADR-0002、EXP-20260919-09）。
"""
import gc
import os
import sys

# Kaggle は main.py を `exec(code, {})` で読み込むため **`__file__` が存在しない**
# （kaggle_environments/agent.py `get_last_callable`）。__file__ を直接使うと
# NameError で提出がエラーになる（実測：submission 56333731）。
# 本番では Kaggle 側が main.py のあるディレクトリを sys.path に追加してくれる。
if "__file__" in globals():  # ローカル実行（importlib 経由）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
elif os.path.isdir("/kaggle_simulations/agent"):  # 本番の保険
    sys.path.insert(0, "/kaggle_simulations/agent")

from agent import execute, macro  # noqa: E402

# 推論そのものは中央値1ms・最悪4msだが、GC のポーズが入ると最悪65msまで伸びる。
# 実測でメモリは変わらなかった（720ターンで 58MB のまま）ので、GC を止めておく。
gc.disable()

FALLBACK = {"farmer": ["PASS"], "hands": [], "market": []}


def agent(obs, config=None):
    """1ターン分の行動。例外は必ず握りつぶしてフォールバックを返す（NFR-2）。"""
    try:
        market = macro.decide_market(obs, config=config)
        units = execute.assign(obs, config=config)
        return {"farmer": units["farmer"], "hands": units["hands"], "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
