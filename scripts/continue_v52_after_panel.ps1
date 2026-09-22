param(
    [int]$PanelPid = 6280
)

$ErrorActionPreference = 'Stop'
$python = 'C:\Users\nay92\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe'
$env:PYTHONPATH = '.venv\Lib\site-packages'
$candidate = 'opponents\v52\main.py'
$panelDir = 'data\eval\v52_base_panel'

$panelProcess = Get-Process -Id $PanelPid -ErrorAction SilentlyContinue
if ($panelProcess) {
    Wait-Process -Id $PanelPid
}

$expected = @(
    'jaxa_2802', 'farming_v2', 'v49', 'v50', 'tetsutani_dpts_b',
    'metav4_v13', 'v12', 'story_of_seasons', 'pipe16',
    'dz_one_more_wheat', 'dz_more_wheat'
)
$missing = @($expected | Where-Object { -not (Test-Path -LiteralPath (Join-Path $panelDir "vs_$_.json")) })
if ($missing.Count -gt 0) {
    @{ status = 'incomplete'; missing = $missing } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $panelDir 'summary.json') -Encoding UTF8
    throw "Panel incomplete: $($missing -join ', ')"
}

$baselineFiles = @{
    jaxa_2802 = 'data\eval\v51\v51_jaxa_2802_reg.json'
    farming_v2 = 'data\eval\v51\v51_farming_v2_reg.json'
    v49 = 'data\eval\v51\v51_v49_reg.json'
    v50 = 'data\eval\v51\v51_v50_reg.json'
    tetsutani_dpts_b = 'data\eval\v51\v51_tetsutani_dpts_b_reg.json'
}

$mandatory = @()
$regressions = @()
foreach ($name in $baselineFiles.Keys) {
    $current = Get-Content -LiteralPath (Join-Path $panelDir "vs_$name.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    $baseline = Get-Content -LiteralPath $baselineFiles[$name] -Raw -Encoding UTF8 | ConvertFrom-Json
    $regressed = ($current.wins -lt $baseline.wins) -or ($current.losses -gt $baseline.losses)
    if ($regressed) { $regressions += $name }
    $mandatory += [pscustomobject]@{
        name = $name
        wins = $current.wins
        losses = $current.losses
        draws = $current.draws
        pair_diff_mean = $current.pair_diff_mean
        baseline_wins = $baseline.wins
        baseline_losses = $baseline.losses
        baseline_pair_diff_mean = $baseline.pair_diff_mean
        regressed = $regressed
    }
}

$safetyFailures = @()
foreach ($name in $expected) {
    $result = Get-Content -LiteralPath (Join-Path $panelDir "vs_$name.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if (($result.exceptions.a -ne 0) -or ($result.exceptions.b -ne 0) -or ($result.health.a.animals_lost -ne 0)) {
        $safetyFailures += $name
    }
}
$direct = Get-Content -LiteralPath (Join-Path $panelDir 'vs_v12.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$passed = ($regressions.Count -eq 0) -and ($safetyFailures.Count -eq 0) -and ($direct.wins -eq 10) -and ($direct.losses -eq 0)
$route = if ($passed) { 'expanded_regression' } else { 'targeted_confirmation' }

@{
    status = 'complete'
    passed_initial_gate = $passed
    route = $route
    direct_v12 = @{
        wins = $direct.wins; losses = $direct.losses; draws = $direct.draws
        pair_diff_mean = $direct.pair_diff_mean; pair_diff_stderr = $direct.pair_diff_stderr
    }
    mandatory = $mandatory
    regressions = $regressions
    safety_failures = $safetyFailures
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $panelDir 'summary.json') -Encoding UTF8

if ($passed) {
    $nextDir = 'data\eval\v52_base_stage2'
    New-Item -ItemType Directory -Force -Path $nextDir | Out-Null
    $nextJobs = @(
        @('v47', 'opponents\v47\main.py'),
        @('k256_h2_q_v1', 'opponents\k256_h2_q_v1\main.py'),
        @('shop_router_v7', 'opponents\shop_router_v7\main.py'),
        @('thomas_router_93', 'opponents\thomas_router_93\main.py'),
        @('smaller_market_shock', 'opponents\smaller_market_shock\main.py'),
        @('ready_stock', 'opponents\ready_stock\main.py'),
        @('market_rhythm', 'opponents\market_rhythm\main.py'),
        @('peak_2950', 'opponents\peak_2950\main.py'),
        @('gods_mode', 'opponents\gods_mode\main.py'),
        @('salem_2900', 'opponents\salem_2900\main.py')
    )
    foreach ($job in $nextJobs) {
        $json = Join-Path $nextDir "vs_$($job[0]).json"
        & $python scripts\eval.py $candidate $job[1] -n 10 -j 4 --seed-start 241 --json $json
        if ($LASTEXITCODE -ne 0) { throw "Stage 2 failed: $($job[0])" }
    }
    @{ status = 'complete'; route = $route; opponents = @($nextJobs | ForEach-Object { $_[0] }) } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $nextDir 'status.json') -Encoding UTF8
}
else {
    $confirmDir = 'data\eval\v52_base_confirm'
    New-Item -ItemType Directory -Force -Path $confirmDir | Out-Null
    $opponentPaths = @{
        jaxa_2802 = 'opponents\jaxa_2802\main.py'
        farming_v2 = 'opponents\farming_v2\main.py'
        v49 = 'opponents\v49\main.py'
        v50 = 'opponents\v50\main.py'
        tetsutani_dpts_b = 'opponents\tetsutani_dpts_b\main.py'
    }
    foreach ($name in $regressions) {
        $opponent = $opponentPaths[$name]
        & $python scripts\eval.py $candidate $opponent -n 20 -j 4 --seed-start 601 --json (Join-Path $confirmDir "v52_vs_$name.json")
        if ($LASTEXITCODE -ne 0) { throw "Confirmation failed: v52 vs $name" }
        & $python scripts\eval.py 'submissions\v12_v51safe\main.py' $opponent -n 20 -j 4 --seed-start 601 --json (Join-Path $confirmDir "v12_vs_$name.json")
        if ($LASTEXITCODE -ne 0) { throw "Confirmation failed: v12 vs $name" }
    }
    @{ status = 'complete'; route = $route; opponents = $regressions; safety_failures = $safetyFailures } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $confirmDir 'status.json') -Encoding UTF8
}
