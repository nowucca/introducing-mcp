#!/bin/bash
set -e

# Start the server in the background
echo "Starting MCP server..."
./run_server.sh &
SERVER_PID=$!

# Wait for a moment to ensure the server is running
sleep 2

# Start the client
echo "Starting MCP client..."
./run_client.sh

# Kill the server when done
kill $SERVER_PID
