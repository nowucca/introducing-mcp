# MCP Tool Advertisement Example

This example demonstrates how MCP servers advertise tools to clients. It provides two implementations to progressively learn the Model Context Protocol (MCP).

## What This Example Does

When you run this example:
1. The server initializes and prepares to advertise a tool
2. The client connects to the server
3. The client requests the list of available tools
4. The server responds with tool advertisements
5. The client displays the available tools

## Key Concepts

- **Tool Advertisement**: How MCP servers inform clients about available tools
- **JSON-RPC Protocol**: The underlying message format used by MCP
- **Protocol Initialization**: How clients and servers establish communication
- **Implementation Approaches**: Comparing raw protocol vs. high-level abstractions

## Learning Objectives

- Understand how MCP servers advertise tools to clients
- See the JSON-RPC message exchange in MCP
- Learn how to build MCP-compatible tools
- Progress from explicit protocol to high-level abstractions

## Implementation Approaches

This example provides two complementary implementations:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

## Learning Path

1. **Start with the WebSocket implementation** to see the JSON-RPC protocol
2. **Examine each message** to understand the initialization and tool discovery flow
3. **Then explore the SDK implementation** to see how these details are abstracted
4. **Compare the implementations** to understand the trade-offs

## Implementation Details

### WebSocket Implementation: See the Protocol in Action

The WebSocket implementation makes the MCP protocol visible, showing all JSON-RPC messages exchanged between client and server.

#### Key Files
- `server/server_websocket.py`: Explicit JSON-RPC message handling
- `client/client_websocket.py`: Visible protocol exchange

#### Running the WebSocket Example

This example should be run inside a Docker container for consistent results across all environments.

##### Linux/macOS
```bash
# Build and run with Docker
./docker-build.sh
./docker-run.sh
```

##### Windows
```powershell
# Build and run with Docker
.\docker-build.ps1
.\docker-run.ps1
```

#### What to Look For

When running the WebSocket implementation, watch for these JSON-RPC messages:

1. **Initialize Request**: The client sends capabilities to the server
2. **Initialize Response**: The server responds with its capabilities
3. **Initialized Notification**: The client confirms initialization
4. **Tools List Request**: The client asks what tools are available
5. **Tools List Response**: The server advertises its tools

These messages show the core MCP protocol in action!

### High-Level SDK Implementation: Clean and Simple

After understanding the protocol, explore the high-level SDK implementation which abstracts away the protocol details.

#### Key Files
- `server/server.py`: Uses the decorator pattern for tool definition
- `client/client.py`: Simplified client with automatic protocol handling

#### Running the SDK Example

This example should also be run inside a Docker container for consistent results.

##### Linux/macOS
```bash
# Run the SDK implementation with Docker
IMPLEMENTATION=sdk ./docker-run.sh
```

##### Windows
```powershell
# Run the SDK implementation with Docker
$env:IMPLEMENTATION = "sdk"
.\docker-run.ps1
```

#### Key Differences

- **Decorator-based API**: Define tools with `@server.tool` decorators
- **Type Hints**: Automatically generate JSON schemas
- **Protocol Abstraction**: No manual JSON-RPC handling
- **Resource Management**: Automatic cleanup with AsyncExitStack

## Implementation Comparison

| Feature | WebSocket Implementation | High-Level SDK |
|---------|--------------------------|---------------|
| Lines of Code | ~100 (explicit protocol) | ~30 (abstracted) |
| Protocol Visibility | High (all JSON-RPC visible) | Low (handled internally) |
| Learning Value | See how MCP works | See best practices |
| Production Readiness | Medium | High |

## Running the Example

### Docker Support

This example includes Docker support with helpful scripts:

#### Linux/macOS
- `docker-build.sh`: Builds the Docker image
- `docker-run.sh`: Runs the container with WebSocket implementation
- `docker-clean.sh`: Cleans up containers and images
- `docker-stop.sh`: Stops running containers

These scripts use a shared implementation in `../shared/docker.sh`.

#### Windows
- `docker-build.ps1`: Builds the Docker image
- `docker-run.ps1`: Runs the container with WebSocket implementation
- `docker-clean.ps1`: Cleans up containers and images
- `docker-stop.ps1`: Stops running containers

These PowerShell scripts use a shared implementation in `../shared/docker.ps1`.

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

### Windows Support

This project includes PowerShell scripts for Windows users that provide Docker functionality:

- `docker-build.ps1`: Builds the Docker image
- `docker-run.ps1`: Runs the container (use with `$env:IMPLEMENTATION = "sdk"` for SDK implementation)
- `docker-clean.ps1`: Cleans up containers and images
- `docker-stop.ps1`: Stops running containers

#### PowerShell Execution Policy

If you encounter execution policy restrictions when trying to run the PowerShell scripts, you may need to adjust your execution policy. You can do this in one of the following ways:

1. **Temporary bypass for a single script**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\docker-build.ps1
   ```

2. **Change the execution policy for your current PowerShell session**:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. **Change the execution policy for your user account** (requires admin privileges):
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

The PowerShell scripts use `$PSScriptRoot` to determine their location, ensuring they work correctly regardless of your current working directory.
