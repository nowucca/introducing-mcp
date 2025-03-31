#!/bin/bash
set -e

# Default to WebSocket implementation if not specified
IMPLEMENTATION=${IMPLEMENTATION:-websocket}

if [ "$IMPLEMENTATION" = "websocket" ]; then
  echo "Starting MCP WebSocket server..."
  # Start the WebSocket server in the background
  python server/server_websocket.py &
  SERVER_PID=$!
  
  # Wait for initialization
  echo "Waiting for server to initialize..."
  sleep 2
  
  # Set up cleanup
  cleanup() {
    echo "Shutting down server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null || true
  }
  trap cleanup EXIT
  
  # Run the WebSocket client
  echo "Starting MCP WebSocket client..."
  python client/client_websocket.py
  
elif [ "$IMPLEMENTATION" = "sdk" ]; then
  echo "Starting MCP high-level SDK client (which will spawn the server)..."
  # The high-level client runs the server itself
  python client/client.py
  
else
  echo "Unknown implementation: $IMPLEMENTATION"
  echo "Valid options: websocket, sdk"
  exit 1
fi

echo "Client execution completed"
