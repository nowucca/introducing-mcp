#!/usr/bin/env python3
import asyncio
import json
import logging
import sys
import uuid
import traceback
from contextlib import AsyncExitStack
from typing import Dict, Any, Tuple

from mcp import ClientSession
from mcp.types import CallToolResult
from mcp.types import (
    TextContent,
)

from mcp.client.stdio import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='CLIENT: %(message)s')
logger = logging.getLogger(__name__)

async def execute_tool_call(session, tool_name, arguments):
    """Execute a tool call and return the result
    
    Args:
        session: The MCP ClientSession
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
        
    Returns:
        Tuple of (success, result/error)
    """
    ref_id = str(uuid.uuid4())
    
    logger.info(f"Executing tool call {tool_name}")
    logger.debug(f"Arguments: {json.dumps(arguments, indent=2)}")
    
    try:
        # Call the tool
        result: CallToolResult = await session.call_tool(name=tool_name, arguments=arguments)
        logger.info(f"Tool call {tool_name} completed")
        
        if result.isError == True:
            # Tool returned an error
            assert len(result.content) == 1
            content = result.content[0]
            assert isinstance(content, TextContent)
            logger.error(f"Tool call {tool_name} returned an error: {content.text}")
            return False, content.text
        else:
            # Tool succeeded
            text_content = []
            for content_item in result.content:
                if content_item.type == "text":
                    text_content.append(content_item.text)
            return True, text_content
    except Exception as e:
        # Exception during tool call
        logger.error(f"Tool call {tool_name} failed with exception: {e}")
        return False, str(e)

async def run_client():
    """Connect to the MCP server and demonstrate error handling"""
    logger.info("Starting MCP Error Handling client")
    
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
                
                print("\n" + "=" * 60)
                print("ERROR HANDLING EXAMPLE")
                print("=" * 60)
                
                # Test error handling with different scenarios
                print("\nTesting error handling with different scenarios:")
                print("-" * 60)
                
                # Scenario 1: Basic error with default message
                print("\nScenario 1: Basic error with default message")
                success, result = await execute_tool_call(session, "get_error", {})
                print(f"Success: {success}")
                print(f"Result: {result}")
                
                # Scenario 2: Error with custom message
                print("\nScenario 2: Error with custom message")
                success, result = await execute_tool_call(session, "get_error", {
                    "message": "This is a custom error message"
                })
                print(f"Success: {success}")
                print(f"Result: {result}")
                
                # Scenario 3: Call non-existent tool
                print("\nScenario 3: Call non-existent tool")
                success, result = await execute_tool_call(session, "non_existent_tool", {})
                print(f"Success: {success}")
                print(f"Result: {result}")
                
                print("=" * 60)
                print("All error handling tests completed!")
                print("=" * 60)
                
            else:
                logger.info("No tools advertised by the server")
                print("No tools were advertised by the server.")
                
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
