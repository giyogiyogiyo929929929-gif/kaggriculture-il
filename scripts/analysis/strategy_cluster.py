# -*- coding: utf-8 -*-
"""Public replay digests -> behavior profiles -> strategy clusters -> opponent-pool draft.

This is analysis-only. It never executes public notebook code and never changes the champion.
Input reuses scripts/fetch_replays.py + scripts/digest_replay.py.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.digest_replay import load_digest  # noqa: E402

ITEMS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
         "EGG", "MILK", "WOOL", "FERTILIZER")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("GOOSE", "COW", "SHEEP")
UNIT_KINDS = ("PLANT", "WATER", "HARVEST", "FERTILIZE", "FEED", "CARE",
              "COLLECT_FERTILIZER", "BUILD_COOP", "BUILD_PASTURE", "DIG", "PASS")
MARKET_KINDS = ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT", "SELL", "HIRE", "BUY_LAND")
FEATURE_NAMES = (
    tuple(f"unit_{kind.lower()}_rate" for kind in UNIT_KINDS)
    + tuple(f"market_{kind.lower()}_rate" for kind in MARKET_KINDS)
    + ("market_order_rate", "sell_total_log", "sell_first_turn", "sell_late_share",
       "sell_collision_share", "sell_reactive_1_2_share", "hire_total_log",
       "land_buy_count", "first_land_day", "first_animal_day", "end_quadrants")
    + tuple(f"sell_{item.lower()}_share" for item in ITEMS)
    + tuple(f"end_crop_{item.lower()}_log" for item in CROPS)
    + tuple(f"end_animal_{item.lower()}_log" for item in ANIMALS)
)


def _qty(order: list[Any]) -> int:
    if len(order) > 2 and isinstance(order[2], (int, float)):
        return max(0, int(order[2]))
    return 1


def _command_kind(command: Any) -> str:
    if isinstance(command, (list, tuple)) and command and isinstance(command[0], str):
        return command[0]
    return "PASS"


def _sell_schedule(digest: dict, seat: int) -> dict[str, dict[int, int]]:
    schedule: dict[str, dict[int, int]] = collections.defaultdict(dict)
    for turn in digest.get("turns") or []:
        actions = turn.get("a") or []
        if seat >= len(actions):
            continue
        for order in (actions[seat] or {}).get("m") or []:
            if not isinstance(order, list) or len(order) < 2 or order[0] != "SELL":
                continue
            item = str(order[1])
            t = int(turn.get("t", 0) or 0)
            schedule[item][t] = schedule[item].get(t, 0) + _qty(order)
    return schedule


def _reaction_units(mine: dict[str, dict[int, int]],
                    theirs: dict[str, dict[int, int]]) -> tuple[int, int]:
    collision = reactive = 0
    for item in set(mine) | set(theirs):
        my_steps = mine.get(item, {})
        their_steps = theirs.get(item, {})
        for t, qty in my_steps.items():
            collision += min(qty, their_steps.get(t, 0))
            reactive += min(qty, their_steps.get(t - 1, 0) + their_steps.get(t - 2, 0))
    return collision, reactive


def episode_profile(digest: dict, seat: int) -> dict[str, float]:
    """Extract behavior features from one seat of one digest."""
    turns = digest.get("turns") or []
    unit = collections.Counter()
    market = collections.Counter()
    sells = collections.Counter()
    total_unit = total_orders = total_sell = late_sell = hire_total = land_buys = 0
    first_sell: int | None = None

    for turn in turns:
        actions = turn.get("a") or []
        if seat >= len(actions):
            continue
        action = actions[seat] or {}
        commands = [action.get("f")] + list(action.get("h") or [])
        for command in commands:
            kind = _command_kind(command)
            unit[kind] += 1
            total_unit += 1
        day = int(turn.get("day", 0) or 0)
        t = int(turn.get("t", 0) or 0)
        for order in action.get("m") or []:
            if not isinstance(order, list) or not order:
                continue
            kind = str(order[0])
            qty = _qty(order)
            market[kind] += 1
            total_orders += 1
            if kind == "SELL" and len(order) > 1:
                item = str(order[1])
                sells[item] += qty
                total_sell += qty
                if day >= 25:
                    late_sell += qty
                if first_sell is None:
                    first_sell = t
            elif kind == "HIRE":
                hire_total += qty
            elif kind == "BUY_LAND":
                land_buys += 1

    mine = _sell_schedule(digest, seat)
    other = _sell_schedule(digest, 1 - seat) if len(digest.get("seats") or []) == 2 else {}
    collision, reactive = _reaction_units(mine, other)

    day_records = digest.get("days") or []
    first_land_day: int | None = None
    first_animal_day: int | None = None
    final_state: dict[str, Any] = {}
    for day in day_records:
        states = day.get("seats") or []
        if seat >= len(states):
            continue
        state = states[seat] or {}
        final_state = state
        day_no = int(day.get("day", 0) or 0)
        if first_land_day is None and len(state.get("quadrants") or []) > 1:
            first_land_day = day_no
        animals = ((state.get("tiles") or {}).get("animals") or {})
        if first_animal_day is None and sum(int(v or 0) for v in animals.values()) > 0:
            first_animal_day = day_no

    nturns = max(1, len(turns))
    unit_den = max(1, total_unit)
    features: dict[str, float] = {}
    for kind in UNIT_KINDS:
        features[f"unit_{kind.lower()}_rate"] = unit[kind] / unit_den
    for kind in MARKET_KINDS:
        features[f"market_{kind.lower()}_rate"] = market[kind] / nturns
    features["market_order_rate"] = total_orders / nturns
    features["sell_total_log"] = math.log1p(total_sell)
    features["sell_first_turn"] = (first_sell if first_sell is not None else 720) / 720.0
    features["sell_late_share"] = late_sell / max(1, total_sell)
    features["sell_collision_share"] = collision / max(1, total_sell)
    features["sell_reactive_1_2_share"] = reactive / max(1, total_sell)
    features["hire_total_log"] = math.log1p(hire_total)
    features["land_buy_count"] = min(3, land_buys) / 3.0
    features["first_land_day"] = (first_land_day if first_land_day is not None else 30) / 30.0
    features["first_animal_day"] = (first_animal_day if first_animal_day is not None else 30) / 30.0

    for item in ITEMS:
        features[f"sell_{item.lower()}_share"] = sells[item] / max(1, total_sell)

    tiles = final_state.get("tiles") or {}
    features["end_quadrants"] = len(final_state.get("quadrants") or ["NW"]) / 4.0
    end_crops = tiles.get("crops") or {}
    end_animals = tiles.get("animals") or {}
    for item in CROPS:
        features[f"end_crop_{item.lower()}_log"] = math.log1p(float(end_crops.get(item, 0) or 0))
    for item in ANIMALS:
        features[f"end_animal_{item.lower()}_log"] = math.log1p(float(end_animals.get(item, 0) or 0))

    return {name: float(features.get(name, 0.0)) for name in FEATURE_NAMES}


def load_manifest(meta_dir: Path) -> dict[str, dict]:
    path = Path(meta_dir) / "manifest.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value.get("episodes", {}) if isinstance(value, dict) else {}


def identity(digest: dict, seat: int, manifest: dict[str, dict]) -> tuple[str, dict]:
    seats = digest.get("seats") or []
    info = seats[seat] if seat < len(seats) else {}
    episode = str(digest.get("episode_id"))
    record = manifest.get(episode, {})
    team_name = str(info.get("team_name") or f"seat{seat}")
    team_id = str(info.get("team_id") or record.get("teamId") or team_name)
    submission_id = str(record.get("submissionId") or "unknown")
    return f"{team_id}:{submission_id}", {
        "team_name": team_name,
        "team_id": team_id,
        "submission_id": submission_id,
        "rank": info.get("rank"),
        "public_score": info.get("public_score"),
    }


def aggregate_profiles(digest_dir: Path, meta_dir: Path, min_games: int = 2) -> list[dict]:
    manifest = load_manifest(meta_dir)
    buckets: dict[str, list[tuple[dict[str, float], dict, int]]] = collections.defaultdict(list)
    for path in sorted(Path(digest_dir).glob("*.json.gz")):
        digest = load_digest(path)
        for seat in range(len(digest.get("seats") or [])):
            key, meta = identity(digest, seat, manifest)
            buckets[key].append((episode_profile(digest, seat), meta, int(digest.get("episode_id") or 0)))

    profiles = []
    for key, games in sorted(buckets.items()):
        if len(games) < min_games:
            continue
        features = {
            name: statistics.mean(game[0][name] for game in games)
            for name in FEATURE_NAMES
        }
        metas = [game[1] for game in games]
        ranks = [m["rank"] for m in metas if isinstance(m.get("rank"), (int, float))]
        profiles.append({
            "key": key,
            "team_name": metas[0]["team_name"],
            "team_id": metas[0]["team_id"],
            "submission_id": metas[0]["submission_id"],
            "games": len(games),
            "episodes": [game[2] for game in games],
            "mean_rank": statistics.mean(ranks) if ranks else None,
            "features": features,
        })
    return profiles


def standardize(profiles: list[dict]) -> tuple[list[list[float]], dict]:
    if not profiles:
        return [], {"mean": {}, "scale": {}}
    means, scales = {}, {}
    for name in FEATURE_NAMES:
        values = [float(p["features"][name]) for p in profiles]
        mean = statistics.mean(values)
        scale = statistics.pstdev(values)
        means[name] = mean
        scales[name] = scale if scale > 1e-12 else 1.0
    points = [[(float(p["features"][name]) - means[name]) / scales[name] for name in FEATURE_NAMES]
              for p in profiles]
    return points, {"mean": means, "scale": scales}


def _sqdist(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def kmeans(points: list[list[float]], k: int, max_iter: int = 100) -> tuple[list[int], list[list[float]]]:
    if not 1 <= k <= len(points):
        raise ValueError("k out of range")
    dims = len(points[0])
    global_center = [statistics.mean(row[d] for row in points) for d in range(dims)]
    first = min(range(len(points)), key=lambda i: (_sqdist(points[i], global_center), i))
    centers = [points[first][:]]
    chosen = {first}
    while len(centers) < k:
        idx = max((i for i in range(len(points)) if i not in chosen),
                  key=lambda i: (min(_sqdist(points[i], c) for c in centers), -i))
        chosen.add(idx)
        centers.append(points[idx][:])

    labels = [-1] * len(points)
    for _ in range(max_iter):
        new_labels = [min(range(k), key=lambda c: (_sqdist(point, centers[c]), c))
                      for point in points]
        if new_labels == labels:
            break
        labels = new_labels
        new_centers = []
        for c in range(k):
            members = [points[i] for i, label in enumerate(labels) if label == c]
            if not members:
                farthest = max(range(len(points)),
                               key=lambda i: min(_sqdist(points[i], center) for center in centers))
                new_centers.append(points[farthest][:])
            else:
                new_centers.append([statistics.mean(row[d] for row in members) for d in range(dims)])
        centers = new_centers
    return labels, centers


def silhouette(points: list[list[float]], labels: list[int]) -> float:
    clusters = collections.defaultdict(list)
    for i, label in enumerate(labels):
        clusters[label].append(i)
    if len(clusters) < 2:
        return 0.0
    scores = []
    for i, point in enumerate(points):
        own = clusters[labels[i]]
        if len(own) <= 1:
            scores.append(0.0)
            continue
        a = statistics.mean(math.sqrt(_sqdist(point, points[j])) for j in own if j != i)
        b = min(statistics.mean(math.sqrt(_sqdist(point, points[j])) for j in members)
                for label, members in clusters.items() if label != labels[i])
        scores.append((b - a) / max(a, b, 1e-12))
    return statistics.mean(scores)


def choose_k(points: list[list[float]], max_k: int = 8) -> tuple[int, dict[int, float]]:
    n = len(points)
    if n < 2:
        return 1, {1: 0.0}
    if n < 4:
        return 2, {2: silhouette(points, kmeans(points, 2)[0])}
    upper = min(max_k, n - 1)
    scores: dict[int, float] = {}
    for k in range(2, upper + 1):
        labels, _ = kmeans(points, k)
        scores[k] = silhouette(points, labels)
    best = max(scores, key=lambda k: (scores[k], -k))
    return best, scores


def cluster_profiles(profiles: list[dict], k: int | None = None, max_k: int = 8) -> dict:
    ordered = sorted(profiles, key=lambda p: p["key"])
    points, scaler = standardize(ordered)
    if not ordered:
        return {"k": 0, "silhouette": None, "k_scores": {}, "clusters": [], "profiles": []}
    if k is None:
        k, k_scores = choose_k(points, max_k=max_k)
    else:
        k_scores = {}
    labels, centers = kmeans(points, k)
    score = silhouette(points, labels) if k > 1 else 0.0

    raw_clusters = []
    for label in range(k):
        members = [i for i, x in enumerate(labels) if x == label]
        center = centers[label]
        representative = min(members, key=lambda i: (_sqdist(points[i], center), ordered[i]["key"]))
        top = sorted(
            ((FEATURE_NAMES[d], center[d]) for d in range(len(FEATURE_NAMES))),
            key=lambda item: (-abs(item[1]), item[0]),
        )[:6]
        raw_clusters.append({
            "old_label": label,
            "representative_key": ordered[representative]["key"],
            "representative_team": ordered[representative]["team_name"],
            "members": [ordered[i]["key"] for i in members],
            "size": len(members),
            "top_features": [{"name": name, "z": round(value, 3)} for name, value in top],
        })

    raw_clusters.sort(key=lambda c: c["representative_key"])
    remap = {c["old_label"]: idx for idx, c in enumerate(raw_clusters)}
    for profile, label in zip(ordered, labels):
        profile["cluster"] = remap[label]
    clusters = []
    for idx, cluster in enumerate(raw_clusters):
        cluster = dict(cluster)
        cluster.pop("old_label")
        cluster["cluster"] = idx
        clusters.append(cluster)

    return {
        "k": k,
        "silhouette": score,
        "k_scores": {str(key): value for key, value in k_scores.items()},
        "feature_names": list(FEATURE_NAMES),
        "scaler": scaler,
        "clusters": clusters,
        "profiles": ordered,
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_pool(clustered: dict, mapping: dict[str, Any] | None = None,
               root: Path = ROOT) -> dict:
    """Resolve cluster representatives only from explicitly verified local mappings."""
    mapping = mapping or {}
    resolved, unresolved = [], []
    by_key = {p["key"]: p for p in clustered.get("profiles", [])}
    for cluster in clustered.get("clusters", []):
        key = cluster["representative_key"]
        entry = mapping.get(key)
        if not isinstance(entry, dict) or not entry.get("verified"):
            unresolved.append({"cluster": cluster["cluster"], "representative_key": key,
                               "team_name": cluster["representative_team"],
                               "reason": "no verified local-agent mapping"})
            continue
        path = Path(entry.get("path", ""))
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            unresolved.append({"cluster": cluster["cluster"], "representative_key": key,
                               "team_name": cluster["representative_team"],
                               "reason": f"mapped path missing: {entry.get('path')}"})
            continue
        actual = sha256(path)
        expected = entry.get("sha256")
        if expected and actual != expected:
            unresolved.append({"cluster": cluster["cluster"], "representative_key": key,
                               "team_name": cluster["representative_team"],
                               "reason": "mapped SHA256 mismatch"})
            continue
        profile = by_key.get(key, {})
        resolved.append({
            "name": f"cluster_{cluster['cluster']}_{profile.get('team_name', key)}",
            "cluster": cluster["cluster"],
            "representative_key": key,
            "team_name": profile.get("team_name"),
            "path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
            "sha256": actual,
            "evidence": entry.get("evidence"),
        })
    return {"resolved": resolved, "unresolved": unresolved,
            "cluster_count": len(clustered.get("clusters", []))}


def render_summary(clustered: dict, pool: dict) -> str:
    lines = [
        "# Strategy clusters", "",
        f"- profiles: {len(clustered.get('profiles', []))}",
        f"- k: {clustered.get('k')}",
        f"- silhouette: {clustered.get('silhouette')}",
        f"- resolved pool representatives: {len(pool.get('resolved', []))}/{pool.get('cluster_count', 0)}",
        "",
    ]
    for cluster in clustered.get("clusters", []):
        tops = ", ".join(f"{x['name']}={x['z']:+.2f}" for x in cluster["top_features"])
        lines += [
            f"## cluster {cluster['cluster']} ({cluster['size']} profiles)",
            f"representative: `{cluster['representative_key']}` / {cluster['representative_team']}",
            f"top z-features: {tops}", "",
        ]
    if pool.get("unresolved"):
        lines += ["## Unresolved representatives", ""]
        for row in pool["unresolved"]:
            lines.append(f"- cluster {row['cluster']}: `{row['representative_key']}` — {row['reason']}")
        lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cluster public replay agents by observed strategy")
    parser.add_argument("--digest-dir", type=Path, default=ROOT / "data/digest")
    parser.add_argument("--meta-dir", type=Path, default=ROOT / "data/meta")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data/analysis/strategy_pool")
    parser.add_argument("--min-games", type=int, default=2)
    parser.add_argument("--k", type=int)
    parser.add_argument("--max-k", type=int, default=8)
    parser.add_argument("--agent-map", type=Path,
                        help="JSON: profile key -> {path, verified:true, sha256?, evidence?}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    profiles = aggregate_profiles(args.digest_dir, args.meta_dir, min_games=args.min_games)
    if len(profiles) < 2:
        print(f"strategy clustering needs >=2 profiles; got {len(profiles)}", file=sys.stderr)
        return 2
    clustered = cluster_profiles(profiles, k=args.k, max_k=args.max_k)
    mapping = {}
    if args.agent_map:
        mapping = json.loads(args.agent_map.read_text(encoding="utf-8"))
    pool = build_pool(clustered, mapping)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "clusters.json").write_text(
        json.dumps(clustered, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out_dir / "opponent_pool.json").write_text(
        json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out_dir / "summary.md").write_text(render_summary(clustered, pool), encoding="utf-8")
    print(f"{len(profiles)} profiles -> {clustered['k']} clusters; "
          f"pool resolved {len(pool['resolved'])}/{pool['cluster_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
