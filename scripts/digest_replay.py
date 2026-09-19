"""生リプレイ（33MB）を学習・分析に使うダイジェスト（gzip 約30KB）に変換する。

仕様: docs/02_data_pipeline.md §4（スキーマ）, §4.3（受け入れ条件）, 03_replay_schema.md

使い方:
    .venv\\Scripts\\python.exe scripts\\digest_replay.py data\\raw\\*.json
    .venv\\Scripts\\python.exe scripts\\digest_replay.py data\\raw --delete-raw
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- 集計


def tile_summary(tiles: list[list]) -> dict:
    """10x10 の tiles を集計値に潰す（doc 02 §4.2）。

    容量の99%が tiles なので、ここで捨てる。動物は COOP/PASTURE の上に乗るため
    `structures` と `animals` は別々に数える（タイル数の合計には structures を使う）。
    `watered_today` / `fed_today` は hour 0 では必ず false なので入れない。
    """
    crops: collections.Counter = collections.Counter()
    animals: collections.Counter = collections.Counter()
    structures: collections.Counter = collections.Counter()
    weeds = empty = locked = 0
    yield_units = 0
    for row in tiles:
        for tile in row:
            if tile is None:
                empty += 1
            elif tile == "LOCKED":
                locked += 1
            elif isinstance(tile, dict):
                kind = tile.get("kind")
                if kind == "PLANT":
                    crops[tile.get("crop")] += 1
                    yield_units += tile.get("yield_units", 0)
                elif kind == "WEED":
                    weeds += 1
                else:  # COOP / PASTURE
                    structures[kind] += 1
                    if tile.get("animal"):
                        animals[tile["animal"]] += 1
                        yield_units += tile.get("yield_units", 0)
    return {
        "crops": dict(crops),
        "animals": dict(animals),
        "structures": dict(structures),
        "weeds": weeds,
        "empty": empty,
        "locked": locked,
        "yield_units": yield_units,
    }


def _nonzero(mapping: dict | None) -> dict:
    return {k: v for k, v in (mapping or {}).items() if v}


# ---------------------------------------------------------------- 変換


def digest_replay(rep: dict, teams: dict[str, dict] | None = None) -> dict:
    """リプレイ JSON をダイジェストに変換する（doc 02 §4.1）。"""
    info = rep.get("info") or {}
    steps = rep.get("steps") or []
    rewards = rep.get("rewards") or []
    team_names = info.get("TeamNames") or [a.get("Name") for a in info.get("Agents", [])]

    seats = []
    for i, name in enumerate(team_names):
        seat = {
            "team_name": name,
            "final_money": rewards[i] if i < len(rewards) else None,
            "won": bool(rewards and rewards[i] == max(rewards) and rewards.count(max(rewards)) == 1),
        }
        extra = (teams or {}).get(name)
        if extra:
            seat.update(extra)
        seats.append(seat)

    turns = []
    for t in range(1, len(steps)):
        prev = steps[t - 1][0].get("observation") or {}
        entry = {
            "t": t,
            # 行動を決めた観測（steps[t-1]）の時刻。03 §3.1
            "day": prev.get("day"),
            "hour": prev.get("hour"),
            "a": [],
        }
        for seat_index in range(len(steps[t])):
            action = steps[t][seat_index].get("action") or {}
            entry["a"].append(
                {"f": action.get("farmer"), "h": action.get("hands"), "m": action.get("market")}
            )
        turns.append(entry)

    days = []
    for t, step in enumerate(steps):
        obs0 = step[0].get("observation") or {}
        if obs0.get("hour") != 0:
            continue
        day = {
            "day": obs0.get("day"),
            "t": t,
            "prices": (obs0.get("market") or {}).get("prices"),
            "inventory": (obs0.get("market") or {}).get("inventory"),
            "shops": (obs0.get("town") or {}).get("unlocked_shops"),
            "seats": [],
        }
        farms = obs0.get("farms") or []
        for seat_index in range(len(farms)):
            farm = farms[seat_index]
            private = {}
            if seat_index < len(step):
                private = (step[seat_index].get("observation") or {}).get("private") or {}
            day["seats"].append(
                {
                    "money": farm.get("money"),
                    "quadrants": farm.get("unlocked_quadrants"),
                    "hires_today": farm.get("hires_today"),
                    "tiles": tile_summary(farm.get("tiles") or []),
                    "shed": _nonzero(private.get("shed")),
                    "seeds": _nonzero(private.get("seeds")),
                }
            )
        days.append(day)

    return {
        "episode_id": info.get("EpisodeId"),
        "module_version": rep.get("module_version"),
        "seed": info.get("seed"),
        "configuration": rep.get("configuration"),
        "seats": seats,
        "turns": turns,
        "days": days,
    }


# ---------------------------------------------------------------- 入出力


def load_teams(meta_dir: Path) -> dict[str, dict]:
    """`data\\meta\\leaderboard.csv` から teamName → 順位・teamId を作る（doc 02 §4.2）。"""
    path = Path(meta_dir) / "leaderboard.csv"
    if not path.exists():
        return {}
    teams: dict[str, dict] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for rank, row in enumerate(csv.DictReader(handle), start=1):
            name = row.get("teamName")
            if not name or name in teams:  # 同名チームは先勝ち（doc 02 §2 の TODO）
                continue
            try:
                score = float(row.get("score", ""))
            except (TypeError, ValueError):
                score = None
            teams[name] = {"team_id": row.get("teamId"), "rank": rank, "public_score": score}
    return teams


def write_digest(digest: dict, out_dir: Path) -> Path:
    """`<out_dir>\\<episode_id>.json.gz` に書く。"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{digest.get('episode_id')}.json.gz"
    payload = json.dumps(digest, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with path.open("wb") as raw_handle:
        # mtime=0：同じ入力なら同じバイト列になるようにする
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", compresslevel=6, mtime=0) as gz:
            gz.write(payload)
    return path


def load_digest(path: Path) -> dict:
    with gzip.open(Path(path), "rt", encoding="utf-8") as handle:
        return json.load(handle)


def digest_file(
    raw_path: Path,
    out_dir: Path,
    teams: dict[str, dict] | None = None,
    delete_raw: bool = False,
) -> Path:
    """生リプレイ1本をダイジェスト化する。成功時のみ生データを消す。"""
    raw_path = Path(raw_path)
    rep = json.loads(raw_path.read_text(encoding="utf-8"))
    digest = digest_replay(rep, teams=teams)
    if digest.get("episode_id") is None:
        raise ValueError(f"episode_id が取れない: {raw_path}")
    out = write_digest(digest, out_dir)
    if delete_raw:
        raw_path.unlink()
    return out


def update_manifest(meta_dir: Path, episode_id: str | int, **info) -> Path | None:
    """`data\\meta\\manifest.json` の該当エピソードを更新する（doc 02 §4.3）。

    fetch_replays.py 以外（このスクリプト単体）でダイジェスト化したときも状態を合わせるため。
    manifest が無ければ何もしない。
    """
    path = Path(meta_dir) / "manifest.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None
    episodes = data.setdefault("episodes", {})
    record = episodes.setdefault(str(episode_id), {})
    record.update(info)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _iter_inputs(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in paths:
        path = Path(item)
        if path.is_dir():
            files.extend(sorted(path.glob("*.json")))
        elif any(ch in item for ch in "*?"):
            files.extend(sorted(Path().glob(item)))
        else:
            files.append(path)
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="生リプレイをダイジェストに変換する（docs/02_data_pipeline.md §4）"
    )
    parser.add_argument("inputs", nargs="+", help="リプレイ JSON かディレクトリ")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "digest")
    parser.add_argument("--meta-dir", type=Path, default=ROOT / "data" / "meta")
    parser.add_argument("--delete-raw", action="store_true", help="成功した生リプレイを削除する")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    teams = load_teams(args.meta_dir)
    files = _iter_inputs(args.inputs)
    if not files:
        print("入力が無い", file=sys.stderr)
        return 2
    total_raw = total_digest = 0
    for raw_path in files:
        raw_size = raw_path.stat().st_size
        out = digest_file(raw_path, args.out, teams=teams, delete_raw=args.delete_raw)
        size = out.stat().st_size
        total_raw += raw_size
        total_digest += size
        update_manifest(
            args.meta_dir,
            out.stem.replace(".json", ""),
            status="digested",
            path=str(out),
            digest_bytes=size,
            bytes=raw_size,
        )
        print(f"{raw_path.name} {raw_size:,} bytes -> {out.name} {size:,} bytes "
              f"(1/{raw_size // max(size, 1)})")
    if files:
        print(f"合計: {total_raw:,} -> {total_digest:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
