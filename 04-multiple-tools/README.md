# MCP Multiple Tools Example

This example demonstrates how to advertise multiple tools from an MCP server. It builds on the previous examples by adding a second tool to the server.

## Overview

In this example, the server advertises two tools:
1. `get_time` - Returns the current time in a specified timezone
2. `get_weather` - Returns the weather for a specified city

The client connects to the server, receives the tool advertisements, and passes them to the OpenAI API. When the user asks a question, the LLM decides which tool to use based on the query.



## Prerequisites

Before running this example, you need:

1. Python 3.8 or higher
2. An OpenAI API key

## Setup

1. Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Example

You can run this example with either WebSocket transport (default) or SDK transport:

```bash
# On Linux/macOS
# Run with WebSocket transport (default)
./run.sh

# Run with SDK transport
IMPLEMENTATION=sdk ./run.sh
# or
./sdk-run.sh

# On Windows
# Run with WebSocket transport (default)
.\run.ps1

# Run with SDK transport
$env:IMPLEMENTATION="sdk"; .\run.ps1
# or
.\sdk-run.ps1
```

### Running with Docker

Build and run the Docker container:

```bash
# On Linux/macOS
./docker-build.sh
./docker-run.sh

# On Windows
.\docker-build.ps1
.\docker-run.ps1
```

## Example Queries

Try asking the assistant questions like:

- "What is the time in Tokyo?"
- "What is the weather in Tokyo?"
- "Tell me the current time in London"
- "How's the weather in New York?"

## Code Structure

- `server/server.py` - MCP server using stdio transport
- `server/server_websocket.py` - MCP server using WebSocket transport
- `client/client.py` - MCP client using stdio transport
- `client/client_websocket.py` - MCP client using WebSocket transport

## Key Concepts

1. **Multiple Tool Registration**: The server registers multiple tools that can be advertised to clients.
2. **Tool Selection by LLM**: The LLM decides which tool to use based on the user's query.
3. **Parameter Handling**: The client handles parameter mapping and validation before calling the tools.

## Notes

- This example uses hardcoded responses for the weather tool. In a real application, you would connect to a weather API.
- The client includes a city-to-timezone mapping to handle cases where the user asks for the time in a city rather than a timezone.
