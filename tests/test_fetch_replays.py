"""取得パイプラインの受け入れ条件テスト（ネットワークは使わない）。

仕様: docs/02_data_pipeline.md §2, §3, §6
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import fetch_replays as fr  # noqa: E402

LEADERBOARD_CSV = (
    "Next Page Token = CfDJ8OasvsPDUMMY\n"
    "teamId,teamName,submissionDate,score\n"
    "16730612,Unknown Mother-Goose,2026-09-16 02:07:02.966000,3180.4\n"
    "16718819,Majkel1337,2026-09-13 23:03:27.150000,3175.6\n"
    "16640510,SpaTaro,2026-09-16 20:14:02.966000,3148.6\n"
)

SUBMISSIONS_CSV = {
    "16730612": (
        "id,dateSubmitted,publicScore\n"
        "56266899,2026-09-16 02:07:02.967000,3152.4\n"
        "56266758,2026-09-16 01:59:10.273000,3180.4\n"
    ),
    "16718819": (
        "id,dateSubmitted,publicScore\n"
        "56100001,2026-09-13 23:03:27.150000,3175.6\n"
    ),
}

EPISODES_CSV = {
    # 1本は VALIDATION、1本は未完了。どちらも除外されるべき
    "56266758": (
        "id,createTime,endTime,state,type\n"
        "110451333,2026-09-18 13:29:33.405000,2026-09-18 13:35:00.494000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"
        "110450393,2026-09-18 13:25:33.202000,2026-09-18 13:34:10.413000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"
        "110444193,2026-09-18 13:01:33.975000,2026-09-18 13:13:38.004000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"
        "110400001,2026-09-17 10:00:00.000000,2026-09-17 10:10:00.000000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_VALIDATION\n"
        "110400002,2026-09-17 11:00:00.000000,,"
        "EpisodeState.RUNNING,EpisodeType.EPISODE_TYPE_PUBLIC\n"
    ),
    "56100001": (
        "id,createTime,endTime,state,type\n"
        "110451333,2026-09-18 13:29:33.405000,2026-09-18 13:35:00.494000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"  # 手順1のチームとの対戦＝重複
        "110300001,2026-09-15 09:00:00.000000,2026-09-15 09:10:00.000000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"
    ),
}


class FakeKaggle:
    """kaggle CLI の代わり。呼ばれた引数を記録し、決め打ちの CSV を返す。"""

    def __init__(self, raw_dir: Path, episodes: dict[str, str] | None = None):
        self.calls: list[list[str]] = []
        self.raw_dir = raw_dir
        self.episodes = episodes or EPISODES_CSV

    def __call__(self, args: list[str]) -> str:
        self.calls.append(list(args))
        if args[1] == "leaderboard":
            return LEADERBOARD_CSV
        if args[1] == "team-submissions":
            return SUBMISSIONS_CSV[args[2]]
        if args[1] == "episodes":
            return self.episodes[args[2]]
        if args[1] == "replay":
            episode_id = args[2]
            out = Path(args[args.index("-p") + 1])
            out.mkdir(parents=True, exist_ok=True)
            (out / f"episode-{episode_id}-replay.json").write_text(
                json.dumps({"steps": [], "info": {"EpisodeId": int(episode_id)}}), encoding="utf-8"
            )
            return f"Replay downloaded to: {out}"
        raise AssertionError(f"想定外の呼び出し: {args}")

    def downloads(self) -> list[str]:
        return [c[2] for c in self.calls if c[1] == "replay"]


@pytest.fixture
def pipeline(tmp_path):
    fake = FakeKaggle(tmp_path / "raw")
    pipe = fr.FetchPipeline(
        config=fr.FetchConfig(
            competition="kaggriculture",
            top_n=2,
            submissions_per_team=1,
            episodes_per_team=2,
            request_interval_sec=0.0,
            meta_dir=tmp_path / "meta",
            raw_dir=tmp_path / "raw",
            digest_dir=tmp_path / "digest",
        ),
        runner=fake,
    )
    return pipe, fake


def test_parse_csv_skips_page_token():
    """`Next Page Token = ...` 行を読み飛ばしてヘッダから読む（doc 02 §2）。"""
    rows, token = fr.parse_csv_stdout(LEADERBOARD_CSV, "teamId")
    assert len(rows) == 3
    assert rows[0]["teamId"] == "16730612"
    assert rows[0]["teamName"] == "Unknown Mother-Goose"
    assert token == "CfDJ8OasvsPDUMMY"


def test_parse_csv_without_token():
    rows, token = fr.parse_csv_stdout(SUBMISSIONS_CSV["16730612"], "id")
    assert [r["id"] for r in rows] == ["56266899", "56266758"]
    assert token is None


def test_pick_submissions_by_score():
    rows, _ = fr.parse_csv_stdout(SUBMISSIONS_CSV["16730612"], "id")
    picked = fr.pick_submissions(rows, 1)
    assert [r["id"] for r in picked] == ["56266758"]  # publicScore 3180.4 の方


def test_select_episodes_excludes_validation_and_incomplete():
    """Validation Episode と未完了エピソードを除外する（doc 02 §3 / 03 §5.2）。"""
    rows, _ = fr.parse_csv_stdout(EPISODES_CSV["56266758"], "id")
    selected = fr.select_episodes(rows, limit=10)
    ids = [r["id"] for r in selected]
    assert "110400001" not in ids  # VALIDATION
    assert "110400002" not in ids  # RUNNING
    assert ids == ["110451333", "110450393", "110444193"]  # createTime 降順


def test_select_episodes_respects_limit():
    rows, _ = fr.parse_csv_stdout(EPISODES_CSV["56266758"], "id")
    assert len(fr.select_episodes(rows, limit=2)) == 2


def test_run_downloads_and_writes_meta(pipeline):
    """2チーム×2エピソードで手順1〜4が通る（doc 02 §6）。"""
    pipe, fake = pipeline
    result = pipe.run()
    assert result["teams"] == 2
    # チーム1から2本、チーム2から2本（うち1本は重複なので実際は3本）
    assert sorted(fake.downloads()) == ["110300001", "110450393", "110451333"]
    meta = pipe.config.meta_dir
    assert (meta / "leaderboard.csv").exists()
    assert (meta / "submissions.csv").exists()
    assert (meta / "episodes.csv").exists()
    assert (meta / "manifest.json").exists()


def test_run_digests_and_deletes_raw(pipeline):
    """取得したら即ダイジェスト化して生データを削除する（doc 02 §3, §4.3）。"""
    pipe, fake = pipeline
    result = pipe.run()
    assert result["digested"] == 3
    for episode_id in fake.downloads():
        assert (pipe.config.digest_dir / f"{episode_id}.json.gz").exists()
        assert not (pipe.config.raw_dir / f"episode-{episode_id}-replay.json").exists()
    record = pipe.manifest.data["episodes"][fake.downloads()[0]]
    assert record["status"] == "digested"
    assert record["digest_bytes"] > 0


def test_keep_raw_skips_digest(pipeline):
    pipe, fake = pipeline
    pipe.config.keep_raw = True
    result = pipe.run()
    assert result["digested"] == 0
    for episode_id in fake.downloads():
        assert (pipe.config.raw_dir / f"episode-{episode_id}-replay.json").exists()


def test_team_lookup_from_leaderboard():
    rows, _ = fr.parse_csv_stdout(LEADERBOARD_CSV, "teamId")
    lookup = fr._team_lookup(rows)
    assert lookup["Unknown Mother-Goose"] == {
        "team_id": "16730612", "rank": 1, "public_score": 3180.4
    }
    assert lookup["SpaTaro"]["rank"] == 3


def test_rerun_is_idempotent(pipeline):
    """再実行で重複取得せず再開できる（doc 02 §6）。"""
    pipe, fake = pipeline
    pipe.run()
    first = list(fake.downloads())
    pipe.run()
    assert fake.downloads() == first, "2回目でダウンロードが増えている"


def test_resume_after_interrupt(tmp_path):
    """途中で強制終了した状態（manifest に一部だけ記録）から再開する。"""
    meta = tmp_path / "meta"
    meta.mkdir(parents=True)
    (meta / "manifest.json").write_text(
        json.dumps({"episodes": {"110451333": {"status": "downloaded"}}}), encoding="utf-8"
    )
    fake = FakeKaggle(tmp_path / "raw")
    pipe = fr.FetchPipeline(
        config=fr.FetchConfig(
            competition="kaggriculture",
            top_n=2,
            submissions_per_team=1,
            episodes_per_team=2,
            request_interval_sec=0.0,
            meta_dir=meta,
            raw_dir=tmp_path / "raw",
            digest_dir=tmp_path / "digest",
        ),
        runner=fake,
    )
    pipe.run()
    assert "110451333" not in fake.downloads()


def test_retry_with_backoff(tmp_path, monkeypatch):
    """失敗時は指数バックオフで再試行する（doc 02 §3 / NFR-4）。"""
    sleeps: list[float] = []
    monkeypatch.setattr(fr.time, "sleep", lambda s: sleeps.append(s))
    attempts = {"n": 0}

    def flaky(args):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise fr.KaggleCommandError("一時的な失敗")
        return "ok"

    out = fr.call_with_retry(flaky, ["competitions", "episodes", "1"], retries=3, base_delay=1.0)
    assert out == "ok"
    assert attempts["n"] == 3
    assert sleeps == [1.0, 2.0]


def test_dry_run_downloads_nothing(pipeline):
    pipe, fake = pipeline
    pipe.config.dry_run = True
    result = pipe.run()
    assert fake.downloads() == []
    assert result["planned"] == 3


def test_run_kaggle_forces_utf8(monkeypatch):
    """絵文字入りチーム名で CLI が cp932 で落ちるのを防ぐ（doc 02 §2）。"""
    captured = {}

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs.get("env")
        return Result()

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    assert fr.run_kaggle(["competitions", "leaderboard", "kaggriculture"]) == "ok"
    assert captured["env"]["PYTHONIOENCODING"] == "utf-8"
    assert captured["env"]["PYTHONUTF8"] == "1"


def test_per_team_cap_is_cumulative(tmp_path):
    """上限は累積。再実行時に新しいエピソードが増えていても上限を超えて取らない（doc 02 §3）。"""
    config = fr.FetchConfig(
        competition="kaggriculture",
        top_n=1,
        submissions_per_team=1,
        episodes_per_team=2,
        request_interval_sec=0.0,
        meta_dir=tmp_path / "meta",
        raw_dir=tmp_path / "raw",
        digest_dir=tmp_path / "digest",
    )
    first = FakeKaggle(tmp_path / "raw")
    fr.FetchPipeline(config=config, runner=first).run()
    assert len(first.downloads()) == 2

    # 2回目：新しいエピソードが2本増えた状態
    newer = dict(EPISODES_CSV)
    newer["56266758"] = (
        "id,createTime,endTime,state,type\n"
        "110999002,2026-09-19 10:00:00.000000,2026-09-19 10:10:00.000000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"
        "110999001,2026-09-19 09:00:00.000000,2026-09-19 09:10:00.000000,"
        "EpisodeState.COMPLETED,EpisodeType.EPISODE_TYPE_PUBLIC\n"
    ) + EPISODES_CSV["56266758"].split("\n", 1)[1]
    second = FakeKaggle(tmp_path / "raw", episodes=newer)
    fr.FetchPipeline(config=config, runner=second).run()
    assert second.downloads() == [], "上限を超えて追加取得している"
