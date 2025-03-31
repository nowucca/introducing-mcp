#!/bin/bash
set -e

# Build the Docker image
docker build -t mcp-multiple-tools .

echo "Docker image 'mcp-multiple-tools' built successfully"
