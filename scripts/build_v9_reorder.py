# -*- coding: utf-8 -*-
r"""submissions/v9_reorder/main.py を作る：v7_relax の末尾に候補E の層を足す。

仕様: docs/07_v4_improvement.md §3 候補E（約定ルールの確認は E.1b、根拠は EXP-20260920-23）

    .venv\Scripts\python.exe scripts\build_v9_reorder.py

v9/4 の原本も v5〜v7 の層も1バイトも変えない。末尾に層を足すだけ。
候補D（v8_lategate）とは独立に効果を測るため、土台は v8 ではなく v7 にする。
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 候補E の層。`scripts\\build_v10_de.py`（候補D ＋ 候補E）からも同じものを使う。
LAYER = '''

# ---- kaggriculture-il 追加：候補E「同じターンに出す SELL の並べ替え」 ----
# 仕様: docs/07_v4_improvement.md §3 候補E（市場の約定ルールは E.1b に実装を読んで書いた）
# 機構の出典: thomastschinkel/the-metav4-farm-submission-v13（Apache-2.0）の _v44y_reorder。
#
# 市場は「スロットごと・1個ずつ」で約定し、売るたびに在庫が増えて値が下がる（E.1b）。
# v9/4 はテープの順のまま売るので、同じターンに複数の品を出すと順序の分だけ損をする。
# この層は注文の中身（品目と数量）を一切変えず、**順序だけ**を入れ替える。
# 相手の注文は見えないので、相手も同じ注文列を出す（＝コピー）と仮定して
# 「自分の手取り − 相手の手取り」が最大になる並びを選ぶ。
# ここで先に内側（v7 の最後の callable）を捕まえる。import はそのあと。
# （先に `from time import perf_counter` をすると、それが「最後の callable」になってしまう）
_KIL_E_INNER = [value for value in list(globals().values()) if callable(value)][-1]

import itertools as _kil_e_it
from time import perf_counter as _kil_e_clock

_KIL_E_START = 216          # ここより前は売る品が少なく、並べ替えの余地がない
_KIL_E_MAXBLOCK = 6         # 連続する SELL のかたまりは6件まで見る（6! = 720 通り）
_KIL_E_MINGAIN = 0.5        # これ以下の改善では並べ替えない（無駄な入れ替えを避ける）
_KIL_E_BUDGET_MS = 25.0     # 1ターンの探索にかける上限（NFR-1：最悪 200ms 未満）
_KIL_E_REPORT = dict(e_turns=0, e_blocks=0, e_gain=0.0, e_timeouts=0, e_errors=0)


def _kil_e_params(observation):
    """市場パラメータ（v9/4 が持つ既定値に、観測で渡された分を上書きする）。"""
    params = {item: dict(value) for item, value in _R37_MARKET_PARAMS.items()}
    patches = (observation.get("market") or {}).get("params") or {}
    for item, patch in patches.items():
        if item in params and isinstance(patch, dict):
            params[item].update(patch)
    return params


def _kil_e_revenue(item, mine, theirs, inventory, stock, params):
    """1品目ぶん、エンジンの約定を再現して (自分の手取り, 相手の手取り) を返す。

    mine / theirs は {スロット番号: 個数}。doc 07 §3 候補E E.1b の 2〜5 をそのまま写した：
    スロットの小さい順に、1個ずつ、両者が同じ「コミット前の在庫」の価格で売る。
    価格が 1 より大きいときだけ在庫が増える。
    """
    inv = int(inventory)
    left = [int(stock), int(stock)]
    revenue = [0.0, 0.0]
    for slot in sorted(set(mine) | set(theirs)):
        remaining = [int(mine.get(slot, 0)), int(theirs.get(slot, 0))]
        while True:
            price = _r37_market_price(item, inv, params)
            committed = False
            for side in (0, 1):
                if remaining[side] <= 0 or left[side] <= 0:
                    continue
                revenue[side] += price
                left[side] -= 1
                remaining[side] -= 1
                if price > 1:
                    inv += 1
                committed = True
            if not committed:
                break
    return revenue[0], revenue[1]


def _kil_e_schedules(orders, params):
    """注文列を {品目: {スロット番号: 個数}} にする（SELL だけ）。"""
    out = {}
    for slot, order in enumerate(orders):
        if not order or len(order) < 3 or order[0] != "SELL" or order[1] not in params:
            continue
        try:
            quantity = int(order[2])
        except (TypeError, ValueError):
            continue
        if quantity > 0:
            slots = out.setdefault(order[1], {})
            slots[slot] = slots.get(slot, 0) + quantity
    return out


def _kil_e_blocks(orders):
    """連続する SELL のかたまり（2〜_KIL_E_MAXBLOCK 件）の範囲を返す。"""
    blocks = []
    index = 0
    while index < len(orders):
        order = orders[index]
        if order and order[0] == "SELL":
            end = index
            while end < len(orders) and orders[end] and orders[end][0] == "SELL":
                end += 1
            if 2 <= end - index <= _KIL_E_MAXBLOCK:
                blocks.append((index, end))
            index = end
        else:
            index += 1
    return blocks


def _kil_e_reorder(observation, action):
    """SELL のかたまりを、手取りの差が最大になる順に並べ替えた action を返す。"""
    orders = [list(order) for order in (action.get("market") or [])]
    if len(orders) < 2:
        return action
    blocks = _kil_e_blocks(orders)
    if not blocks:
        return action
    params = _kil_e_params(observation)
    inventory = (observation["market"] or {}).get("inventory") or {}
    stock = projected_shed(action, FarmView(observation))
    stock = {item: max(0, int(value)) for item, value in stock.items()}
    opponent = _kil_e_schedules(orders, params)

    cache = {}

    def margin(candidate):
        """自分の手取り − 相手の手取り（相手は元の並びのまま）。品目ごとに独立なので足せる。"""
        total = 0.0
        for item, schedule in _kil_e_schedules(candidate, params).items():
            key = (item, tuple(sorted(schedule.items())))
            value = cache.get(key)
            if value is None:
                mine, theirs = _kil_e_revenue(
                    item, schedule, opponent.get(item, {}),
                    int(inventory.get(item, 0)), stock.get(item, 0), params,
                )
                value = mine - theirs
                cache[key] = value
            total += value
        return total

    deadline = _kil_e_clock() + _KIL_E_BUDGET_MS / 1000.0
    base = margin(orders)
    best = base
    changed = False
    for start, end in blocks:
        block = orders[start:end]
        best_orders = None
        seen = set()
        for permutation in _kil_e_it.permutations(range(len(block))):
            if _kil_e_clock() > deadline:
                _KIL_E_REPORT["e_timeouts"] += 1
                break
            key = tuple((block[p][1], int(block[p][2])) for p in permutation)
            if key in seen:
                continue
            seen.add(key)
            candidate = orders[:start] + [block[p] for p in permutation] + orders[end:]
            value = margin(candidate)
            if value > best + _KIL_E_MINGAIN:
                best = value
                best_orders = candidate
        if best_orders is not None:
            orders = best_orders
            changed = True
    if not changed:
        return action
    _KIL_E_REPORT["e_turns"] += 1
    _KIL_E_REPORT["e_blocks"] += len(blocks)
    _KIL_E_REPORT["e_gain"] += best - base
    out = dict(action)
    out["market"] = orders
    return out


def _kil_e_agent(observation, configuration=None):
    action = _KIL_E_INNER(observation, configuration)
    try:
        if int(observation["step"]) >= _KIL_E_START:
            action = _kil_e_reorder(observation, action)
    except Exception:
        # 何かあっても試合を止めない（doc 01 NFR-2）。内側の行動をそのまま返す。
        _KIL_E_REPORT["e_errors"] += 1
    return action


_kil_e_agent.telemetry = _KIL_E_REPORT
'''

def build(base_name: str, out_name: str) -> Path:
    """`base_name` の末尾に候補E の層を足して `out_name` に書く。土台は1バイトも変えない。"""
    original = (ROOT / "submissions" / "thomas_v94" / "main.py").read_bytes()
    base = (ROOT / "submissions" / base_name / "main.py").read_bytes()
    assert base.startswith(original), f"{base_name} の先頭が v9/4 原本と一致しない"

    out_dir = ROOT / "submissions" / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    body = base + LAYER.encode("utf-8")
    target = out_dir / "main.py"
    target.write_bytes(body)

    assert body[: len(base)] == base, f"{base_name} の部分が変わっている"
    print(f"{target}: {len(body):,} bytes")
    print(f"  v9/4 原本と同じ先頭: {len(original):,} bytes  SHA-256 {hashlib.sha256(original).hexdigest()[:16]}…")
    print(f"  {base_name} と同じ先頭: {len(base):,} bytes  SHA-256 {hashlib.sha256(base).hexdigest()[:16]}…")
    print(f"  main.py            : SHA-256 {hashlib.sha256(body).hexdigest()}")
    return target


if __name__ == "__main__":
    build("v7_relax", "v9_reorder")
