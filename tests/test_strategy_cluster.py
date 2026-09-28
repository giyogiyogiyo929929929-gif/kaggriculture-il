# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "strategy_cluster", ROOT / "scripts/analysis/strategy_cluster.py"
)
sc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sc)


def profile(key, x, y):
    return {
        "key": key, "team_name": key, "team_id": key, "submission_id": "s",
        "games": 3, "episodes": [1, 2, 3], "mean_rank": None,
        "features": {name: 0.0 for name in sc.FEATURE_NAMES}
                 | {"sell_total_log": x, "end_animal_sheep_log": y},
    }


def synthetic_digest():
    turns = []
    for t in range(1, 7):
        a0_market = [["SELL", "WOOL", 10]] if t >= 4 else []
        a1_market = [["BUY_LAND"]] if t == 2 else []
        turns.append({
            "t": t, "day": 26 if t >= 4 else 1, "hour": t,
            "a": [
                {"f": ["HARVEST"], "h": [], "m": a0_market},
                {"f": ["PLANT"], "h": [], "m": a1_market},
            ],
        })
    return {
        "episode_id": 1,
        "seats": [{"team_name": "wool"}, {"team_name": "crop"}],
        "turns": turns,
        "days": [
            {"day": 0, "seats": [
                {"quadrants": ["NW"], "tiles": {"crops": {}, "animals": {}, "structures": {}}},
                {"quadrants": ["NW"], "tiles": {"crops": {}, "animals": {}, "structures": {}}},
            ]},
            {"day": 29, "seats": [
                {"quadrants": ["NW"], "tiles": {
                    "crops": {}, "animals": {"SHEEP": 8}, "structures": {"PASTURE": 8}}},
                {"quadrants": ["NW", "NE"], "tiles": {
                    "crops": {"WHEAT": 12}, "animals": {}, "structures": {}}},
            ]},
        ],
    }


def test_episode_profile_captures_sell_and_farm_shape():
    digest = synthetic_digest()
    wool = sc.episode_profile(digest, 0)
    crop = sc.episode_profile(digest, 1)
    assert wool["sell_wool_share"] == 1.0
    assert wool["sell_late_share"] == 1.0
    assert wool["end_animal_sheep_log"] > 0
    assert crop["land_buy_count"] > 0
    assert crop["end_crop_wheat_log"] > 0


def test_auto_cluster_separates_obvious_strategy_groups():
    profiles = [
        profile("a1", 0.0, 0.0), profile("a2", 0.1, 0.1), profile("a3", -0.1, 0.0),
        profile("b1", 8.0, 7.5), profile("b2", 8.2, 7.6), profile("b3", 7.9, 7.4),
    ]
    result = sc.cluster_profiles(profiles, k=2)
    labels = {row["key"]: row["cluster"] for row in result["profiles"]}
    assert labels["a1"] == labels["a2"] == labels["a3"]
    assert labels["b1"] == labels["b2"] == labels["b3"]
    assert labels["a1"] != labels["b1"]
    assert result["silhouette"] > 0.8


def test_pool_accepts_only_verified_sha_checked_mapping(tmp_path):
    agent = tmp_path / "main.py"
    agent.write_text("def agent(obs):\n    return {}\n", encoding="utf-8")
    profiles = [profile("a", 0, 0), profile("b", 8, 8)]
    clustered = sc.cluster_profiles(profiles, k=2)
    mapping = {}
    for cluster in clustered["clusters"]:
        mapping[cluster["representative_key"]] = {
            "path": str(agent), "verified": True, "sha256": sc.sha256(agent),
            "evidence": "fingerprint_exact",
        }
    pool = sc.build_pool(clustered, mapping, root=tmp_path)
    assert len(pool["resolved"]) == 2
    assert not pool["unresolved"]

    first = clustered["clusters"][0]["representative_key"]
    mapping[first]["sha256"] = "0" * 64
    pool = sc.build_pool(clustered, mapping, root=tmp_path)
    assert len(pool["resolved"]) == 1
    assert any("SHA256 mismatch" in row["reason"] for row in pool["unresolved"])
