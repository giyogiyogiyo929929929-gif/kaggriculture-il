"""学習データ作成（タスク 1-1）の受け入れ条件テスト。

仕様: docs/04_model_design.md §3.3（ラベル・特徴量・除外）, §3.6（受け入れ条件）
"""
import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import features  # noqa: E402
from scripts import build_dataset as bd  # noqa: E402
from scripts import digest_replay as dr  # noqa: E402

SIZE = 4  # テスト用の小さい盤


def _tiles():
    """4x4 の盤。PLANT 3枚・WEED 1枚・COOP(GOOSE)・PASTURE(空)・LOCKED 2枚・残りは空き。"""
    blank = [[None] * SIZE for _ in range(SIZE)]
    blank[0][0] = {"kind": "PLANT", "crop": "WHEAT", "yield_units": 2}
    blank[0][1] = {"kind": "PLANT", "crop": "WHEAT", "yield_units": 3}
    blank[0][2] = {"kind": "PLANT", "crop": "STRAWBERRY", "yield_units": 4}
    blank[1][0] = {"kind": "WEED"}
    blank[1][1] = {"kind": "COOP", "animal": "GOOSE", "yield_units": 1}
    blank[1][2] = {"kind": "PASTURE"}
    blank[2][0] = "LOCKED"
    blank[2][1] = "LOCKED"
    return blank


