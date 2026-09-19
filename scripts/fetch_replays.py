"""上位チームのリプレイを Kaggle CLI 経由で取得する。

仕様: docs/02_data_pipeline.md §2（手順）, §3（取得ルール）, §5（設定値）, §6（受け入れ条件）

使い方:
    .venv\\Scripts\\python.exe scripts\\fetch_replays.py --top-n 2 --episodes-per-team 2
    .venv\\Scripts\\python.exe scripts\\fetch_replays.py --dry-run

生リプレイは1本33MB（03 §4）。取得したら即ダイジェスト化して
`data\\digest\\<episode_id>.json.gz`（約30KB）にし、生データは削除する（doc 02 §3）。
生データを残したいときだけ `--keep-raw`。
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import digest_replay  # noqa: E402

# doc 02 §3：除外条件
VALIDATION_TYPE = "EpisodeType.EPISODE_TYPE_VALIDATION"
COMPLETED_STATE = "EpisodeState.COMPLETED"


class KaggleCommandError(RuntimeError):
    """kaggle CLI の呼び出しが失敗した。"""


# ---------------------------------------------------------------- CLI 呼び出し


def kaggle_executable() -> str:
    """同じ仮想環境の kaggle 実行ファイルを探す。無ければ PATH の kaggle。"""
    scripts_dir = Path(sys.executable).parent
    for name in ("kaggle.exe", "kaggle"):
        candidate = scripts_dir / name
        if candidate.exists():
            return str(candidate)
    return "kaggle"


def run_kaggle(args: list[str]) -> str:
    """kaggle CLI を呼んで標準出力を返す。

    `PYTHONIOENCODING=utf-8` を必ず渡す。絵文字入りのチーム名があるため、
    既定の cp932 のままだと CLI が `illegal multibyte sequence` で exit 1 になる（doc 02 §2）。
    """
    cmd = [kaggle_executable(), *args]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env
    )
    if proc.returncode != 0:
        raise KaggleCommandError(
            f"失敗 (exit {proc.returncode}): {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}"
        )
    return proc.stdout


def call_with_retry(
    runner: Callable[[list[str]], str],
    args: list[str],
    retries: int = 3,
    base_delay: float = 2.0,
) -> str:
    """指数バックオフ付きで呼ぶ（doc 02 §3, NFR-4）。"""
    delay = base_delay
    last: Exception | None = None
    for attempt in range(retries):
        try:
            return runner(args)
        except KaggleCommandError as exc:  # ネットワーク・レート制限の一時障害を想定
            last = exc
            if attempt == retries - 1:
                break
            print(f"  再試行 {attempt + 1}/{retries - 1}（{delay:.1f}秒待機）: {exc}", file=sys.stderr)
            time.sleep(delay)
            delay *= 2
    raise KaggleCommandError(f"再試行しても失敗: {' '.join(args)}") from last


# ---------------------------------------------------------------- CSV パース


def parse_csv_stdout(text: str, first_column: str) -> tuple[list[dict[str, str]], str | None]:
    """CLI の標準出力から CSV を取り出す。

    `leaderboard -s` は CSV の前に `Next Page Token = ...` を出すため、
    `first_column` で始まるヘッダ行を探してそこから読む（doc 02 §2）。
    戻り値は (行のリスト, ページトークン or None)。
    """
    token: str | None = None
    lines = text.splitlines()
    header_index: int | None = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Next Page Token"):
            _, _, value = stripped.partition("=")
            token = value.strip() or None
        if header_index is None and stripped.split(",")[0] == first_column:
            header_index = i
    if header_index is None:
        return [], token
    body = "\n".join(lines[header_index:])
    rows = [row for row in csv.DictReader(io.StringIO(body)) if row.get(first_column)]
    return rows, token


def _to_float(value: str | None) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float("-inf")


def pick_submissions(rows: Iterable[dict[str, str]], count: int) -> list[dict[str, str]]:
    """publicScore が高い順に count 本選ぶ（doc 02 §2）。"""
    return sorted(rows, key=lambda r: _to_float(r.get("publicScore")), reverse=True)[:count]


def select_episodes(rows: Iterable[dict[str, str]], limit: int) -> list[dict[str, str]]:
    """Validation と未完了を除き、新しい順に limit 本選ぶ（doc 02 §3, 03 §5.2）。"""
    usable = [
        r
        for r in rows
        if r.get("type") != VALIDATION_TYPE and r.get("state") == COMPLETED_STATE
    ]
    usable.sort(key=lambda r: r.get("createTime", ""), reverse=True)
    return usable[:limit]


# ---------------------------------------------------------------- manifest


class Manifest:
    """処理済み episodeId の記録。再実行で続きから再開するために使う（doc 02 §3）。"""

    def __init__(self, path: Path):
        self.path = path
        self.data: dict = {"episodes": {}, "teams": {}}
        if path.exists():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self.data.update(loaded)
                    self.data.setdefault("episodes", {})
                    self.data.setdefault("teams", {})
            except ValueError:
                print(f"manifest が壊れているので作り直す: {path}", file=sys.stderr)

    def is_done(self, episode_id: str) -> bool:
        return str(episode_id) in self.data["episodes"]

    def count_for_team(self, team_id: str) -> int:
        """そのチームから既に取得済みのエピソード数（doc 02 §3 の上限は累積で数える）。"""
        return sum(
            1 for info in self.data["episodes"].values() if str(info.get("teamId")) == str(team_id)
        )

    def mark(self, episode_id: str, **info) -> None:
        self.data["episodes"][str(episode_id)] = {"fetched_at": _now(), **info}
        self.save()

    def mark_team(self, team_id: str, **info) -> None:
        self.data["teams"][str(team_id)] = {"fetched_at": _now(), **info}
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- パイプライン


@dataclass
class FetchConfig:
    """doc 02 §5 の設定値。"""

    competition: str = "kaggriculture"
    top_n: int = 50
    submissions_per_team: int = 1
    episodes_per_team: int = 20
    request_interval_sec: float = 1.5
    meta_dir: Path = field(default_factory=lambda: ROOT / "data" / "meta")
    raw_dir: Path = field(default_factory=lambda: ROOT / "data" / "raw")
    digest_dir: Path = field(default_factory=lambda: ROOT / "data" / "digest")
    dry_run: bool = False
    keep_raw: bool = False  # True にすると生リプレイ（1本33MB）を残す
    page_size: int = 200


class FetchPipeline:
    """手順1〜4（doc 02 §2）を順に実行する。"""

    def __init__(self, config: FetchConfig, runner: Callable[[list[str]], str] = run_kaggle):
        self.config = config
        self.runner = runner
        self.manifest = Manifest(config.meta_dir / "manifest.json")

    # -- CLI ラッパ ------------------------------------------------

    def _call(self, args: list[str]) -> str:
        out = call_with_retry(self.runner, args)
        if self.config.request_interval_sec:
            time.sleep(self.config.request_interval_sec)
        return out

    def fetch_leaderboard(self) -> list[dict[str, str]]:
        """手順1：上位 top_n チーム。必要ならページングする。"""
        rows: list[dict[str, str]] = []
        token: str | None = None
        while len(rows) < self.config.top_n:
            args = [
                "competitions", "leaderboard", self.config.competition,
                "-s", "--format", "csv", "--page-size", str(self.config.page_size),
            ]
            if token:
                args += ["--page-token", token]
            page, token = parse_csv_stdout(self._call(args), "teamId")
            if not page:
                break
            rows.extend(page)
            if not token:
                break
        return rows[: self.config.top_n]

    def fetch_submissions(self, team_id: str) -> list[dict[str, str]]:
        """手順2：チームの提出一覧。"""
        out = self._call(["competitions", "team-submissions", str(team_id), "--format", "csv"])
        rows, _ = parse_csv_stdout(out, "id")
        return rows

    def fetch_episodes(self, submission_id: str) -> list[dict[str, str]]:
        """手順3：提出のエピソード一覧。"""
        out = self._call(["competitions", "episodes", str(submission_id), "--format", "csv"])
        rows, _ = parse_csv_stdout(out, "id")
        return rows

    def download_replay(self, episode_id: str) -> Path:
        """手順4：リプレイ本体（1本33MB）。"""
        self.config.raw_dir.mkdir(parents=True, exist_ok=True)
        self._call(["competitions", "replay", str(episode_id), "-p", str(self.config.raw_dir)])
        return self.config.raw_dir / f"episode-{episode_id}-replay.json"

    # -- 実行 ------------------------------------------------------

    def run(self) -> dict:
        cfg = self.config
        cfg.meta_dir.mkdir(parents=True, exist_ok=True)

        teams = self.fetch_leaderboard()
        _write_csv(cfg.meta_dir / "leaderboard.csv", teams)
        print(f"[1] 上位チーム: {len(teams)}件")

        all_submissions: list[dict[str, str]] = []
        all_episodes: list[dict[str, str]] = []
        planned: list[tuple[dict[str, str], dict[str, str]]] = []
        seen: set[str] = set()

        for rank, team in enumerate(teams, start=1):
            team_id = team["teamId"]
            submissions = pick_submissions(self.fetch_submissions(team_id), cfg.submissions_per_team)
            for sub in submissions:
                sub = {**sub, "teamId": team_id, "teamName": team.get("teamName", ""), "rank": str(rank)}
                all_submissions.append(sub)
                episodes = self.fetch_episodes(sub["id"])
                # 上限は累積。再実行のたびに新しいエピソードを足し続けないようにする（doc 02 §3）
                remaining = max(0, cfg.episodes_per_team - self.manifest.count_for_team(team_id))
                for ep in select_episodes(episodes, cfg.episodes_per_team):
                    ep = {**ep, "teamId": team_id, "teamName": team.get("teamName", ""),
                          "submissionId": sub["id"], "rank": str(rank)}
                    all_episodes.append(ep)
                    episode_id = ep["id"]
                    if episode_id in seen or self.manifest.is_done(episode_id):
                        continue
                    if remaining <= 0:
                        continue
                    seen.add(episode_id)
                    remaining -= 1
                    planned.append((ep, team))
            self.manifest.mark_team(team_id, rank=rank, teamName=team.get("teamName", ""))

        _write_csv(cfg.meta_dir / "submissions.csv", all_submissions)
        _write_csv(cfg.meta_dir / "episodes.csv", all_episodes)
        print(f"[2] 提出: {len(all_submissions)}件  [3] エピソード候補: {len(all_episodes)}件")
        print(f"[4] 新規ダウンロード対象: {len(planned)}件")

        team_lookup = _team_lookup(teams)
        downloaded = 0
        digested = 0
        for ep, team in planned:
            episode_id = ep["id"]
            if cfg.dry_run:
                print(f"  (dry-run) {episode_id}  {team.get('teamName')}")
                continue
            path = self.download_replay(episode_id)
            size = path.stat().st_size if path.exists() else 0
            downloaded += 1
            record = {
                "status": "downloaded",
                "teamId": ep["teamId"],
                "teamName": ep["teamName"],
                "submissionId": ep["submissionId"],
                "path": str(path),
                "bytes": size,
            }
            # 取得したら即ダイジェスト化して生データを削除する（doc 02 §3）
            if not cfg.keep_raw:
                digest_path = digest_replay.digest_file(
                    path, cfg.digest_dir, teams=team_lookup, delete_raw=True
                )
                record.update(
                    status="digested",
                    path=str(digest_path),
                    digest_bytes=digest_path.stat().st_size,
                )
                digested += 1
            self.manifest.mark(episode_id, **record)
            suffix = f" -> {record['digest_bytes']:,} bytes" if "digest_bytes" in record else ""
            print(f"  取得 {episode_id} ({size:,} bytes){suffix} {ep['teamName']}")

        return {
            "teams": len(teams),
            "submissions": len(all_submissions),
            "episodes": len(all_episodes),
            "planned": len(planned),
            "downloaded": downloaded,
            "digested": digested,
        }


def _team_lookup(teams: list[dict[str, str]]) -> dict[str, dict]:
    """リーダーボード行から teamName → 順位・teamId を作る（doc 02 §4.2）。"""
    lookup: dict[str, dict] = {}
    for rank, team in enumerate(teams, start=1):
        name = team.get("teamName")
        if not name or name in lookup:
            continue
        try:
            score = float(team.get("score", ""))
        except (TypeError, ValueError):
            score = None
        lookup[name] = {"team_id": team.get("teamId"), "rank": rank, "public_score": score}
    return lookup


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    defaults = FetchConfig()
    parser = argparse.ArgumentParser(description="上位チームのリプレイを取得する（docs/02_data_pipeline.md）")
    parser.add_argument("--competition", default=defaults.competition)
    parser.add_argument("--top-n", type=int, default=defaults.top_n)
    parser.add_argument("--submissions-per-team", type=int, default=defaults.submissions_per_team)
    parser.add_argument("--episodes-per-team", type=int, default=defaults.episodes_per_team)
    parser.add_argument("--interval", type=float, default=defaults.request_interval_sec)
    parser.add_argument("--meta-dir", type=Path, default=defaults.meta_dir)
    parser.add_argument("--raw-dir", type=Path, default=defaults.raw_dir)
    parser.add_argument("--digest-dir", type=Path, default=defaults.digest_dir)
    parser.add_argument("--keep-raw", action="store_true", help="生リプレイを消さずに残す（1本33MB）")
    parser.add_argument("--dry-run", action="store_true", help="ダウンロードせず対象だけ表示する")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    config = FetchConfig(
        competition=args.competition,
        top_n=args.top_n,
        submissions_per_team=args.submissions_per_team,
        episodes_per_team=args.episodes_per_team,
        request_interval_sec=args.interval,
        meta_dir=args.meta_dir,
        raw_dir=args.raw_dir,
        digest_dir=args.digest_dir,
        dry_run=args.dry_run,
        keep_raw=args.keep_raw,
    )
    result = FetchPipeline(config).run()
    print(f"完了: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
