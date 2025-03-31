# MCP Time Tool Example

This project demonstrates the Model Context Protocol (MCP), focusing on tool invocation. It provides two implementations to progressively learn MCP - first seeing the raw protocol messages, then the simplified high-level approach.

## What You'll Learn

- How MCP servers advertise tools to clients
- How clients invoke tools and receive responses
- The JSON-RPC message exchange in MCP
- How to build MCP-compatible tools
- Progression from explicit protocol to high-level abstractions

## Implementation Approaches

This example provides two complementary implementations:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

## Learning Path

1. **Start with the WebSocket implementation** to see the JSON-RPC protocol
2. **Examine each message** to understand the initialization, tool discovery, and invocation flow
3. **Then explore the SDK implementation** to see how these details are abstracted
4. **Compare the implementations** to understand the trade-offs

## WebSocket Implementation: See the Protocol in Action

The WebSocket implementation makes the MCP protocol visible, showing all JSON-RPC messages exchanged between client and server.

### Key Files
- `server/server_websocket.py`: Explicit JSON-RPC message handling
- `client/client_websocket.py`: Visible protocol exchange

### Running the WebSocket Example

This example should be run inside a Docker container for consistent results across all environments.

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

### What to Look For

When running the WebSocket implementation, watch for these JSON-RPC messages:

1. **Initialize Request**: The client sends capabilities to the server
2. **Initialize Response**: The server responds with its capabilities
3. **Initialized Notification**: The client confirms initialization
4. **Tools List Request**: The client asks what tools are available
5. **Tools List Response**: The server advertises its tools
6. **Tool Call Request**: The client invokes the time tool
7. **Tool Call Response**: The server returns the current time

These messages show the core MCP protocol in action!

## High-Level SDK Implementation: Clean and Simple

After understanding the protocol, explore the high-level SDK implementation which abstracts away the protocol details.

### Key Files
- `server/server.py`: Uses the decorator pattern for tool definition
- `client/client.py`: Simplified client with automatic protocol handling

### Running the SDK Example

This example should also be run inside a Docker container for consistent results.

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

### Key Differences

- **Decorator-based API**: Define tools with `@server.tool` decorators
- **Type Hints**: Automatically generate JSON schemas
- **Protocol Abstraction**: No manual JSON-RPC handling
- **Resource Management**: Automatic cleanup with AsyncExitStack

## Implementation Comparison

| Feature | WebSocket Implementation | High-Level SDK |
|---------|--------------------------|---------------|
| Lines of Code | ~150 (explicit protocol) | ~50 (abstracted) |
| Protocol Visibility | High (all JSON-RPC visible) | Low (handled internally) |
| Learning Value | See how MCP works | See best practices |
| Production Readiness | Medium | High |

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
