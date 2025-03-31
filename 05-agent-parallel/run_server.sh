#!/bin/bash
echo "Starting MCP server..."
cd "$(dirname "$0")"
python server/server.py
