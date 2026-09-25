#!/usr/bin/env python3
from __future__ import annotations
import runpy
from pathlib import Path
from types import SimpleNamespace

ITEMS = ('CARROT','TOMATO','STRAWBERRY','MELON','EGG','MILK','WOOL')


def load(path: str, name: str):
    g = runpy.run_path(path, run_name=name)
    return g


def configure_race(fn):
    gl = fn.__globals__
    routes = {0: [{'market': []} for _ in range(719)], 2: [{'market': []} for _ in range(719)]}
    routes[0][110] = {'market': [['SELL', 'MILK', 1]]}
    gl['_IMPL'] = SimpleNamespace(chassis=SimpleNamespace(players={0: {'route': 0}}, routes=routes))
    gl['_race_town'] = lambda step, shops: {}


def obs(milk_inventory: int):
    inv = {item: 10000 for item in ITEMS}
    inv['MILK'] = milk_inventory
    return {'step': 101, 'player': 0, 'market': {'inventory': inv}}


def prev_state():
    inv = {item: 10000 for item in ITEMS}
    prices = {item: 100 for item in ITEMS}
    return {
        'prev': {
            'step': 100,
            'inventory': inv,
            'prices': prices,
            'shops': [],
            'view': SimpleNamespace(shed={'MILK': 5}),
        }
    }


def main() -> int:
    root = Path('eval_agents/v97')
    g96 = load(str(root/'v96_champion_lead11_milkshops2.py'), '__v96_synthetic__')
    g97 = load(str(root/'v97_candidate_actual_trade_race.py'), '__v97_synthetic__')

    s96 = prev_state(); s96['prev_action'] = {'market': []}
    configure_race(g96['_race_lost'])
    assert g96['_race_lost'](obs(10005), s96) is True, 'v96 false rival attribution not reproduced'

    s97 = prev_state(); s97['prev_actual_sales'] = {'MILK': 5}
    configure_race(g97['_race_lost'])
    assert g97['_race_lost'](obs(10005), s97) is False, 'v97 failed to filter own-only sale'

    s97m = prev_state(); s97m['prev_actual_sales'] = {'MILK': 5}
    configure_race(g97['_race_lost'])
    assert g97['_race_lost'](obs(10008), s97m) is True, 'v97 suppressed genuine rival sale'

    gl = g97['_v97_actual_sales'].__globals__
    gl['FarmView'] = lambda observation: None
    gl['projected_shed'] = lambda action, view: {'MILK': 5}
    action = {'market': [['SELL','MILK',4], ['SELL','MILK',4]]}
    assert g97['_v97_actual_sales']({}, action) == {'MILK': 5}

    print('synthetic_v97: PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
