#!/usr/bin/env python3
import logging
import traceback
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='SERVER: %(message)s')
logger = logging.getLogger(__name__)

# Create server with minimal configuration
server = FastMCP(name="MCP Time Tool Server")

# Define our time tool using the decorator pattern
@server.tool(description="Returns the current time")
def get_time(format: str = "%H:%M:%S") -> str:
    """Returns the current time with the specified format"""
    logger.info(f"Tool get_time called with format: {format}")
    
    # Get the current time with the specified format
    current_time = datetime.now().strftime(format)
    logger.info(f"Current time: {current_time}")
    
    # Return the formatted time
    return f"The current time is: {current_time}"

# Run server
if __name__ == "__main__":
    logger.info("Starting MCP server")
    
    # List all tools before starting the server
    tools = server._tool_manager.list_tools()
    logger.info(f"Server has {len(tools)} tools registered:")
    for tool in tools:
        logger.info(f"  - {tool.name}: {tool.description}")
    
    try:
        # Run the server with stdio transport
        logger.info("Starting server with stdio transport")
        server.run("stdio")
    except Exception as e:
        logger.error(f"Server error: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
