# -*- coding: utf-8 -*-
"""Cross-analyse v80 public replays and downloaded public assets.

Specification: docs/experiments/EXP-20260925-69-v80-public-asset-analysis.md
Public notebook cells are never executed; this script only reads downloaded data.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import statistics
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "own_v80_recent"
IMPORT = ROOT / "data" / "imports" / "public_analysis_20260925"
META = IMPORT / "kaggriculture_episodes_meta"
ARCHIVE = IMPORT / "top10_archive" / "files"
OUT = ROOT / "data" / "analysis" / "v80_public_assets"
ME_MARKER = "giyogoio"
PREFIXES = (24, 48, 100, 136, 200, 300, 400, 719)


def action_hashes(replay: dict, seat: int) -> dict[str, str | int | None]:
    """Use the public dataset's canonical JSON + NUL prefix-hash convention."""
    digest = hashlib.sha256()
    row: dict[str, str | int | None] = {"turns": max(0, len(replay["steps"]) - 1)}
    for turn, step in enumerate(replay["steps"]):
        if turn == 0:
            continue
        action = step[seat].get("action") or {}
        digest.update(json.dumps(action, sort_keys=True, separators=(",", ":")).encode())
        digest.update(b"\0")
        if turn in PREFIXES:
            row[f"stream_h{turn}"] = digest.hexdigest()[:16]
    for turn in PREFIXES:
        row.setdefault(f"stream_h{turn}", None)
    return row


def strip_weeds(farm: dict) -> tuple:
    tiles = tuple(tuple(None if isinstance(tile, dict) and tile.get("kind") == "WEED"
                        else json.dumps(tile, sort_keys=True, ensure_ascii=False)
                        for tile in row) for row in farm.get("tiles", []))
    rest = tuple(sorted((key, json.dumps(value, sort_keys=True, ensure_ascii=False))
                        for key, value in farm.items() if key not in ("tiles", "money")))
    return tiles, rest


def first_physical_difference(replay: dict) -> int | None:
    for turn, step in enumerate(replay["steps"]):
        farms = step[0]["observation"]["farms"]
        if strip_weeds(farms[0]) != strip_weeds(farms[1]):
            return turn
    return None


def local_games() -> tuple[pd.DataFrame, pd.DataFrame]:
    games: list[dict] = []
    hashes: list[dict] = []
    for path in sorted(RAW.glob("*.json")):
        replay = json.loads(path.read_text(encoding="utf-8"))
        names = replay["info"]["TeamNames"]
        me = next((seat for seat, name in enumerate(names) if ME_MARKER in name.lower()), None)
        if me is None:
            continue
        op = 1 - me
        final_obs = replay["steps"][-1][0]["observation"]
        money = [float(farm["money"]) for farm in final_obs["farms"]]
        shops = list(final_obs.get("town", {}).get("unlocked_shops", []))
        diff = money[me] - money[op]
        episode = int(replay["info"]["EpisodeId"])
        games.append({
            "episode_id": episode,
            "team_name": names[me],
            "opponent": names[op],
            "me_seat": me,
            "seed": replay["info"].get("seed"),
            "money_me": money[me],
            "money_op": money[op],
            "diff": diff,
            "result": "win" if diff > 0 else "loss" if diff < 0 else "draw",
            "first_shop": shops[0] if shops else None,
            "second_shop": shops[1] if len(shops) > 1 else None,
            "world2": " / ".join(shops[:2]),
            "early_yarn": "YARN_STORE" in shops[:2],
            "early_pet": "PET_CAFE" in shops[:2],
            "early_brunch": "BRUNCH_SPOT" in shops[:2],
            "first_physical_diff": first_physical_difference(replay),
        })
        for seat in (0, 1):
            hashes.append({"episode_id": episode, "seat": seat,
                           "role": "me" if seat == me else "opponent",
                           "team_name": names[seat], **action_hashes(replay, seat)})
    return pd.DataFrame(games), pd.DataFrame(hashes)


def group_stats(frame: pd.DataFrame, key: str, minimum: int = 1) -> list[dict]:
    rows = []
    for value, part in frame.groupby(key, dropna=False):
        if len(part) < minimum:
            continue
        rows.append({
            key: None if pd.isna(value) else value,
            "games": len(part),
            "wins": int((part.result == "win").sum()),
            "losses": int((part.result == "loss").sum()),
            "draws": int((part.result == "draw").sum()),
            "win_rate": round(float((part.result == "win").mean()), 4),
            "mean_diff": round(float(part["diff"].mean()), 2),
            "median_diff": round(float(part["diff"].median()), 2),
        })
    return sorted(rows, key=lambda row: (-row["games"], row["mean_diff"]))


