#!/bin/bash
set -e

# Stop any running containers
echo "Stopping any running containers..."
docker ps -q --filter "ancestor=mcp-context-memory" | xargs -r docker stop

echo "Docker containers stopped"
