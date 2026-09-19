"""ダイジェスト化の受け入れ条件テスト。

仕様: docs/02_data_pipeline.md §4（スキーマ）, §4.3（受け入れ条件）
"""
import gzip
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import digest_replay as dr  # noqa: E402

BOARD = 10


def _tiles(entries: dict[tuple[int, int], object]) -> list[list[object]]:
    """(x, y) → タイル の指定から 10x10 の tiles を作る。既定は None（空き）。"""
    grid: list[list[object]] = [[None] * BOARD for _ in range(BOARD)]
    for y in range(BOARD):
        for x in range(BOARD):
            if x >= 5 or y >= 5:  # NW 以外は最初ロック
                grid[y][x] = "LOCKED"
    for (x, y), tile in entries.items():
        grid[y][x] = tile
    return grid


def _obs(day: int, hour: int, seat: int, tiles, money=3000.0, shed=None, seeds=None):
    return {
        "player": seat,
        "day": day,
        "hour": hour,
        "farms": [
            {"money": money, "tiles": tiles, "farmer": [4, 4], "hands": [],
             "unlocked_quadrants": ["NW"], "hires_today": 0},
            {"money": 2500.0, "tiles": _tiles({}), "farmer": [4, 4], "hands": [],
             "unlocked_quadrants": ["NW"], "hires_today": 1},
        ],
        "market": {"prices": {"WHEAT": 25}, "inventory": {"WHEAT": 10000}},
        "town": {"unlocked_shops": ["BAKERY"]},
        "private": {"shed": shed or {"WHEAT": 3, "MELON": 0}, "seeds": seeds or {"MELON": 2, "WHEAT": 0},
                    "inventories": [{}]},
    }


@pytest.fixture
def replay():
    """2日ぶん（hour 0,1）の小さなリプレイ。"""
    tiles = _tiles({
        (0, 0): {"kind": "PLANT", "crop": "WHEAT", "yield_units": 3, "watered_today": False},
        (1, 0): {"kind": "PLANT", "crop": "MELON", "yield_units": 0, "watered_today": True},
        (2, 0): {"kind": "WEED"},
        (3, 0): {"kind": "COOP", "animal": "GOOSE", "yield_units": 2, "fed_today": False},
        (4, 0): {"kind": "PASTURE", "animal": None, "yield_units": 0, "fed_today": False},
    })
    steps = []
    for t, (day, hour) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
        actions = [
            {"farmer": ["WATER"], "hands": [["PASS"]], "market": [["SELL", "WHEAT", t]]},
            {"farmer": ["PASS"], "hands": [], "market": []},
        ]
        steps.append([
            {"observation": _obs(day, hour, 0, tiles), "action": actions[0],
             "reward": 0, "status": "ACTIVE", "info": {}},
            {"observation": _obs(day, hour, 1, tiles), "action": actions[1],
             "reward": 0, "status": "ACTIVE", "info": {}},
        ])
    steps[-1][0]["reward"] = 5000.0
    steps[-1][0]["status"] = "DONE"
    return {
        "id": "uuid-x",
        "name": "kaggriculture",
        "module_version": "1.32.7",
        "schema_version": 1,
        "configuration": {"episodeSteps": 4, "turnsPerDay": 24, "boardSize": BOARD},
        "specification": {"大きい": "x" * 5000},
        "steps": steps,
        "rewards": [5000.0, 4000.0],
        "statuses": ["DONE", "DONE"],
        "info": {"EpisodeId": 110451333, "TeamNames": ["わたし", "あいて"], "seed": 42},
    }


def test_tile_summary_counts_all_tiles(replay):
    """タイル数の合計が boardSize^2 になる（doc 02 §4.3）。"""
    tiles = replay["steps"][0][0]["observation"]["farms"][0]["tiles"]
    summary = dr.tile_summary(tiles)
    total = (
        sum(summary["crops"].values())
        + sum(summary["structures"].values())
        + summary["weeds"]
        + summary["empty"]
        + summary["locked"]
    )
    assert total == BOARD * BOARD
    assert summary["crops"] == {"WHEAT": 1, "MELON": 1}
    assert summary["animals"] == {"GOOSE": 1}  # 動物は structures の上に乗るので別勘定
    assert summary["structures"] == {"COOP": 1, "PASTURE": 1}
    assert summary["weeds"] == 1
    assert summary["locked"] == 75
    assert summary["yield_units"] == 5  # 作物3 + 家畜2


def test_digest_structure(replay):
    digest = dr.digest_replay(replay)
    assert digest["episode_id"] == 110451333
    assert digest["module_version"] == "1.32.7"
    assert digest["seed"] == 42
    assert "specification" not in digest
    assert digest["seats"][0] == {"team_name": "わたし", "final_money": 5000.0, "won": True}
    assert digest["seats"][1]["won"] is False


