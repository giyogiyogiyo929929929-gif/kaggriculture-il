from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V131_SHA256 = "43bc48f7d44eefce3dd16bb215d6d58801ff6ce0a7dfb920a42d35427b17b1c4"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    return source.replace(old, new)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("champion")
    parser.add_argument("out")
    args = parser.parse_args()

    champion = Path(args.champion)
    source = champion.read_text(encoding="utf-8")
    got = sha256_text(source)
    if got != V115_SHA256:
        raise SystemExit(f"v115 source sha256 mismatch: {got} != {V115_SHA256}")

    source = replace_once(
        source,
        "_ADV_REPORT=dict(adv_turns=0,adv_units=0,adv_errors=0)\n",
        "_ADV_REPORT=dict(adv_turns=0,adv_units=0,adv_errors=0,late_draw_skips=0,late_draw_units=0,late_draw_latches=0)\n_ADV_LATE_DRAW_GATE={}\n",
        "report/state insertion",
    )

    source = replace_once(
        source,
        """    protected=first[1] if _ADV_PROTECT and first is not None and first[0]=='SELL' else None\n    plan=[(t,item,q) for t,item,q in plan if item!=protected]\n    if not plan:return action\n""",
        """    protected=first[1] if _ADV_PROTECT and first is not None and first[0]=='SELL' else None\n    plan=[(t,item,q) for t,item,q in plan if item!=protected]\n    # v131: fail-closed late-game guard.  If a scheduled sale would normally benefit from\n    # an actual town consumption tick before its due turn, preserve the native timing\n    # instead of pulling it up to three turns forward.  The guard only activates after\n    # a large public cash lead is latched at step 577; all other worlds are byte-policy\n    # equivalent to v115 at this layer.\n    if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False):\n        shops=tuple((obs.get('town',{}) or {}).get('unlocked_shops',[]) or [])\n        def _draw_before_due(item,due):\n            for u in range(step,due):\n                if u%24==0:\n                    return True\n                if u%4==0 and any(item in _RACE_SHOPS.get(shop,()) for shop in shops):\n                    return True\n            return False\n        kept=[]\n        for t,item,q in plan:\n            if _draw_before_due(item,t):\n                _ADV_REPORT['late_draw_skips']+=1\n                _ADV_REPORT['late_draw_units']+=q\n            else:\n                kept.append((t,item,q))\n        plan=kept\n    if not plan:return action\n""",
        "town-cross filter insertion",
    )

    source = replace_once(
        source,
        """    try:\n        if int(observation['step'])==0:_ADV_REPORT.update(adv_turns=0,adv_units=0,adv_errors=0)\n        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)])\n""",
        """    try:\n        step=int(observation['step']);player=int(observation['player'])\n        if step==0:\n            _ADV_REPORT.update(adv_turns=0,adv_units=0,adv_errors=0,late_draw_skips=0,late_draw_units=0,late_draw_latches=0)\n            _ADV_LATE_DRAW_GATE.pop(player,None)\n        if step==577:\n            farms=observation['farms']\n            _ADV_LATE_DRAW_GATE[player]=(float(farms[player]['money'])-float(farms[1-player]['money'])>=5000.0)\n            if _ADV_LATE_DRAW_GATE[player]:_ADV_REPORT['late_draw_latches']+=1\n        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)])\n""",
        "late lead latch insertion",
    )

    got = sha256_text(source)
    if got != V131_SHA256:
        raise SystemExit(f"v131 sha256 mismatch: {got} != {V131_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v131_sha256={got}")
    print(f"v131_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
