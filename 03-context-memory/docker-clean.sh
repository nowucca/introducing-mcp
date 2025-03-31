#!/bin/bash
set -e

# Stop any running containers
echo "Stopping any running containers..."
docker ps -q --filter "ancestor=mcp-context-memory" | xargs -r docker stop

# Remove the Docker image
echo "Removing Docker image..."
docker rmi -f mcp-context-memory 2>/dev/null || true

echo "Docker cleanup completed"
