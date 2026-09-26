from pathlib import Path
import hashlib
import sys

PARENT_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"

OVERLAY = r'''
# ---- v150 candidate: v147 confirmation mechanism with pre-reorder duplicate SELL guard ----
# Built directly on exact formal v115. The duplicate-item check is placed immediately
# before the confirmed second-pass _v111_reorder so the dangerous reorder cannot occur.
_V150_PARENT = agent
_V150_STATE = {}
_V150_REPORT = {
    'calls': 0,
    'probes': 0,
    'confirmed': 0,
    'rejected': 0,
    'second_pass_changed': 0,
    'duplicate_sell_guard_skips': 0,
    'errors': 0,
}

def _v150_has_duplicate_sell_items(action):
    market = action.get('market') or []
    sell_items = []
    for order in market:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and order[0] == 'SELL':
            sell_items.append(order[1])
    return len(sell_items) != len(set(sell_items))

def _v150_state(player, step):
    st = _V150_STATE.get(player)
    if st is None or step <= st.get('step', -1):
        st = _V150_STATE[player] = {
            'step': -1,
            'pending': None,
            'confirmed': False,
            'rejected': False,
        }
    st['step'] = step
    return st

def agent(observation, configuration=None):
    step = int(observation.get('step', 0))
    player = int(observation.get('player', 0))
    if step == 0:
        _V150_STATE.pop(player, None)
        for key in _V150_REPORT:
            _V150_REPORT[key] = 0
    _V150_REPORT['calls'] += 1
    st = _v150_state(player, step)

    try:
        pending = st.get('pending')
        if pending and pending['step'] == step - 1 and not st['rejected']:
            farms = observation['farms']
            own_delta = int(farms[player]['money']) - pending['own_money']
            rival_delta = int(farms[1-player]['money']) - pending['rival_money']
            if own_delta == rival_delta:
                if not st['confirmed']:
                    _V150_REPORT['confirmed'] += 1
                st['confirmed'] = True
            else:
                st['confirmed'] = False
                st['rejected'] = True
                _V150_REPORT['rejected'] += 1
        st['pending'] = None
    except Exception:
        _V150_REPORT['errors'] += 1

    before_changes = int(_V111_REPORT.get('changed_turns', 0))
    action = _V150_PARENT(observation, configuration)
    parent_changed = int(_V111_REPORT.get('changed_turns', 0)) > before_changes

    try:
        if parent_changed and not st['confirmed'] and not st['rejected']:
            farms = observation['farms']
            st['pending'] = {
                'step': step,
                'own_money': int(farms[player]['money']),
                'rival_money': int(farms[1-player]['money']),
            }
            _V150_REPORT['probes'] += 1

        if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):
            if _v150_has_duplicate_sell_items(action):
                _V150_REPORT['duplicate_sell_guard_skips'] += 1
            else:
                before_market = action.get('market') or []
                candidate = _v111_reorder(observation, action)
                if candidate.get('market') != before_market:
                    _V150_REPORT['second_pass_changed'] += 1
                    action = candidate
                    race = _RACE_STATE.get(player)
                    if race is not None and race.get('prev_action') is not None and race.get('step') == step:
                        race['prev_action'] = action
    except Exception:
        _V150_REPORT['errors'] += 1
    return action

agent.telemetry = _V150_REPORT
kaggle_submission_agent_v150 = agent
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    got = sha256(src)
    if got != PARENT_SHA256:
        raise SystemExit(f"v115 parent sha256 mismatch: {got} != {PARENT_SHA256}")
    dst.write_bytes(src.read_bytes() + b'\n' + OVERLAY.lstrip('\n').encode('utf-8'))
    compile(dst.read_text(encoding='utf-8'), str(dst), 'exec')
    print(f"v150_sha256={sha256(dst)}")
    print(f"v150_bytes={dst.stat().st_size}")
