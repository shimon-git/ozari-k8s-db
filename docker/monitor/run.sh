#!/bin/bash

# Build the docker image
docker build -t disk-monitor .

# Delete running containers if exist
docker rm -f disk-monitor

# Run the container
docker run -d --name disk-monitor   -p 5000:5000   -v $(pwd)/config.yaml:/app/config.yaml   disk-monitor

# List running containers
docker ps
