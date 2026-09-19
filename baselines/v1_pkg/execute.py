"""実行層：farmer と hands に1ターン分のタスクを割り当てる。

仕様: docs/04_model_design.md §5.3（優先度と割り当て）, §5.1（環境の制約）
"""
from __future__ import annotations

from v1_pkg import features
from v1_pkg.macro import PARAMS

# 優先度（小さいほど先）。doc 04 §5.3
P_FEED = 1           # 水やりより先。家畜は1頭400〜500で、逃げると買い直しになる（§5.3 注記3）
P_PICKUP_WHEAT = 1   # 餌が手元に無ければ給餌と同じ優先度で取りに行く
P_WATER = 2
P_HARVEST = 3
P_DROP = 4
P_PLACE = 5
P_PICKUP_ANIMAL = 6
P_BUILD = 7          # 家畜が shed で待っているときだけ。植え付けより先（§5.3 の注記）
P_CARE = 8
P_PLANT = 9
P_DIG = 10


def _harvestable(tile, day: int) -> bool:
    """収穫してよいか。一度きりの作物は最大収量日まで待つ。"""
    if tile.get("yield_units", 0) <= 0:
        return False
    if tile.get("kind") != "PLANT":
        return True  # 家畜：溜まっていれば取る
    crop = features.CROPS.get(tile.get("crop"))
    if crop is None:
        return False
    age = day - tile.get("planted_day", 0)
    if age < crop["first_yield_day"]:
        return False
    if crop["ongoing"]:
        return True
    return age >= crop["max_yield_day"]


def _plant_crop(day: int, seeds: dict, params) -> str | None:
    """その日に植える作物（doc 04 §5.2 の遷移）。"""
    if day >= params["stop_planting_day"]:
        return None
    if day <= 1:
        order = ["MELON", "WHEAT"]
    elif day >= params["late_switch_day"]:
        order = ["CARROT", "WHEAT"]
    else:
        order = ["STRAWBERRY", "WHEAT", "MELON", "TOMATO", "CARROT"]
    for crop in order:
        if seeds.get(crop, 0) > 0:
            return crop
    for crop, count in seeds.items():
        if count > 0 and crop in features.CROPS:
            return crop
    return None


def _build_tasks(obs, config, params) -> list[dict]:
    """タイルから割り当て可能なタスクを作る。"""
    farm = features.my_farm(obs)
    day = int(obs.get("day", 0))
    shed = features.shed(obs)
    seeds = features.seeds(obs)
    size = features.board_size(obs, config)

    tasks: list[dict] = []
    empties: list[tuple[int, int]] = []
    free_structures: list[tuple[int, int]] = []

    for x, y, tile in features.iter_tiles(farm):
        if tile == "LOCKED":
            continue
        if tile is None:
            empties.append((x, y))
            continue
        if not isinstance(tile, dict):
            continue
        kind = tile.get("kind")
        if kind == "PLANT":
            if not tile.get("watered_today"):
                tasks.append({"p": P_WATER, "op": ["WATER"], "pos": (x, y)})
            if _harvestable(tile, day):
                tasks.append({"p": P_HARVEST, "op": ["HARVEST"], "pos": (x, y)})
        elif kind == "WEED":
            tasks.append({"p": P_DIG, "op": ["DIG"], "pos": (x, y)})
        elif kind in ("COOP", "PASTURE"):
            if tile.get("animal"):
                if not tile.get("fed_today"):
                    tasks.append({"p": P_FEED, "op": ["FEED"], "pos": (x, y), "needs": "WHEAT"})
                if _harvestable(tile, day):
                    tasks.append({"p": P_HARVEST, "op": ["HARVEST"], "pos": (x, y)})
                if tile.get("fertilizer_available"):
                    tasks.append({"p": P_CARE, "op": ["COLLECT_FERTILIZER"], "pos": (x, y)})
                if not tile.get("cared_today"):
                    tasks.append({"p": P_CARE, "op": ["CARE"], "pos": (x, y)})
            else:
                free_structures.append((x, y))

    shed_tiles = features.shed_access_tiles(size)

    # 置き場（COOP / PASTURE）と、置けていない家畜の関係を先に整理する。
    # これを間違えると「買う→shed に溜まる→置けない→また買う」で資金が溶ける。
    carried = features.count_carried_animals(obs)
    free = features.free_structures(farm)
    slots = {kind: len(positions) for kind, positions in free.items()}

    # 手持ちの家畜は置き場を先に埋める
    for animal, count in carried.items():
        structure = features.ANIMALS[animal]["structure"]
        slots[structure] = max(0, slots.get(structure, 0) - count)

    # 足りない置き場を建てる（植え付けより優先。§5.3 注記）
    reserved: list[tuple[int, int]] = []
    for structure in ("PASTURE", "COOP"):
        animals_for = [a for a, spec in features.ANIMALS.items() if spec["structure"] == structure]
        unplaced = sum(int(shed.get(a, 0)) + carried.get(a, 0) for a in animals_for)
        missing = unplaced - len(free.get(structure, []))
        for pos in empties:
            if missing <= 0:
                break
            if pos in reserved:
                continue
            reserved.append(pos)
            tasks.append({"p": P_BUILD, "op": ["BUILD_" + structure], "pos": pos})
            missing -= 1

    # shed の家畜は「空いている置き場のぶんだけ」取りに行く
    for animal in features.ANIMALS:
        in_shed = int(shed.get(animal, 0))
        structure = features.ANIMALS[animal]["structure"]
        take = min(in_shed, slots.get(structure, 0))
        for _ in range(take):
            tasks.append({
                "p": P_PICKUP_ANIMAL, "op": ["PICKUP", animal, 1], "pos": shed_tiles[0],
                "any_of": shed_tiles,
            })
        slots[structure] = slots.get(structure, 0) - take

    # 植え付け（種の数だけ）
    crop = _plant_crop(day, seeds, params)
    if crop:
        # 空きタイル全部をタスクにする（近いユニットが植えられるように）。
        # 実際に植える本数は種の在庫で assign 側が制限する。
        build_positions = {task["pos"] for task in tasks if task["p"] == P_BUILD}
        for pos in empties:
            if pos not in build_positions:
                tasks.append({"p": P_PLANT, "op": ["PLANT", crop], "pos": pos})

    return tasks


