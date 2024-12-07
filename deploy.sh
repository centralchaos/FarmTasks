#!/bin/bash

echo "🚀 Deploying FarmTasks to Docker..."

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 failed"
        exit 1
    fi
}

# Stop any running containers
echo "📥 Stopping existing containers..."
docker-compose down
check_status "Stop containers"

# Remove old volumes if they exist
echo "🗑️ Cleaning up volumes..."
docker-compose down -v
check_status "Clean volumes"

# Build fresh images
echo "🏗️ Building Docker images..."
docker-compose build --no-cache
check_status "Build images"

# Start services
echo "🚀 Starting services..."
docker-compose up -d
check_status "Start services"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check services status
echo "🔍 Checking service status..."
docker-compose ps
check_status "Service status check"

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=50

echo "✨ Deployment complete! Application should be available at http://localhost:5000" 