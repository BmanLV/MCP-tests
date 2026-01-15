# Troubleshooting Claude Desktop Configuration

## Common Issues and Solutions

### Issue: Claude Desktop doesn't find the weather.py file

#### Solution 1: Use Full Paths

Make sure both the Python executable and the script use **absolute paths** (full paths starting with `C:\`).

**Example configuration:**
```json
{
  "mcpServers": {
    "weather": {
      "command": "C:\\Users\\PC\\AppData\\Local\\Python\\bin\\python.exe",
      "args": ["C:\\Users\\PC\\MCP-tests\\weather.py"]
    }
  }
}
```

**Important:**
- Use double backslashes (`\\`) in JSON paths
- Or use forward slashes (`/`) - both work: `C:/Users/PC/MCP-tests/weather.py`
- Make sure the path to `weather.py` is correct

#### Solution 2: Find Your Python Path

Run this command to find your Python executable:
```powershell
where.exe python
```

Then use the full path in the configuration.

#### Solution 3: Find Your Project Path

Run this command to get the absolute path to weather.py:
```powershell
cd C:\Users\PC\MCP-tests
python -c "import os; print(os.path.abspath('weather.py'))"
```

#### Solution 4: Use the Configuration Generator

Run the provided script to automatically generate the correct configuration:
```powershell
.\generate_config.ps1
```

### Issue: Server not showing up in Claude Desktop

1. **Check JSON Syntax**
   - Make sure your JSON is valid (no trailing commas, proper quotes)
   - Use a JSON validator: https://jsonlint.com/

2. **Verify File Location**
   - Configuration file must be at: `%APPDATA%\Claude\claude_desktop_config.json`
   - Full path: `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`
   - Create the `Claude` folder if it doesn't exist

3. **Fully Quit Claude Desktop**
   - Right-click Claude icon in system tray → Quit/Exit
   - Don't just close the window - you must fully quit
   - Restart Claude Desktop

4. **Check Logs**
   - Logs are at: `%APPDATA%\Claude\Logs\`
   - Check `mcp.log` for connection errors
   - Check `mcp-server-weather.log` for server-specific errors

### Issue: Python not found when Claude Desktop runs

**Problem:** Claude Desktop might not have access to your PATH environment variable.

**Solution:** Use the full path to Python.exe in the configuration:
```json
{
  "mcpServers": {
    "weather": {
      "command": "C:\\Users\\PC\\AppData\\Local\\Python\\bin\\python.exe",
      "args": ["C:\\Users\\PC\\MCP-tests\\weather.py"]
    }
  }
}
```

### Issue: Server starts but tools don't work

1. **Test the server manually:**
   ```powershell
   python weather.py
   ```
   (It won't show output - that's normal for stdio servers)

2. **Test with the test script:**
   ```powershell
   python test_server.py
   ```

3. **Check for import errors:**
   ```powershell
   python -c "from weather import mcp; print('OK')"
   ```

### Issue: "Unable to fetch" errors

- The National Weather Service API only works for US locations
- Make sure you're using US state codes (CA, NY, TX, etc.)
- Make sure coordinates are within the United States
- Check your internet connection

## Configuration File Examples

### Using Backslashes (Windows style)
```json
{
  "mcpServers": {
    "weather": {
      "command": "C:\\Users\\PC\\AppData\\Local\\Python\\bin\\python.exe",
      "args": ["C:\\Users\\PC\\MCP-tests\\weather.py"]
    }
  }
}
```

### Using Forward Slashes (also works on Windows)
```json
{
  "mcpServers": {
    "weather": {
      "command": "C:/Users/PC/AppData/Local/Python/bin/python.exe",
      "args": ["C:/Users/PC/MCP-tests/weather.py"]
    }
  }
}
```

### Using Python from PATH (if accessible)
```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["C:/Users/PC/MCP-tests/weather.py"]
    }
  }
}
```

## Verification Steps

1. ✅ Configuration file exists at correct location
2. ✅ JSON syntax is valid
3. ✅ Python path is absolute and correct
4. ✅ weather.py path is absolute and correct
5. ✅ Python can run weather.py without errors
6. ✅ Claude Desktop was fully quit and restarted
7. ✅ Check Claude Desktop logs for errors

## Getting Help

If none of these solutions work:
1. Check the Claude Desktop logs: `%APPDATA%\Claude\Logs\mcp.log`
2. Verify your Python installation works: `python --version`
3. Test the server: `python test_server.py`
4. Check the MCP documentation: https://modelcontextprotocol.io/docs
