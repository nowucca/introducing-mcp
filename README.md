# MCP Examples Runner

This repository contains a collection of Model Context Protocol (MCP) exercises that demonstrate various aspects of the protocol. The `run_exercises.py` script provides an easy way to build and run each exercise.

## Available Exercises

- **00-advertise-tool**: Demonstrates how MCP servers advertise tools to clients
- **01-invoke-time-tool**: Shows how to invoke a simple time tool
- **02-llm-client**: Demonstrates how an LLM can decide whether to call MCP tools (requires OpenAI API key)
- **03-context-memory**: Shows how to maintain context between tool calls
- **04-multiple-tools**: Demonstrates using multiple tools in a single server
- **05-agent-parallel**: Shows how to run multiple agents in parallel
- **06-agent-planning**: Demonstrates agent planning with MCP tools

## Using the Runner Script

The `run_exercises.py` script allows you to run any of the exercises with either the WebSocket or SDK implementation. It requires a student name and 4-digit password to generate an API key. The script is cross-platform and works on both Windows and Unix-like systems (Linux/macOS).

### Basic Usage

```bash
# Display the list of available exercises
python run_exercises.py -n student_name -p 1234

# Run a specific exercise (with WebSocket implementation by default)
python run_exercises.py -n student_name -p 1234 -e 00

# Run a specific exercise with the SDK implementation
python run_exercises.py -n student_name -p 1234 -e 03 -i sdk

# Run all exercises with the WebSocket implementation
python run_exercises.py -n student_name -p 1234 -e all

# Run all exercises with the SDK implementation
python run_exercises.py -n student_name -p 1234 -e all -i sdk
```

### Cross-Platform Support

The script automatically detects your operating system and uses the appropriate scripts:

- On **Windows**: Uses PowerShell scripts (`.ps1`) with `-ExecutionPolicy Bypass` for security
- On **Linux/macOS**: Uses Bash scripts (`.sh`)

This allows you to run the exercises seamlessly on any platform without manual configuration.

### API Key Generation

The script generates an API key using base64 encoding of the student name and password:
```
API_KEY = base64(student_name:password)
```

This API key is automatically added to the `.env` file for each exercise that requires it.

### Exercise Requirements

- Exercises 02, 03, 05, and 06 require API keys, which are automatically generated and configured
- The script creates `.env` files with the proper configuration for each exercise

## Implementation Details

Each exercise provides two complementary implementations:

1. **WebSocket Implementation (Default)**: Shows the raw JSON-RPC messages for learning
2. **High-Level SDK Implementation**: Demonstrates a cleaner, production-ready approach

## Docker Support

Most exercises include Docker support with helpful scripts:

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

## Notes

- The runner script uses the appropriate scripts for your platform (`.sh` or `.ps1`)
- For exercises that require user input, the script will display appropriate prompts
- The script will provide feedback on the execution status of each exercise
- If you encounter PowerShell execution policy errors on Windows, you may need to run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```
- On Linux/macOS, if you encounter permission errors, you may need to make scripts executable:
  ```bash
  chmod +x script.sh
  ```