def test_turns_and_days_counts(replay):
    """turns は steps 数-1、days は hour==0 の数（doc 02 §4.3）。"""
    digest = dr.digest_replay(replay)
    assert len(digest["turns"]) == len(replay["steps"]) - 1
    assert len(digest["days"]) == 2
    assert [d["day"] for d in digest["days"]] == [0, 1]


def test_turn_action_matches_source(replay):
    """turns[0] の m が steps[1] の market 注文と一致する（doc 02 §4.3）。"""
    digest = dr.digest_replay(replay)
    first = digest["turns"][0]
    assert first["t"] == 1
    assert first["a"][0]["m"] == replay["steps"][1][0]["action"]["market"]
    assert first["a"][0]["f"] == replay["steps"][1][0]["action"]["farmer"]
    assert first["a"][0]["h"] == replay["steps"][1][0]["action"]["hands"]
    # day/hour は行動を決めた観測（steps[t-1]）のもの
    assert (first["day"], first["hour"]) == (0, 0)
    assert (digest["turns"][1]["day"], digest["turns"][1]["hour"]) == (0, 1)


def test_day_snapshot_contents(replay):
    digest = dr.digest_replay(replay)
    day0 = digest["days"][0]
    assert day0["prices"] == {"WHEAT": 25}
    assert day0["inventory"] == {"WHEAT": 10000}
    assert day0["shops"] == ["BAKERY"]
    seat0 = day0["seats"][0]
    assert seat0["money"] == 3000.0
    assert seat0["quadrants"] == ["NW"]
    assert seat0["shed"] == {"WHEAT": 3}  # 0 の品目は落とす
    assert seat0["seeds"] == {"MELON": 2}
    assert "watered" not in seat0["tiles"]  # hour 0 では常に false なので入れない


def test_meta_enrichment(replay):
    """順位・teamId はリーダーボード meta から結合する（doc 02 §4.2）。"""
    teams = {"わたし": {"team_id": "111", "rank": 1, "public_score": 3180.4}}
    digest = dr.digest_replay(replay, teams=teams)
    assert digest["seats"][0]["team_id"] == "111"
    assert digest["seats"][0]["rank"] == 1
    assert digest["seats"][0]["public_score"] == 3180.4
    assert "rank" not in digest["seats"][1]  # meta に無いチームは付けない


def test_write_and_load_roundtrip(replay, tmp_path):
    digest = dr.digest_replay(replay)
    path = dr.write_digest(digest, tmp_path)
    assert path.name == "110451333.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        loaded = json.load(handle)
    assert loaded == digest
    assert dr.load_digest(path) == digest


def test_digest_file_deletes_raw(replay, tmp_path):
    """ダイジェスト化に成功したら生リプレイを削除する（doc 02 §3, §4.3）。"""
    raw = tmp_path / "episode-110451333-replay.json"
    raw.write_text(json.dumps(replay), encoding="utf-8")
    out = dr.digest_file(raw, tmp_path / "digest", delete_raw=True)
    assert out.exists()
    assert not raw.exists()


def test_digest_file_keeps_raw_by_default(replay, tmp_path):
    raw = tmp_path / "episode-110451333-replay.json"
    raw.write_text(json.dumps(replay), encoding="utf-8")
    dr.digest_file(raw, tmp_path / "digest")
    assert raw.exists()


def test_load_teams_from_leaderboard(tmp_path):
    csv_path = tmp_path / "leaderboard.csv"
    csv_path.write_text(
        "teamId,teamName,submissionDate,score\n"
        "16730612,Unknown Mother-Goose,2026-09-16 02:07:02.966000,3180.4\n"
        "16718819,Majkel1337,2026-09-13 23:03:27.150000,3175.6\n",
        encoding="utf-8",
    )
    teams = dr.load_teams(tmp_path)
    assert teams["Unknown Mother-Goose"] == {"team_id": "16730612", "rank": 1, "public_score": 3180.4}
    assert teams["Majkel1337"]["rank"] == 2


def test_update_manifest(tmp_path):
    """単体実行でも manifest を digested に更新する（doc 02 §4.3）。"""
    meta = tmp_path / "meta"
    meta.mkdir()
    (meta / "manifest.json").write_text(
        json.dumps({"episodes": {"110451333": {"status": "downloaded", "teamName": "X"}}}),
        encoding="utf-8",
    )
    dr.update_manifest(meta, "110451333", status="digested", digest_bytes=123)
    data = json.loads((meta / "manifest.json").read_text(encoding="utf-8"))
    record = data["episodes"]["110451333"]
    assert record["status"] == "digested"
    assert record["digest_bytes"] == 123
    assert record["teamName"] == "X"  # 既存の情報は消さない


def test_update_manifest_without_file(tmp_path):
    assert dr.update_manifest(tmp_path, "1", status="digested") is None
