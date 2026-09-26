from pathlib import Path
import sys

OVERLAY = r'''
# ---- v149 candidate: v147 confirmed second-pass with late-game safety guard ----
# v147's only observed negative single-seat leg first diverged at step 673.
# Preserve the confirmed second-pass earlier in the game, but disable it from
# step 648 onward (final 72 turns / final 3 days) to avoid late seat-sensitive
# order perturbations when little time remains for market-state recovery.
_V149_PARENT = agent
_V149_STATE = {}
_V149_REPORT = {'calls':0,'probes':0,'confirmed':0,'rejected':0,'late_guard':0,'second_pass_changed':0,'errors':0}

def _v149_state(player, step):
    st = _V149_STATE.get(player)
    if st is None or step <= st.get('step', -1):
        st = _V149_STATE[player] = {'step':-1,'pending':None,'confirmed':False,'rejected':False}
    st['step'] = step
    return st

def agent(observation, configuration=None):
    step = int(observation.get('step',0)); player = int(observation.get('player',0))
    if step == 0:
        _V149_STATE.pop(player, None)
        for _k in _V149_REPORT: _V149_REPORT[_k] = 0
    _V149_REPORT['calls'] += 1
    st = _v149_state(player, step)
    try:
        pending = st.get('pending')
        if pending and pending['step'] == step - 1 and not st['rejected']:
            farms = observation['farms']
            own_delta = int(farms[player]['money']) - pending['own_money']
            rival_delta = int(farms[1-player]['money']) - pending['rival_money']
            if own_delta == rival_delta:
                if not st['confirmed']:
                    _V149_REPORT['confirmed'] += 1
                st['confirmed'] = True
            else:
                st['confirmed'] = False
                st['rejected'] = True
                _V149_REPORT['rejected'] += 1
        st['pending'] = None
    except Exception:
        _V149_REPORT['errors'] += 1

    before_changes = int(_V111_REPORT.get('changed_turns',0))
    action = _V149_PARENT(observation, configuration)
    parent_changed = int(_V111_REPORT.get('changed_turns',0)) > before_changes
    try:
        if parent_changed and not st['confirmed'] and not st['rejected']:
            farms = observation['farms']
            st['pending'] = {'step':step,'own_money':int(farms[player]['money']),'rival_money':int(farms[1-player]['money'])}
            _V149_REPORT['probes'] += 1
        if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):
            if step >= 648:
                _V149_REPORT['late_guard'] += 1
            else:
                before_market = action.get('market') or []
                candidate = _v111_reorder(observation, action)
                if candidate.get('market') != before_market:
                    _V149_REPORT['second_pass_changed'] += 1
                    action = candidate
                    race = _RACE_STATE.get(player)
                    if race is not None and race.get('prev_action') is not None and race.get('step') == step:
                        race['prev_action'] = action
    except Exception:
        _V149_REPORT['errors'] += 1
    return action

agent.telemetry = _V149_REPORT
kaggle_submission_agent_v149 = agent
'''

if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    dst.write_bytes(src.read_bytes() + b'\n' + OVERLAY.lstrip('\n').encode('utf-8'))
