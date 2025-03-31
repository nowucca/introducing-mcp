#!/usr/bin/env python3
import asyncio
import json
import logging
import uuid
import os
import traceback
from typing import Dict, Any, Optional, List

import pytz
import websockets
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='CLIENT %(levelname)5s [%(asctime)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables for OpenAI
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")

# Create OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url
)

# Client memory - stores user preferences and context
memory = {
    "timezone": "America/New_York"  # Default timezone (US Eastern)
}

# City to timezone mapping for common cities
CITY_TO_TIMEZONE = {
    # North America
    "new york": "America/New_York",
    "boston": "America/New_York",
    "washington": "America/New_York",
    "atlanta": "America/New_York",
    "miami": "America/New_York",
    "chicago": "America/Chicago",
    "dallas": "America/Chicago",
    "houston": "America/Chicago",
    "denver": "America/Denver",
    "phoenix": "America/Phoenix",
    "los angeles": "America/Los_Angeles",
    "san francisco": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",
    "vancouver": "America/Vancouver",
    "toronto": "America/Toronto",
    "montreal": "America/Montreal",
    
    # Europe
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "rome": "Europe/Rome",
    "madrid": "Europe/Madrid",
    "amsterdam": "Europe/Amsterdam",
    "brussels": "Europe/Brussels",
    "zurich": "Europe/Zurich",
    "stockholm": "Europe/Stockholm",
    "oslo": "Europe/Oslo",
    "helsinki": "Europe/Helsinki",
    "athens": "Europe/Athens",
    "moscow": "Europe/Moscow",
    
    # Asia
    "tokyo": "Asia/Tokyo",
    "osaka": "Asia/Tokyo",
    "seoul": "Asia/Seoul",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "hong kong": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei",
    "singapore": "Asia/Singapore",
    "bangkok": "Asia/Bangkok",
    "mumbai": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "dubai": "Asia/Dubai",
    
    # Australia/Pacific
    "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "brisbane": "Australia/Brisbane",
    "perth": "Australia/Perth",
    "auckland": "Pacific/Auckland",
    "wellington": "Pacific/Auckland",
    
    # South America
    "sao paulo": "America/Sao_Paulo",
    "rio de janeiro": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "santiago": "America/Santiago",
    "lima": "America/Lima",
    "bogota": "America/Bogota",
    
    # Africa
    "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg",
    "lagos": "Africa/Lagos",
    "nairobi": "Africa/Nairobi",
    "casablanca": "Africa/Casablanca"
}

def get_timezone_for_city(city_name: str) -> str:
    """Get the timezone for a given city name
    
    Args:
        city_name: The name of the city
        
    Returns:
        The timezone string for the city, or None if not found
    """
    if not city_name:
        return None
        
    # Normalize the city name (lowercase, remove extra spaces)
    normalized_name = city_name.lower().strip()
    
    # Check if the city is in our mapping
    if normalized_name in CITY_TO_TIMEZONE:
        timezone = CITY_TO_TIMEZONE[normalized_name]
        logger.info(f"Mapped city '{city_name}' to timezone '{timezone}'")
        return timezone
    
    # If we don't have a mapping, return None
    logger.info(f"No timezone mapping found for city '{city_name}'")
    return None

def is_valid_timezone(timezone_str: str) -> bool:
    """Check if a timezone string is valid
    
    Args:
        timezone_str: The timezone string to check
        
    Returns:
        True if the timezone is valid, False otherwise
    """
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False

