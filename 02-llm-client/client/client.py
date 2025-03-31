#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
import json
import traceback
from contextlib import AsyncExitStack

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

async def run_client():
    """Connect to the MCP server, list tools, and let the LLM decide whether to call them"""
    logger.info("Starting MCP LLM client")
    
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
                
                # Get user input
                user_input = input("\nWhat would you like the assistant to do? ")
                logger.info(f"User input: {user_input}")
                
                # Send user input to OpenAI with tools
                logger.info("Sending user input to OpenAI with tools")
                try:
                    completion = client.chat.completions.create(
                        model=openai_model,
                        messages=[{"role": "user", "content": user_input}],
                        tools=openai_tools,
                        tool_choice="auto"
                    )
                    
                    # Check if the LLM decided to call a tool
                    if completion.choices[0].message.tool_calls:
                        logger.info("LLM decided to call a tool")
                        
                        for tool_call in completion.choices[0].message.tool_calls:
                            tool_name = tool_call.function.name
                            try:
                                arguments = json.loads(tool_call.function.arguments)
                            except json.JSONDecodeError:
                                arguments = {}
                            
                            logger.info(f"Calling tool: {tool_name} with arguments: {json.dumps(arguments, indent=2)}")
                            
                            # Call the tool
                            tool_result = await asyncio.wait_for(
                                session.call_tool(name=tool_name, arguments=arguments),
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
