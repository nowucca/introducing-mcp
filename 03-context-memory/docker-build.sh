#!/bin/bash
set -e

# Build the Docker image
docker build -t mcp-context-memory .

echo "Docker image 'mcp-context-memory' built successfully"
