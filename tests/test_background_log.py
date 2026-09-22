# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("background_log", ROOT / "scripts/background_log.py")
background_log = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(background_log)


def test_append_event_has_time_name_pid_and_detail(tmp_path):
    path = tmp_path / "background.log"
    line = background_log.append_event("started", "sample runner", 12345, "job=x", path)
    assert "JST | STARTED | sample runner | pid: 12345 | job=x" in line
    assert path.read_text(encoding="utf-8") == line + "\n"


def test_append_event_appends_instead_of_overwriting(tmp_path):
    path = tmp_path / "background.log"
    background_log.append_event("STARTED", "one", 1, log_path=path)
    background_log.append_event("STOPPED", "one", 1, log_path=path)
    text = path.read_text(encoding="utf-8")
    assert text.count("\n") == 2
    assert "STARTED" in text and "STOPPED" in text
