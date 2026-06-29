import asyncio
import json
import inspect
import sys
import os

async def mcp_call(tool_name: str, **kwargs):
    """Bypasses stdio process spawning to run MCP tools directly in-process.
    This prevents console windows from popping up on Windows and improves execution speed by 10-100x.
    """
    # Dynamically import mcp_server to avoid circular imports during setup
    import mcp_server
    
    # Retrieve the tool function
    func = getattr(mcp_server, tool_name, None)
    if not func:
        raise AttributeError(f"Tool '{tool_name}' not found on MCP server module.")
        
    # Execute the function (handles both synchronous and asynchronous functions)
    if inspect.iscoroutinefunction(func):
        result = await func(**kwargs)
    else:
        result = func(**kwargs)
        
    return result