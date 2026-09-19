"""マクロ層：その日の買う・売る・雇う・土地を決めて market 注文にする。

仕様: docs/04_model_design.md §5.2（パラメータは EXP-20260918-01 の中央値）
"""
from __future__ import annotations

from v2_pkg import features

PARAMS = {
    # MELON は種80で6個×約158と高利回り。減らすと悪化した（EXP-20260919-05 の試行1）
    "day0_seeds": {"MELON": 12, "WHEAT": 10},
    "day0_animals": {"COW": 3, "SHEEP": 2},
    "mid_crops": {"STRAWBERRY": 33, "WHEAT": 25},
    "mid_animals": {"COW": 8, "SHEEP": 6, "GOOSE": 3},
    "hires_per_day": 10,         # §5.6：タスク消化率を見て 6 → 10 に増やした
    "land_buy_days": {6: 2, 11: 3},   # day → 欲しい quadrant 数
    "late_switch_day": 25,
    "stop_planting_day": 27,
    "feed_per_animal": 1,        # 実際の消費は1頭1日1個（kaggriculture.py FEED）
    "feed_buffer": 12,           # 予備。shed は100上限なので持ちすぎない
    "seed_batch": 8,             # 1ターンに買う種の上限
    "max_orders": 10,
    "reserved_for_buys": 5,      # 種・家畜・餌のために HIRE で埋めない枠
    "sell_slots": 5,             # SELL のために必ず空けておく注文枠
    "max_unplaced_animals": 2,   # 未設置の家畜がこれ以上たまったら買わない
    "max_feed_carriers": 3,      # 餌を運ぶユニット数の上限
    "cash_floor": 800,           # 雇用・餌・投資のために残す現金（EXP-20260919-05）
    "drop_threshold": 10,        # インベントリが何個で shed に戻すか（execute で使用）
}


def _seed_targets(day: int, farm, params) -> dict:
    """その日に欲しい「種の在庫＋植え付け済み」の目標数。"""
    if day >= params["stop_planting_day"]:
        return {}
    if day <= 1:
        return dict(params["day0_seeds"])
    if day >= params["late_switch_day"]:
        empty = len(features.empty_tiles(farm))
        return {"CARROT": max(0, empty)}
    return dict(params["mid_crops"])


def _animal_targets(day: int, params) -> dict:
    return dict(params["day0_animals"]) if day <= 1 else dict(params["mid_animals"])


def decide_market(obs, config=None, params=None) -> list[list]:
    """1ターン分の market 注文（最大 `max_orders` 件）。"""
    params = params or PARAMS
    farm = features.my_farm(obs)
    day = int(obs.get("day", 0))
    hour = int(obs.get("hour", 0))
    money = float(farm.get("money", 0))
    shed = features.shed(obs)
    seeds = features.seeds(obs)
    placed_animals = features.count_animals(farm)
    planted = features.count_crops(farm)

    buys: list[list] = []
    budget = money

    def afford(cost: float) -> bool:
        nonlocal budget
        if cost > budget:
            return False
        budget -= cost
        return True

    # 1. 土地（NE → SW → SE、1000 / 2000 / 4000）
    unlocked = len(farm.get("unlocked_quadrants") or ["NW"])
    # 予定日「以降」で判定する。予定日ちょうどに資金が無いことが多いため（§5.2 注記）
    wanted = 1
    for scheduled_day, quadrants in sorted(params["land_buy_days"].items()):
        if day >= scheduled_day:
            wanted = max(wanted, quadrants)
    if unlocked < wanted and unlocked - 1 < len(features.LAND_PRICES):
        if afford(features.LAND_PRICES[unlocked - 1]):
            buys.append(["BUY_LAND"])

    # 2. 雇用（朝の数ターンに分ける。1ターン全部を HIRE で埋めると種も家畜も買えない）
    if hour <= 2:
        remaining = max(0, params["hires_per_day"] - int(farm.get("hires_today", 0)))
        per_turn = max(0, params["max_orders"] - params["reserved_for_buys"])
        for n in range(min(remaining, per_turn)):
            buys.append(["HIRE"])
            budget -= 1 + n  # fib の概算。実費は fib(n) だが多めに見ておく

    # 3. 餌用の WHEAT（FEED はユニットのインベントリから1消費。doc 04 §5.1）
    animal_count = sum(placed_animals.values())
    feed_need = animal_count * params["feed_per_animal"] + params["feed_buffer"]
    wheat_stock = shed.get("WHEAT", 0)
    if animal_count and wheat_stock < feed_need:
        short = feed_need - wheat_stock
        if afford(short * 25):  # 基準価格で概算
            buys.append(["BUY_PRODUCT", "WHEAT", short])

    # 4. 種（目標 − （植え付け済み＋在庫））
    budget = max(0.0, budget - params["cash_floor"])  # 雇用・餌のぶんは手を付けない
    capacity = len(features.empty_tiles(farm))
    for crop, target in _seed_targets(day, farm, params).items():
        have = planted.get(crop, 0) + seeds.get(crop, 0)
        # 植える場所が無いのに種を買わない（買った種は使われず資金だけ消える）
        target = min(target, planted.get(crop, 0) + capacity)
        short = target - have
        if day > 1:  # 序盤の型（§5.2）はそのまま買い、以降は1ターンの上限をかける
            short = min(short, params["seed_batch"])
        if short <= 0:
            continue
        cost = features.CROPS[crop]["seed"] * short
        if afford(cost):
            buys.append(["BUY_SEED", crop, short])

    # 5. 家畜（目標 − （設置済み＋shed 在庫））
    carried = features.count_carried_animals(obs)
    unplaced_total = sum(shed.get(a, 0) for a in features.ANIMALS) + sum(carried.values())
    for animal, target in _animal_targets(day, params).items():
        have = placed_animals.get(animal, 0) + shed.get(animal, 0) + carried.get(animal, 0)
        short = target - have
        # 置けていない家畜が溜まっているうちは買い足さない（牧舎・鶏舎が足りていない）
        if short <= 0 or unplaced_total >= params["max_unplaced_animals"]:
            continue
        cost = features.ANIMALS[animal]["cost"] * short
        if not afford(cost):
            short = int(budget // features.ANIMALS[animal]["cost"])
            if short <= 0:
                continue
            budget -= features.ANIMALS[animal]["cost"] * short
        buys.append(["BUY_ANIMAL", animal, short])

    # 6. 売却（shed からしか売れない。WHEAT は餌の分を残す。doc 04 §5.1）
    sells: list[list] = []
    for product in features.PRODUCTS:
        quantity = int(shed.get(product, 0))
        if product == "WHEAT":
            # 餌（1頭1日1個）＋予備だけ残す。抱えすぎると shed 100 を食い潰す
            quantity -= feed_need
        if quantity > 0:
            sells.append(["SELL", product, quantity])

    reserved = min(len(sells), params["sell_slots"])
    orders = buys[: max(0, params["max_orders"] - reserved)]
    orders += sells[: params["max_orders"] - len(orders)]
    return orders
