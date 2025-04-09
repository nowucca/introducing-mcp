#!/usr/bin/env python3
import asyncio
import json
import logging
import uuid
import sys
import traceback
from typing import Dict, Any, Tuple, Optional

import websockets

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='CLIENT %(levelname)5s [%(asctime)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Dictionary to store pending requests
pending_requests = {}  # ref_id → future

async def execute_tool_call(websocket, tool_name, arguments):
    """Execute a tool call and return the result
    
    Args:
        websocket: WebSocket connection
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
        
    Returns:
        Tuple of (success, result/error)
    """
    ref_id = str(uuid.uuid4())
    
    logger.info(f"Executing tool call {tool_name}")
    logger.debug(f"Arguments: {json.dumps(arguments, indent=2)}")
    
    # Prepare the tool call request
    tool_call_request = {
        "jsonrpc": "2.0",
        "id": ref_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    # Create a future to hold the result
    fut = asyncio.get_event_loop().create_future()
    pending_requests[ref_id] = fut
    
    try:
        # Send the request
        await websocket.send(json.dumps(tool_call_request))
        logger.info(f"Sent tool call {tool_name} with ref_id {ref_id}")
        
        # Wait for the response
        result = await fut
        logger.info(f"Tool call {tool_name} completed")
        
        # Check if the result is an error
        if isinstance(result, dict) and "error" in result:
            # Tool returned an error
            error_msg = result["error"]["message"]
            logger.error(f"Tool call {tool_name} returned an error: {error_msg}")
            return False, error_msg
        elif isinstance(result, dict) and "content" in result:
            # Tool succeeded
            text_content = []
            for content_item in result["content"]:
                if content_item.get("type") == "text":
                    text_content.append(content_item["text"])
            return True, text_content
        else:
            # Unexpected result format
            return False, f"Unexpected result format: {result}"
    except Exception as e:
        # Exception during tool call
        logger.error(f"Tool call {tool_name} failed with exception: {e}")
        return False, str(e)

async def connect_to_server():
    """Connect to the MCP server and demonstrate error handling"""
    uri = "ws://localhost:8765"
    logger.info(f"Connecting to MCP server at {uri}")
    logger.debug(f"Using WebSocket URI: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connection established")
            logger.debug("WebSocket connection successfully established")
            
            # Set up response handler
            response_handler_task = asyncio.create_task(handle_server_messages(websocket))
            
            # Send initialize request (must be first request)
            logger.info("Sending initialize request")
            init_id = str(uuid.uuid4())
            init_request = {
                "jsonrpc": "2.0",
                "id": init_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {
                        "name": "MCP Error Handling WebSocket Client",
                        "version": "0.1.0"
                    },
                    "capabilities": {
                        "tools": {
                            "listChanged": True  # We support tool list changed notifications
                        }
                    }
                }
            }
            
            # Create a future for the initialize response
            init_future = asyncio.get_event_loop().create_future()
            pending_requests[init_id] = init_future
            
            logger.debug(f"Initialize request payload: {json.dumps(init_request, indent=2)}")
            await websocket.send(json.dumps(init_request))
            
            # Wait for initialize response
            try:
                init_response = await asyncio.wait_for(init_future, timeout=10.0)
                logger.info(f"Received initialize response")
                logger.debug(f"Initialize response: {json.dumps(init_response, indent=2)}")
                
                # Send initialized notification to server
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                logger.debug(f"Initialized notification payload: {json.dumps(initialized_notification, indent=2)}")
                await websocket.send(json.dumps(initialized_notification))
                logger.info("Sent initialized notification to server")
                
                # Request the tools list
                logger.info("Requesting tool list")
                tools_id = str(uuid.uuid4())
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": tools_id,
                    "method": "tools/list",
                    "params": {}
                }
                
                # Create a future for the tools list response
                tools_future = asyncio.get_event_loop().create_future()
                pending_requests[tools_id] = tools_future
                
                logger.debug(f"Tools list request payload: {json.dumps(list_tools_request, indent=2)}")
                await websocket.send(json.dumps(list_tools_request))
                
                # Wait for tools response
                tools_response = await asyncio.wait_for(tools_future, timeout=10.0)
                logger.info(f"Received tools response from server")
                logger.debug(f"Tools response: {json.dumps(tools_response, indent=2)}")
                
                # Parse and store tools
                tools = []
                if "tools" in tools_response:
                    tools = tools_response["tools"]
                    logger.info(f"Server advertised {len(tools)} tools:")
                    for tool in tools:
                        logger.info(f"  - {tool['name']}: {tool['description']}")
                    
                    print("\n" + "=" * 60)
                    print("ERROR HANDLING EXAMPLE")
                    print("=" * 60)
                    
                    # Test error handling with different scenarios
                    print("\nTesting error handling with different scenarios:")
                    print("-" * 60)
                    
                    # Scenario 1: Basic error with default message
                    print("\nScenario 1: Basic error with default message")
                    success, result = await execute_tool_call(websocket, "get_error", {})
                    print(f"Success: {success}")
                    print(f"Result: {result}")
                    
                    # Scenario 2: Error with custom message
                    print("\nScenario 2: Error with custom message")
                    success, result = await execute_tool_call(websocket, "get_error", {
                        "message": "This is a custom error message"
                    })
                    print(f"Success: {success}")
                    print(f"Result: {result}")
                    
                    # Scenario 3: Call non-existent tool
                    print("\nScenario 3: Call non-existent tool")
                    success, result = await execute_tool_call(websocket, "non_existent_tool", {})
                    print(f"Success: {success}")
                    print(f"Result: {result}")
                    
                    print("=" * 60)
                    print("All error handling tests completed!")
                    print("=" * 60)
                    
                else:
                    logger.info("No tools advertised by the server")
                    logger.debug(f"Response contained no tools: {json.dumps(tools_response, indent=2)}")
                    print("No tools were advertised by the server.")
                
            except asyncio.TimeoutError:
                logger.error("Operation timed out")
                
            # Cancel the message handler
            response_handler_task.cancel()
            try:
                await response_handler_task
            except asyncio.CancelledError:
                pass
                
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"Connection closed: {e}")
        logger.debug(f"WebSocket connection closed with code: {e.code}, reason: {e.reason}")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.debug(f"Exception details: {type(e).__name__}, {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")

