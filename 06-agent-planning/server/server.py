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
server = FastMCP(name="MCP Multiple Tools Server")

# Define our error tool that always fails
@server.tool(description="This tool always fails (for error handling demonstration)")
def get_error(message: str = "Default error message") -> str:
    """Always fails with an error (for demonstrating error handling)
    
    Args:
        message: Optional custom error message
        
    Returns:
        Never returns successfully, always raises an exception
    """
    logger.info(f"Tool get_error called with message: {message}")
    error_msg = f"Intentional error triggered: {message}"
    logger.error(error_msg)
    raise ValueError(error_msg)

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

# Define our weather tool using the decorator pattern
@server.tool(description="Get weather information for a city")
def get_weather(city: str) -> str:
    """Returns the current weather for the specified city
    
    Args:
        city: City name (e.g., 'New York', 'London', 'Tokyo')
    
    Returns:
        String with the current weather in the specified city
    """
    logger.info(f"Tool get_weather called with city: {city}")
    
    # In a real implementation, this would call a weather API
    # For this example, we'll just return a hardcoded response
    weather_info = f"Sunny in {city}"
    logger.info(f"Weather in {city}: {weather_info}")
    
    # Return the weather information
    return weather_info

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
