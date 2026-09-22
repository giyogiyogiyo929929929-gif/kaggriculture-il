"""ADR-0004 第2段の判定と、記録によって行動が変わらないことの検証。

仕様: docs/adr/0004-switch-base-to-v51.md 第2段。
"""
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ns():
    path = ROOT / 'submissions/v13_v51copy/main.py'
    namespace = {}
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), namespace)
    return namespace


def obs(step):
    return {'step': step, 'player': 0, 'farms': [
        {'money': 100, 'tiles': [[None]], 'farmer': [0, 0]},
        {'money': 150, 'tiles': [[None]], 'farmer': [0, 0]},
    ]}


def test_original_and_entry(ns):
    assert (ROOT / 'submissions/v13_v51copy/main.py').read_bytes().startswith(
        (ROOT / 'opponents/v51/main.py').read_bytes())
    assert [v for v in ns.values() if callable(v)][-1].__name__ == '_kil_safe_agent'
    assert ns['_KIL_INNER_AGENT'] is ns['_kil_c_agent']
    assert ns['_KIL_C_INNER'].__name__ == '_e350_agent'


@pytest.mark.parametrize('difference', ['none', 'weed', 'money', 'farm'])
def test_detection_and_action_passthrough(ns, difference):
    sentinel = {'farmer': ['PASS'], 'hands': [], 'market': []}
    ns['_KIL_C_INNER'] = lambda observation, configuration=None: sentinel
    for step in range(180):
        observation = obs(step)
        if step == 120:
            if difference == 'weed':
                observation['farms'][1]['tiles'] = [[{'kind': 'WEED'}]]
            elif difference == 'money':
                observation['farms'][1]['money'] += 1
            elif difference == 'farm':
                observation['farms'][1]['farmer'] = [1, 0]
        before = deepcopy(observation)
        assert ns['_kil_safe_agent'](observation) is sentinel
        assert observation == before
    expected = difference in ('none', 'weed')
    assert ns['_KIL_C_REPORT'] == {
        'copy_games': int(expected), 'copy_turns': 13 if expected else 0, 'c_errors': 0}
    ns['_kil_safe_agent'](obs(0))
    assert ns['_KIL_C_REPORT'] == {'copy_games': 0, 'copy_turns': 0, 'c_errors': 0}


def test_detector_error_still_calls_inner(ns):
    sentinel = {'farmer': ['PASS'], 'hands': [], 'market': []}
    ns['_KIL_C_INNER'] = lambda observation, configuration=None: sentinel
    assert ns['_kil_safe_agent']({}) is sentinel
    assert ns['_KIL_C_REPORT']['c_errors'] == 1
