#!/bin/bash
set -e

# Default to WebSocket implementation if not specified
IMPLEMENTATION=${IMPLEMENTATION:-websocket}

# Run the Docker container with the specified implementation
docker run -it --rm \
  -e IMPLEMENTATION=$IMPLEMENTATION \
  -e OPENAI_API_KEY \
  -e OPENAI_BASE_URL \
  -e OPENAI_MODEL \
  mcp-context-memory

echo "Docker container execution completed"
