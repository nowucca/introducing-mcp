#!/bin/bash
set -e

echo "Starting MCP high-level SDK client (which will spawn the server)..."
# The high-level client runs the server itself
python client/client.py
  
echo "Client execution completed"
