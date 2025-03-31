# MCP Context Memory Example

This example demonstrates how to use client-side memory to automatically fill in missing parameters in MCP tool calls. It shows how a client can maintain context (like user preferences) and apply it to tool calls without requiring the user or LLM to specify these values every time.

## What This Example Does

When you run this example:
1. The server advertises a "get_time" tool that accepts a timezone parameter (defaults to UTC)
2. The client maintains memory with a default timezone ("America/New_York" - US Eastern)
3. When the LLM decides to call the get_time tool:
   - If the timezone parameter is provided, it's used as-is
   - If a city name is provided, it's mapped to the appropriate timezone
   - If no timezone or city is provided, the client automatically adds the default timezone from memory
4. The server returns the current time in the specified timezone

## Key Concepts

- **Client-Side Memory**: How clients can maintain context between tool calls
- **Parameter Filling**: Automatically providing missing parameters based on context
- **City-to-Timezone Mapping**: Converting user-friendly inputs to technical parameters
- **Parameter Validation**: Ensuring parameters are valid before sending to the server

## Learning Objectives

- Understand how to maintain client-side context in MCP applications
- Learn how to automatically fill in missing parameters in tool calls
- See how to validate and transform parameters before sending to the server
- Explore patterns for enhancing user experience with contextual memory

## Client Memory Implementation

The client maintains a simple dictionary of context values:

```python
memory = {
    "timezone": "America/New_York"  # Default timezone (US Eastern)
}
```

The client also includes a city-to-timezone mapping:

```python
CITY_TO_TIMEZONE = {
    "new york": "America/New_York",
    "chicago": "America/Chicago",
    "los angeles": "America/Los_Angeles",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "tokyo": "Asia/Tokyo",
    # ... and many more
}
```

When a tool call is made, the client checks for city names, validates timezones, and fills in missing parameters:

```python
def fill_args_if_missing(arguments):
    # Make a copy to avoid modifying the original
    filled_args = arguments.copy()
    
    # Check if there's a city parameter that we can map to a timezone
    if "city" in filled_args and "timezone" not in filled_args:
        timezone = get_timezone_for_city(filled_args["city"])
        if timezone:
            filled_args["timezone"] = timezone
            # Remove the city parameter as it's not part of the tool's schema
            del filled_args["city"]
    
    # Check if the timezone is valid, if not, use the one from memory
    if "timezone" in filled_args and not is_valid_timezone(filled_args["timezone"]):
        logger.info(f"Invalid timezone '{filled_args['timezone']}', using default from memory")
        filled_args["timezone"] = memory["timezone"]
    
    # Add timezone from memory if not provided
    if "timezone" not in filled_args and "timezone" in memory:
        filled_args["timezone"] = memory["timezone"]
    
    return filled_args
```

This pattern is useful for:
- User preferences (timezone, language, units)
- User identity (user ID, session info)
- Conversation context (previous topics, entities)
- Application state (current view, selected items)

## Interactive Experience

When you run the example, you'll see the current memory settings and be prompted:

```
Current memory settings:
  - timezone: America/New_York

What would you like the assistant to do?
```

Try these examples:

- **Using memory**: "What is the time?" (the client will automatically use America/New_York timezone)
- **Using city names**: "What is the time in San Francisco?" (the client will map "San Francisco" to "America/Los_Angeles")
- **Other city examples**: "What time is it in Chicago?" (maps to "America/Chicago")
- **Using explicit timezones**: "What's the current time in UTC+2?" (the LLM will specify the timezone directly)

## Implementation Approaches

This example provides two complementary implementations:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

## Implementation Details

### WebSocket Implementation

The WebSocket implementation makes the MCP protocol visible, showing all JSON-RPC messages exchanged between client and server.

#### Key Files
- `server/server_websocket.py`: Implements the time tool with timezone parameter
- `client/client_websocket.py`: Maintains memory and fills in missing parameters

### High-Level SDK Implementation

The SDK implementation uses the MCP SDK for a cleaner, more abstracted approach.

#### Key Files
- `server/server.py`: Uses the decorator pattern for the time tool
- `client/client.py`: Uses the ClientSession with memory management

#### Running the SDK Example

```bash
# Linux/macOS
./sdk-run.sh

# Windows
.\sdk-run.ps1
```
## Running the Example

### Prerequisites: OpenAI API Key

Before running this example, set up your OpenAI API key in the `.env` file:

1. Create an account on [OpenAI](https://platform.openai.com/) if you don't have one
2. Generate an API key from the OpenAI dashboard
3. Edit the `.env` file in this directory:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4o
   ```

> **Note**: If you use the `run_exercises.py` script to run this example, the `.env` file will be created for you automatically.

> **Note for VT Students**: The default configuration uses the VT proxy server. If you're a VT student, you can use this configuration without an OpenAI API key.

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
