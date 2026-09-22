$ErrorActionPreference = 'Stop'
$python = 'C:\Users\nay92\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe'
$env:PYTHONPATH = '.venv\Lib\site-packages'
$candidate = 'submissions\v16_antiv52\main.py'
$resultDir = 'data\eval\v16_antiv52_regression'
New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

$jobs = @(
    @('jaxa_2802', 'opponents\jaxa_2802\main.py', 241, 'data\eval\v52_base_panel\vs_jaxa_2802.json'),
    @('farming_v2', 'opponents\farming_v2\main.py', 241, 'data\eval\v52_base_panel\vs_farming_v2.json'),
    @('v49', 'opponents\v49\main.py', 241, 'data\eval\v52_base_panel\vs_v49.json'),
    @('v50', 'opponents\v50\main.py', 241, 'data\eval\v52_base_panel\vs_v50.json'),
    @('tetsutani_dpts_b', 'opponents\tetsutani_dpts_b\main.py', 241, 'data\eval\v52_base_panel\vs_tetsutani_dpts_b.json'),
    @('metav4_v13', 'opponents\metav4_v13\main.py', 241, 'data\eval\v52_base_panel\vs_metav4_v13.json'),
    @('v12', 'submissions\v12_v51safe\main.py', 301, 'data\eval\v52_base_panel\vs_v12.json'),
    @('story_of_seasons', 'opponents\story_of_seasons\main.py', 301, 'data\eval\v52_base_panel\vs_story_of_seasons.json'),
    @('pipe16', 'opponents\pipe16\main.py', 301, 'data\eval\v52_base_panel\vs_pipe16.json'),
    @('dz_one_more_wheat', 'opponents\dz_one_more_wheat\main.py', 301, 'data\eval\v52_base_panel\vs_dz_one_more_wheat.json'),
    @('dz_more_wheat', 'opponents\dz_more_wheat\main.py', 301, 'data\eval\v52_base_panel\vs_dz_more_wheat.json'),
    @('v47', 'opponents\v47\main.py', 241, 'data\eval\v52_base_stage2\vs_v47.json'),
    @('k256_h2_q_v1', 'opponents\k256_h2_q_v1\main.py', 241, 'data\eval\v52_base_stage2\vs_k256_h2_q_v1.json'),
    @('shop_router_v7', 'opponents\shop_router_v7\main.py', 241, 'data\eval\v52_base_stage2\vs_shop_router_v7.json'),
    @('thomas_router_93', 'opponents\thomas_router_93\main.py', 241, 'data\eval\v52_base_stage2\vs_thomas_router_93.json'),
    @('smaller_market_shock', 'opponents\smaller_market_shock\main.py', 241, 'data\eval\v52_base_stage2\vs_smaller_market_shock.json'),
    @('ready_stock', 'opponents\ready_stock\main.py', 241, 'data\eval\v52_base_stage2\vs_ready_stock.json'),
    @('market_rhythm', 'opponents\market_rhythm\main.py', 241, 'data\eval\v52_base_stage2\vs_market_rhythm.json'),
    @('peak_2950', 'opponents\peak_2950\main.py', 241, 'data\eval\v52_base_stage2\vs_peak_2950.json'),
    @('gods_mode', 'opponents\gods_mode\main.py', 241, 'data\eval\v52_base_stage2\vs_gods_mode.json'),
    @('salem_2900', 'opponents\salem_2900\main.py', 241, 'data\eval\v52_base_stage2\vs_salem_2900.json')
)

$rows = @()
foreach ($job in $jobs) {
    $name, $opponent, $seed, $baselinePath = $job
    $json = Join-Path $resultDir "vs_$name.json"
    & $python scripts\eval.py $candidate $opponent -n 10 -j 4 --seed-start $seed --json $json
    if ($LASTEXITCODE -ne 0) { throw "v16 regression failed: $name" }
    $current = Get-Content -LiteralPath $json -Raw -Encoding UTF8 | ConvertFrom-Json
    $baseline = Get-Content -LiteralPath $baselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $rows += [pscustomobject]@{
        name = $name
        wins = $current.wins; losses = $current.losses; draws = $current.draws
        pair_diff_mean = $current.pair_diff_mean; pair_diff_stderr = $current.pair_diff_stderr
        baseline_wins = $baseline.wins; baseline_losses = $baseline.losses; baseline_draws = $baseline.draws
        baseline_pair_diff_mean = $baseline.pair_diff_mean
        win_regression = ($current.wins -lt $baseline.wins) -or ($current.losses -gt $baseline.losses)
        mean_delta = $current.pair_diff_mean - $baseline.pair_diff_mean
        exceptions_a = $current.exceptions.a; exceptions_b = $current.exceptions.b
        animals_lost = $current.health.a.animals_lost
    }
}

$regressions = @($rows | Where-Object { $_.win_regression } | ForEach-Object { $_.name })
$safety = @($rows | Where-Object { $_.exceptions_a -ne 0 -or $_.exceptions_b -ne 0 -or $_.animals_lost -ne 0 } | ForEach-Object { $_.name })
@{ status = 'complete'; passed = ($regressions.Count -eq 0 -and $safety.Count -eq 0); regressions = $regressions; safety_failures = $safety; results = $rows } |
    ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $resultDir 'summary.json') -Encoding UTF8
