#!/bin/bash
set -e

# Stop the container if it's running
if docker ps -q --filter "name=mcp-multiple-tools-container" | grep -q .; then
    echo "Stopping MCP Multiple Tools container..."
    docker stop mcp-multiple-tools-container
    echo "Container stopped"
fi

# Remove the image if it exists
if docker images -q mcp-multiple-tools | grep -q .; then
    echo "Removing MCP Multiple Tools image..."
    docker rmi mcp-multiple-tools
    echo "Image removed"
else
    echo "MCP Multiple Tools image does not exist"
fi
