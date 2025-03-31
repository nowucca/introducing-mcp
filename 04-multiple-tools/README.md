# MCP Multiple Tools Example

This example demonstrates how to advertise multiple tools from an MCP server. It builds on the previous examples by adding a second tool to the server.

## What This Example Does

When you run this example:
1. The server initializes and advertises two tools:
   - `get_time` - Returns the current time in a specified timezone
   - `get_weather` - Returns the weather for a specified city
2. The client connects to the server
3. The client requests the list of available tools
4. The server responds with tool advertisements for both tools
5. You'll be prompted to enter a question or request
6. The LLM decides which tool to call (or none) based on your input
7. The client executes the selected tool call
8. You'll see the tool result or a direct LLM response

## Key Concepts

- **Multiple Tool Registration**: How servers can advertise multiple tools to clients
- **Tool Selection by LLM**: How LLMs decide which tool to use based on user queries
- **Parameter Handling**: Managing parameters for different tools
- **Implementation Approaches**: Comparing raw protocol vs. high-level abstractions

## Learning Objectives

- Understand how to register multiple tools in an MCP server
- Learn how LLMs select the appropriate tool based on user input
- See how to handle different parameter requirements for each tool
- Explore patterns for building multi-tool MCP applications

## Interactive Experience

When you run the example, you'll be prompted:

```
What would you like the assistant to do?
```

Try these examples:

- **Time queries**: "What is the time in Tokyo?" or "Tell me the current time in London"
- **Weather queries**: "What is the weather in Tokyo?" or "How's the weather in New York?"
- **Direct LLM responses**: "Tell me a joke" or "What is the capital of France?"

The LLM will intelligently decide which tool to call based on your input.

## Implementation Approaches

This example provides two complementary implementations:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

## Implementation Details

### WebSocket Implementation

The WebSocket implementation makes the MCP protocol visible, showing all JSON-RPC messages exchanged between client and server.

#### Key Files
- `server/server_websocket.py`: Implements both tools with explicit JSON-RPC handling
- `client/client_websocket.py`: Handles tool selection and parameter mapping

### High-Level SDK Implementation

The SDK implementation uses the MCP SDK for a cleaner, more abstracted approach.

#### Key Files
- `server/server.py`: Uses the decorator pattern for tool definitions
- `client/client.py`: Uses the ClientSession with automatic protocol handling

#### Running the SDK Example

```bash
# Linux/macOS
./sdk-run.sh

# Windows
.\sdk-run.ps1
```

## Notes

- This example uses hardcoded responses for the weather tool. In a real application, you would connect to a weather API.
- The client includes a city-to-timezone mapping to handle cases where the user asks for the time in a city rather than a timezone.
## Running the Example

### Prerequisites: OpenAI API Key

Before running this example, set up your OpenAI API key in the `.env` file:

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

> **Note**: If you use the `run_exercises.py` script to run this example, the `.env` file will be created for you automatically.

### Docker Support

This example includes Docker support with helpful scripts:

#### Linux/macOS
- `docker-build.sh`: Builds the Docker image
- `docker-run.sh`: Runs the container with WebSocket implementation
- `docker-clean.sh`: Cleans up containers and images
- `docker-stop.sh`: Stops running containers
- `sdk-run.sh`: Runs the container with SDK implementation

#### Windows
- `docker-build.ps1`: Builds the Docker image
- `docker-run.ps1`: Runs the container with WebSocket implementation
- `docker-clean.ps1`: Cleans up containers and images
- `docker-stop.ps1`: Stops running containers
- `sdk-run.ps1`: Runs the container with SDK implementation

### Internal Scripts (For Docker Use Only)

The `run.sh` script is used internally by the Docker container and is not intended to be run directly:

```bash
# This is used internally by Docker - DO NOT RUN DIRECTLY
./run.sh
```

It handles:
1. Starting the server in the background
2. Waiting for initialization
3. Running the appropriate client
4. Cleaning up processes when done

> **Important**: Students should always use the Docker scripts (`docker-build.sh`/`docker-run.sh` or `docker-build.ps1`/`docker-run.ps1`) to run the examples, not the internal scripts.
