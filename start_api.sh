#!/bin/bash

echo "🚀 Starting TikTok API Server..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start the API server
echo "📦 Building Docker image..."
docker-compose build

echo "🔧 Starting API server on port 5000..."
docker-compose up -d

echo "⏳ Waiting for server to be ready..."
sleep 10

# Test the API
echo "🧪 Testing API connection..."
python3 test_api.py

echo "✅ API server should now be running on http://localhost:5000"
echo "📋 Available endpoints:"
echo "   - GET  http://localhost:5000/health"
echo "   - POST http://localhost:5000/extract_tiktok"
echo ""
echo "🔧 To stop the server: docker-compose down"
echo "📊 To view logs: docker-compose logs -f"