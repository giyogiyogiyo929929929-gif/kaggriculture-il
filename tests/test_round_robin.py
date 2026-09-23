from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "analysis"))
import round_robin as rr


def test_schedule_each_unordered_pair_once_and_pilot_first():
    agents = [{"name": f"submitted/{name}", "category": "submitted"}
              for name in ("v22_antiv52_brunchguard", "v27_orderbook_layer_d", "other")]
    pairs = rr.schedule(agents)
    assert len(pairs) == 3
    assert {x["name"] for x in pairs[0]} == {
        "submitted/v22_antiv52_brunchguard", "submitted/v27_orderbook_layer_d"}
    assert len({rr.pair_key(a, b) for a, b in pairs}) == 3


def test_standings_mirror_result():
    agents = [{"name": name, "category": "submitted", "aliases": [name]}
              for name in ("a", "b")]
    rows = rr.standings([{"status": "complete", "a": "a", "b": "b", "wins": 1,
                          "losses": 0, "draws": 0, "pair_diff_mean": 10}], agents)
    assert [(x["name"], x["wins"], x["losses"], x["pair_diff_total"]) for x in rows] == [
        ("a", 1, 0, 10), ("b", 0, 1, -10)]


def test_refresh_adds_new_agent_but_preserves_existing_identity(monkeypatch, tmp_path):
    monkeypatch.setattr(rr, "ROOT", tmp_path)
    for name in ("a", "b", "c"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "main.py").write_text(name, encoding="utf-8")
    old = {"name": "submitted/a", "category": "submitted", "path": "a/main.py",
           "sha256": "sha-a", "aliases": ["submitted/a"]}
    manifest = {"agents": [old], "excluded": [], "pairs": 0}
    monkeypatch.setattr(rr, "discover", lambda: {"agents": [
        {"name": "automation/a-copy", "category": "automation", "path": "b/main.py",
         "sha256": "sha-a", "aliases": ["automation/a-copy"]},
        {"name": "automation/c", "category": "automation", "path": "c/main.py",
         "sha256": "sha-c", "aliases": ["automation/c"]},
    ], "excluded": []})
    updated, added = rr.refresh_manifest(manifest)
    assert added == 1
    assert updated["pairs"] == 1
    assert updated["agents"][1]["name"] == "submitted/a"
    assert updated["agents"][1]["aliases"] == ["submitted/a", "automation/a-copy"]
