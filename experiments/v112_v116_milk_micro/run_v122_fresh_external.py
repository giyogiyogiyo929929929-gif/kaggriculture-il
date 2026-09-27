from __future__ import annotations
import copy, importlib.util, json, statistics, sys, time, hashlib
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMPION = ROOT / "v112_wheat_lead3_lowdemand.py"
CANDIDATE = ROOT / "v122_wool_lowrisk_front1.py"
SEEDS = list(range(315001, 315005))
OPPONENTS = {
    "v49": REPO / "opponents/v49/main.py",
    "v50": REPO / "opponents/v50/main.py",
    "metav4_v13": REPO / "opponents/metav4_v13/main.py",
    "k256_h2_q_v1": REPO / "opponents/k256_h2_q_v1/main.py",
    "market_rhythm": REPO / "opponents/market_rhythm/main.py",
    "story_of_seasons": REPO / "opponents/story_of_seasons/main.py",
    "thomas_router_93": REPO / "opponents/thomas_router_93/main.py",
    "tetsutani_dpts_b": REPO / "opponents/tetsutani_dpts_b/main.py",
    "jaxa_2802": REPO / "opponents/jaxa_2802/main.py",
    "ready_stock": REPO / "opponents/ready_stock/main.py",
}

def load(path, tag):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(tag, path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec); sys.modules[tag] = mod
    parent = str(path.parent); sys.path.insert(0, parent)
    try: spec.loader.exec_module(mod)
    finally:
        try: sys.path.remove(parent)
        except ValueError: pass
    fn = getattr(mod, "agent", None)
    if not callable(fn):
        for v in vars(mod).values():
            if callable(v): fn = v
    if not callable(fn): raise RuntimeError(f"no callable agent in {path}")
    return mod, fn

def game(a, b, seed, swap=False):
    _, fa = load(a, f"a_{seed}_{swap}_{time.time_ns()}")
    _, fb = load(b, f"b_{seed}_{swap}_{time.time_ns()}")
    env = make("kaggriculture", configuration={"seed": int(seed)}, debug=False)
    env.run([fb, fa] if swap else [fa, fb])
    raw = [x.reward for x in env.state]
    if any(x is None for x in raw):
        raise RuntimeError(f"missing reward seed={seed} swap={swap} rewards={raw}")
    rewards = [float(x) for x in raw]
    ar, br = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    return {"agent_reward": ar, "opponent_reward": br, "delta": ar-br,
            "telemetry": copy.deepcopy(getattr(fa, "telemetry", {}))}

def pair(a, b, seed):
    x=game(a,b,seed,False); y=game(a,b,seed,True)
    return {"seed":seed,"pair_diff":(x["delta"]+y["delta"])/2.0,"games":[x,y]}

def tele(row):
    out={"steps":[]}
    for g in row["games"]:
        d=(g.get("telemetry") or {}).get("wool_lowrisk_front1") or {}
        for k,v in d.items():
            if k=="steps": out["steps"].extend(list(v))
            elif isinstance(v,(int,float)): out[k]=out.get(k,0)+v
    return out

def sign(x): return 1 if x>0 else -1 if x<0 else 0

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    rows=[]
    for name,opp in OPPONENTS.items():
        for seed in SEEDS:
            ch=pair(CHAMPION,opp,seed); ca=pair(CANDIDATE,opp,seed)
            d=ca["pair_diff"]-ch["pair_diff"]
            t=tele(ca)
            rec={"opponent":name,"seed":seed,"champion_pair_diff":ch["pair_diff"],
                 "candidate_pair_diff":ca["pair_diff"],"candidate_minus_champion":d,
                 "champion_outcome":sign(ch["pair_diff"]),"candidate_outcome":sign(ca["pair_diff"]),
                 "outcome_regression":sign(ca["pair_diff"])<sign(ch["pair_diff"]),
                 "outcome_improvement":sign(ca["pair_diff"])>sign(ch["pair_diff"]),
                 "candidate_telemetry":t}
            rows.append(rec)
            print(name,seed,"delta",d,"reorders",t.get("reorders",0),flush=True)
    vals=[r["candidate_minus_champion"] for r in rows]
    active=[r for r in rows if r["candidate_telemetry"].get("reorders",0)>0]
    avals=[r["candidate_minus_champion"] for r in active]
    out={"engine":"kaggle_environments==1.32.7","champion":"v112_wheat_lead3_lowdemand",
         "candidate":"v122_wool_lowrisk_front1","sha256":{"champion":sha(CHAMPION),"candidate":sha(CANDIDATE)},
         "sign":"candidate_minus_champion = candidate - champion","seeds":SEEDS,
         "summary":{"pairs":len(rows),"mean":statistics.mean(vals),"median":statistics.median(vals),
                    "worst":min(vals),"best":max(vals),
                    "outcome_regressions":sum(r["outcome_regression"] for r in rows),
                    "outcome_improvements":sum(r["outcome_improvement"] for r in rows),
                    "active_pairs":len(active),"active_mean":statistics.mean(avals) if avals else 0.0,
                    "active_worst":min(avals) if avals else 0.0,"active_best":max(avals) if avals else 0.0},
         "rows":rows}
    (ROOT/"v122_fresh_external.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print("SUMMARY",json.dumps(out["summary"],indent=2),flush=True)

if __name__=="__main__": main()
