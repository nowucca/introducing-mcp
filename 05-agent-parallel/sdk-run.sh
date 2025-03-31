#!/bin/bash
echo "Running MCP example with SDK..."
cd "$(dirname "$0")"
python -m mcp.cli run --stdio --command "python client/client.py" server/server.py
