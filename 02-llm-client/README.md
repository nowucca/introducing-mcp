# MCP LLM Client Example

This project demonstrates how an LLM (Large Language Model) can decide whether to call MCP tools based on user input. It shows how to integrate OpenAI's API with the Model Context Protocol (MCP).

## What This Example Does

When you run this example:

1. The server advertises a "get_time" tool
2. The client connects and discovers this tool
3. You'll be prompted to enter a question or request
4. The LLM decides whether to call the time tool based on your input
5. You'll see either the tool result or a direct LLM response

## Interactive Experience

When you run the example, you'll be prompted:

```
What would you like the assistant to do?
```

Try these examples:

- **To trigger tool use**: "What time is it right now?" or "Can you tell me the current time?"
- **To see tool parameters**: "What time is it in 24-hour format?" (the LLM will use the format parameter)
- **To see direct LLM response**: "Tell me a joke" or "What is the capital of France?"

The LLM will intelligently decide whether to call the time tool based on your input.

## How to Run the Example

### Prerequisites: OpenAI API Key

Before running this example, set up your OpenAI API key in the `.env` file:

```
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

### Running with Docker

#### Linux/macOS

```bash
# Build and run with Docker
./docker-build.sh
./docker-run.sh
```

#### Windows

```powershell
# Build and run with Docker
.\docker-build.ps1
.\docker-run.ps1
```

## LLM Integration Explained

This example demonstrates the key steps for integrating an LLM with MCP:

1. **Tool Discovery**: The client connects to the server and discovers available tools
2. **Tool Format Conversion**: MCP tools are converted to OpenAI function format
3. **User Input**: The client gets input from the user
4. **LLM Decision**: The input and tools are sent to the LLM, which decides whether to call a tool
5. **Tool Invocation**: If the LLM decides to call a tool, the client sends the request to the server
6. **Result Display**: The client displays the tool result or the LLM's direct response

## Learning Path

This example provides two complementary implementations to help you understand MCP:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

### WebSocket Implementation: See the Protocol in Action

The WebSocket implementation makes the MCP protocol visible, showing all JSON-RPC messages exchanged between client and server.

#### Key Files

- `server/server_websocket.py`: Explicit JSON-RPC message handling
- `client/client_websocket.py`: Visible protocol exchange with LLM integration

#### What to Look For

When running the WebSocket implementation, watch for these key steps:

1. **Initialize Request/Response**: The client and server establish a connection
2. **Tools List Request/Response**: The client discovers available tools
3. **OpenAI API Call**: The client sends tools and user input to OpenAI
4. **LLM Decision**: The LLM decides whether to call a tool
5. **Tool Call Request/Response**: If the LLM decides to call a tool, the client sends the request and receives the result

### High-Level SDK Implementation: Clean and Simple

After understanding the protocol, explore the high-level SDK implementation which abstracts away the protocol details.

#### Key Files

- `server/server.py`: Uses the decorator pattern for tool definition
- `client/client.py`: Simplified client with automatic protocol handling and LLM integration

#### Running the SDK Example

#### Linux/macOS

```bash
# Run the SDK implementation with Docker
IMPLEMENTATION=sdk ./docker-run.sh
# Or use the convenience script
./sdk-run.sh
```

#### Windows

```powershell
# Run the SDK implementation with Docker
$env:IMPLEMENTATION = "sdk"
.\docker-run.ps1
# Or use the convenience script
.\sdk-run.ps1
```

#### Key Differences

- **Decorator-based API**: Define tools with `@server.tool` decorators
- **Type Hints**: Automatically generate JSON schemas
- **Protocol Abstraction**: No manual JSON-RPC handling
- **Resource Management**: Automatic cleanup with AsyncExitStack

## Implementation Comparison

| Feature              | WebSocket Implementation    | High-Level SDK           |
| -------------------- | --------------------------- | ------------------------ |
| Lines of Code        | ~200 (explicit protocol)    | ~100 (abstracted)        |
| Protocol Visibility  | High (all JSON-RPC visible) | Low (handled internally) |
| Learning Value       | See how MCP works           | See best practices       |
| Production Readiness | Medium                      | High                     |

## What You'll Learn

- How MCP servers advertise tools to LLM clients
- How LLMs can decide whether to call tools based on user input
- The JSON-RPC message exchange in MCP
- How to integrate OpenAI's API with MCP
- Progression from explicit protocol to high-level abstractions

## Docker Support

This example includes Docker support with helpful scripts:

### Linux/macOS

- `docker-build.sh`: Builds the Docker image
- `docker-run.sh`: Runs the container with WebSocket implementation
- `docker-clean.sh`: Cleans up containers and images
- `docker-stop.sh`: Stops running containers
- `sdk-run.sh`: Runs the container with SDK implementation

### Windows

- `docker-build.ps1`: Builds the Docker image
- `docker-run.ps1`: Runs the container with WebSocket implementation
- `docker-clean.ps1`: Cleans up containers and images
- `docker-stop.ps1`: Stops running containers
- `sdk-run.ps1`: Runs the container with SDK implementation

## Internal Scripts (For Docker Use Only)

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
