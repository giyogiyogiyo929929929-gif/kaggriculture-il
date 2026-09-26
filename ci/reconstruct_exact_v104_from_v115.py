from __future__ import annotations
import argparse, hashlib
from pathlib import Path

BASE_SHA256 = 'c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2'
TARGET_SHA256 = '78519fbec9086be2c78ef9ac0a10d2f39edc19fd17748286131242b9adcc1a9e'

MODS = [(3444, 3445, ['    base_h=_R37_HORIZONS.get(player,2)\n', '    if h<=base_h:return _RACE_ORIG_RESERVE(obs,action)\n', '    # v104-branch96: mirror EGG uses a 20-turn reservation only while the public EGG market is scarce; every other item keeps v96 horizon.\n', '    if h!=_RACE_HORIZON_MIRROR:\n']), (3450, 3451, ["    step=int(obs['step'])\n", '    if not 216<=step<696:return action\n', '    native=_IMPL.chassis.players[player]\n', "    tape=_IMPL.chassis.routes[native['route']]\n", "    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]\n", '    view=FarmView(obs)\n', "    if any(len(c)>1 and c[0]=='PLACE' and c[1] in ANIMAL_STRUCTURE\n", '           and view.inv(i).get(c[1],0)>0 for i,c in enumerate(commands[:len(view.positions)])):\n', '        return action\n', '    stock=projected_shed(action,view)\n', "    market=action.get('market',[])\n", "    blocked={o[1] for o in market if len(o)>1 and o[0] in ('SELL','BUY_PRODUCT')}\n", "    blocked.update(c[1] for c in commands if len(c)>1 and c[0]=='PICKUP')\n", "    blocked.update(c[1] for queue in native['pending'].values() for pos,c in queue\n", "                   if len(c)>1 and c[0]=='PICKUP')\n", "    debts=native['sell_state'].setdefault('r36_debts',{})\n", '    block_end=(step//72+1)*72-1\n', '    for item in PRODUCTS:\n', "        if item in ('WHEAT','FERTILIZER') or item in blocked or view.prices.get(item,0)<2:continue\n", '        available=max(0,int(stock.get(item,0)))\n', '        if not available or len(market)>=10:continue\n', '        # v104h20-branch96: shorten EGG reservation only while the public EGG market is scarce.\n', "        # Once inventory reaches the engine's I0=10000 reference level, retain v96's 24-turn mirror horizon.\n", "        egg_inventory=int(obs['market']['inventory'].get('EGG',10000))\n", "        item_h=20 if item=='EGG' and egg_inventory<10000 else h\n", '        end=min(695,step+item_h,block_end)\n', '        if end<=step:continue\n', '        reservations=[]\n', '        for due_step in range(step+1,end+1):\n', '            future=tape[due_step]\n', "            work=[future.get('farmer') or ['PASS'],*(future.get('hands') or [])]\n", "            if any(len(c)>1 and c[:2]==['PICKUP',item] for c in work):break\n", "            if any(len(o)>1 and o[:2]==['BUY_PRODUCT',item] for o in future.get('market',[])):break\n", "            planned=sum(max(0,int(o[2])) for o in future.get('market',[]) if len(o)>=3 and o[:2]==['SELL',item])\n", '            amount=min(available,max(0,planned-debts.get(due_step,{}).get(item,0)))\n', '            if amount:\n', '                reservations.append((due_step,amount));available-=amount\n', '            if not available:break\n', '        qty=sum(q for _,q in reservations)\n', '        if qty:\n', "            market.append(['SELL',item,qty])\n", '            for due,q in reservations:\n', '                debt=debts.setdefault(due,{})\n', '                debt[item]=debt.get(item,0)+q\n', "            _R36_SALE_REPORT['sale_reserved_units']+=qty\n", "            _R36_SALE_REPORT['sale_reservations']+=1\n", '    return action\n']), (3520, 3523, ["                    market=[['BUY_PRODUCT','WHEAT',_OPEN_ATTACK]]+market;_OPEN_REPORT['open_attack']=1\n"]), (3524, 3524, ["        elif standard and step==2 and _OPEN_REPORT.get('open_attack'):\n", "            action=dict(action,market=[['SELL','WHEAT',_OPEN_ATTACK]]+[list(o) for o in action.get('market',[])][:9]);_OPEN_REPORT['open_turns']+=1\n"]), (4761, 4762, ['_OR2_SLOT_MARGIN = 20.0   # v13\n']), (6347, 6347, ['        if item == "MILK":\n', '            _milk_shops = sum(shop in ("PIZZA_SHOP","ICE_CREAM_SHOP","SMOOTHIE_SHOP")\n', '                              for shop in (obs.get("town") or {}).get("unlocked_shops", []))\n', '            if _milk_shops < 2:\n', '                continue\n']), (6454, 6455, ['_KIL_V52_LEAD = 11\n']), (6537, 6537, ['        if item == "MILK":\n', '            _milk_shops = sum(shop in ("PIZZA_SHOP","ICE_CREAM_SHOP","SMOOTHIE_SHOP")\n', '                              for shop in (observation.get("town") or {}).get("unlocked_shops", []))\n', '            if _milk_shops < 2:\n', '                continue\n']), (6999, 7313, [])]

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source'); ap.add_argument('output')
    a=ap.parse_args()
    src=Path(a.source); dst=Path(a.output)
    raw=src.read_bytes()
    got=sha256(raw)
    if got != BASE_SHA256:
        raise SystemExit(f'v115 sha mismatch: {got}')
    lines=raw.decode('utf-8').splitlines(keepends=True)
    for i1,i2,repl in reversed(MODS):
        lines[i1:i2]=repl
    out=''.join(lines).encode('utf-8')
    got=sha256(out)
    if got != TARGET_SHA256:
        raise SystemExit(f'v104 sha mismatch: {got}')
    dst.write_bytes(out)
    compile(out.decode('utf-8'),str(dst),'exec')
    print(f'v104_sha256={got}')
    print(f'v104_bytes={len(out)}')

if __name__=='__main__':
    main()
