# -*- coding: utf-8 -*-
"""分析スクリプトの共通部品（エージェントの読み込み・1試合の実行・コピー判定用の農場キー）。

仕様: docs/05_evaluation.md §8（分析ツール）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from kaggle_environments import make  # noqa: E402

from scripts import preflight  # noqa: E402

# リプレイの TeamNames に出る自分側の名前（チーム結成の前後で変わる。doc 06）
ME_NAMES = ("giyogoio hlrlqll", "giyogoioがすべてのエージェントを破壊します")
ITEMS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")


def path(p) -> Path:
    """相対パスはリポジトリ直下から解決する。"""
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def load(p):
    """Kaggle と同じ読み込み方（最後の callable、__file__ なし）でエージェントを返す。"""
    return preflight.load_like_kaggle(path(p))


def wrap(agent):
    return lambda o, c=None: preflight.call_like_kaggle(agent, o, c)


def play(a, b, seed: int, swap: bool = False, steps: int | None = None):
    """a・b（パスか読み込み済みエージェント）を対戦させて env を返す。swap=False なら a が席0。"""
    agents = [wrap(load(x) if isinstance(x, (str, Path)) else x) for x in (a, b)]
    if swap:
        agents.reverse()
    config = {"seed": seed}
    if steps:
        config["episodeSteps"] = steps
    env = make("kaggriculture", configuration=config)
    env.run(agents)
    return env


def rewards(env):
    return [env.state[0]["reward"], env.state[1]["reward"]]


def my_seat(team_names, me: str | None = None) -> int:
    names = (me,) if me else ME_NAMES
    for i, n in enumerate(team_names):
        if n in names:
            return i
    raise ValueError(f"自分の名前が見つからない: {team_names}（--me で指定）")


def strip_weeds(farm):
    return [[None if isinstance(t, dict) and t.get("kind") == "WEED" else t for t in row] for row in farm.get("tiles") or []]


def copy_key(farm, ignore_money: bool = False):
    """コピー判定用のキー。雑草は空きとみなす（v5/v6 は所持金込み、v7 は所持金を除く。doc 07 候補A・A3）。"""
    drop = ("tiles", "money") if ignore_money else ("tiles",)
    return strip_weeds(farm), {k: v for k, v in farm.items() if k not in drop}


class Ledger:
    """環境の _process_market / _commit_unit を包み、約定1個ずつ (step, player, op, item, price) を記録する。挙動は変えない。"""

    def __init__(self):
        from kaggle_environments.envs.kaggriculture import kaggriculture as K
        self.K, self.rows, self._cur = K, [], {}
        self._orig = (K._process_market, K._commit_unit)
        orig_process, orig_commit = self._orig
        cur, rows = self._cur, self.rows

        def process(state, env):
            cur["farms"] = state[0].observation.farms
            cur["step"] = state[0].observation.step
            return orig_process(state, env)

        def commit(op, item, price, farm, private, market, shed_capacity=100):
            ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
            if ok:
                rows.append((cur["step"], 0 if farm is cur["farms"][0] else 1, op, item, price))
            return ok

        K._process_market, K._commit_unit = process, commit

    def close(self):
        self.K._process_market, self.K._commit_unit = self._orig
