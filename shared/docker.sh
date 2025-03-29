#!/bin/bash
set -e

# Determine the exact directory this script is being called from
CALLING_DIR="$(pwd)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Extract the example folder name (e.g., "00-advertise-tool")
EXAMPLE_DIR=$(basename "$CALLING_DIR")
IMAGE_NAME="mcp-example-${EXAMPLE_DIR}"

# Function to show usage information
show_usage() {
  echo "Usage: ../shared/docker.sh [build|run|stop|clean]"
  echo ""
  echo "Commands:"
  echo "  build    Build the Docker image for the current example"
  echo "  run      Run the Docker container for the current example"
  echo "  stop     Stop any running containers of this example"
  echo "  clean    Remove the Docker image and containers for this example"
  echo ""
  echo "Current example: $EXAMPLE_DIR"
  echo "Docker image name: $IMAGE_NAME"
  echo ""
}

# Build the Docker image
build() {
  echo "Building Docker image: $IMAGE_NAME for example: $EXAMPLE_DIR"
  docker build -t "$IMAGE_NAME" "$CALLING_DIR"
  echo "Build complete"
}

# Run the Docker container
run() {
  echo "Running Docker container from image: $IMAGE_NAME"
  docker run -it --rm \
    -e PYTHONUNBUFFERED=1 \
    -e IMPLEMENTATION=${IMPLEMENTATION:-websocket} \
    "$IMAGE_NAME"
}

# Stop any running containers of this image
stop() {
  echo "Stopping running containers for $IMAGE_NAME..."
  docker ps -q --filter ancestor="$IMAGE_NAME" | xargs -r docker stop
  echo "Containers stopped"
}

# Clean up containers and images
clean() {
  echo "Stopping running containers for $IMAGE_NAME..."
  docker ps -q --filter ancestor="$IMAGE_NAME" | xargs -r docker stop
  
  echo "Removing stopped containers for $IMAGE_NAME..."
  docker ps -a -q --filter ancestor="$IMAGE_NAME" | xargs -r docker rm
  
  echo "Removing Docker image: $IMAGE_NAME"
  docker rmi -f "$IMAGE_NAME" 2>/dev/null || true
  
  echo "Cleanup complete"
}

# Main script logic
case "$1" in
  build)
    build
    ;;
  run)
    run
    ;;
  stop)
    stop
    ;;
  clean)
    clean
    ;;
  *)
    show_usage
    exit 1
    ;;
esac
