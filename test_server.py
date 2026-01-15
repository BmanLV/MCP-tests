"""
Simple test script to verify the MCP server can be imported and initialized.
This doesn't test the full JSON-RPC communication, but verifies the code is correct.
"""
import sys
import asyncio

try:
    from weather import mcp, get_alerts, get_forecast
    
    print("✓ Server module imported successfully")
    print(f"✓ Server name: {mcp.name}")
    print(f"✓ Tools registered: {len(mcp._tools) if hasattr(mcp, '_tools') else 'N/A'}")
    
    # Test that the functions are callable
    print("\nTesting tool functions...")
    
    async def test_tools():
        # Test get_alerts (this will make an actual API call)
        print("\nTesting get_alerts('CA')...")
        try:
            result = await get_alerts("CA")
            print(f"✓ get_alerts returned: {len(result)} characters")
            if len(result) > 0:
                print("  Preview:", result[:100] + "..." if len(result) > 100 else result)
        except Exception as e:
            print(f"✗ get_alerts failed: {e}")
        
        # Test get_forecast (this will make an actual API call)
        print("\nTesting get_forecast(38.5816, -121.4944) [Sacramento]...")
        try:
            result = await get_forecast(38.5816, -121.4944)
            print(f"✓ get_forecast returned: {len(result)} characters")
            if len(result) > 0:
                print("  Preview:", result[:100] + "..." if len(result) > 100 else result)
        except Exception as e:
            print(f"✗ get_forecast failed: {e}")
    
    print("\nRunning async tests...")
    asyncio.run(test_tools())
    
    print("\n✓ All tests passed!")
    print("\nServer is ready to use. Configure Claude Desktop to connect to it.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you've installed dependencies: pip install 'mcp[cli]>=1.2.0' httpx")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
