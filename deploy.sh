#!/bin/bash
echo "Deploying BHIV-Integrated Gurukul Content Platform..."

# Build and deploy
docker-compose down
docker-compose build
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Run smoke tests
python smoke_test.py

echo "Deployment complete! Access at http://localhost:8000"
