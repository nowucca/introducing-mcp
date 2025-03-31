#!/usr/bin/env python3
import asyncio
import json
import logging
import uuid
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

import pytz
import websockets
from websockets.server import WebSocketServerProtocol

# Import MCP types for proper protocol formatting
from mcp.types import Tool, ListToolsResult, JSONRPCRequest, JSONRPCResponse, JSONRPCError, LATEST_PROTOCOL_VERSION

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='SERVER %(levelname)5s [%(asctime)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define our tools
error_tool = Tool(
    name="get_error",
    description="This tool always fails (for error handling demonstration)",
    inputSchema={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Optional custom error message"
            }
        }
    }
)

time_tool = Tool(
    name="get_time",
    description="Returns the current time in the specified timezone",
    inputSchema={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Timezone name (e.g., 'US/Pacific', 'Europe/London', 'Asia/Tokyo')"
            }
        }
    }
)

weather_tool = Tool(
    name="get_weather",
    description="Get weather information for a city",
    inputSchema={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name (e.g., 'New York', 'London', 'Tokyo')"
            }
        },
        "required": ["city"]
    }
)

async def handle_message(websocket: WebSocketServerProtocol):
    """Handle incoming messages from clients"""
    client_address = websocket.remote_address
    logger.info(f"New connection from {client_address}")
    logger.debug(f"Client connected from {client_address[0]}:{client_address[1]}")
    
    # Track whether this connection has been initialized
    initialized = False
    
    try:
        async for message in websocket:
            logger.info(f"Received message from client")
            logger.debug(f"Raw message: {message}")
            
            # Parse the message as JSON
            try:
                data = json.loads(message)
                logger.debug(f"Parsed JSON: {json.dumps(data, indent=2)}")
                
                # Check if it's a valid JSON-RPC request
                if "jsonrpc" in data and data["jsonrpc"] == "2.0" and "method" in data:
                    
                    # Handle requests (has "id")
                    if "id" in data:
                        request = JSONRPCRequest(
                            jsonrpc="2.0",
                            id=data.get("id"),
                            method=data["method"],
                            params=data.get("params", {})
                        )
                        logger.debug(f"Handling request: method={request.method}, id={request.id}")
                        
                        # Handle different method requests
                        if request.method == "initialize":
                            logger.info(f"Processing initialize request")
                            logger.debug(f"Initialize params: {json.dumps(request.params, indent=2)}")
                            
                            # Respond to initialize request
                            response = JSONRPCResponse(
                                jsonrpc="2.0",
                                id=request.id,
                                result={
                                    "protocolVersion": LATEST_PROTOCOL_VERSION,
                                    "serverInfo": {
                                        "name": "MCP Multiple Tools Server",
                                        "version": "0.1.0"
                                    },
                                    "capabilities": {
                                        "tools": {
                                            "listChanged": True  # We support tool list changed notifications
                                        }
                                    }
                                }
                            )
                            response_json = json.dumps(response.model_dump(exclude_none=True))
                            logger.debug(f"Initialize response: {response_json}")
                            await websocket.send(response_json)
                            
                            # Do NOT send initialized notification - wait for client to send it
                            logger.info("Sent initialize response, waiting for client's initialized notification")
                            logger.debug("Server is now waiting for client to send notifications/initialized")
                            
                        elif not initialized:
                            # We must not respond to any requests before initialization
                            logger.warning(f"Received request {request.method} before initialization")
                            error_response = {
                                "jsonrpc": "2.0",
                                "id": request.id,
                                "error": {
                                    "code": -32002,  # Server not initialized
                                    "message": "Server not initialized"
                                }
                            }
                            logger.debug(f"Sending error response: {json.dumps(error_response, indent=2)}")
                            await websocket.send(json.dumps(error_response))
                            
                        elif request.method == "tools/list":
                            logger.info(f"Processing tools/list request")
                            # Respond with our tool advertisements
                            tools_result = ListToolsResult(tools=[time_tool, weather_tool, error_tool])
                            response = JSONRPCResponse(
                                jsonrpc="2.0",
                                id=request.id,
                                result=tools_result.model_dump()
                            )
                            response_json = json.dumps(response.model_dump(exclude_none=True))
                            logger.debug(f"Tools list response: {response_json}")
                            await websocket.send(response_json)
                            logger.info("Sent tool advertisements")
                        
                        elif request.method == "tools/call":
                            logger.info(f"Processing tools/call request")
                            logger.debug(f"Tool call params: {json.dumps(request.params, indent=2)}")
                            
                            # Extract tool name and arguments
                            tool_name = request.params.get("name")
                            arguments = request.params.get("arguments", {})
                            
                            if tool_name == "get_time":
                                # Get the timezone if provided, otherwise use UTC
                                timezone_str = arguments.get("timezone", "UTC")
                                
                                try:
                                    # Get the timezone object
                                    timezone = pytz.timezone(timezone_str)
                                    
                                    # Get the current time in the specified timezone
                                    current_time = datetime.now(timezone).strftime("%H:%M:%S %Z")
                                    logger.info(f"Current time in {timezone_str}: {current_time}")
                                    
                                    # Send the response
                                    response = JSONRPCResponse(
                                        jsonrpc="2.0",
                                        id=request.id,
                                        result={
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": f"The current time in {timezone_str} is: {current_time}"
                                                }
                                            ]
                                        }
                                    )
                                    response_json = json.dumps(response.model_dump(exclude_none=True))
                                    logger.debug(f"Tool call response: {response_json}")
                                    await websocket.send(response_json)
                                    logger.info("Sent time tool response")
                                except pytz.exceptions.UnknownTimeZoneError:
                                    # Invalid timezone
                                    logger.warning(f"Unknown timezone: {timezone_str}")
                                    response = JSONRPCError(
                                        jsonrpc="2.0",
                                        id=request.id,
                                        error={
                                            "code": -32602,
                                            "message": f"Invalid timezone: {timezone_str}"
                                        }
                                    )
                                    response_json = json.dumps(response.model_dump(exclude_none=True))
                                    logger.debug(f"Invalid timezone response: {response_json}")
                                    await websocket.send(response_json)
                            
                            elif tool_name == "get_error":
                                # Get the message if provided
                                message = arguments.get("message", "Default error message")
                                error_msg = f"Intentional error triggered: {message}"
                                logger.error(error_msg)
                                
                                # Return error response
                                response = JSONRPCError(
                                    jsonrpc="2.0",
                                    id=request.id,
                                    error={
                                        "code": -32000,
                                        "message": error_msg
                                    }
                                )
                                response_json = json.dumps(response.model_dump(exclude_none=True))
                                logger.debug(f"Error tool response: {response_json}")
                                await websocket.send(response_json)
                                logger.info("Sent error tool response")
                            
                            elif tool_name == "get_weather":
                                # Get the city parameter
                                city = arguments.get("city", "")
                                
                                if not city:
                                    # Missing required parameter
                                    logger.warning("Missing required city parameter")
                                    response = JSONRPCError(
                                        jsonrpc="2.0",
                                        id=request.id,
                                        error={
                                            "code": -32602,
                                            "message": "Missing required parameter: city"
                                        }
                                    )
                                    response_json = json.dumps(response.model_dump(exclude_none=True))
                                    logger.debug(f"Missing parameter response: {response_json}")
                                    await websocket.send(response_json)
                                else:
                                    # In a real implementation, this would call a weather API
                                    # For this example, we'll just return a hardcoded response
                                    weather_info = f"Sunny in {city}"
                                    logger.info(f"Weather in {city}: {weather_info}")
                                    
                                    # Send the response
                                    response = JSONRPCResponse(
                                        jsonrpc="2.0",
                                        id=request.id,
                                        result={
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": weather_info
                                                }
                                            ]
                                        }
                                    )
                                    response_json = json.dumps(response.model_dump(exclude_none=True))
                                    logger.debug(f"Tool call response: {response_json}")
                                    await websocket.send(response_json)
                                    logger.info("Sent weather tool response")
                            
                            else:
                                # Unknown tool
                                logger.warning(f"Unknown tool requested: {tool_name}")
                                response = JSONRPCError(
                                    jsonrpc="2.0",
                                    id=request.id,
                                    error={
                                        "code": -32601,
                                        "message": f"Tool not found: {tool_name}"
                                    }
                                )
                                response_json = json.dumps(response.model_dump(exclude_none=True))
                                logger.debug(f"Tool not found response: {response_json}")
                                await websocket.send(response_json)
                        
                        else:
                            # Unknown method
                            logger.warning(f"Unknown method requested: {request.method}")
                            response = JSONRPCError(
                                jsonrpc="2.0",
                                id=request.id,
                                error={
                                    "code": -32601,
                                    "message": f"Method not found: {request.method}"
                                }
                            )
                            response_json = json.dumps(response.model_dump(exclude_none=True))
                            logger.debug(f"Method not found response: {response_json}")
                            await websocket.send(response_json)
                    
                    # Handle notifications from client (no "id")
                    elif "method" in data:
                        logger.debug(f"Handling notification: method={data['method']}")
                        
                        if data["method"] == "notifications/initialized":
                            logger.info("Received initialized notification from client")
                            logger.debug(f"Initialized notification params: {json.dumps(data.get('params', {}), indent=2)}")
                            
                            # NOW we can mark as initialized
                            initialized = True
                            logger.debug("Connection marked as initialized")
                            
                            # Send tool list changed notification after receiving initialized
                            tools_notification = {
                                "jsonrpc": "2.0", 
                                "method": "notifications/tools/list_changed",
                                "params": {}
                            }
                            notification_json = json.dumps(tools_notification)
                            logger.debug(f"Sending tools/list_changed notification: {notification_json}")
                            await websocket.send(notification_json)
                            logger.info("Sent tools/list_changed notification")
                        
                        elif data["method"] == "notifications/cancelled":
                            request_id = data.get("params", {}).get("requestId")
                            logger.info(f"Received cancellation for request: {request_id}")
                            logger.debug(f"Cancellation notification params: {json.dumps(data.get('params', {}), indent=2)}")
                        
                        else:
                            logger.info(f"Received unhandled notification: {data['method']}")
                            logger.debug(f"Unhandled notification params: {json.dumps(data.get('params', {}), indent=2)}")
                
                else:
                    logger.warning(f"Unknown message format received")
                    logger.debug(f"Unknown format data: {json.dumps(data, indent=2)}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received")
                logger.debug(f"JSON decode error: {str(e)}, message: {message}")
            except Exception as e:
                logger.error(f"Error processing message: {type(e).__name__}: {e}")
                logger.debug(f"Exception details: {traceback.format_exc()}")
    
    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"Connection closed: {e}")
        logger.debug(f"WebSocket connection closed with code: {e.code}, reason: {e.reason}")
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        logger.debug(f"Exception details: {traceback.format_exc()}")

async def main():
    """Start the WebSocket server"""
    host = "localhost"
    port = 8765
    
    logger.info(f"Starting MCP server on ws://{host}:{port}")
    logger.debug(f"Server binding to {host}:{port}")
    logger.info(f"Server has 3 tools registered:")
    logger.info(f"  - {time_tool.name}: {time_tool.description}")
    logger.info(f"  - {weather_tool.name}: {weather_tool.description}")
    logger.info(f"  - {error_tool.name}: {error_tool.description}")
    logger.debug(f"Time tool details: {json.dumps(time_tool.model_dump(), indent=2)}")
    logger.debug(f"Weather tool details: {json.dumps(weather_tool.model_dump(), indent=2)}")
    logger.debug(f"Error tool details: {json.dumps(error_tool.model_dump(), indent=2)}")
    
    async with websockets.serve(handle_message, host, port):
        logger.info(f"WebSocket server started successfully")
        # Keep the server running indefinitely
        await asyncio.Future()

if __name__ == "__main__":
    try:
        logger.info("Initializing MCP WebSocket server")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {type(e).__name__}: {e}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
