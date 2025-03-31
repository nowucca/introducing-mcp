#!/bin/bash
set -e

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ] && [ ! -f .env ]; then
    echo "ERROR: OpenAI API key not set"
    echo "Please set your API key in the .env file or as an environment variable"
    echo "Create a .env file with the following content:"
    echo "OPENAI_API_KEY=your-api-key"
    echo "OPENAI_BASE_URL=https://api.openai.com/v1"
    echo "OPENAI_MODEL=gpt-4o"
    exit 1
fi

# Default to WebSocket implementation if not specified
IMPLEMENTATION=${IMPLEMENTATION:-websocket}

# Run the Docker container with the specified implementation
if [ -f .env ]; then
    docker run --rm -it --name mcp-multiple-tools-container \
        -e IMPLEMENTATION=$IMPLEMENTATION \
        --env-file .env \
        mcp-multiple-tools
else
    docker run --rm -it --name mcp-multiple-tools-container \
        -e IMPLEMENTATION=$IMPLEMENTATION \
        -e OPENAI_API_KEY="$OPENAI_API_KEY" \
        -e OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}" \
        -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o}" \
        mcp-multiple-tools
fi

echo "Docker container execution completed"
