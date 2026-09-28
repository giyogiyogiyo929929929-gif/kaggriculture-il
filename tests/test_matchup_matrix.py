# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "matchup_matrix", ROOT / "scripts/analysis/matchup_matrix.py"
)
mm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mm)


def test_directed_matrix_inverts_result_and_pair_diff():
    agents = [{"name": "A"}, {"name": "B"}]
    results = [{
        "status": "complete", "a": "A", "b": "B",
        "wins": 6, "losses": 2, "draws": 2, "pair_diff_mean": 123.5,
    }]
    cells = mm.directed_cells(agents, results)
    assert cells["A"]["B"]["win_rate"] == 0.7
    assert cells["B"]["A"]["win_rate"] == 0.3
    assert cells["A"]["B"]["pair_diff_mean"] == 123.5
    assert cells["B"]["A"]["pair_diff_mean"] == -123.5


def test_pair_key_depends_on_fixed_seed_panel_not_argument_order():
    a, b = {"name": "A"}, {"name": "B"}
    assert mm.pair_key(a, b, 100, 8) == mm.pair_key(b, a, 100, 8)
    assert mm.pair_key(a, b, 100, 8) != mm.pair_key(a, b, 101, 8)


def test_weakness_summary_uses_all_available_opponents():
    agents = [{"name": "A", "source": "extra"}, {"name": "B", "source": "cluster"}]
    cells = mm.directed_cells(agents, [{
        "status": "complete", "a": "A", "b": "B",
        "wins": 3, "losses": 5, "draws": 0, "pair_diff_mean": -20,
    }])
    rows = {row["name"]: row for row in mm.weakness_summary(agents, cells)}
    assert rows["A"]["matchups"] == 1
    assert rows["A"]["mean_win_rate"] == 3 / 8
    assert rows["B"]["worst_win_rate"] == 5 / 8
