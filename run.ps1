# PowerShell script to run the backend server
# Usage: .\run.ps1 [local|dev|prod]

param(
    [string]$Mode = "local"
)

# Set the APP_MODE environment variable
$env:APP_MODE = $Mode
$env:PYTHONPATH = $PSScriptRoot

Write-Host "Starting backend server in $Mode mode..." -ForegroundColor Green
Write-Host "APP_MODE=$env:APP_MODE" -ForegroundColor Yellow
Write-Host "PYTHONPATH=$env:PYTHONPATH" -ForegroundColor Yellow

# Check if poetry is available
if (Get-Command poetry -ErrorAction SilentlyContinue) {
    Write-Host "Using Poetry to run the server..." -ForegroundColor Cyan
    # Use poetry run to execute in the virtual environment
    poetry run python silicon/_microservices/admin/manage.py runserver
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Using Python directly (make sure dependencies are installed)..." -ForegroundColor Cyan
    python silicon/_microservices/admin/manage.py runserver
} else {
    Write-Host "Error: Neither Poetry nor Python found in PATH" -ForegroundColor Red
    Write-Host "Please install Poetry: pip install poetry" -ForegroundColor Yellow
    Write-Host "Then run: poetry install" -ForegroundColor Yellow
    exit 1
}