async def handle_server_messages(websocket):
    """Process incoming messages from the server"""
    try:
        async for message in websocket:
            logger.info(f"Received message from server")
            logger.debug(f"Raw message: {message}")
            
            try:
                data = json.loads(message)
                
                # Handle JSON-RPC responses (has "id")
                if "id" in data:
                    resp_id = data["id"]
                    logger.debug(f"Processing response for id: {resp_id}")
                    
                    if resp_id in pending_requests:
                        future = pending_requests[resp_id]
                        if "result" in data:
                            future.set_result(data["result"])
                        elif "error" in data:
                            future.set_exception(Exception(data["error"]["message"]))
                        else:
                            future.set_exception(Exception("Malformed response: no result or error"))
                    else:
                        logger.warning(f"Received response for unknown id: {resp_id}")
                
                # Handle notifications (no "id")
                elif "method" in data:
                    logger.debug(f"Processing notification: method={data['method']}")
                    
                    if data["method"] == "notifications/tools/list_changed":
                        logger.info("Received tools/list_changed notification")
                    else:
                        logger.info(f"Received unhandled notification: {data['method']}")
                
                else:
                    logger.warning(f"Unknown message format received")
                    logger.debug(f"Unknown format data: {json.dumps(data, indent=2)}")
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received")
                logger.debug(f"Invalid JSON: {message}")
                
    except asyncio.CancelledError:
        logger.debug("Message handler task cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        logger.debug(f"Exception details: {traceback.format_exc()}")

def main():
    """Entry point function"""
    try:
        logger.info("Starting MCP Agent Planning WebSocket client")
        asyncio.run(connect_to_server())
        return 0
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.debug(f"Unhandled exception details: {type(e).__name__}, {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
