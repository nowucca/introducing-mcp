# Strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get the current directory this script is being called from
$CallingDir = (Get-Location).Path
$RepoRoot = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))

# Extract the example folder name (e.g., "00-advertise-tool")
$ExampleDir = (Split-Path -Leaf $CallingDir)
$ImageName = "mcp-example-${ExampleDir}"

# Function to show usage information
function Show-Usage {
    Write-Host "Usage: ../shared/docker.ps1 [build|run|stop|clean]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build    Build the Docker image for the current example"
    Write-Host "  run      Run the Docker container for the current example"
    Write-Host "  stop     Stop any running containers of this example"
    Write-Host "  clean    Remove the Docker image and containers for this example"
    Write-Host ""
    Write-Host "Current example: $ExampleDir"
    Write-Host "Docker image name: $ImageName"
    Write-Host ""
}

# Build the Docker image
function Build-DockerImage {
    Write-Host "Building Docker image: $ImageName for example: $ExampleDir"
    docker build -t $ImageName $CallingDir
    Write-Host "Build complete"
}

# Run the Docker container
function Run-DockerContainer {
    Write-Host "Running Docker container from image: $ImageName"
    $Implementation = if ($env:IMPLEMENTATION) { $env:IMPLEMENTATION } else { "websocket" }
    docker run -it --rm `
        -e PYTHONUNBUFFERED=1 `
        -e IMPLEMENTATION=$Implementation `
        $ImageName
}

# Stop any running containers of this image
function Stop-DockerContainers {
    Write-Host "Stopping running containers for $ImageName..."
    $containers = docker ps -q --filter ancestor=$ImageName
    if ($containers) {
        docker stop $containers
    }
    Write-Host "Containers stopped"
}

# Clean up containers and images
function Clean-DockerResources {
    Write-Host "Stopping running containers for $ImageName..."
    $runningContainers = docker ps -q --filter ancestor=$ImageName
    if ($runningContainers) {
        docker stop $runningContainers
    }
    
    Write-Host "Removing stopped containers for $ImageName..."
    $stoppedContainers = docker ps -a -q --filter ancestor=$ImageName
    if ($stoppedContainers) {
        docker rm $stoppedContainers
    }
    
    Write-Host "Removing Docker image: $ImageName"
    try {
        docker rmi -f $ImageName
    } catch {
        # Ignore errors if image doesn't exist
    }
    
    Write-Host "Cleanup complete"
}

# Main script logic
switch ($args[0]) {
    "build" { 
        Build-DockerImage
        break
    }
    "run" {
        Run-DockerContainer
        break
    }
    "stop" {
        Stop-DockerContainers
        break
    }
    "clean" {
        Clean-DockerResources
        break
    }
    default {
        Show-Usage
        exit 1
    }
}
