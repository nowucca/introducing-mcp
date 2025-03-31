# Check if OpenAI API key is set
if ((-not $env:OPENAI_API_KEY) -and (-not (Test-Path -Path ".env"))) {
    Write-Host "ERROR: OpenAI API key not set"
    Write-Host "Please set your API key in the .env file or as an environment variable"
    Write-Host "Create a .env file with the following content:"
    Write-Host "OPENAI_API_KEY=your-api-key"
    Write-Host "OPENAI_BASE_URL=https://api.openai.com/v1"
    Write-Host "OPENAI_MODEL=gpt-4o"
    exit 1
}

# Default to WebSocket implementation if not specified
if (-not $env:IMPLEMENTATION) {
    $env:IMPLEMENTATION = "websocket"
}

# Run the Docker container with the specified implementation
if (Test-Path -Path ".env") {
    docker run --rm -it --name mcp-multiple-tools-container `
        -e IMPLEMENTATION=$env:IMPLEMENTATION `
        --env-file .env `
        mcp-multiple-tools
} else {
    $openai_base_url = if ($env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL } else { "https://api.openai.com/v1" }
    $openai_model = if ($env:OPENAI_MODEL) { $env:OPENAI_MODEL } else { "gpt-4o" }
    
    docker run --rm -it --name mcp-multiple-tools-container `
        -e IMPLEMENTATION=$env:IMPLEMENTATION `
        -e OPENAI_API_KEY="$env:OPENAI_API_KEY" `
        -e OPENAI_BASE_URL="$openai_base_url" `
        -e OPENAI_MODEL="$openai_model" `
        mcp-multiple-tools
}

Write-Host "Docker container execution completed"
