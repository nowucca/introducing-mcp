#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
import json
import traceback
from contextlib import AsyncExitStack
from typing import Dict, Any

import pytz
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='CLIENT: %(message)s')
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

async def run_client():
    """Connect to the MCP server, list tools, and let the LLM decide whether to call them"""
    logger.info("Starting MCP Context Memory client")
    
    # Check if OpenAI API key is set
    if not openai_api_key or openai_api_key == "your-api-key":
        logger.error("OpenAI API key not set")
        print("\nERROR: OpenAI API key not set. Please set your API key in the .env file.")
        print("Create a .env file with the following content:")
        print("OPENAI_API_KEY=your-api-key")
        print("OPENAI_BASE_URL=https://api.openai.com/v1")
        print("OPENAI_MODEL=gpt-4o\n")
        return 1
    
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
                
                # Convert MCP tools to OpenAI function format
                openai_tools = []
                for tool in tools_response.tools:
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}}
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
                                tool_result = await asyncio.wait_for(
                                    session.call_tool(name=tool_name, arguments=filled_args),
                                    timeout=10.0
                                )
                                
                                # Display the result
                                if tool_result.content:
                                    for content_item in tool_result.content:
                                        if content_item.type == "text":
                                            print("\n" + "=" * 40)
                                            print("LLM TOOL RESULT:")
                                            print(content_item.text)
                                            print("=" * 40 + "\n")
                                            logger.info(f"Tool result: {content_item.text}")
                                else:
                                    logger.warning("Tool returned no content")
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
