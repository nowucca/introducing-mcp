#!/usr/bin/env python3
import asyncio
import json
import logging
import uuid
import os
import sys
import traceback
from typing import Dict, Any, List, Optional

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

# Load .env file
load_dotenv()

# Load environment variables for OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")

# Create OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url
)

# Dictionary to store pending requests
pending_requests = {}  # ref_id → future

async def execute_tool_call(websocket, tool_call):
    """Execute a single tool call and return the result with its reference
    
    Args:
        websocket: WebSocket connection
        tool_call: Dictionary containing tool name and arguments
        
    Returns:
        Tuple of (tool_call, result/exception)
    """
    ref_id = str(uuid.uuid4())
    tool_name = tool_call["name"]
    arguments = tool_call["arguments"]
    
    logger.info(f"Queuing tool call {tool_name} with ref_id {ref_id}")
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
        logger.info(f"Tool call {tool_name} (ref_id {ref_id}) succeeded")
        return tool_call, result
    except Exception as e:
        logger.error(f"Tool call {tool_name} (ref_id {ref_id}) failed: {e}")
        return tool_call, e

async def do_plan(websocket, plan):
    """Execute a plan of multiple tool calls concurrently
    
    Args:
        websocket: WebSocket connection
        plan: A list of tool call specifications, each with name and arguments
        
    Returns:
        List of results from all tool calls
    """
    logger.info(f"Executing plan with {len(plan)} tool calls")
    logger.debug(f"Plan details: {json.dumps(plan, indent=2)}")
    
    # Create a list of coroutines to execute
    coroutines = [execute_tool_call(websocket, tool_call) for tool_call in plan]
    
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
            if isinstance(result, dict) and "content" in result:
                for content_item in result["content"]:
                    if content_item.get("type") == "text":
                        text_content.append(content_item["text"])
            
            processed_results.append({
                "tool": tool_call["name"],
                "success": True,
                "result": text_content
            })
    
    return processed_results

async def generate_plan_with_llm(tools, query):
    """Use the LLM to generate a plan of tool calls based on the user query
    
    Args:
        tools: List of available tools
        query: User query string
        
    Returns:
        List of tool call specifications
    """
    logger.info(f"Generating plan with LLM for query: {query}")
    
    # Check if OpenAI API key is set
    if not openai_api_key or openai_api_key == "your-api-key":
        logger.error("OpenAI API key not set")
        print("\nERROR: OpenAI API key not set. Please set your API key in the .env file.")
        print("Create a .env file with the following content:")
        print("OPENAI_API_KEY=your-api-key")
        print("OPENAI_BASE_URL=https://api.openai.com/v1")
        print("OPENAI_MODEL=gpt-4o\n")
        return []
    
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
    
    # Send query to OpenAI with tools
    logger.info("Sending query to OpenAI with tools")
    try:
        completion = client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": query}],
            tools=openai_tools,
            tool_choice="auto"
        )
        
        # Check if the LLM decided to call tools
        if completion.choices[0].message.tool_calls:
            logger.info("LLM generated a plan with tool calls")
            
            # Extract tool calls from the response
            plan = []
            for tool_call in completion.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                plan.append({
                    "name": tool_name,
                    "arguments": arguments
                })
            
            logger.info(f"Generated plan with {len(plan)} tool calls")
            logger.debug(f"Plan details: {json.dumps(plan, indent=2)}")
            return plan
        else:
            # LLM decided not to call any tools
            logger.info("LLM decided not to call any tools")
            logger.debug(f"LLM response: {completion.choices[0].message.content}")
            return []
    
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        logger.debug(f"OpenAI API error details: {traceback.format_exc()}")
        return []

async def connect_to_server():
    """Connect to the MCP server and execute a plan of tool calls"""
    uri = "ws://localhost:8765"
    logger.info(f"Connecting to MCP server at {uri}")
    logger.debug(f"Using WebSocket URI: {uri}")
    
    # Check if OpenAI API key is set
    if not openai_api_key or openai_api_key == "your-api-key":
        logger.error("OpenAI API key not set")
        print("\nERROR: OpenAI API key not set. Please set your API key in the .env file.")
        print("Create a .env file with the following content:")
        print("OPENAI_API_KEY=your-api-key")
        print("OPENAI_BASE_URL=https://api.openai.com/v1")
        print("OPENAI_MODEL=gpt-4o\n")
        return 1
    
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
                        "name": "MCP Agent Planning WebSocket Client",
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
                
                # The server might send a tools/list_changed notification right after initialized
                # We handle it in the message handler task
                
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
                    
                    # Define our user query (hardcoded for this example)
                    user_query = "What's the weather and time in Sydney, Australia?"
                    
                    print("\n" + "=" * 60)
                    print("AGENT PLANNING EXAMPLE")
                    print("=" * 60)
                    print(f"User Query: {user_query}")
                    print("-" * 60)
                    
                    # Generate a plan using the LLM
                    print("Generating plan with LLM...")
                    plan = await generate_plan_with_llm(tools, user_query)
                    
                    if plan:
                        # Display the plan
                        print("\nLLM-GENERATED PLAN:")
                        print("-" * 60)
                        for i, tool_call in enumerate(plan):
                            print(f"  {i+1}. {tool_call['name']}({json.dumps(tool_call['arguments'])})")
                        print("-" * 60)
                        
                        # Execute the plan
                        print("\nExecuting plan...")
                        results = await do_plan(websocket, plan)
                        
                        # Display results
                        print("\nRESULTS OF PLAN EXECUTION:")
                        print("-" * 60)
                        for i, result in enumerate(results):
                            print(f"Tool {i+1}: {result['tool']}")
                            if result['success']:
                                for text in result['result']:
                                    print(f"  → {text}")
                            else:
                                print(f"  → ERROR: {result['error']}")
                        print("=" * 60)
                        print("All tool calls completed!")
                        print("=" * 60)
                        
                        # Test error handling with direct tool call
                        print("\nTesting error handling with direct tool call...")
                        print("-" * 60)
                        
                        # Create and execute an error tool call
                        error_tool_call = {
                            "name": "get_error",
                            "arguments": {
                                "message": "This is a test error from client_websocket.py"
                            }
                        }
                        
                        # Execute the error tool call
                        error_result = await execute_tool_call(websocket, error_tool_call)
                        tool_call, result = error_result
                        
                        # Display the result
                        print(f"Error tool test: {error_tool_call['name']}")
                        if isinstance(result, Exception):
                            print(f"  → ERROR (as expected): {str(result)}")
                        else:
                            print(f"  → Unexpected success: {result}")
                        print("=" * 60)
                    else:
                        print("\nThe LLM did not generate any tool calls for this query.")
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
