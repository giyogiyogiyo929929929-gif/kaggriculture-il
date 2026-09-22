$ErrorActionPreference = 'Stop'
$python = 'C:\Users\nay92\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe'
$env:PYTHONPATH = '.venv\Lib\site-packages'
$resultDir = 'data\eval\v52_base_confirm'
$opponent = 'opponents\market_rhythm\main.py'

New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

& $python scripts\eval.py 'opponents\v52\main.py' $opponent -n 20 -j 4 --seed-start 601 --json (Join-Path $resultDir 'v52_vs_market_rhythm.json')
if ($LASTEXITCODE -ne 0) { throw 'Confirmation failed: v52 vs market_rhythm' }

& $python scripts\eval.py 'submissions\v12_v51safe\main.py' $opponent -n 20 -j 4 --seed-start 601 --json (Join-Path $resultDir 'v12_vs_market_rhythm.json')
if ($LASTEXITCODE -ne 0) { throw 'Confirmation failed: v12 vs market_rhythm' }

@{ status = 'complete'; opponent = 'market_rhythm'; seed_start = 601; pairs = 20 } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $resultDir 'status.json') -Encoding UTF8
