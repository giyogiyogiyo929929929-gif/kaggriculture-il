# -*- coding: utf-8 -*-
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service = load("recent_notebook_service", "scripts/analysis/recent_notebook_service.py")
watcher = load("watch_recent_notebook_service", "scripts/analysis/watch_recent_notebook_service.py")


def test_parse_real_kaggle_list_shape():
    rows = service.parse_kernel_list(
        '[{"ref":"owner/slug","title":"A","lastRunTime":"2026-09-22T01:02:03"}]'
    )
    assert rows[0]["ref"] == "owner/slug"
    assert service.version_key(rows[0]) == "owner/slug@2026-09-22T01:02:03"


def test_parse_wrapped_future_shape_and_noise():
    rows = service.parse_kernel_list('notice\n{"kernels":[{"ref":"a/b"}]}')
    assert rows == [{"ref": "a/b"}]


def test_safe_name_removes_path_characters():
    assert service.safe_name("owner/slug:time") == "owner_slug_time"


def test_strict_audit_allows_plain_agent(tmp_path):
    path = tmp_path / "main.py"
    path.write_text("def agent(obs, config):\n    return []\n", encoding="utf-8")
    assert service.strict_static_audit(path) == []


def test_strict_audit_rejects_process_launch(tmp_path):
    path = tmp_path / "main.py"
    path.write_text("import subprocess\nsubprocess.Popen(['x'])\n", encoding="utf-8")
    problems = service.strict_static_audit(path)
    assert problems


def test_watcher_accepts_sleep_until_next_poll():
    future = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    state, runner = watcher.health({"state": "sleeping", "next_poll_at": future}, 60)
    assert (state, runner) == ("healthy", "sleeping")


def test_watcher_reports_terminal():
    assert watcher.health({"state": "stopped"}, 60) == ("runner_terminal", "stopped")
