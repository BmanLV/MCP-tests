# Generate Claude Desktop Configuration
# This script creates the correct configuration file with absolute paths

Write-Host "MCP Weather Server - Configuration Generator" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$projectPath = $PSScriptRoot
if (-not $projectPath) {
    $projectPath = (Get-Location).Path
}

$weatherPyPath = Join-Path $projectPath "weather.py"

Write-Host "Project path: $projectPath" -ForegroundColor Yellow
Write-Host "weather.py path: $weatherPyPath" -ForegroundColor Yellow
Write-Host ""

# Find Python executable
$pythonPath = ""
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $pythonPath = $pythonCmd.Source
    Write-Host "Found Python: $pythonPath" -ForegroundColor Green
} catch {
    Write-Host "Python not found in PATH, trying py launcher..." -ForegroundColor Yellow
    try {
        $pythonCmd = Get-Command py -ErrorAction Stop
        $pythonPath = "py"
        Write-Host "Using Python launcher: py" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Python not found at all." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Create configuration object
$configObject = @{
    mcpServers = @{
        weather = @{
            command = $pythonPath
            args    = @($weatherPyPath)
        }
    }
}

$configJson = $configObject | ConvertTo-Json -Depth 10

# Claude Desktop config location
$claudeConfigDir  = Join-Path $env:APPDATA "Claude"
$claudeConfigFile = Join-Path $claudeConfigDir "claude_desktop_config.json"

Write-Host "Claude Desktop config location:" -ForegroundColor Cyan
Write-Host "  $claudeConfigFile" -ForegroundColor White
Write-Host ""

# Ensure config directory exists
if (-not (Test-Path $claudeConfigDir)) {
    Write-Host "Creating Claude config directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
}

# Handle existing config
if (Test-Path $claudeConfigFile) {
    Write-Host "WARNING: Configuration file already exists!" -ForegroundColor Yellow
    Write-Host ""
    Get-Content $claudeConfigFile | Write-Host -ForegroundColor Gray
    Write-Host ""

    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Aborted." -ForegroundColor Yellow

        $backupFile = "$claudeConfigFile.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $claudeConfigFile $backupFile
        Write-Host "Backup created: $backupFile" -ForegroundColor Green

        $exampleFile = Join-Path $projectPath "claude_desktop_config.json.generated"
        $configJson | Out-File -FilePath $exampleFile -Encoding utf8

        Write-Host ""
        Write-Host "Generated example config saved to:" -ForegroundColor Green
        Write-Host "  $exampleFile" -ForegroundColor White
        exit
    }
}

# Write configuration
Write-Host "Writing configuration..." -ForegroundColor Yellow
$configJson | Out-File -FilePath $claudeConfigFile -Encoding utf8


