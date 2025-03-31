# Stop the container if it's running
$container = docker ps -q --filter "name=mcp-multiple-tools-container"
if ($container) {
    Write-Host "Stopping MCP Multiple Tools container..."
    docker stop mcp-multiple-tools-container
    Write-Host "Container stopped"
}

# Remove the image if it exists
$image = docker images -q mcp-multiple-tools
if ($image) {
    Write-Host "Removing MCP Multiple Tools image..."
    docker rmi mcp-multiple-tools
    Write-Host "Image removed"
} else {
    Write-Host "MCP Multiple Tools image does not exist"
}
