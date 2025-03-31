# Stop any running containers
Write-Host "Stopping any running containers..."
$containers = docker ps -q --filter "ancestor=mcp-context-memory"
if ($containers) {
    docker stop $containers
}

Write-Host "Docker containers stopped"
