from pathlib import Path
import sys

OVERLAY = r'''
# ---- v148 candidate: v147 confirmed second-pass + duplicate-SELL safety guard ----
# Telemetry on burned seed 691 showed the only representative seat-reversing
# first divergence occurred when one item had multiple SELL orders in the same
# action. Preserve v147 on unique-item SELL sets, but do not second-pass reorder
# actions containing duplicate SELL item kinds.
_V148_PARENT = agent
_V148_STATE = {}
_V148_REPORT = {
    'calls': 0,
    'probes': 0,
    'confirmed': 0,
    'rejected': 0,
    'duplicate_sell_guard': 0,
    'second_pass_changed': 0,
    'errors': 0,
}

def _v148_state(player, step):
    st = _V148_STATE.get(player)
    if st is None or step <= st.get('step', -1):
        st = _V148_STATE[player] = {'step': -1, 'pending': None, 'confirmed': False, 'rejected': False}
    st['step'] = step
    return st

def _v148_duplicate_sell_item(action):
    seen = set()
    for order in (action.get('market') or []):
        if len(order) >= 3 and order[0] == 'SELL':
            item = order[1]
            if item in seen:
                return True
            seen.add(item)
    return False

def agent(observation, configuration=None):
    step = int(observation.get('step', 0)); player = int(observation.get('player', 0))
    if step == 0:
        _V148_STATE.pop(player, None)
        for _k in _V148_REPORT:
            _V148_REPORT[_k] = 0
    _V148_REPORT['calls'] += 1
    st = _v148_state(player, step)
    try:
        pending = st.get('pending')
        if pending and pending['step'] == step - 1 and not st['rejected']:
            farms = observation['farms']
            own_delta = int(farms[player]['money']) - pending['own_money']
            rival_delta = int(farms[1-player]['money']) - pending['rival_money']
            if own_delta == rival_delta:
                if not st['confirmed']:
                    _V148_REPORT['confirmed'] += 1
                st['confirmed'] = True
            else:
                st['confirmed'] = False
                st['rejected'] = True
                _V148_REPORT['rejected'] += 1
        st['pending'] = None
    except Exception:
        _V148_REPORT['errors'] += 1

    before_changes = int(_V111_REPORT.get('changed_turns', 0))
    action = _V148_PARENT(observation, configuration)
    parent_changed = int(_V111_REPORT.get('changed_turns', 0)) > before_changes
    try:
        if parent_changed and not st['confirmed'] and not st['rejected']:
            farms = observation['farms']
            st['pending'] = {
                'step': step,
                'own_money': int(farms[player]['money']),
                'rival_money': int(farms[1-player]['money']),
            }
            _V148_REPORT['probes'] += 1
        if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):
            if _v148_duplicate_sell_item(action):
                _V148_REPORT['duplicate_sell_guard'] += 1
            else:
                before_market = action.get('market') or []
                candidate = _v111_reorder(observation, action)
                if candidate.get('market') != before_market:
                    _V148_REPORT['second_pass_changed'] += 1
                    action = candidate
                    race = _RACE_STATE.get(player)
                    if race is not None and race.get('prev_action') is not None and race.get('step') == step:
                        race['prev_action'] = action
    except Exception:
        _V148_REPORT['errors'] += 1
    return action

agent.telemetry = _V148_REPORT
kaggle_submission_agent_v148 = agent
'''

if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    data = src.read_bytes() + b'\n' + OVERLAY.lstrip('\n').encode('utf-8')
    dst.write_bytes(data)
