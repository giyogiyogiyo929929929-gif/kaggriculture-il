$ErrorActionPreference='Stop'
Set-Location (Resolve-Path "$PSScriptRoot\..")

$gitUsr='C:\Program Files\Git\usr\bin'
if (!(Test-Path (Join-Path $gitUsr 'patch.exe'))) { throw 'Git for Windows patch.exe not found' }
$env:Path="$gitUsr;$env:Path"

python -m pip install --no-deps "kaggle-environments==1.32.7"
python -m pip install jsonschema requests
python -c "import kaggle_environments; assert kaggle_environments.__version__ == '1.32.7'"

Remove-Item -Recurse -Force tmp\sealed2_local,results\sealed2_local -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path tmp\sealed2_local,results\sealed2_local,results\sealed2_local\transition | Out-Null
Copy-Item submissions\v27_orderbook_layer_d\main.py tmp\sealed2_local\main.py

@'
from pathlib import Path
for name in ('tmp/sealed2_local/main.py','ci/v76.patch'):
    p=Path(name); p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
'@ | python -

Push-Location tmp\sealed2_local
patch --binary --batch -p3 -i ..\..\ci\v76.patch
if ($LASTEXITCODE -ne 0) { throw 'v76 patch failed' }
Pop-Location

@'
from pathlib import Path
p=Path('tmp/sealed2_local/main.py')
p.write_bytes(p.read_bytes()+b'\n# Force Kaggle-compatible last-callable selection.\nkaggle_submission_agent_v77 = agent\n')
'@ | python -
Move-Item tmp\sealed2_local\main.py tmp\sealed2_local\v77.py

python ci\reconstruct_exact_v115.py tmp\sealed2_local\v77.py tmp\sealed2_local\v115.py
python ci\build_v147_confirmed_v111_clone.py tmp\sealed2_local\v115.py tmp\sealed2_local\v147.py
python ci\build_v153_v147_dense_self_exposure_guard.py tmp\sealed2_local\v147.py tmp\sealed2_local\v153.py
python -m py_compile tmp\sealed2_local\v115.py tmp\sealed2_local\v147.py tmp\sealed2_local\v153.py

@'
import hashlib
from pathlib import Path
exp={
 'tmp/sealed2_local/v115.py':'c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2',
 'tmp/sealed2_local/v147.py':'8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923',
 'tmp/sealed2_local/v153.py':'128836e8e945d9b5b8c6776dc68cd45f4c21775713ebd3bd50655cd2f711ebfd',
}
for p,w in exp.items():
    g=hashlib.sha256(Path(p).read_bytes()).hexdigest()
    print(p,g)
    assert g==w,(p,g,w)
'@ | python -

@'
import json,math,statistics,time
from pathlib import Path
from scripts.eval import evaluate
seeds=[961200427,1307503965,1065712661,1202442902,949799007,1206911468,1103449975,1059124859,911799718,1207510134,1366430876,1251623999]
rows=[]; games=[]; t0=time.perf_counter()
for seed in seeds:
    s=evaluate('tmp/sealed2_local/v153.py','tmp/sealed2_local/v147.py',pairs=1,jobs=1,seed_start=seed)
    ds=[]
    for g in sorted(s['matches_detail'],key=lambda x:bool(x['swap'])):
        d=float(g['money'][0])-float(g['money'][1]); ds.append(d)
        games.append({'seed':seed,'swap':bool(g['swap']),'candidate_minus_champion':d})
    v=statistics.fmean(ds)
    r={'seed':seed,'seat_deltas':ds,'pair_mean_delta':v,'outcome':'W' if v>0 else 'L' if v<0 else 'D','candidate_exceptions':int(s['exceptions']['a']),'champion_exceptions':int(s['exceptions']['b'])}
    rows.append(r); print('SEALED2_PAIR',json.dumps(r))
