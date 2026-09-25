from pathlib import Path
import hashlib,sys

EXPECTED_PARENT = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
EXPECTED_OUT = "8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923"
APPEND = b'''\n# ---- v147 candidate: confirmed v111-layer clone before second-pass response ----\n# A strategic clone can share farm/sale quantities without sharing the final v111\n# order-layer. Use a first-pass v111 change as a no-intervention probe; on the next\n# observation, require identical realized cash deltas before enabling the second pass.\n_V147_PARENT = agent\n_V147_STATE = {}\n_V147_REPORT = {'calls':0,'probes':0,'confirmed':0,'rejected':0,'second_pass_changed':0,'errors':0}\n\ndef _v147_state(player, step):\n    st = _V147_STATE.get(player)\n    if st is None or step <= st.get('step', -1):\n        st = _V147_STATE[player] = {'step':-1,'pending':None,'confirmed':False,'rejected':False}\n    st['step'] = step\n    return st\n\ndef agent(observation, configuration=None):\n    step = int(observation.get('step',0)); player = int(observation.get('player',0))\n    if step == 0:\n        _V147_STATE.pop(player, None)\n        for _k in _V147_REPORT: _V147_REPORT[_k] = 0\n    _V147_REPORT['calls'] += 1\n    st = _v147_state(player, step)\n    try:\n        pending = st.get('pending')\n        if pending and pending['step'] == step - 1 and not st['rejected']:\n            farms = observation['farms']\n            own_delta = int(farms[player]['money']) - pending['own_money']\n            rival_delta = int(farms[1-player]['money']) - pending['rival_money']\n            if own_delta == rival_delta:\n                if not st['confirmed']:_V147_REPORT['confirmed'] += 1\n                st['confirmed'] = True\n            else:\n                st['confirmed'] = False; st['rejected'] = True; _V147_REPORT['rejected'] += 1\n        st['pending'] = None\n    except Exception:\n        _V147_REPORT['errors'] += 1\n\n    before_changes = int(_V111_REPORT.get('changed_turns',0))\n    action = _V147_PARENT(observation, configuration)\n    parent_changed = int(_V111_REPORT.get('changed_turns',0)) > before_changes\n    try:\n        if parent_changed and not st['confirmed'] and not st['rejected']:\n            farms = observation['farms']\n            st['pending'] = {'step':step,'own_money':int(farms[player]['money']),'rival_money':int(farms[1-player]['money'])}\n            _V147_REPORT['probes'] += 1\n        if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):\n            before_market = action.get('market') or []\n            candidate = _v111_reorder(observation, action)\n            if candidate.get('market') != before_market:\n                _V147_REPORT['second_pass_changed'] += 1\n                action = candidate\n                race = _RACE_STATE.get(player)\n                if race is not None and race.get('prev_action') is not None and race.get('step') == step:\n                    race['prev_action'] = action\n    except Exception:\n        _V147_REPORT['errors'] += 1\n    return action\nagent.telemetry = _V147_REPORT\nkaggle_submission_agent_v147 = agent\n'''

def main():
    src=Path(sys.argv[1]); out=Path(sys.argv[2])
    raw=src.read_bytes()
    got=hashlib.sha256(raw).hexdigest()
    if got != EXPECTED_PARENT: raise SystemExit(f"parent sha mismatch: {got}")
    out.write_bytes(raw + APPEND)
    sha=hashlib.sha256(out.read_bytes()).hexdigest()
    if sha != EXPECTED_OUT: raise SystemExit(f"v147 sha mismatch: {sha}")
    print(f"v147_sha256={sha}")
    print(f"v147_bytes={out.stat().st_size}")

if __name__ == "__main__": main()
