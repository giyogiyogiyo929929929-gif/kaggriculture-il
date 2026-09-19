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
