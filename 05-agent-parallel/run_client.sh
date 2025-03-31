#!/bin/bash
echo "Starting MCP client..."
cd "$(dirname "$0")"
python client/client.py
