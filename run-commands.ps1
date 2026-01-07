# PowerShell script with common backend commands
# Usage: .\run-commands.ps1 [command] [mode]
# Commands: run, migrate, mm (makemigrations), su (createsuperuser), setup_knowledge

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [string]$Mode = "local"
)

# Set the APP_MODE environment variable
$env:APP_MODE = $Mode
$env:PYTHONPATH = $PSScriptRoot

$djangoCmd = switch ($Command.ToLower()) {
    "run" { "runserver" }
    "migrate" { "migrate" }
    "mm" { "makemigrations" }
    "su" { "createsuperuser" }
    "csu" { "create_super_users" }
    "setup_knowledge" { "setup_knowledge" }
    "collectstatic" { "collectstatic" }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Available commands: run, migrate, mm, su, csu, setup_knowledge, collectstatic" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Running: $Command in $Mode mode" -ForegroundColor Green
Write-Host "APP_MODE=$env:APP_MODE" -ForegroundColor Yellow
Write-Host "PYTHONPATH=$env:PYTHONPATH" -ForegroundColor Yellow

# Check if poetry is available
if (Get-Command poetry -ErrorAction SilentlyContinue) {
    Write-Host "Using Poetry to run the command..." -ForegroundColor Cyan
    poetry run python silicon/_microservices/admin/manage.py $djangoCmd
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Using Python directly (make sure dependencies are installed)..." -ForegroundColor Cyan
    python silicon/_microservices/admin/manage.py $djangoCmd
} else {
    Write-Host "Error: Neither Poetry nor Python found in PATH" -ForegroundColor Red
    Write-Host "Please install Poetry: pip install poetry" -ForegroundColor Yellow
    Write-Host "Then run: poetry install" -ForegroundColor Yellow
    exit 1
}