def fill_args_if_missing(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Fill in missing arguments from memory
    
    Args:
        arguments: The original arguments dictionary
        
    Returns:
        The arguments dictionary with missing values filled from memory
    """
    # Make a copy to avoid modifying the original
    filled_args = arguments.copy()
    
    # Check if there's a city parameter that we can map to a timezone
    if "city" in filled_args and "timezone" not in filled_args:
        timezone = get_timezone_for_city(filled_args["city"])
        if timezone:
            filled_args["timezone"] = timezone
            logger.info(f"Added timezone '{timezone}' based on city '{filled_args['city']}'")
            # Remove the city parameter as it's not part of the tool's schema
            del filled_args["city"]
    
    # Check if the timezone is valid, if not, use the one from memory
    if "timezone" in filled_args and not is_valid_timezone(filled_args["timezone"]):
        logger.info(f"Invalid timezone '{filled_args['timezone']}', using default from memory")
        filled_args["timezone"] = memory["timezone"]
        logger.info(f"Replaced with timezone from memory: {memory['timezone']}")
    
    # Add timezone from memory if not provided
    if "timezone" not in filled_args and "timezone" in memory:
        filled_args["timezone"] = memory["timezone"]
        logger.info(f"Added timezone from memory: {memory['timezone']}")
    
    return filled_args

async def connect_to_server():
    """Connect to the MCP server, list tools, and let the LLM decide whether to call them"""
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
                        "name": "MCP Context Memory WebSocket Client",
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
            
            # Parse and store tools
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
            
            # Convert MCP tools to OpenAI function format
            openai_tools = []
            for tool in tools:
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
                    }
                }
                openai_tools.append(openai_tool)
            
            # Display current memory
            print("\nCurrent memory settings:")
            for key, value in memory.items():
                print(f"  - {key}: {value}")
            
            # Get user input
            user_input = input("\nWhat would you like the assistant to do? ")
            logger.info(f"User input: {user_input}")
            
            # Send user input to OpenAI with tools
            logger.info("Sending user input to OpenAI with tools")
            try:
                # Add a system message to encourage tool use
                system_message = "You are a helpful assistant that provides the current time. When asked about the time, always use the get_time tool, even if no timezone is specified. The client will automatically fill in any missing parameters."
                
                completion = client.chat.completions.create(
                    model=openai_model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_input}
                    ],
                    tools=openai_tools,
                    tool_choice="auto"
                )
                
                # Check if the LLM decided to call a tool
                if completion.choices[0].message.tool_calls:
                    logger.info("LLM decided to call a tool")
                    
                    for tool_call in completion.choices[0].message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            # Parse the original arguments
                            original_args = json.loads(tool_call.function.arguments)
                            logger.info(f"Original arguments: {json.dumps(original_args, indent=2)}")
                            
                            # Fill in missing arguments from memory
                            filled_args = fill_args_if_missing(original_args)
                            logger.info(f"Arguments after filling: {json.dumps(filled_args, indent=2)}")
                            
                            # Call the tool with filled arguments
                            tool_call_request = {
                                "jsonrpc": "2.0",
                                "id": str(uuid.uuid4()),
                                "method": "tools/call",
                                "params": {
                                    "name": tool_name,
                                    "arguments": filled_args
                                }
                            }
                            logger.debug(f"Tool call request payload: {json.dumps(tool_call_request, indent=2)}")
                            await websocket.send(json.dumps(tool_call_request))
                            
                            # Wait for tool call response
                            tool_response = await websocket.recv()
                            logger.info(f"Received tool call response")
                            logger.debug(f"Tool response payload: {tool_response}")
                            
                            # Parse and display the result
                            try:
                                response_data = json.loads(tool_response)
                                if "result" in response_data and "content" in response_data["result"]:
                                    content = response_data["result"]["content"]
                                    for item in content:
                                        if item["type"] == "text":
                                            print("\n" + "=" * 40)
                                            print("LLM TOOL RESULT:")
                                            print(item["text"])
                                            print("=" * 40 + "\n")
                                            logger.info(f"Tool result: {item['text']}")
                                else:
                                    logger.error("Invalid tool response format")
                                    logger.debug(f"Expected 'result.content' in response: {json.dumps(response_data, indent=2)}")
                            except (json.JSONDecodeError, KeyError) as e:
                                logger.error(f"Error parsing tool response: {e}")
                                logger.debug(f"Parse error details: {str(e)}, response: {tool_response}")
                        except json.JSONDecodeError:
                            logger.error("Failed to parse tool arguments")
                            logger.debug(f"JSON parse error on arguments: {tool_call.function.arguments}")
                else:
                    # LLM decided not to call a tool
                    logger.info("LLM decided not to call a tool")
                    print("\n" + "=" * 40)
                    print("LLM RESPONSE:")
                    print(completion.choices[0].message.content)
                    print("=" * 40 + "\n")
                    logger.info(f"LLM response: {completion.choices[0].message.content}")
            
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                logger.debug(f"OpenAI API error details: {traceback.format_exc()}")
                print(f"\nError calling OpenAI API: {e}")
            
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
        # Check if OpenAI API key is set
        if not openai_api_key or openai_api_key == "your-api-key":
            print("\nERROR: OpenAI API key not set. Please set your API key in the .env file.")
            print("Create a .env file with the following content:")
            print("OPENAI_API_KEY=your-api-key")
            print("OPENAI_BASE_URL=https://api.openai.com/v1")
            print("OPENAI_MODEL=gpt-4o\n")
            return 1
            
        logger.info("Starting MCP Context Memory WebSocket client")
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
