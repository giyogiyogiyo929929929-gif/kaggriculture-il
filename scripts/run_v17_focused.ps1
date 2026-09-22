$ErrorActionPreference = 'Stop'
$python = 'C:\Users\nay92\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe'
$env:PYTHONPATH = '.venv\Lib\site-packages'
$candidate = 'submissions\v17_antiv52_strict\main.py'
$resultDir = 'data\eval\v17_antiv52_strict'
New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

$jobs = @(
    @('v52', 'opponents\v52\main.py', 501),
    @('v49', 'opponents\v49\main.py', 241),
    @('v50', 'opponents\v50\main.py', 241)
)
foreach ($job in $jobs) {
    & $python scripts\eval.py $candidate $job[1] -n 10 -j 4 --seed-start $job[2] --json (Join-Path $resultDir "vs_$($job[0]).json")
    if ($LASTEXITCODE -ne 0) { throw "v17 focused evaluation failed: $($job[0])" }
}