def lineage_matches(local_hashes: pd.DataFrame, public_hashes: pd.DataFrame,
                    agents: pd.DataFrame, teams: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    public = public_hashes.merge(agents, left_on=["episode_id", "seat"],
                                 right_on=["episode_id", "agent_index"], how="left")
    public = public.merge(teams[["team_id", "team_name", "ladder_score"]],
                          on="team_id", how="left")
    summary: list[dict] = []
    common: collections.Counter[tuple] = collections.Counter()
    for role in ("me", "opponent"):
        own = local_hashes[local_hashes.role == role]
        for turn in (100, 136, 200, 300, 400, 719):
            column = f"stream_h{turn}"
            candidates = set(own[column].dropna())
            hit = public[public[column].isin(candidates)]
            matched_local = own[column].isin(set(hit[column])).sum()
            summary.append({
                "role": role,
                "prefix": turn,
                "local_games": len(own),
                "matched_local_games": int(matched_local),
                "public_rows": len(hit),
                "public_episodes": int(hit.episode_id.nunique()),
                "submissions": int(hit.submission_id.nunique()),
                "teams": int(hit.team_id.nunique()),
            })
            for item in hit[["team_name", "submission_id", "ladder_score"]].drop_duplicates().itertuples(index=False):
                common[(role, turn, item.team_name, item.submission_id, item.ladder_score)] += 1
    common_rows = [{"role": key[0], "prefix": key[1], "team_name": key[2],
                    "submission_id": None if pd.isna(key[3]) else int(key[3]),
                    "ladder_score": None if pd.isna(key[4]) else round(float(key[4]), 1),
                    "matched_hashes": count}
                   for key, count in common.items() if key[2] is not None and key[1] >= 300]
    common_rows.sort(key=lambda row: (-row["prefix"], -row["matched_hashes"], row["team_name"]))
    return summary, common_rows[:200]


def population_comparison(features: pd.DataFrame, agents: pd.DataFrame,
                          episodes: pd.DataFrame, teams: pd.DataFrame) -> dict:
    latest = pd.to_datetime(episodes.create_time, utc=True).max()
    cutoff = latest - pd.Timedelta(days=14)
    recent_ids = set(episodes.loc[pd.to_datetime(episodes.create_time, utc=True) >= cutoff, "episode_id"])
    merged = features[features.episode_id.isin(recent_ids)].merge(
        agents[["episode_id", "agent_index", "team_id"]],
        left_on=["episode_id", "seat"], right_on=["episode_id", "agent_index"], how="inner")
    merged = merged.merge(teams[["team_id", "ladder_score"]], on="team_id", how="left")
    columns = ["final_money", "peak_crew", "total_hires", "first_land_day", "elbow_day",
               "tiles_planted", "plants_carrot", "plants_melon", "plants_strawberry",
               "plants_tomato", "plants_wheat"]
    team_level = merged.groupby("team_id")[columns + ["ladder_score"]].median(numeric_only=True)
    bands = {"top_2600_plus": team_level[team_level.ladder_score >= 2600],
             "middle_2200_2500": team_level[(team_level.ladder_score >= 2200)
                                             & (team_level.ladder_score < 2500)]}
    result = {"data_latest": latest.isoformat(), "cutoff": cutoff.isoformat(),
              "recent_episodes": len(recent_ids), "team_rows": len(team_level), "bands": {}}
    for name, part in bands.items():
        result["bands"][name] = {"teams": len(part), "medians": {
            column: None if math.isnan(float(part[column].median()))
            else round(float(part[column].median()), 2) for column in columns}}
    return result


def top10_summary(history: pd.DataFrame, archive_episodes: pd.DataFrame,
                  local_games_frame: pd.DataFrame) -> dict:
    latest_date = history.date.max()
    latest = history[history.date == latest_date].sort_values("rank")
    local_names = set(local_games_frame.opponent) | set(local_games_frame.team_name)
    archive_names = set(archive_episodes.team_name.dropna())
    return {
        "date_range": [history.date.min(), latest_date],
        "days": int(history.date.nunique()),
        "unique_teams": int(history.team_name.nunique()),
        "latest_proxy_top10": latest[["rank", "team_name", "score_proxy"]].to_dict("records"),
        "most_appearances": (history.groupby("team_name").size().sort_values(ascending=False)
                             .head(15).rename("days").reset_index().to_dict("records")),
        "local_names_in_archive": sorted(local_names & archive_names),
        "note": "rank is a pair-average proxy, not the official leaderboard rank",
    }


def clean(value):
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def main() -> int:
    games, local_hashes = local_games()
    agents = pd.read_csv(META / "agents.csv")
    episodes = pd.read_csv(META / "episodes.csv")
    teams = pd.read_csv(META / "teams.csv")
    features = pd.read_csv(META / "episode_features.csv")
    public_hashes = pd.read_csv(META / "stream_hashes.csv")
    history = pd.read_parquet(ARCHIVE / "top10_history.parquet")
    archive_episodes = pd.read_parquet(ARCHIVE / "episodes.parquet")

    team_scores = teams.drop_duplicates("team_name", keep="last").set_index("team_name")["ladder_score"]
    games["opponent_ladder_score_20260922"] = games.opponent.map(team_scores)
    games["rating_band"] = pd.cut(games.opponent_ladder_score_20260922,
                                   bins=[-math.inf, 2200, 2500, math.inf],
                                   labels=["under_2200", "2200_2500", "2500_plus"])
    games["physical_band"] = games.first_physical_diff.map(
        lambda value: "turn_0_3" if pd.notna(value) and value <= 3 else "turn_4_plus")
    games["early_yarn_label"] = games.early_yarn.map({True: "early_yarn", False: "no_early_yarn"})
    games["early_pet_label"] = games.early_pet.map({True: "early_pet", False: "no_early_pet"})
    lineage, common = lineage_matches(local_hashes, public_hashes, agents, teams)
    ordered = games.sort_values("episode_id")
    windows = []
    for name, part in (("earliest_24", ordered.head(24)),
                       ("middle_5", ordered.iloc[24:-24]),
                       ("latest_24", ordered.tail(24))):
        windows.append({
            "window": name, "games": len(part),
            "wins": int((part.result == "win").sum()),
            "losses": int((part.result == "loss").sum()),
            "mean_diff": round(float(part["diff"].mean()), 2),
            "median_diff": round(float(part["diff"].median()), 2),
        })
    physical_seat = []
    for (band, seat), part in games.groupby(["physical_band", "me_seat"]):
        physical_seat.append({
            "physical_band": band, "me_seat": int(seat), "games": len(part),
            "wins": int((part.result == "win").sum()),
            "losses": int((part.result == "loss").sum()),
            "mean_diff": round(float(part["diff"].mean()), 2),
            "median_diff": round(float(part["diff"].median()), 2),
        })

    result = {
        "generated_from": {
            "local_replays": str(RAW), "local_games": len(games),
            "meta_latest": episodes.create_time.max(),
            "top10_latest": history.date.max(),
            "rating_reference": "teams.csv ladder_score snapshot (last submissions through 2026-09-22)",
        },
        "overall": {
            "games": len(games), "wins": int((games.result == "win").sum()),
            "losses": int((games.result == "loss").sum()),
            "draws": int((games.result == "draw").sum()),
            "mean_diff": round(float(games["diff"].mean()), 2),
            "median_diff": round(float(games["diff"].median()), 2),
            "rating_joined": int(games.opponent_ladder_score_20260922.notna().sum()),
        },
        "by_seat": group_stats(games, "me_seat"),
        "chronological_windows": windows,
        "by_first_shop": group_stats(games, "first_shop", minimum=2),
        "by_world2_repeated": group_stats(games, "world2", minimum=2),
        "by_early_yarn": group_stats(games, "early_yarn_label"),
        "by_early_pet": group_stats(games, "early_pet_label"),
        "by_physical_band": group_stats(games, "physical_band"),
        "physical_band_by_seat": physical_seat,
        "by_rating_band": group_stats(games.dropna(subset=["rating_band"]), "rating_band"),
        "worst_games": games.sort_values("diff").head(15).to_dict("records"),
        "lineage": lineage,
        "lineage_examples": common,
        "population": population_comparison(features, agents, episodes, teams),
        "top10_archive": top10_summary(history, archive_episodes, games),
    }
    result = clean(result)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    games.sort_values("episode_id").to_csv(OUT / "local_games.csv", index=False, encoding="utf-8")
    local_hashes.sort_values(["episode_id", "seat"]).to_csv(
        OUT / "local_stream_hashes.csv", index=False, encoding="utf-8")
    print(json.dumps({"output": str(OUT / "summary.json"), **result["overall"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
