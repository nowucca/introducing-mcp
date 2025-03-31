#!/bin/bash
set -e

# Stop the Docker container if it's running
if docker ps -q --filter "name=mcp-multiple-tools-container" | grep -q .; then
    echo "Stopping MCP Multiple Tools container..."
    docker stop mcp-multiple-tools-container
    echo "Container stopped"
else
    echo "MCP Multiple Tools container is not running"
fi
