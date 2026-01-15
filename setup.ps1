# MCP Weather Server Setup Script for Windows
# This script helps set up the MCP server environment

Write-Host "MCP Weather Server Setup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow

# Try to find Python - first check PATH, then common locations
$pythonExe = $null

# Try python from PATH
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $pythonExe = $pythonCmd.Source
    Write-Host "Found Python in PATH: $pythonExe" -ForegroundColor Green
} catch {
    # Try common installation locations
    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $pythonExe = $path
            Write-Host "Found Python at: $pythonExe" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonExe) {
    Write-Host "ERROR: Python is not installed or not found" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check Python version
$pythonVersion = & $pythonExe --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Check if Python version is >= 3.10
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-Host "ERROR: Python 3.10 or higher is required" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Warning: Could not parse Python version, continuing anyway..." -ForegroundColor Yellow
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
} else {
    & $pythonExe -m venv .venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Use venv Python for subsequent commands
$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install "mcp[cli]>=1.2.0" httpx

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the virtual environment: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Test the server: python weather.py" -ForegroundColor White
Write-Host "3. Configure Claude Desktop: .\generate_config.ps1" -ForegroundColor White
Write-Host "4. Fully quit and restart Claude Desktop" -ForegroundColor White
