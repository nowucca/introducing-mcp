# Default to WebSocket implementation if not specified
if (-not $env:IMPLEMENTATION) {
    $env:IMPLEMENTATION = "websocket"
}

# Run the Docker container with the specified implementation
docker run -it --rm `
  -e IMPLEMENTATION=$env:IMPLEMENTATION `
  -e OPENAI_API_KEY=$env:OPENAI_API_KEY `
  -e OPENAI_BASE_URL=$env:OPENAI_BASE_URL `
  -e OPENAI_MODEL=$env:OPENAI_MODEL `
  mcp-context-memory

Write-Host "Docker container execution completed"
