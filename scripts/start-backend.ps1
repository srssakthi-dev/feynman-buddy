$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$localConfig = Join-Path $projectRoot ".local/runtime.json"
$pythonPath = Join-Path $projectRoot ".venv/Scripts/python.exe"
if (Test-Path -LiteralPath $localConfig) {
    $runtimeConfig = Get-Content -LiteralPath $localConfig -Raw | ConvertFrom-Json
    $pythonPath = $runtimeConfig.python
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Python environment missing. Follow README.md."
}
Push-Location (Join-Path $projectRoot "backend")
try { & $pythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8001 }
finally { Pop-Location }
