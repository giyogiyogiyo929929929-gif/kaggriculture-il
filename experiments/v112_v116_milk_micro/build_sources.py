from pathlib import Path
import base64,zlib,hashlib
root=Path(__file__).resolve().parent
def parts(prefix):
    return ''.join(x.read_text() for x in sorted(root.glob(prefix+'.part*')))
a=zlib.decompress(base64.b85decode(parts('v110b'))).decode()
OLD='# v110b_wheat_late_batch_lead2: selective 2-turn WHEAT lead ablation on top of v105.\n_V110_PARENT = agent\n_V110_STATE = {0: {"due_step": -1, "due": 0}, 1: {"due_step": -1, "due": 0}}\n_V110_REPORT = {"lead1_shifts": 0, "lead2_shifts": 0, "units": 0, "demand_blocks": 0, "errors": 0}\n\ndef _v110_planned_wheat(target):\n    if target >= len(_ACTIONS): return 0\n    return sum(max(0, int(o[2])) for o in (_ACTIONS[target].get("market") or []) if len(o)>=3 and o[0]=="SELL" and o[1]=="WHEAT")\n\ndef _v110_wheat_demand_now(obs, step):\n    if step % 24 == 0: return True\n    if step % 4 != 0: return False\n    shops=list(_get(_get(obs,"town",{}) or {},"unlocked_shops",[]) or [])\n    return any("WHEAT" in _SHOP_PRODUCTS.get(shop,()) for shop in shops)\n\ndef _v110_lead(obs, step):\n    target2=step+2\n    if (target2 >= 300) and _v110_planned_wheat(target2)>0 and not _v110_wheat_demand_now(obs,step) and not _v110_wheat_demand_now(obs,step+1):\n        return 2\n    return 1\n'
NEW='# v112_wheat_lead3_lowdemand: allow a 3-turn late-batch WHEAT lead only when\n# public town composition has at most 3 WHEAT-demanding unlocked shops; otherwise\n# retain v110b\'s 2-turn late-batch lead. Early micro trades remain lead1.\n_V110_PARENT = agent\n_V110_STATE = {0: {"due_step": -1, "due": 0}, 1: {"due_step": -1, "due": 0}}\n_V110_REPORT = {"lead1_shifts": 0, "lead2_shifts": 0, "lead3_shifts": 0, "units": 0, "demand_blocks": 0, "errors": 0}\n\ndef _v110_planned_wheat(target):\n    if target >= len(_ACTIONS): return 0\n    return sum(max(0, int(o[2])) for o in (_ACTIONS[target].get("market") or []) if len(o)>=3 and o[0]=="SELL" and o[1]=="WHEAT")\n\ndef _v110_wheat_demand_now(obs, step):\n    if step % 24 == 0: return True\n    if step % 4 != 0: return False\n    shops=list(_get(_get(obs,"town",{}) or {},"unlocked_shops",[]) or [])\n    return any("WHEAT" in _SHOP_PRODUCTS.get(shop,()) for shop in shops)\n\ndef _v110_wheat_demand_shop_count(obs):\n    shops=list(_get(_get(obs,"town",{}) or {},"unlocked_shops",[]) or [])\n    return sum(1 for shop in shops if "WHEAT" in _SHOP_PRODUCTS.get(shop,()))\n\ndef _v110_lead(obs, step):\n    target3=step+3\n    if (_v110_wheat_demand_shop_count(obs) <= 3 and target3 >= 300 and\n            _v110_planned_wheat(target3)>0 and\n            all(not _v110_wheat_demand_now(obs,step+k) for k in range(3))):\n        return 3\n    target2=step+2\n    if (target2 >= 300) and _v110_planned_wheat(target2)>0 and not _v110_wheat_demand_now(obs,step) and not _v110_wheat_demand_now(obs,step+1):\n        return 2\n    return 1\n'
assert a.count(OLD)==1
b=a.replace(OLD,NEW,1)
b=b.replace('_V110_REPORT["lead2_shifts" if lead==2 else "lead1_shifts"]+=1; _V110_REPORT["units"]+=target_q','_V110_REPORT["lead3_shifts" if lead==3 else "lead2_shifts" if lead==2 else "lead1_shifts"]+=1; _V110_REPORT["units"]+=target_q',1)
b=b.replace('agent.__version__="v110b_wheat_late_batch_lead2"','agent.__version__="v112_wheat_lead3_lowdemand"',1)
c=b+zlib.decompress(base64.b85decode(parts('suffix'))).decode()
d=b+zlib.decompress(base64.b85decode(parts('v117_suffix'))).decode()
entries=[
 ('v110b_wheat_late_batch_lead2.py',a,'c783859b141886ea5bd78e728ea907407d12ac4d8ded08e604c28d97f46a7d0b'),
 ('v112_wheat_lead3_lowdemand.py',b,'1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771'),
 ('v116_milk_micro_lead1.py',c,'7a040533a8086b19435a9a0df592d5189d301c3fb457410adf7291314577fc1c'),
 ('v117_wheat_post_town_delay1.py',d,None),
]
for name,text,sha in entries:
 p=root/name; p.write_text(text); got=hashlib.sha256(p.read_bytes()).hexdigest()
 if sha is not None: assert got==sha,(name,got,sha)
 print(name,got)