vals=[r['pair_mean_delta'] for r in rows]
se=statistics.stdev(vals)/math.sqrt(len(vals)) if len(vals)>1 else 0.0
s0=[r['seat_deltas'][0] for r in rows]; s1=[r['seat_deltas'][1] for r in rows]
out={'label':'PRECOMMITTED_V153_FRESH_SEALED_2','candidate':'v153','champion':'v147','champion_sha256':'8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923','candidate_sha256':'128836e8e945d9b5b8c6776dc68cd45f4c21775713ebd3bd50655cd2f711ebfd','engine':'kaggle-environments==1.32.7','seeds':seeds,'games':games,'pair_wld':{k:sum(r['outcome']==k for r in rows) for k in 'WLD'},'mean_candidate_minus_champion':statistics.fmean(vals),'median_candidate_minus_champion':statistics.median(vals),'se':se,'mean_minus_2se':statistics.fmean(vals)-2*se,'worst_regression':min(vals),'best_improvement':max(vals),'seat0_mean':statistics.fmean(s0),'seat1_mean':statistics.fmean(s1),'seat_mean_gap':statistics.fmean(s0)-statistics.fmean(s1),'candidate_exceptions':sum(r['candidate_exceptions'] for r in rows),'champion_exceptions':sum(r['champion_exceptions'] for r in rows),'elapsed_sec':time.perf_counter()-t0,'pairs':rows}
Path('results/sealed2_local/sealed2_direct.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('SEALED2_SUMMARY',json.dumps({k:v for k,v in out.items() if k not in ('pairs','games')},indent=2))
assert out['candidate_exceptions']==0 and out['champion_exceptions']==0,out
'@ | python -

$seeds=@(961200427,1307503965,1065712661,1202442902,949799007,1206911468,1103449975,1059124859,911799718,1207510134,1366430876,1251623999)
foreach($seed in $seeds){
  python ci\eval_candidate_vs_champion_panel.py --candidate tmp\sealed2_local\v153.py --champion tmp\sealed2_local\v147.py --opponent opponents\score_2820\main.py --seed-start $seed --seed-count 1 --jobs 1 --out ("results\sealed2_local\transition\"+$seed+".json")
  if($LASTEXITCODE -ne 0){ throw "transition panel failed seed $seed" }
}

@'
import glob,json,statistics
from pathlib import Path
def state(x): return 'W' if x>0 else ('L' if x<0 else 'D')
transitions={k:0 for k in ('W->L','W->D','D->L','L->W','L->D','D->W','W->W','L->L','D->D')}
changed=[]; seed_cash=[]; seat_cash={False:[],True:[]}; cexc=hexc=0
for p in sorted(glob.glob('results/sealed2_local/transition/*.json')):
    d=json.loads(Path(p).read_text(encoding='utf-8')); cexc+=int(d.get('candidate_exceptions',0)); hexc+=int(d.get('champion_exceptions',0))
    for row in d['rows']:
        seed=int(row['seed']); seed_cash.append((seed,float(row['candidate_minus_champion_money'])))
        for s in row['seats']:
            h=state(float(s['champion_margin'])); c=state(float(s['candidate_margin'])); k=f'{h}->{c}'; transitions[k]=transitions.get(k,0)+1
            seat_cash[bool(s['swap'])].append(float(s['candidate_minus_champion_money']))
            if h!=c: changed.append({'seed':seed,'swap':bool(s['swap']),'transition':k,'candidate_margin':s['candidate_margin'],'champion_margin':s['champion_margin'],'candidate_minus_champion_money':s['candidate_minus_champion_money']})
vals=[v for _,v in seed_cash]
out={'opponent':'score_2820','transitions':transitions,'requested_regressions':{k:transitions[k] for k in ('W->L','W->D','D->L')},'requested_improvements':{k:transitions[k] for k in ('L->W','L->D','D->W')},'changed_outcomes':changed,'mean_candidate_minus_champion':statistics.fmean(vals),'worst_regression':min(vals),'best_improvement':max(vals),'seat0_mean':statistics.fmean(seat_cash[False]),'seat1_mean':statistics.fmean(seat_cash[True]),'candidate_exceptions':cexc,'champion_exceptions':hexc,'seed_cash':seed_cash}
Path('results/sealed2_local/sealed2_transition_score2820.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('TRANSITION_SUMMARY',json.dumps({k:v for k,v in out.items() if k not in ('changed_outcomes','seed_cash')},indent=2))
print('CHANGED_OUTCOMES',json.dumps(changed,indent=2))
assert cexc==0 and hexc==0,out
'@ | python -

Write-Host "DONE: results\sealed2_local\sealed2_direct.json"
Write-Host "DONE: results\sealed2_local\sealed2_transition_score2820.json"
