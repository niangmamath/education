# PowerShell script to activate the virtual environment
# Usage: .\activate.ps1

$venvPath = ".venv"
$pythonPath = Join-Path -Path $venvPath -ChildPath "Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Error "Virtual environment not found at $venvPath"
    Write-Host "Please run: python -m venv .venv"
    exit 1
}

# Activate the virtual environment
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
} else {
    Write-Error "Activate script not found at $activateScript"
    exit 1
}

Write-Host "Virtual environment activated: $venvPath" -ForegroundColor Green