def _unit_specific_tasks(obs, config, params, unit_index, position, inventory) -> list[dict]:
    """そのユニットにしか作れないタスク（手持ちに依存するもの）。"""
    farm = features.my_farm(obs)
    size = features.board_size(obs, config)
    shed_tiles = features.shed_access_tiles(size)
    tasks: list[dict] = []

    # 手持ちの家畜を空いている構造物に置く
    for animal in features.ANIMALS:
        if inventory.get(animal, 0) <= 0:
            continue
        structure = features.ANIMALS[animal]["structure"]
        for x, y, tile in features.iter_tiles(farm):
            if isinstance(tile, dict) and tile.get("kind") == structure and not tile.get("animal"):
                tasks.append({"p": P_PLACE, "op": ["PLACE", animal, 1], "pos": (x, y)})

    # インベントリが溜まったら shed に戻す（SELL は shed からしかできない）
    carried = sum(v for k, v in inventory.items() if k not in features.ANIMALS)
    if carried >= params["drop_threshold"]:
        tasks.append({"p": P_DROP, "op": ["DROP"], "pos": shed_tiles[0], "any_of": shed_tiles})

    return tasks


def _nearest(position, task) -> tuple[int, tuple[int, int]]:
    """タスクまでの距離と目標タイル（`any_of` があればその中で最も近いもの）。"""
    candidates = task.get("any_of") or [task["pos"]]
    best = min(candidates, key=lambda pos: features.manhattan(position, pos))
    return features.manhattan(position, best), best


def assign(obs, config=None, params=None) -> dict:
    """farmer と hands の行動を返す（doc 04 §5.3）。

    割り当ては「全ユニット × 全タスク」を (優先度, 距離) で並べた貪欲法。
    ユニットごとに順番に選ぶと、毎ターン目標が入れ替わってユニットが往復してしまう。
    """
    params = params or PARAMS
    farm = features.my_farm(obs)
    size = features.board_size(obs, config)
    shed = features.shed(obs)
    positions = features.unit_positions(obs)
    invs = features.inventories(obs)
    shed_tiles = features.shed_access_tiles(size)

    tasks = _build_tasks(obs, config, params)
    needs_feeding = sum(1 for task in tasks if task["p"] == P_FEED)
    animal_count = sum(features.count_animals(farm).values())

    # 手持ちに依存するタスク（PLACE / DROP / 餌の PICKUP）は、そのユニット専用にする
    carriers = sum(1 for inv in invs if inv.get("WHEAT", 0) > 0)
    for index, position in enumerate(positions):
        inventory = invs[index] if index < len(invs) else {}
        for task in _unit_specific_tasks(obs, config, params, index, position, inventory):
            tasks.append(dict(task, only_unit=index))
        if needs_feeding and inventory.get("WHEAT", 0) <= 0 and shed.get("WHEAT", 0) > 0:
            # 餌の運び役は必要な数だけ（全員が取りに行くと畑が止まる）
            if carriers < min(needs_feeding, params["max_feed_carriers"]):
                carriers += 1
                amount = min(int(shed.get("WHEAT", 0)),
                             max(1, animal_count * params["feed_per_animal"]))
                tasks.append({
                    "p": P_PICKUP_WHEAT, "op": ["PICKUP", "WHEAT", amount],
                    "pos": shed_tiles[0], "any_of": shed_tiles, "only_unit": index,
                })

    # (優先度, 距離) の小さい順に (ユニット, タスク) を確定していく
    pairs = []
    for unit_index, position in enumerate(positions):
        inventory = invs[unit_index] if unit_index < len(invs) else {}
        has_wheat = inventory.get("WHEAT", 0) > 0
        for task_index, task in enumerate(tasks):
            owner = task.get("only_unit")
            if owner is not None and owner != unit_index:
                continue
            if task.get("needs") == "WHEAT" and not has_wheat:
                continue  # 餌を持っていないユニットは給餌タスクを取れない
            distance, target = _nearest(position, task)
            pairs.append((task["p"], distance, unit_index, task_index, target))
    pairs.sort(key=lambda pair: (pair[0], pair[1], pair[2]))

    # 同じターンに種の在庫以上を植えると全部無効になる（README）ので本数を制限する
    plant_budget = {crop: int(count) for crop, count in features.seeds(obs).items()}
    chosen: dict[int, tuple[dict, tuple[int, int], int]] = {}
    taken: set[int] = set()
    for priority, distance, unit_index, task_index, target in pairs:
        if unit_index in chosen or task_index in taken:
            continue
        task = tasks[task_index]
        if task["p"] == P_PLANT:
            crop = task["op"][1]
            if plant_budget.get(crop, 0) <= 0:
                continue
            plant_budget[crop] -= 1
        chosen[unit_index] = (task, target, distance)
        taken.add(task_index)

    actions: list[list] = []
    for unit_index, position in enumerate(positions):
        if unit_index not in chosen:
            actions.append(["PASS"])
            continue
        task, target, distance = chosen[unit_index]
        if distance == 0:
            actions.append(list(task["op"]))
        else:
            actions.append([features.step_toward(position, target)])

    return {"farmer": actions[0] if actions else ["PASS"], "hands": actions[1:]}
