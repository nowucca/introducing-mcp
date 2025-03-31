# Stop any running containers
Write-Host "Stopping any running containers..."
$containers = docker ps -q --filter "ancestor=mcp-context-memory"
if ($containers) {
    docker stop $containers
}

# Remove the Docker image
Write-Host "Removing Docker image..."
docker rmi -f mcp-context-memory 2>$null

Write-Host "Docker cleanup completed"
