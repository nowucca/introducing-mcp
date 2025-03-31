#!/usr/bin/env python3
import asyncio
import logging
import sys
import traceback
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='CLIENT: %(message)s')
logger = logging.getLogger(__name__)

async def run_client():
    """Connect to the MCP server, list tools, call the time tool, and display the result"""
    logger.info("Starting MCP client")
    
    # Create server parameters for stdio transport
    server_params = StdioServerParameters(
        command="python",
        args=["server/server.py"],
        env=None
    )
    
    # Use AsyncExitStack for proper resource cleanup
    exit_stack = AsyncExitStack()
    
    try:
        # Connect to the server
        logger.info("Opening stdio connection...")
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = stdio_transport
        logger.info("Stdio connection established")
        
        # Create a session
        logger.info("Creating ClientSession...")
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        logger.info("ClientSession created")
        
        # Initialize the connection
        logger.info("Initializing connection...")
        try:
            initialize_result = await asyncio.wait_for(session.initialize(), timeout=10.0)
            logger.info(f"Connected to server: {initialize_result.serverInfo.name}")
            
            # Request the list of tools
            logger.info("Requesting tool list...")
            tools_response = await asyncio.wait_for(session.list_tools(), timeout=10.0)
            
            # Display tool advertisements
            if tools_response.tools:
                logger.info(f"Server advertised {len(tools_response.tools)} tools:")
                for tool in tools_response.tools:
                    logger.info(f"  - {tool.name}: {tool.description}")
                logger.info("Tool advertisement received successfully!")
                
                # Find the time tool
                time_tool = next((tool for tool in tools_response.tools if tool.name == "get_time"), None)
                if time_tool:
                    # Call the time tool
                    logger.info("Calling the get_time tool...")
                    tool_result = await asyncio.wait_for(
                        session.call_tool(name="get_time", arguments={}),
                        timeout=10.0
                    )
                    
                    # Display the result
                    if tool_result.content:
                        for content_item in tool_result.content:
                            if content_item.type == "text":
                                print("\n" + "=" * 40)
                                print(content_item.text)
                                print("=" * 40 + "\n")
                                logger.info(f"Time tool result: {content_item.text}")
                    else:
                        logger.warning("Time tool returned no content")
                else:
                    logger.warning("The get_time tool was not found in the server's tool list")
            else:
                logger.info("No tools advertised by the server")
                
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            return 1
            
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1
    finally:
        # AsyncExitStack will properly clean up resources
        await exit_stack.aclose()
    
    return 0

def main():
    """Entry point function"""
    try:
        return asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
