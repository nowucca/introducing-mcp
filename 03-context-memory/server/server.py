#!/usr/bin/env python3
import logging
import traceback
from datetime import datetime
import pytz
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='SERVER: %(message)s')
logger = logging.getLogger(__name__)

# Create server with minimal configuration
server = FastMCP(name="MCP Context Memory Server")

# Define our time tool using the decorator pattern
@server.tool(description="Returns the current time in the specified timezone")
def get_time(timezone: str = "UTC") -> str:
    """Returns the current time in the specified timezone
    
    Args:
        timezone: Timezone name (e.g., 'US/Pacific', 'Europe/London', 'Asia/Tokyo')
    
    Returns:
        String with the current time in the specified timezone
    """
    logger.info(f"Tool get_time called with timezone: {timezone}")
    
    try:
        # Get the timezone object
        tz = pytz.timezone(timezone)
        
        # Get the current time in the specified timezone
        current_time = datetime.now(tz).strftime("%H:%M:%S %Z")
        logger.info(f"Current time in {timezone}: {current_time}")
        
        # Return the formatted time
        return f"The current time in {timezone} is: {current_time}"
    except pytz.exceptions.UnknownTimeZoneError:
        error_msg = f"Invalid timezone: {timezone}"
        logger.error(error_msg)
        raise ValueError(error_msg)

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
