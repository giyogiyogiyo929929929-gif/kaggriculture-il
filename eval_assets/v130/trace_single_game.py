#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED_VERSION = "1.32.7"
BUILTINS = {"starter", "random", "pass"}


def resolve(spec: str) -> str:
    if spec in BUILTINS:
        return spec
    p=Path(spec)
    if p.is_dir(): p=p/"main.py"
    if not p.is_file(): raise FileNotFoundError(spec)
    return str(p)


def compact_obs(obs: dict) -> dict:
    player=int(obs.get("player",0)); farms=obs.get("farms") or [{},{}]
    own=farms[player] if player < len(farms) else {}
    rival=farms[1-player] if 1-player < len(farms) else {}
    market=obs.get("market") or {}; town=obs.get("town") or {}
    raw=json.dumps(obs,sort_keys=True,separators=(",",":"),default=str).encode()
    return {
        "obs_sha256":hashlib.sha256(raw).hexdigest(),
        "own_money":own.get("money"),"rival_money":rival.get("money"),
        "own_products":dict(own.get("products") or own.get("inventory") or {}),
        "rival_products":dict(rival.get("products") or rival.get("inventory") or {}),
        "market_inventory":dict(market.get("inventory") or {}),
        "market_prices":dict(market.get("prices") or {}),
        "shops":list(town.get("unlocked_shops") or []),
    }


def load_target(spec: str, trace: list[dict]):
    from kaggle_environments.agent import get_last_callable
    path=resolve(spec); raw=Path(path).read_text(encoding="utf-8")
    fn=get_last_callable(raw,path=path); call_index=0
    def wrapped(obs,config=None):
        nonlocal call_index
        if obs.get("step") is None: obs["step"]=call_index
        step=int(obs["step"]); call_index+=1
        snap=compact_obs(obs)
        action=fn(obs,config)
        if step>=560:
            gate=None
            try:
                g=fn.__globals__.get("_ADV_LATE_DRAW_GATE")
                if isinstance(g,dict): gate=g.get(int(obs.get("player",0)))
            except Exception: pass
            trace.append({"step":step,"player":int(obs.get("player",0)),"action":action,"late_draw_gate":gate,**snap})
        return action
    return wrapped


def load_plain(spec: str):
    if spec in BUILTINS: return spec
    from kaggle_environments.agent import get_last_callable
    path=resolve(spec); raw=Path(path).read_text(encoding="utf-8")
    fn=get_last_callable(raw,path=path); call_index=0
    def wrapped(obs,config=None):
        nonlocal call_index
        if obs.get("step") is None: obs["step"]=call_index
        call_index+=1
        return fn(obs,config)
    return wrapped


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--target",required=True); ap.add_argument("--opponent",required=True)
    ap.add_argument("--target-seat",type=int,choices=[0,1],required=True)
    ap.add_argument("--seed",type=int,required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    import kaggle_environments
    from kaggle_environments import make
    assert kaggle_environments.__version__==EXPECTED_VERSION
    trace=[]; target=load_target(args.target,trace); opp=load_plain(args.opponent)
    agents=[target,opp] if args.target_seat==0 else [opp,target]
    env=make("kaggriculture",configuration={"episodeSteps":720,"seed":args.seed},debug=False)
    env.run(agents); final=env.steps[-1]
    rewards=[float(final[i].reward or 0.0) for i in range(2)]
    out={"seed":args.seed,"target":args.target,"opponent":args.opponent,"target_seat":args.target_seat,
         "rewards":rewards,"statuses":[str(final[i].status) for i in range(2)],"trace":trace}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
