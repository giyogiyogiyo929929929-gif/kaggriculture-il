from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V104_SHA256='78519fbec9086be2c78ef9ac0a10d2f39edc19fd17748286131242b9adcc1a9e'
V122_SHA256='ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1'
V123_SHA256='a489de893be614667d1700ee92882990200f13bbae0c3eb1a59c9857ca844eca'
V122_OVERLAY="\n# v122 candidate: at step649, delay WHEAT only when a FERTILIZER SELL remains behind it\n# in the same initial contiguous SELL block. Preserve all quantities, turn, barriers, and\n# relative order of every non-WHEAT order.\n_V122_PARENT = agent\n_V122_REPORT = {'fires': 0, 'skips_no_fert_after': 0, 'errors': 0}\ndef agent(observation, configuration=None):\n    action = _V122_PARENT(observation, configuration)\n    try:\n        step = int(observation.get('step', 0)); player = int(observation.get('player', 0))\n        if step == 0 and player == 0:\n            _V122_REPORT.update(fires=0, skips_no_fert_after=0, errors=0)\n        if step != 649:\n            return action\n        market = [list(o) if isinstance(o, (list, tuple)) else o for o in (action.get('market') or [])]\n        end = 0\n        while end < len(market) and market[end] and market[end][0] == 'SELL':\n            end += 1\n        block = market[:end]\n        wi = next((i for i,o in enumerate(block) if len(o)>=3 and o[:2]==['SELL','WHEAT']), None)\n        if wi is None or wi == end - 1:\n            return action\n        if not any(len(o)>=3 and o[:2]==['SELL','FERTILIZER'] for o in block[wi+1:]):\n            _V122_REPORT['skips_no_fert_after'] += 1\n            return action\n        wheat = block.pop(wi); block.append(wheat); market[:end] = block\n        _V122_REPORT['fires'] += 1\n        out = dict(action); out['market'] = market\n        return out\n    except Exception:\n        _V122_REPORT['errors'] += 1\n        return action\nagent.telemetry = _V122_REPORT\nkaggle_submission_agent_v122 = agent\n"
V123_OVERLAY="\n\n# v123 diagnostic only: behavior-preserving step-649 market telemetry on exact v122.\n# No action mutation is permitted in this layer.\n_V123_PARENT = agent\n_V123_REPORT = {\n    'calls': 0,\n    'step649': [],\n    'errors': 0,\n}\n\ndef _v123_copy_orders(market):\n    return [list(o) if isinstance(o, (list, tuple)) else o for o in (market or [])]\n\ndef _v123_sell_block(market):\n    out = []\n    for o in market:\n        if not o or not isinstance(o, (list, tuple)) or o[0] != 'SELL':\n            break\n        out.append(list(o))\n    return out\n\ndef agent(observation, configuration=None):\n    before_fires = int(_V122_REPORT.get('fires', 0))\n    action = _V123_PARENT(observation, configuration)\n    _V123_REPORT['calls'] += 1\n    try:\n        step = int(observation.get('step', 0)); player = int(observation.get('player', 0))\n        if step == 0 and player == 0:\n            _V123_REPORT['step649'].clear(); _V123_REPORT['errors'] = 0\n        if step == 649:\n            market = _v123_copy_orders(action.get('market') or [])\n            block = _v123_sell_block(market)\n            own = observation['farms'][player]\n            rival = observation['farms'][1-player]\n            _V123_REPORT['step649'].append({\n                'player': player,\n                'v122_fired_this_call': int(_V122_REPORT.get('fires', 0)) > before_fires,\n                'market': market,\n                'initial_sell_block': block,\n                'sell_items': [o[1] for o in block if len(o) >= 2],\n                'sell_qty': [int(o[2]) for o in block if len(o) >= 3],\n                'market_inventory': dict(observation.get('market', {}).get('inventory', {})),\n                'market_prices': dict(observation.get('market', {}).get('prices', {})),\n                'own_money': own.get('money'),\n                'rival_money': rival.get('money'),\n                'shed': dict(observation.get('private', {}).get('shed', {})),\n                'shops': list(observation.get('town', {}).get('unlocked_shops', [])),\n            })\n    except Exception:\n        _V123_REPORT['errors'] += 1\n    return action\n\nagent.telemetry = _V123_REPORT\nkaggle_submission_agent_v123_diag = agent\n"

def sha(b: bytes)->str:
    return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('v104'); ap.add_argument('v122'); ap.add_argument('v123')
    a=ap.parse_args()
    b104=Path(a.v104).read_bytes()
    if sha(b104)!=V104_SHA256: raise SystemExit(f'v104 sha mismatch: {sha(b104)}')
    b122=b104+V122_OVERLAY.encode('utf-8')
    if sha(b122)!=V122_SHA256: raise SystemExit(f'v122 sha mismatch: {sha(b122)}')
    b123=b122+V123_OVERLAY.encode('utf-8')
    if sha(b123)!=V123_SHA256: raise SystemExit(f'v123 sha mismatch: {sha(b123)}')
    Path(a.v122).write_bytes(b122); Path(a.v123).write_bytes(b123)
    compile(b122.decode('utf-8'),a.v122,'exec'); compile(b123.decode('utf-8'),a.v123,'exec')
    print(f'v122_sha256={sha(b122)} bytes={len(b122)}')
    print(f'v123_sha256={sha(b123)} bytes={len(b123)}')

if __name__=='__main__': main()
