from pathlib import Path
import hashlib, sys

PARENT_SHA256 = 'ae4c0f5a9afabf2e6d668cf0571b41bfe9a52a9179b499a71aeb6b7508ace8f1'
OVERLAY = r'''

# v123 diagnostic only: behavior-preserving step-649 market telemetry on exact v122.
# No action mutation is permitted in this layer.
_V123_PARENT = agent
_V123_REPORT = {'calls': 0, 'step649': [], 'errors': 0}

def _v123_copy_orders(market):
    return [list(o) if isinstance(o, (list, tuple)) else o for o in (market or [])]

def _v123_sell_block(market):
    out = []
    for o in market:
        if not o or not isinstance(o, (list, tuple)) or o[0] != 'SELL': break
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
            own = observation['farms'][player]; rival = observation['farms'][1-player]
            _V123_REPORT['step649'].append({
                'player': player,
                'v122_fired_this_call': int(_V122_REPORT.get('fires', 0)) > before_fires,
                'market': market,
                'initial_sell_block': block,
                'sell_items': [o[1] for o in block if len(o) >= 2],
                'sell_qty': [int(o[2]) for o in block if len(o) >= 3],
                'market_inventory': dict(observation.get('market', {}).get('inventory', {})),
                'market_prices': dict(observation.get('market', {}).get('prices', {})),
                'own_money': own.get('money'), 'rival_money': rival.get('money'),
                'shed': dict(observation.get('private', {}).get('shed', {})),
                'shops': list(observation.get('town', {}).get('unlocked_shops', [])),
            })
    except Exception:
        _V123_REPORT['errors'] += 1
    return action

agent.telemetry = _V123_REPORT
kaggle_submission_agent_v123_diag = agent
'''

def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if __name__ == '__main__':
    src, dst = map(Path, sys.argv[1:3])
    got = sha256(src)
    if got != PARENT_SHA256: raise SystemExit(f'v122 parent sha mismatch: {got}')
    dst.write_bytes(src.read_bytes() + OVERLAY.encode('utf-8'))
    compile(dst.read_text(encoding='utf-8'), str(dst), 'exec')
    print('parent_sha256', got)
    print('candidate_sha256', sha256(dst))
