"""観測の読み取りと、ゲーム定数。

仕様: docs/04_model_design.md §5.1, docs/03_replay_schema.md §3.2
定数は kaggle_environments/envs/kaggriculture/kaggriculture.py（1.32.7）の CROPS / ANIMALS と同じ値。
提出環境では kaggle_environments を import しない方針なので、ここに写している。
"""
from __future__ import annotations

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]

CROPS = {
    "WHEAT": {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "ongoing": False},
    "CARROT": {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "ongoing": False},
    "TOMATO": {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "ongoing": True},
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "ongoing": False},
}

ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP", "product": "EGG"},
    "COW": {"cost": 400, "structure": "PASTURE", "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "product": "WOOL"},
}

LAND_PRICES = [1000, 2000, 4000]  # NE, SW, SE の順（kaggriculture.py LAND_ORDER）
DEFAULT_TURNS_PER_DAY = 24
DEFAULT_BOARD_SIZE = 10


def _cfg(config, key, default):
    if config is None:
        return default
    try:
        value = config[key] if key in config else getattr(config, key, default)
    except (TypeError, KeyError):
        value = getattr(config, key, default)
    return default if value is None else value


def turns_per_day(obs, config=None) -> int:
    return int(_cfg(config, "turnsPerDay", DEFAULT_TURNS_PER_DAY))


def board_size(obs, config=None) -> int:
    farm = my_farm(obs)
    tiles = farm.get("tiles") if farm else None
    if tiles:
        return len(tiles)
    return int(_cfg(config, "boardSize", DEFAULT_BOARD_SIZE))


def turn_index(obs, config=None) -> int:
    """ターン番号。`obs["step"]` は席1に無いので day/hour から作る（doc 03 §3.2）。"""
    return int(obs.get("day", 0)) * turns_per_day(obs, config) + int(obs.get("hour", 0))


def seat(obs) -> int:
    return int(obs.get("player", 0))


def my_farm(obs) -> dict:
    farms = obs.get("farms") or []
    index = seat(obs)
    if index >= len(farms):
        raise IndexError(f"席 {index} の farm が無い")
    return farms[index]


def private(obs) -> dict:
    return obs.get("private") or {}


def shed(obs) -> dict:
    return private(obs).get("shed") or {}


def seeds(obs) -> dict:
    return private(obs).get("seeds") or {}


def inventories(obs) -> list[dict]:
    """[farmer, hand0, hand1, ...] のインベントリ。足りない分は空で埋める。"""
    invs = list(private(obs).get("inventories") or [])
    needed = 1 + len(my_farm(obs).get("hands") or [])
    while len(invs) < needed:
        invs.append({})
    return invs


def unit_positions(obs) -> list[tuple[int, int]]:
    farm = my_farm(obs)
    positions = [tuple(farm.get("farmer") or (0, 0))]
    positions += [tuple(pos) for pos in (farm.get("hands") or [])]
    return positions


def iter_tiles(farm):
    """(x, y, tile) を順に返す。tiles[y][x] の並び（doc 03 §3.2）。"""
    for y, row in enumerate(farm.get("tiles") or []):
        for x, tile in enumerate(row):
            yield x, y, tile


def shed_access_tiles(size: int) -> list[tuple[int, int]]:
    """shed に隣接する中央4タイル（kaggriculture.py `_shed_access_tiles`）。"""
    half = size // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]


def is_shed_adjacent(pos, size: int) -> bool:
    return tuple(pos) in set(shed_access_tiles(size))


def count_animals(farm) -> dict:
    """タイルに placed 済みの家畜数。"""
    counts: dict[str, int] = {}
    for _x, _y, tile in iter_tiles(farm):
        if isinstance(tile, dict) and tile.get("animal"):
            counts[tile["animal"]] = counts.get(tile["animal"], 0) + 1
    return counts


def count_carried_animals(obs) -> dict:
    """ユニットのインベントリに入ったままの家畜。shed から PICKUP したものはここに居る。"""
    counts: dict[str, int] = {}
    for inventory in inventories(obs):
        for animal in ANIMALS:
            if inventory.get(animal, 0):
                counts[animal] = counts.get(animal, 0) + int(inventory[animal])
    return counts


def free_structures(farm) -> dict:
    """家畜が乗っていない COOP / PASTURE の座標。"""
    free: dict[str, list] = {"COOP": [], "PASTURE": []}
    for x, y, tile in iter_tiles(farm):
        if isinstance(tile, dict) and tile.get("kind") in free and not tile.get("animal"):
            free[tile["kind"]].append((x, y))
    return free


def count_crops(farm) -> dict:
    counts: dict[str, int] = {}
    for _x, _y, tile in iter_tiles(farm):
        if isinstance(tile, dict) and tile.get("kind") == "PLANT":
            counts[tile["crop"]] = counts.get(tile["crop"], 0) + 1
    return counts


def count_structures(farm) -> dict:
    """COOP / PASTURE の数（家畜が乗っているものも含む）。"""
    counts: dict[str, int] = {}
    for _x, _y, tile in iter_tiles(farm):
        if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
            counts[tile["kind"]] = counts.get(tile["kind"], 0) + 1
    return counts


def empty_tiles(farm) -> list[tuple[int, int]]:
    return [(x, y) for x, y, tile in iter_tiles(farm) if tile is None]


def manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def step_toward(src, dst) -> str:
    """1マス近づく移動コマンド。x を先に詰める（doc 04 §5.3）。"""
    if src[0] > dst[0]:
        return "WEST"
    if src[0] < dst[0]:
        return "EAST"
    if src[1] > dst[1]:
        return "NORTH"
    if src[1] < dst[1]:
        return "SOUTH"
    return "PASS"


# ------------------------------------------------- 模倣モデルの特徴量（doc 04 §3.3）

CROP_ORDER = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMAL_ORDER = ["GOOSE", "COW", "SHEEP"]
STRUCTURE_ORDER = ["COOP", "PASTURE"]

FEATURE_NAMES = (
    ["day", "money", "quadrants", "weeds", "empty", "locked", "yield_units"]
    + [f"crop_{crop}" for crop in CROP_ORDER]
    + [f"animal_{animal}" for animal in ANIMAL_ORDER]
    + [f"structure_{kind}" for kind in STRUCTURE_ORDER]
    + [f"shed_{item}" for item in PRODUCTS]
    + [f"seeds_{crop}" for crop in CROP_ORDER]
    + [f"price_{item}" for item in PRODUCTS]
    + [f"inv_{item}" for item in PRODUCTS]
)
"""49個。並び順がモデルの入力順そのものなので、**途中に足さない**（doc 04 §3.4）。

`hires_today` は入れない。hour 0 は日次リフレッシュ直後で必ず0になる（doc 02 §4.2）。
"""


def tile_counts(farm) -> dict:
    """タイルを1回走査して集計する。

    **`scripts/digest_replay.py` の `tile_summary` と同じ数え方でなければならない。**
    学習データは days[]（＝`tile_summary` の出力）から、実行時はここから作るため、
    ずれると学習したモデルが提出時に別のものを見ることになる
    （`tests/test_build_dataset.py::test_feature_vector_same_from_obs_and_digest` が見張る）。
    """
    crops: dict = {}
    animals: dict = {}
    structures: dict = {}
    weeds = empty = locked = 0
    yield_units = 0
    for _x, _y, tile in iter_tiles(farm):
        if tile is None:
            empty += 1
        elif tile == "LOCKED":
            locked += 1
        elif isinstance(tile, dict):
            kind = tile.get("kind")
            if kind == "PLANT":
                crops[tile.get("crop")] = crops.get(tile.get("crop"), 0) + 1
                yield_units += tile.get("yield_units", 0) or 0
            elif kind == "WEED":
                weeds += 1
            else:  # COOP / PASTURE
                structures[kind] = structures.get(kind, 0) + 1
                if tile.get("animal"):
                    animals[tile["animal"]] = animals.get(tile["animal"], 0) + 1
                    yield_units += tile.get("yield_units", 0) or 0
    return {
        "crops": crops,
        "animals": animals,
        "structures": structures,
        "weeds": weeds,
        "empty": empty,
        "locked": locked,
        "yield_units": yield_units,
    }


def day_state(obs, config=None) -> dict:
    """実行時の観測から、ダイジェストの days[] と同じ形の状態を作る（doc 04 §3.3）。

    学習側の `scripts/build_dataset.py` の `day_state_from_digest` と同じキーを返す。
    """
    try:
        farm = my_farm(obs)
    except (IndexError, AttributeError):
        farm = {}
    market = obs.get("market") or {}
    counts = tile_counts(farm)
    return {
        "day": int(obs.get("day", 0) or 0),
        "money": float(farm.get("money", 0) or 0),
        "quadrants": len(farm.get("unlocked_quadrants") or ["NW"]),
        "weeds": counts["weeds"],
        "empty": counts["empty"],
        "locked": counts["locked"],
        "yield_units": counts["yield_units"],
        "crops": counts["crops"],
        "animals": counts["animals"],
        "structures": counts["structures"],
        "shed": shed(obs),
        "seeds": seeds(obs),
        "prices": market.get("prices") or {},
        "inventory": market.get("inventory") or {},
    }


def feature_vector(state) -> list[float]:
    """`day_state` の形の状態を `FEATURE_NAMES` の順に並べる。欠けた値は 0 にする。"""
    crops = state.get("crops") or {}
    animals = state.get("animals") or {}
    structures = state.get("structures") or {}
    shed_stock = state.get("shed") or {}
    seed_stock = state.get("seeds") or {}
    prices = state.get("prices") or {}
    inventory = state.get("inventory") or {}
    values = [
        float(state.get("day", 0) or 0),
        float(state.get("money", 0) or 0),
        float(state.get("quadrants", 1) or 0),
        float(state.get("weeds", 0) or 0),
        float(state.get("empty", 0) or 0),
        float(state.get("locked", 0) or 0),
        float(state.get("yield_units", 0) or 0),
    ]
    values += [float(crops.get(crop, 0) or 0) for crop in CROP_ORDER]
    values += [float(animals.get(animal, 0) or 0) for animal in ANIMAL_ORDER]
    values += [float(structures.get(kind, 0) or 0) for kind in STRUCTURE_ORDER]
    values += [float(shed_stock.get(item, 0) or 0) for item in PRODUCTS]
    values += [float(seed_stock.get(crop, 0) or 0) for crop in CROP_ORDER]
    values += [float(prices.get(item, 0) or 0) for item in PRODUCTS]
    values += [float(inventory.get(item, 0) or 0) for item in PRODUCTS]
    return values
