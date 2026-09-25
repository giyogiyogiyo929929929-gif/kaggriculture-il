from pathlib import Path
import sys

OVERLAY = r'''
# ---- v147 candidate: confirmed v111-layer clone before second-pass response ----
# A strategic clone can share farm/sale quantities without sharing the final v111
# order-layer. Use a first-pass v111 change as a no-intervention probe; on the next
# observation, require identical realized cash deltas before enabling the second pass.
_V147_PARENT = agent
_V147_STATE = {}
_V147_REPORT = {'calls':0,'probes':0,'confirmed':0,'rejected':0,'second_pass_changed':0,'errors':0}

def _v147_state(player, step):
    st = _V147_STATE.get(player)
    if st is None or step <= st.get('step', -1):
        st = _V147_STATE[player] = {'step':-1,'pending':None,'confirmed':False,'rejected':False}
    st['step'] = step
    return st

def agent(observation, configuration=None):
    step = int(observation.get('step',0)); player = int(observation.get('player',0))
    if step == 0:
        _V147_STATE.pop(player, None)
        for _k in _V147_REPORT: _V147_REPORT[_k] = 0
    _V147_REPORT['calls'] += 1
    st = _v147_state(player, step)
    try:
        pending = st.get('pending')
        if pending and pending['step'] == step - 1 and not st['rejected']:
            farms = observation['farms']
            own_delta = int(farms[player]['money']) - pending['own_money']
            rival_delta = int(farms[1-player]['money']) - pending['rival_money']
            if own_delta == rival_delta:
                if not st['confirmed']:_V147_REPORT['confirmed'] += 1
                st['confirmed'] = True
            else:
                st['confirmed'] = False; st['rejected'] = True; _V147_REPORT['rejected'] += 1
        st['pending'] = None
    except Exception:
        _V147_REPORT['errors'] += 1

    before_changes = int(_V111_REPORT.get('changed_turns',0))
    action = _V147_PARENT(observation, configuration)
    parent_changed = int(_V111_REPORT.get('changed_turns',0)) > before_changes
    try:
        if parent_changed and not st['confirmed'] and not st['rejected']:
            farms = observation['farms']
            st['pending'] = {'step':step,'own_money':int(farms[player]['money']),'rival_money':int(farms[1-player]['money'])}
            _V147_REPORT['probes'] += 1
        if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):
            before_market = action.get('market') or []
            candidate = _v111_reorder(observation, action)
            if candidate.get('market') != before_market:
                _V147_REPORT['second_pass_changed'] += 1
                action = candidate
                race = _RACE_STATE.get(player)
                if race is not None and race.get('prev_action') is not None and race.get('step') == step:
                    race['prev_action'] = action
    except Exception:
        _V147_REPORT['errors'] += 1
    return action
agent.telemetry = _V147_REPORT
kaggle_submission_agent_v147 = agent
'''

if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    data = src.read_bytes() + b'\n' + OVERLAY.lstrip('\n').encode('utf-8')
    dst.write_bytes(data)
