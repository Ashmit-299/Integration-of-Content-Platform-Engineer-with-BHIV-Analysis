#!/bin/bash
# Example deploy script for a generic container host
docker build -t gurukul-content-platform:latest .
echo "Built. To run locally:"
echo "docker run -p 8000:8000 gurukul-content-platform:latest"