def _obs(day=3, seat=0):
    """実行時の観測（doc 03 §3.2 のキー）。"""
    return {
        "player": seat,
        "day": day,
        "hour": 0,
        "farms": [
            {
                "money": 1234.0,
                "tiles": _tiles(),
                "farmer": [0, 0],
                "hands": [[1, 1]],
                "unlocked_quadrants": ["NW", "NE"],
                "hires_today": 0,
            },
            {
                "money": 999.0,
                "tiles": [[None] * SIZE for _ in range(SIZE)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
        ],
        "market": {
            "prices": {"WHEAT": 39, "CARROT": 47, "TOMATO": 74, "STRAWBERRY": 156,
                       "MELON": 158, "EGG": 52, "MILK": 93, "WOOL": 112, "FERTILIZER": 57},
            "inventory": {"WHEAT": 9000, "CARROT": 100, "TOMATO": 200, "STRAWBERRY": 300,
                          "MELON": 400, "EGG": 500, "MILK": 600, "WOOL": 700, "FERTILIZER": 800},
        },
        "town": {"unlocked_shops": ["BAKERY"]},
        "private": {
            "shed": {"WHEAT": 12, "MILK": 3, "GOOSE": 1},
            "seeds": {"MELON": 2, "WHEAT": 1},
            "inventories": [{}, {}],
        },
    }


def _digest_day(day):
    """ダイジェストの days[] 1件（doc 02 §4.1）。観測と同じ内容を入れる。"""
    obs = _obs(day=day)
    mine = {
        "money": obs["farms"][0]["money"],
        "quadrants": obs["farms"][0]["unlocked_quadrants"],
        "hires_today": 0,
        "tiles": dr.tile_summary(obs["farms"][0]["tiles"]),
        "shed": obs["private"]["shed"],
        "seeds": obs["private"]["seeds"],
    }
    other = {
        "money": 999.0, "quadrants": ["NW"], "hires_today": 0,
        "tiles": dr.tile_summary(obs["farms"][1]["tiles"]), "shed": {}, "seeds": {},
    }
    return {
        "day": day, "t": day * 24,
        "prices": obs["market"]["prices"],
        "inventory": obs["market"]["inventory"],
        "shops": ["BAKERY"],
        "seats": [mine, other],
    }


def _turn(t, day, hour, market0, market1=None):
    return {"t": t, "day": day, "hour": hour,
            "a": [{"f": ["PASS"], "h": [], "m": market0},
                  {"f": ["PASS"], "h": [], "m": market1 or []}]}


@pytest.fixture
def digest():
    """30日ぶんの days と、いくつかの注文を持つダイジェスト。"""
    return {
        "episode_id": 7,
        "module_version": "1.32.7",
        "seed": 42,
        "configuration": {"episodeSteps": 720, "turnsPerDay": 24, "boardSize": SIZE},
        "seats": [
            {"team_name": "上位", "final_money": 120000.0, "won": True,
             "team_id": "1", "rank": 1, "public_score": 3180.4},
            {"team_name": "圏外", "final_money": 90000.0, "won": False,
             "team_id": "2", "rank": None, "public_score": None},
        ],
        "turns": [
            # day3：席0 が WHEAT を 2 + 3 に分けて買い、土地も買う。INVALID / PASS は除外対象
            _turn(1, 3, 0, [["BUY_SEED", "WHEAT", 2], ["HIRE"], ["INVALID"]],
                  [["BUY_SEED", "MELON", 9]]),
            _turn(2, 3, 5, [["BUY_SEED", "WHEAT", 3], ["BUY_LAND"], ["PASS"]]),
            _turn(3, 3, 9, [["BUY_SEED", "STRAWBERRY", 1], ["NOOP"]]),
            # day4：買わない日
            _turn(4, 4, 0, [["SELL", "WHEAT", 5]]),
            # day29：最終日の注文（行としては落とす）
            _turn(5, 29, 0, [["BUY_SEED", "CARROT", 4]]),
        ],
        "days": [_digest_day(d) for d in range(30)],
    }


def _write_leaderboard(meta_dir, names):
    """`leaderboard.csv`（doc 02 §4.2）。行の順番がそのまま順位になる。"""
    meta_dir.mkdir(parents=True, exist_ok=True)
    lines = ["teamId,teamName,submissionDate,score"]
    for index, (team_id, name) in enumerate(names):
        lines.append(f"{team_id},{name},2026-09-18 00:00:00,{3200 - index}")
    (meta_dir / "leaderboard.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return meta_dir


@pytest.fixture
def teams(tmp_path):
    """現在のリーダーボード：「上位」だけが1位で載っている。"""
    return dr.load_teams(_write_leaderboard(tmp_path / "meta_teams", [("1", "上位")]))


@pytest.fixture
def meta_dir(tmp_path):
    return _write_leaderboard(tmp_path / "meta", [("1", "上位")])


@pytest.fixture
def digest_dir(tmp_path, digest):
    out = tmp_path / "digest"
    dr.write_digest(digest, out)
    second = dict(digest)
    second["episode_id"] = 8
    dr.write_digest(second, out)
    return out


def _read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


# ---------------------------------------------------------------- 特徴量


def test_feature_names_are_49_and_unique():
    """doc §3.3 の49個（日・状態・shed・seeds・価格・在庫）。"""
    assert len(features.FEATURE_NAMES) == 49
    assert len(set(features.FEATURE_NAMES)) == 49
    assert "hires_today" not in features.FEATURE_NAMES  # hour 0 では常に0（doc §3.3）
    for leaked in ("final_money", "rank", "won"):
        assert leaked not in features.FEATURE_NAMES


def test_feature_vector_same_from_obs_and_digest():
    """特徴量49個が obs からもダイジェストからも同じ値で作れる（doc §3.6 タスク1-1）。

    学習は days[]、実行は obs から作るので、ここがずれると
    「学習したモデルが提出時に別物を見る」ことになる。
    """
    obs = _obs(day=3)
    from_obs = features.feature_vector(features.day_state(obs))
    digest_state = bd.day_state_from_digest(_digest_day(3), seat=0)
    from_digest = features.feature_vector(digest_state)
    assert from_obs == from_digest
    named = dict(zip(features.FEATURE_NAMES, from_obs))
    assert named["day"] == 3
    assert named["money"] == 1234.0
    assert named["quadrants"] == 2
    assert named["crop_WHEAT"] == 2
    assert named["crop_STRAWBERRY"] == 1
    assert named["animal_GOOSE"] == 1
    assert named["structure_COOP"] == 1
    assert named["structure_PASTURE"] == 1
    assert named["weeds"] == 1
    assert named["locked"] == 2
    assert named["empty"] == SIZE * SIZE - 8
    assert named["yield_units"] == 2 + 3 + 4 + 1
    assert named["shed_WHEAT"] == 12
    assert named["seeds_MELON"] == 2
    assert named["price_STRAWBERRY"] == 156
    assert named["inv_WHEAT"] == 9000


def test_feature_vector_tolerates_missing_keys():
    """壊れた／欠けた観測でも落ちない（提出時のフォールバック条件・NFR-2）。"""
    vector = features.feature_vector(features.day_state({"player": 0, "day": 0,
                                                         "farms": [{"tiles": []}]}))
    assert len(vector) == 49
    assert all(isinstance(v, float) for v in vector)


# ---------------------------------------------------------------- ラベル


def test_labels_are_targets_not_deltas(digest, teams):
    """target = 作物タイル + 種在庫 + その日に買った数（doc §3.3）。"""
    rows = {(r["seat"], r["day"]): r for r in bd.dataset_rows(digest, teams)}
    day3 = rows[(0, 3)]
    # 盤面 WHEAT 2枚 + 種在庫 1 + その日の購入 5（2+3）
    assert day3["buy_seed_WHEAT"] == 5
    assert day3["target_seed_WHEAT"] == 2 + 1 + 5
    assert day3["target_seed_STRAWBERRY"] == 1 + 0 + 1
    assert day3["target_seed_MELON"] == 0 + 2 + 0  # 買っていない日も在庫は目標に入る
    assert day3["buy_land"] == 1
    day4 = rows[(0, 4)]
    assert day4["buy_seed_WHEAT"] == 0
    assert day4["target_seed_WHEAT"] == 2 + 1
    assert day4["buy_land"] == 0


def test_buy_seed_total_matches_source(digest, teams):
    """BUY_SEED 数量の合計が元の注文と一致する（INVALID/PASS/NOOP 除外後。doc §3.6）。"""
    rows = bd.dataset_rows(digest, teams)
    total = sum(r[f"buy_seed_{crop}"] for r in rows for crop in bd.CROPS)
    source = sum(
        order[2]
        for turn in digest["turns"]
        for seat_index, action in enumerate(turn["a"])
        for order in action["m"]
        if order[0] == "BUY_SEED"
        and seat_index == 0             # リーダーボードに載った席だけを採用している
        and turn["day"] <= bd.LAST_DAY  # 最終日は落としている
    )
    assert total == source == 6  # WHEAT 5 + STRAWBERRY 1（MELON 9 は圏外席、CARROT 4 は day29）


def test_invalid_orders_are_excluded(digest, teams):
    """INVALID / PASS / NOOP は注文として数えない（doc 03 §3.3、doc 04 §3.3）。"""
    rows = {(r["seat"], r["day"]): r for r in bd.dataset_rows(digest, teams)}
    assert rows[(0, 3)]["hires"] == 1  # HIRE 1件だけ。INVALID/PASS/NOOP は入らない


# ---------------------------------------------------------------- 行の採用


def test_rows_only_ranked_seats_and_drop_last_day(digest, teams):
    """行数 = リーダーボードに載っている席 × 29日（day 0〜28）。doc §3.3 の採用条件。"""
    rows = bd.dataset_rows(digest, teams)
    assert len(rows) == 1 * 29
    assert {r["seat"] for r in rows} == {0}
    assert max(r["day"] for r in rows) == bd.LAST_DAY == 28


def test_weight_uses_rank_not_score(digest, teams):
    """重みは rank だけで決める（public_score はレーティングなので使わない。doc §3.3）。"""
    rows = bd.dataset_rows(digest, teams)
    assert all(r["weight"] == pytest.approx(2.0) for r in rows)  # rank 1 → 2.0
    for leaked in ("public_score", "final_money", "won"):
        assert leaked not in rows[0]


def test_stale_digest_rank_is_ignored(digest, tmp_path):
    """採用と rank は現在の leaderboard.csv で決まり、ダイジェストの古い rank は使わない（doc §3.3, 02 §4.2）。

    実データで起きたこと：試し取得で作ったダイジェストに、当時2位で今は圏外のチームが
    `rank: 2` のまま残り、現2位のチームは `rank: null` のままだった。
    """
    stale = {**digest, "seats": [
        {**digest["seats"][0], "rank": None, "team_id": None},   # 今は1位なのに null
        {**digest["seats"][1], "rank": 2, "team_id": "2"},        # 今は圏外なのに 2
    ]}
    teams = dr.load_teams(_write_leaderboard(tmp_path / "meta", [("1", "上位")]))
    rows = bd.dataset_rows(stale, teams)
    assert {r["seat"] for r in rows} == {0}
    assert all(r["rank"] == 1 and r["team_id"] == "1" for r in rows)
    assert all(r["weight"] == pytest.approx(2.0) for r in rows)


# ---------------------------------------------------------------- 出力・CLI


def test_build_writes_csv(digest_dir, meta_dir, tmp_path):
    out = tmp_path / "dataset" / "macro.csv"
    result = bd.build(digest_dir, out, meta_dir)
    assert result["episodes"] == 2
    assert result["rows"] == 2 * 29
    rows = _read_csv(out)
    assert len(rows) == 2 * 29
    header = list(rows[0].keys())
    for name in features.FEATURE_NAMES:
        assert name in header, name
    for crop in bd.CROPS:
        assert f"target_seed_{crop}" in header
    assert "buy_land" in header
    assert header[:3] == ["episode_id", "seat", "day"]
    assert len(header) == len(set(header))  # `day` は key と特徴量の両方にあるので重複しやすい
    assert all(row["day"] == str(int(row["day"])) for row in rows)  # 整数のまま書く


def test_team_balancing_equalizes_weight_sum(tmp_path, digest):
    """同じチームのエピソードが多くても、チームごとの重み合計が偏らない（doc §3.3）。"""
    out = tmp_path / "digest"
    for episode_id in (1, 2, 3):          # 同じチームで3本
        dr.write_digest({**digest, "episode_id": episode_id}, out)
    other = {**digest, "episode_id": 4,
             "seats": [{**digest["seats"][0], "team_name": "別チーム"}, digest["seats"][1]]}
    dr.write_digest(other, out)
    meta = _write_leaderboard(tmp_path / "meta", [("1", "上位"), ("9", "別チーム")])
    rows = bd.collect_rows(out, meta)
    totals = {}
    for row in rows:
        totals[row["team_id"]] = totals.get(row["team_id"], 0.0) + row["weight"]
    assert totals["1"] == pytest.approx(totals["9"])


def test_empty_digest_dir_does_not_crash(tmp_path, capsys):
    """ダイジェスト0本でも落ちない（doc §3.6）。"""
    empty = tmp_path / "digest"
    empty.mkdir()
    code = bd.main(["--digest-dir", str(empty), "--out", str(tmp_path / "macro.csv")])
    assert code == 0
    assert "ダイジェスト" in capsys.readouterr().out


def test_all_ranks_missing_does_not_crash(tmp_path, digest, capsys):
    """リーダーボードに載った席が1つも無いときも落ちず、その旨を出す（doc §3.6）。"""
    out = tmp_path / "digest"
    dr.write_digest(digest, out)
    meta = _write_leaderboard(tmp_path / "meta", [("5", "無関係なチーム")])
    code = bd.main(["--digest-dir", str(out), "--meta-dir", str(meta),
                    "--out", str(tmp_path / "macro.csv")])
    assert code == 0
    assert "rank" in capsys.readouterr().out


def test_missing_leaderboard_does_not_crash(tmp_path, digest_dir, capsys):
    """leaderboard.csv が無いときは1行も作らず、その旨を出す（doc §3.3）。"""
    code = bd.main(["--digest-dir", str(digest_dir), "--meta-dir", str(tmp_path / "no_meta"),
                    "--out", str(tmp_path / "macro.csv")])
    assert code == 0
    assert "leaderboard.csv" in capsys.readouterr().out
    assert not (tmp_path / "macro.csv").exists()


def test_cli_end_to_end(digest_dir, meta_dir, tmp_path):
    out = tmp_path / "macro.csv"
    assert bd.main(["--digest-dir", str(digest_dir), "--meta-dir", str(meta_dir),
                    "--out", str(out)]) == 0
    assert out.exists()
