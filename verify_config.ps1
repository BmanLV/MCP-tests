# Verify Claude Desktop Configuration
# This script checks if your configuration is correct

Write-Host "MCP Weather Server - Configuration Verifier" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Check Claude config file location
$claudeConfigFile = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
Write-Host "Checking configuration file..." -ForegroundColor Yellow
Write-Host "Expected location: $claudeConfigFile" -ForegroundColor White

if (-not (Test-Path $claudeConfigFile)) {
    Write-Host "✗ Configuration file NOT FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "The configuration file doesn't exist. Create it using:" -ForegroundColor Yellow
    Write-Host "  .\generate_config.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✓ Configuration file exists" -ForegroundColor Green
Write-Host ""

# Read and parse JSON
try {
    $config = Get-Content $claudeConfigFile -Raw | ConvertFrom-Json
    Write-Host "✓ JSON syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "✗ Invalid JSON syntax: $_" -ForegroundColor Red
    exit 1
}

# Check if weather server is configured
if (-not $config.mcpServers) {
    Write-Host "✗ No 'mcpServers' key found" -ForegroundColor Red
    exit 1
}

if (-not $config.mcpServers.weather) {
    Write-Host "✗ No 'weather' server configured" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Weather server configuration found" -ForegroundColor Green
Write-Host ""

# Check Python command
$pythonCmd = $config.mcpServers.weather.command
Write-Host "Python command: $pythonCmd" -ForegroundColor Cyan

if ($pythonCmd -eq "python") {
    Write-Host "⚠ Warning: Using 'python' from PATH" -ForegroundColor Yellow
    Write-Host "  Claude Desktop might not have access to your PATH" -ForegroundColor Yellow
    Write-Host "  Consider using full path to python.exe" -ForegroundColor Yellow
} else {
    if (Test-Path $pythonCmd) {
        Write-Host "✓ Python executable found at: $pythonCmd" -ForegroundColor Green
    } else {
        Write-Host "✗ Python executable NOT FOUND: $pythonCmd" -ForegroundColor Red
        Write-Host "  Find your Python path with: where.exe python" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check weather.py path
$weatherPy = $config.mcpServers.weather.args[0]
Write-Host "weather.py path: $weatherPy" -ForegroundColor Cyan

if (Test-Path $weatherPy) {
    Write-Host "✓ weather.py found at: $weatherPy" -ForegroundColor Green
} else {
    Write-Host "✗ weather.py NOT FOUND: $weatherPy" -ForegroundColor Red
    Write-Host "  Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "  Expected location: $(Join-Path (Get-Location) 'weather.py')" -ForegroundColor Yellow
}

Write-Host ""

# Display full configuration
Write-Host "Current configuration:" -ForegroundColor Cyan
Get-Content $claudeConfigFile | Write-Host -ForegroundColor Gray
Write-Host ""

# Check logs location
$logsDir = Join-Path $env:APPDATA "Claude\Logs"
if (Test-Path $logsDir) {
    Write-Host "Logs directory: $logsDir" -ForegroundColor Cyan
    $logFiles = Get-ChildItem $logsDir -Filter "mcp*.log" -ErrorAction SilentlyContinue
    if ($logFiles) {
        Write-Host "Found log files:" -ForegroundColor Yellow
        foreach ($log in $logFiles) {
            Write-Host "  - $($log.Name)" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "To view recent errors:" -ForegroundColor Cyan
        Write-Host "  Get-Content '$logsDir\mcp.log' -Tail 20" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Verification complete!" -ForegroundColor Green
Write-Host ""
Write-Host "If everything shows ✓, make sure you:" -ForegroundColor Cyan
Write-Host "1. Fully quit Claude Desktop (system tray → Quit)" -ForegroundColor White
Write-Host "2. Restart Claude Desktop" -ForegroundColor White
Write-Host "3. Check the Connectors menu in Claude Desktop" -ForegroundColor White
