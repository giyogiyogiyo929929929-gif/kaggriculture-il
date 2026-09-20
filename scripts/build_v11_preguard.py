# -*- coding: utf-8 -*-
r"""候補F（day-end guard の前倒し）の層を作って積む。

仕様: docs/07_v4_improvement.md §3 候補F（F.1〜F.4）
機構の出典: thomastschinkel/the-metav4-farm-submission-v13（Apache-2.0）の `_y_preguard`

    .venv\Scripts\python.exe scripts\build_v11_preguard.py            # 既定パラメータで v11_fe を作る
    .venv\Scripts\python.exe scripts\build_v11_preguard.py --explore  # 探索用に何通りか作る

層の順番は **F（内側）→ E（外側）**。metav4_v13 も preguard を reorder より内側に置いている
（F が足した注文を E が並べ替えられるようにするため）。
"""
import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v9_reorder import LAYER as LAYER_E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

_BODY = '''

def _kil_f_apply(observation, action):
    """hour 21・22 に、hour 23 で捨てるはめになる分を先に売る（doc 07 §3 候補F）。"""
    step = int(observation["step"])
    if step % 24 not in _KIL_F_HOURS or step // 24 < _KIL_F_MINDAY or step >= _KIL_F_END:
        return action
    orders = [list(order) for order in (action.get("market") or [])]
    if len(orders) >= 10:
        return action
    _, private = _ov_fields(observation, action)
    stock, _, _ = _r97_market_stock(private["shed"], orders)
    carried = sum(max(0, int(n)) for bag in private["inventories"] for n in bag.values())
    needed = sum(max(0, int(value)) for value in stock.values()) + carried - 100 - _KIL_F_MARGIN
    if needed <= 0:
        return action
    prices = observation["market"]["prices"]
    extra = []
    for item in sorted(PRODUCTS, key=lambda it: -int(prices.get(it, 0))):
        available = max(0, int(stock.get(item, 0)))
        quantity = min(needed, available)
        if quantity <= 0:
            continue
        if item in _KIL_F_ITEMS and int(prices.get(item, 0)) >= _KIL_F_MINPRICE:
            extra.append(["SELL", item, quantity])
        needed -= quantity
        if needed <= 0:
            break
    if not extra or len(orders) + len(extra) > 10:
        return action
    _KIL_F_REPORT["f_turns"] += 1
    _KIL_F_REPORT["f_units"] += sum(order[2] for order in extra)
    return dict(action, market=orders + extra)


def _kil_f_agent(observation, configuration=None):
    action = _KIL_F_INNER(observation, configuration)
    try:
        standard = configuration is None or all(
            configuration.get(key, value) == value for key, value in
            (("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100), ("maxMarketOrdersPerTurn", 10)))
        if standard:
            action = _kil_f_apply(observation, action)
    except Exception:
        # 何かあっても試合を止めない（doc 01 NFR-2）。
        _KIL_F_REPORT["f_errors"] += 1
    return action


_kil_f_agent.telemetry = _KIL_F_REPORT
'''


def layer_f(hours=(21, 22), items=("MILK", "STRAWBERRY", "MELON", "WOOL", "TOMATO"),
            margin=-7, minprice=2, minday=1, end=696) -> str:
    """候補F の層を、パラメータを埋めた形で返す（探索用）。

    `margin` は「shed に残す余裕」。売る量は `shed + 持ち分 − 100 − margin` で、
    metav4_v13 の `_y_preguard` は 99 と −6（＝93 を超えた分）。ここでは 100 と −7 で同じ値になる。
    """
    return f'''

# ---- kaggriculture-il 追加：候補F「day-end guard の前倒し」 ----
# 仕様: docs/07_v4_improvement.md §3 候補F（F.1 はいまの作り、F.2 は相手の作り）
# 機構の出典: thomastschinkel/the-metav4-farm-submission-v13（Apache-2.0）の `_y_preguard`。
#
# v9/4 の day-end guard（`_ov_apply`）は hour 23 にしか動かないので、shed に入り切らない分は
# その時刻の値段でしか売れない。相手は同じ時刻に同じ品を出してくるので、競り負ける。
# この層は、**hour 21・22 のうちに、あふれる見込みの分を値段の高い順に売っておく**。
# 売るのは指定した品目だけ、値段が下限以上のときだけ。注文の枠（10件）を超えるなら何もしない。
_KIL_F_INNER = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_F_HOURS = {hours!r}
_KIL_F_ITEMS = {items!r}
_KIL_F_MINDAY = {minday!r}
_KIL_F_MARGIN = {margin!r}
_KIL_F_MINPRICE = {minprice!r}
_KIL_F_END = {end!r}
_KIL_F_REPORT = dict(f_turns=0, f_units=0, f_errors=0)
{_BODY}'''


def build(base_name: str, out_name: str, layer: str, with_e: bool = True) -> Path:
    """`base_name` の末尾に候補F の層（必要なら続けて候補E の層）を足して `out_name` に書く。"""
    original = (ROOT / "submissions" / "thomas_v94" / "main.py").read_bytes()
    base = (ROOT / "submissions" / base_name / "main.py").read_bytes()
    assert base.startswith(original), f"{base_name} の先頭が v9/4 原本と一致しない"

    body = base + layer.encode("utf-8")
    if with_e:
        body += LAYER_E.encode("utf-8")
    out_dir = ROOT / "submissions" / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "main.py"
    target.write_bytes(body)
    assert body[: len(base)] == base, f"{base_name} の部分が変わっている"
    print(f"{target}: {len(body):,} bytes  SHA-256 {hashlib.sha256(body).hexdigest()[:16]}…"
          f"  （{base_name} ＋ F{'＋E' if with_e else ''}）")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--explore", action="store_true", help="探索用に何通りか作る")
    args = parser.parse_args()

    build("v7_relax", "v11_fe", layer_f())
    if args.explore:
        # 案f2：全品目（下限価格だけで絞る）
        build("v7_relax", "v11_f2", layer_f(items=tuple(
            ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"))))
        # 案f3：hour 22 だけ（前倒しを1時間に絞る）
        build("v7_relax", "v11_f3", layer_f(hours=(22,)))
        # 案f4：余裕を広く取る（shed が 85 を超えたら売り始める）
        build("v7_relax", "v11_f4", layer_f(margin=15))
        # 案f5：安値では売らない
        build("v7_relax", "v11_f5", layer_f(minprice=30))
