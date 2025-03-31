#!/usr/bin/env python3
import asyncio
import json
import logging
import uuid
import traceback
from typing import Dict, Any, Optional

import websockets

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='CLIENT %(levelname)5s [%(asctime)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def connect_to_server():
    """Connect to the MCP server, list tools, call the time tool, and display the result"""
    uri = "ws://localhost:8765"
    logger.info(f"Connecting to MCP server at {uri}")
    logger.debug(f"Using WebSocket URI: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connection established")
            logger.debug("WebSocket connection successfully established")
            
            # Send initialize request (must be first request)
            logger.info("Sending initialize request")
            init_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {
                        "name": "MCP Time Tool Client",
                        "version": "0.1.0"
                    },
                    "capabilities": {
                        "tools": {
                            "listChanged": True  # We support tool list changed notifications
                        }
                    }
                }
            }
            logger.debug(f"Initialize request payload: {json.dumps(init_request, indent=2)}")
            await websocket.send(json.dumps(init_request))
            
            # Wait for initialize response
            response = await websocket.recv()
            logger.info(f"Received initialize response")
            logger.debug(f"Initialize response payload: {response}")
            
            # Send initialized notification to server
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            logger.debug(f"Initialized notification payload: {json.dumps(initialized_notification, indent=2)}")
            await websocket.send(json.dumps(initialized_notification))
            logger.info("Sent initialized notification to server")
            
            # The server should send a tools/list_changed notification right after initialized
            try:
                tools_changed = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                logger.info(f"Received notification from server")
                logger.debug(f"Notification payload: {tools_changed}")
                
                # Check if it's a tools/list_changed notification
                try:
                    notif_data = json.loads(tools_changed)
                    if "method" in notif_data and notif_data["method"] == "notifications/tools/list_changed":
                        logger.info("Received tools/list_changed notification")
                        logger.debug("Notification type confirmed as tools/list_changed")
                    else:
                        logger.info(f"Received unexpected notification: {notif_data.get('method', 'unknown')}")
                        logger.debug(f"Expected tools/list_changed but got: {notif_data.get('method', 'unknown')}")
                except json.JSONDecodeError:
                    logger.error("Failed to parse notification")
                    logger.debug(f"JSON parse error on notification: {tools_changed}")
            except asyncio.TimeoutError:
                logger.info("No tools/list_changed notification received within timeout")
                logger.debug("Timed out after 1.0 seconds waiting for tools/list_changed notification")
            
            # Request the tools list
            logger.info("Requesting tool list")
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list",
                "params": {}
            }
            logger.debug(f"Tools list request payload: {json.dumps(list_tools_request, indent=2)}")
            await websocket.send(json.dumps(list_tools_request))
            
            # Wait for tools response
            tools_response = await websocket.recv()
            logger.info(f"Received tools response from server")
            logger.debug(f"Tools response payload: {tools_response}")
            
            # Parse and display tools
            tools = []
            try:
                tools_data = json.loads(tools_response)
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    logger.info(f"Server advertised {len(tools)} tools:")
                    for tool in tools:
                        logger.info(f"  - {tool['name']}: {tool['description']}")
                    logger.debug(f"Full tools data: {json.dumps(tools, indent=2)}")
                    logger.info("Tool advertisement received successfully!")
                else:
                    logger.info("No tools advertised by the server")
                    logger.debug(f"Response contained no tools: {json.dumps(tools_data, indent=2)}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing tools response: {e}")
                logger.debug(f"Parse error details: {str(e)}, response: {tools_response}")
            
            # Call the time tool if it was advertised
            time_tool = next((tool for tool in tools if tool["name"] == "get_time"), None)
            if time_tool:
                logger.info("Calling the get_time tool")
                tool_call_request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": "get_time",
                        "arguments": {}  # Using default format
                    }
                }
                logger.debug(f"Tool call request payload: {json.dumps(tool_call_request, indent=2)}")
                await websocket.send(json.dumps(tool_call_request))
                
                # Wait for tool call response
                tool_response = await websocket.recv()
                logger.info(f"Received tool call response")
                logger.debug(f"Tool response payload: {tool_response}")
                
                # Parse and display the time
                try:
                    response_data = json.loads(tool_response)
                    if "result" in response_data and "content" in response_data["result"]:
                        content = response_data["result"]["content"]
                        for item in content:
                            if item["type"] == "text":
                                print("\n" + "=" * 40)
                                print(item["text"])
                                print("=" * 40 + "\n")
                                logger.info(f"Time tool result: {item['text']}")
                    else:
                        logger.error("Invalid tool response format")
                        logger.debug(f"Expected 'result.content' in response: {json.dumps(response_data, indent=2)}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error parsing tool response: {e}")
                    logger.debug(f"Parse error details: {str(e)}, response: {tool_response}")
            else:
                logger.warning("The get_time tool was not advertised by the server")
            
            logger.info("MCP protocol exchange completed successfully")
            
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"Connection closed: {e}")
        logger.debug(f"WebSocket connection closed with code: {e.code}, reason: {e.reason}")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.debug(f"Exception details: {type(e).__name__}, {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")

def main():
    """Entry point function"""
    try:
        logger.info("Starting MCP WebSocket client")
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
    exit_code = main()
    exit(exit_code)
