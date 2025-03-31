#!/usr/bin/env python3
import asyncio
import json
import logging
import sys
import os
import uuid
import traceback
from contextlib import AsyncExitStack
from typing import Dict, Any, List, Tuple

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='CLIENT: %(message)s')
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

async def execute_tool_call(session, tool_call):
    """Execute a single tool call and return the result with its reference
    
    Args:
        session: The MCP ClientSession
        tool_call: Dictionary containing tool name and arguments
        
    Returns:
        Tuple of (tool_call, result/exception)
    """
    ref_id = str(uuid.uuid4())
    tool_name = tool_call["name"]
    arguments = tool_call["arguments"]
    
    logger.info(f"Queuing tool call {tool_name} with ref_id {ref_id}")
    logger.debug(f"Arguments: {json.dumps(arguments, indent=2)}")
    
    try:
        # Direct call without callback
        result = await session.call_tool(name=tool_name, arguments=arguments)
        logger.info(f"Tool call {tool_name} (ref_id {ref_id}) succeeded")
        return tool_call, result
    except Exception as e:
        logger.error(f"Tool call {tool_name} (ref_id {ref_id}) failed: {e}")
        return tool_call, e

async def do_plan(session, plan):
    """Execute a plan of multiple tool calls concurrently
    
    Args:
        session: The MCP ClientSession
        plan: A list of tool call specifications, each with name and arguments
        
    Returns:
        List of results from all tool calls
    """
    logger.info(f"Executing plan with {len(plan)} tool calls")
    logger.debug(f"Plan details: {json.dumps(plan, indent=2)}")
    
    # Create a list of coroutines to execute
    coroutines = [execute_tool_call(session, tool_call) for tool_call in plan]
    
    # Execute all tool calls concurrently and wait for all results
    logger.info(f"Waiting for {len(plan)} tool call results")
    results = await asyncio.gather(*coroutines, return_exceptions=False)
    
    # Process results
    processed_results = []
    for tool_call, result in results:
        if isinstance(result, Exception):
            processed_results.append({
                "tool": tool_call["name"],
                "success": False,
                "error": str(result)
            })
        else:
            # Extract text from content items
            text_content = []
            if hasattr(result, "content"):
                for content_item in result.content:
                    if content_item.type == "text":
                        text_content.append(content_item.text)
            
            processed_results.append({
                "tool": tool_call["name"],
                "success": True,
                "result": text_content
            })
    
    return processed_results

async def run_client():
    """Connect to the MCP server and execute a plan of tool calls"""
    logger.info("Starting MCP Agent Parallel client")
    
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
                
                # Define our plan of tool calls to execute concurrently
                plan = [
                    {"name": "get_time", "arguments": {}},
                    {"name": "get_weather", "arguments": {"city": "Tokyo"}}
                ]
                
                print("\n" + "=" * 60)
                print("EXECUTING PLAN OF PARALLEL TOOL CALLS")
                print("=" * 60)
                print(f"Plan contains {len(plan)} tool calls:")
                for i, tool_call in enumerate(plan):
                    print(f"  {i+1}. {tool_call['name']}({json.dumps(tool_call['arguments'])})")
                print("-" * 60)
                
                # Execute the plan
                results = await do_plan(session, plan)
                
                # Display results
                print("\nRESULTS OF PARALLEL EXECUTION:")
                print("-" * 60)
                for i, result in enumerate(results):
                    print(f"Tool {i+1}: {result['tool']}")
                    if result['success']:
                        for text in result['result']:
                            print(f"  → {text}")
                    else:
                        print(f"  → ERROR: {result['error']}")
                print("=" * 60)
                print("All tool calls completed concurrently!")
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
