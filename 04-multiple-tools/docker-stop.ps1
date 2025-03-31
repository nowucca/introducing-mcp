# Stop the Docker container if it's running
$container = docker ps -q --filter "name=mcp-multiple-tools-container"
if ($container) {
    Write-Host "Stopping MCP Multiple Tools container..."
    docker stop mcp-multiple-tools-container
    Write-Host "Container stopped"
} else {
    Write-Host "MCP Multiple Tools container is not running"
}
