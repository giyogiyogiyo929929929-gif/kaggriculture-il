$ErrorActionPreference = 'Stop'

$python = 'C:\Users\nay92\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe'
$env:PYTHONPATH = '.venv\Lib\site-packages'
$candidate = 'opponents\v52\main.py'
$resultDir = 'data\eval\v52_base_panel'

New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

$jobs = @(
    @('jaxa_2802', 'opponents\jaxa_2802\main.py', 241),
    @('farming_v2', 'opponents\farming_v2\main.py', 241),
    @('v49', 'opponents\v49\main.py', 241),
    @('v50', 'opponents\v50\main.py', 241),
    @('tetsutani_dpts_b', 'opponents\tetsutani_dpts_b\main.py', 241),
    @('metav4_v13', 'opponents\metav4_v13\main.py', 241),
    @('v12', 'submissions\v12_v51safe\main.py', 301),
    @('story_of_seasons', 'opponents\story_of_seasons\main.py', 301),
    @('pipe16', 'opponents\pipe16\main.py', 301),
    @('dz_one_more_wheat', 'opponents\dz_one_more_wheat\main.py', 301),
    @('dz_more_wheat', 'opponents\dz_more_wheat\main.py', 301)
)

foreach ($job in $jobs) {
    $name = $job[0]
    $opponent = $job[1]
    $seed = $job[2]
    $json = Join-Path $resultDir "vs_$name.json"
    & $python scripts\eval.py $candidate $opponent -n 10 -j 4 --seed-start $seed --json $json
    if ($LASTEXITCODE -ne 0) {
        throw "Evaluation failed: $name (exit $LASTEXITCODE)"
    }
}
