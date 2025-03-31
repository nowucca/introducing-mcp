#!/bin/bash
# Thin wrapper script for running the Docker container
# Pass OpenAI environment variables
export OPENAI_API_KEY
export OPENAI_BASE_URL
export OPENAI_MODEL
../shared/docker.sh run
