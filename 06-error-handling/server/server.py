#!/usr/bin/env python3
import logging
import traceback
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='SERVER: %(message)s')
logger = logging.getLogger(__name__)

# Create server with minimal configuration
server = FastMCP(name="MCP Error Handling Server")

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

# Run server
if __name__ == "__main__":
    logger.info("Starting MCP Error Handling server")
    
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
