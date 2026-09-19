"""パターン分析の受け入れ条件テスト。

仕様: docs/04_model_design.md §2.3（出力）, §2.5（受け入れ条件）
"""
import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import analyze_patterns as ap  # noqa: E402
from scripts import digest_replay as dr  # noqa: E402


def _day(day: int, monies=(3000.0, 2500.0), crops=None, animals=None):
    return {
        "day": day,
        "t": day * 24,
        "prices": {"WHEAT": 25 + day, "MELON": 250},
        "inventory": {"WHEAT": 10000 - day, "MELON": 10000},
        "shops": ["BAKERY"] * (day + 1),
        "seats": [
            {
                "money": monies[seat],
                "quadrants": ["NW", "NE"][: 1 + (day > 1)],
                "hires_today": day,
                "tiles": {
                    "crops": crops or {"WHEAT": 3 + day},
                    "animals": animals or {"GOOSE": day},
                    "structures": {"COOP": day},
                    "weeds": 0, "empty": 22 - day, "locked": 75, "yield_units": day,
                },
                "shed": {"WHEAT": day},
                "seeds": {"MELON": 1},
            }
            for seat in (0, 1)
        ],
    }


def _turn(t, day, hour, market0, market1=None):
    return {
        "t": t, "day": day, "hour": hour,
        "a": [
            {"f": ["WATER"], "h": [["PASS"], ["WATER"]], "m": market0},
            {"f": ["PASS"], "h": [], "m": market1 or []},
        ],
    }


@pytest.fixture
def digest():
    return {
        "episode_id": 1,
        "module_version": "1.32.7",
        "seed": 42,
        "configuration": {"episodeSteps": 72, "turnsPerDay": 24, "boardSize": 10},
        "seats": [
            {"team_name": "勝ち", "final_money": 9000.0, "won": True, "rank": 1,
             "team_id": "1", "public_score": 3180.4},
            {"team_name": "負け", "final_money": 4000.0, "won": False, "rank": 20,
             "team_id": "2", "public_score": 2900.0},
        ],
        "turns": [
            _turn(1, 0, 0, [["BUY_SEED", "WHEAT", 2], ["HIRE"]], [["BUY_SEED", "MELON", 1]]),
            _turn(2, 0, 1, [["BUY_ANIMAL", "GOOSE", 1], ["HIRE"]]),
            _turn(3, 1, 0, [["SELL", "WHEAT", 5], ["BUY_SEED", "WHEAT", 3]]),
            _turn(4, 2, 0, [["BUY_LAND"]], [["SELL", "EGG", 2]]),
        ],
        "days": [_day(0), _day(1), _day(2)],
    }


@pytest.fixture
def digest_dir(tmp_path, digest):
    out = tmp_path / "digest"
    dr.write_digest(digest, out)
    second = dict(digest)
    second["episode_id"] = 2
    dr.write_digest(second, out)
    return out


def _read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_seat_rows(digest):
    rows = ap.seat_rows(digest)
    assert len(rows) == 2
    won = rows[0]
    assert won["episode_id"] == 1
    assert won["seat"] == 0
    assert won["team_name"] == "勝ち"
    assert won["rank"] == 1
    assert won["won"] is True
    assert won["final_money"] == 9000.0
    assert won["total_hires"] == 2
    assert won["land_buys"] == 1
    assert won["first_land_day"] == 2
    assert won["buy_seed_WHEAT"] == 5
    assert won["buy_animal_GOOSE"] == 1
    assert won["sell_WHEAT"] == 5
    lost = rows[1]
    assert lost["total_hires"] == 0
    assert lost["first_land_day"] is None
    assert lost["sell_EGG"] == 2


def test_daily_order_rows_match_source(digest):
    """daily_orders の数量合計が元の market 注文と一致する（doc 04 §2.5）。"""
    rows = ap.daily_order_rows(digest)
    total_buy_seed = sum(r["qty"] for r in rows if r["kind"] == "BUY_SEED")
    source = sum(
        order[2]
        for turn in digest["turns"]
        for seat_action in turn["a"]
        for order in seat_action["m"]
        if order[0] == "BUY_SEED"
    )
    assert total_buy_seed == source == 6
    hires = [r for r in rows if r["kind"] == "HIRE"]
    assert sum(r["qty"] for r in hires) == 2  # HIRE は1件1人
    day0 = [r for r in rows if r["day"] == 0 and r["seat"] == 0]
    assert {r["kind"] for r in day0} == {"BUY_SEED", "HIRE", "BUY_ANIMAL"}


def test_daily_state_rows(digest):
    rows = ap.daily_state_rows(digest)
    assert len(rows) == 3 * 2  # 3日 × 2席
    first = rows[0]
    assert first["day"] == 0 and first["seat"] == 0
    assert first["money"] == 3000.0
    assert first["crop_WHEAT"] == 3
    assert first["animal_GOOSE"] == 0
    assert first["quadrants"] == 1
    assert first["shed_WHEAT"] == 0
    assert rows[-1]["crop_WHEAT"] == 5  # day2


def test_price_rows(digest):
    rows = ap.price_rows(digest)
    assert len(rows) == 3 * 2  # 3日 × 2品目
    wheat_day1 = [r for r in rows if r["day"] == 1 and r["item"] == "WHEAT"][0]
    assert wheat_day1["price"] == 26
    assert wheat_day1["inventory"] == 9999


def test_command_counts(digest):
    counts = ap.command_counts(digest)
    assert counts[(0, "farmer", "WATER")] == 4
    assert counts[(0, "hands", "PASS")] == 4
    assert counts[(1, "farmer", "PASS")] == 4


def test_analyze_writes_all_outputs(digest_dir, tmp_path):
    """4つの CSV と summary.md が出る（doc 04 §2.3, §2.5）。"""
    out = tmp_path / "analysis"
    result = ap.analyze(digest_dir, out)
    assert result["episodes"] == 2
    for name in ("seats.csv", "daily_state.csv", "daily_orders.csv", "prices.csv", "summary.md"):
        assert (out / name).exists(), name
    seats = _read_csv(out / "seats.csv")
    assert len(seats) == 2 * 2  # ダイジェスト数 × 2席
    text = (out / "summary.md").read_text(encoding="utf-8")
    assert "序盤の型" in text
    assert "勝ち席" in text and "負け席" in text
    assert "土地購入" in text
    assert "売却" in text


def test_empty_digest_dir_does_not_crash(tmp_path, capsys):
    """ダイジェスト0本でも落ちない（doc 04 §2.5）。"""
    empty = tmp_path / "digest"
    empty.mkdir()
    code = ap.main(["--digest-dir", str(empty), "--out", str(tmp_path / "analysis")])
    assert code == 0
    assert "ダイジェスト" in capsys.readouterr().out


def test_cli_end_to_end(digest_dir, tmp_path):
    code = ap.main(["--digest-dir", str(digest_dir), "--out", str(tmp_path / "analysis")])
    assert code == 0
    assert (tmp_path / "analysis" / "summary.md").exists()
