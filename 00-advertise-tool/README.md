# MCP Tool Advertisement Example

This project demonstrates the Model Context Protocol (MCP), focusing on tool advertisement. It provides two implementations to progressively learn MCP - first seeing the raw protocol messages, then the simplified high-level approach.

## What You'll Learn

- How MCP servers advertise tools to clients
- The JSON-RPC message exchange in MCP
- How to build MCP-compatible tools
- Progression from explicit protocol to high-level abstractions

## Implementation Approaches

This example provides two complementary implementations:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

## WebSocket Implementation: See the Protocol in Action

The WebSocket implementation makes the MCP protocol visible, showing all JSON-RPC messages exchanged between client and server.

### Key Files
- `server/server_websocket.py`: Explicit JSON-RPC message handling
- `client/client_websocket.py`: Visible protocol exchange

### Running the WebSocket Example

#### Linux/macOS
```bash
# Run locally
./run.sh

# Or with Docker
./docker-build.sh
./docker-run.sh
```

#### Windows
```powershell
# Run with Docker
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

These messages show the core MCP protocol in action!

## High-Level SDK Implementation: Clean and Simple

After understanding the protocol, explore the high-level SDK implementation which abstracts away the protocol details.

### Key Files
- `server/server.py`: Uses the decorator pattern for tool definition
- `client/client.py`: Simplified client with automatic protocol handling

### Running the SDK Example

#### Linux/macOS
```bash
# Run locally
IMPLEMENTATION=sdk ./run.sh
# Or use the helper script
./sdk-run.sh

# With Docker
IMPLEMENTATION=sdk ./docker-run.sh
```

#### Windows
```powershell
# Use the helper script
.\sdk-run.ps1

# Or set environment variable manually
$env:IMPLEMENTATION = "sdk"
.\docker-run.ps1
```

### Key Differences

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

## Docker Support

This example includes Docker support with helpful scripts:

### Linux/macOS
- `docker-build.sh`: Builds the Docker image
- `docker-run.sh`: Runs the container with WebSocket implementation
- `docker-clean.sh`: Cleans up containers and images
- `docker-stop.sh`: Stops running containers

These scripts use a shared implementation in `../shared/docker.sh`.

### Windows
- `docker-build.ps1`: Builds the Docker image
- `docker-run.ps1`: Runs the container with WebSocket implementation
- `docker-clean.ps1`: Cleans up containers and images
- `docker-stop.ps1`: Stops running containers

These PowerShell scripts use a shared implementation in `../shared/docker.ps1`.

## The run.sh Script

The `run.sh` script manages both implementations on Linux/macOS:

```bash
# For WebSocket implementation (default)
./run.sh

# For high-level SDK implementation
IMPLEMENTATION=sdk ./run.sh
```

It handles:
1. Starting the server in the background (WebSocket implementation)
2. Waiting for initialization
3. Running the appropriate client
4. Cleaning up processes when done

> **Note for Windows users**: Windows users should use the PowerShell scripts (`docker-build.ps1`, `docker-run.ps1`, etc.) instead of the bash scripts. The PowerShell scripts provide equivalent functionality through Docker.

## Windows Support

This project includes PowerShell scripts for Windows users that provide equivalent functionality to the bash scripts:

- `docker-build.ps1`, `docker-run.ps1`, `docker-clean.ps1`, `docker-stop.ps1`: Docker operations
- `sdk-run.ps1`: Helper script for running the SDK implementation

### PowerShell Execution Policy

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

## Learning Path

1. **Start with the WebSocket implementation** to see the JSON-RPC protocol
2. **Examine each message** to understand the initialization and tool discovery flow
3. **Then explore the SDK implementation** to see how these details are abstracted
4. **Compare the implementations** to understand the trade-offs
