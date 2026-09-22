$ErrorActionPreference = 'Stop'
$python = 'C:\Users\nay92\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe'
$env:PYTHONPATH = '.venv\Lib\site-packages'
$candidate = 'submissions\v16_antiv52\main.py'
$target = 'opponents\v52\main.py'
$resultDir = 'data\eval\v16_antiv52'

New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

& $python scripts\eval.py $candidate $target -n 10 -j 4 --seed-start 401 --json (Join-Path $resultDir 'smoke_vs_v52.json')
if ($LASTEXITCODE -ne 0) { throw 'v16 smoke failed' }

$smoke = Get-Content -LiteralPath (Join-Path $resultDir 'smoke_vs_v52.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if (($smoke.wins -le $smoke.losses) -or ($smoke.pair_diff_mean -le 0)) {
    @{ status = 'stopped'; stage = 'smoke'; reason = 'no_positive_effect'; wins = $smoke.wins; losses = $smoke.losses; draws = $smoke.draws; mean = $smoke.pair_diff_mean; stderr = $smoke.pair_diff_stderr } |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $resultDir 'status.json') -Encoding UTF8
    exit 0
}

& $python scripts\eval.py $candidate $target -n 30 -j 4 --seed-start 501 --json (Join-Path $resultDir 'confirm_vs_v52.json')
if ($LASTEXITCODE -ne 0) { throw 'v16 confirmation failed' }

$confirm = Get-Content -LiteralPath (Join-Path $resultDir 'confirm_vs_v52.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$passed = ($confirm.wins -gt $confirm.losses) -and ($confirm.pair_diff_mean -gt 2 * $confirm.pair_diff_stderr)
@{ status = 'complete'; stage = 'confirmation'; passed = $passed; wins = $confirm.wins; losses = $confirm.losses; draws = $confirm.draws; mean = $confirm.pair_diff_mean; stderr = $confirm.pair_diff_stderr } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $resultDir 'status.json') -Encoding UTF8
