from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V115_SHA = 'c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2'
V104_SHA = '78519fbec9086be2c78ef9ac0a10d2f39edc19fd17748286131242b9adcc1a9e'
V122_SHA = 'ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1'
V123_SHA = 'a489de893be614667d1700ee92882990200f13bbae0c3eb1a59c9857ca844eca'
V104_BYTES = 1035463

V122_OVERLAY = r'''
# v122 candidate: at step649, delay WHEAT only when a FERTILIZER SELL remains behind it
# in the same initial contiguous SELL block. Preserve all quantities, turn, barriers, and
# relative order of every non-WHEAT order.
_V122_PARENT = agent
_V122_REPORT = {'fires': 0, 'skips_no_fert_after': 0, 'errors': 0}
def agent(observation, configuration=None):
    action = _V122_PARENT(observation, configuration)
    try:
        step = int(observation.get('step', 0)); player = int(observation.get('player', 0))
        if step == 0 and player == 0:
            _V122_REPORT.update(fires=0, skips_no_fert_after=0, errors=0)
        if step != 649:
            return action
        market = [list(o) if isinstance(o, (list, tuple)) else o for o in (action.get('market') or [])]
        end = 0
        while end < len(market) and market[end] and market[end][0] == 'SELL':
            end += 1
        block = market[:end]
        wi = next((i for i,o in enumerate(block) if len(o)>=3 and o[:2]==['SELL','WHEAT']), None)
        if wi is None or wi == end - 1:
            return action
        if not any(len(o)>=3 and o[:2]==['SELL','FERTILIZER'] for o in block[wi+1:]):
            _V122_REPORT['skips_no_fert_after'] += 1
            return action
        wheat = block.pop(wi); block.append(wheat); market[:end] = block
        _V122_REPORT['fires'] += 1
        out = dict(action); out['market'] = market
        return out
    except Exception:
        _V122_REPORT['errors'] += 1
        return action
agent.telemetry = _V122_REPORT
kaggle_submission_agent_v122 = agent
'''

V123_OVERLAY = r'''

# v123 diagnostic only: behavior-preserving step-649 market telemetry on exact v122.
# No action mutation is permitted in this layer.
_V123_PARENT = agent
_V123_REPORT = {
    'calls': 0,
    'step649': [],
    'errors': 0,
}

def _v123_copy_orders(market):
    return [list(o) if isinstance(o, (list, tuple)) else o for o in (market or [])]

def _v123_sell_block(market):
    out = []
    for o in market:
        if not o or not isinstance(o, (list, tuple)) or o[0] != 'SELL':
            break
        out.append(list(o))
    return out

def agent(observation, configuration=None):
    before_fires = int(_V122_REPORT.get('fires', 0))
    action = _V123_PARENT(observation, configuration)
    _V123_REPORT['calls'] += 1
    try:
        step = int(observation.get('step', 0)); player = int(observation.get('player', 0))
        if step == 0 and player == 0:
            _V123_REPORT['step649'].clear(); _V123_REPORT['errors'] = 0
        if step == 649:
            market = _v123_copy_orders(action.get('market') or [])
            block = _v123_sell_block(market)
            own = observation['farms'][player]
            rival = observation['farms'][1-player]
            _V123_REPORT['step649'].append({
                'player': player,
                'v122_fired_this_call': int(_V122_REPORT.get('fires', 0)) > before_fires,
                'market': market,
                'initial_sell_block': block,
                'sell_items': [o[1] for o in block if len(o) >= 2],
                'sell_qty': [int(o[2]) for o in block if len(o) >= 3],
                'market_inventory': dict(observation.get('market', {}).get('inventory', {})),
                'market_prices': dict(observation.get('market', {}).get('prices', {})),
                'own_money': own.get('money'),
                'rival_money': rival.get('money'),
                'shed': dict(observation.get('private', {}).get('shed', {})),
                'shops': list(observation.get('town', {}).get('unlocked_shops', [])),
            })
    except Exception:
        _V123_REPORT['errors'] += 1
    return action

agent.telemetry = _V123_REPORT
kaggle_submission_agent_v123_diag = agent
'''

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('v115'); ap.add_argument('v104'); ap.add_argument('v122'); ap.add_argument('v123')
    a=ap.parse_args()
    b115=Path(a.v115).read_bytes()
    got=sha(b115)
    if got != V115_SHA: raise SystemExit(f'v115 sha mismatch {got}')
    b104=b115[:V104_BYTES]
    got=sha(b104)
    if got != V104_SHA: raise SystemExit(f'v115 prefix is not exact v104: len={len(b104)} sha={got}')
    b122=b104 + V122_OVERLAY.encode('utf-8')
    got=sha(b122)
    if got != V122_SHA: raise SystemExit(f'v122 sha mismatch {got}')
    b123=b122 + V123_OVERLAY.encode('utf-8')
    got=sha(b123)
    if got != V123_SHA: raise SystemExit(f'v123 sha mismatch {got}')
    for path,data in [(a.v104,b104),(a.v122,b122),(a.v123,b123)]: Path(path).write_bytes(data)
    for path in (a.v104,a.v122,a.v123): compile(Path(path).read_text(encoding='utf-8'),path,'exec')
    print('v104',len(b104),V104_SHA); print('v122',len(b122),V122_SHA); print('v123',len(b123),V123_SHA)

if __name__=='__main__': main()
