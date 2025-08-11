#!/bin/bash

# Video Intelligence - Quick Start Script
# One-shot prompt solution for video analysis

echo "================================================"
echo "🎬 Video Intelligence - Prompt Crafting Solution"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  No GEMINI_API_KEY found. Running in mock mode."
    echo "   To use real analysis, set your API key:"
    echo "   export GEMINI_API_KEY='your-key-here'"
    echo ""
    echo "   Get a free API key at: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter to continue in mock mode, or Ctrl+C to exit..."
fi

# Build and start the application
echo "🚀 Starting application..."
echo ""

# Stop any existing containers
docker-compose down 2>/dev/null

# Build and start
docker-compose up -d --build

# Wait for the service to be ready
echo "⏳ Waiting for service to start..."
sleep 5

# Check if the service is running
if curl -s http://localhost:5000 > /dev/null; then
    echo ""
    echo "✅ Application is running!"
    echo ""
    echo "================================================"
    echo "📱 Open in your browser: http://localhost:5000"
    echo "================================================"
    echo ""
    echo "Quick Start:"
    echo "1. Paste a YouTube URL or upload a video"
    echo "2. Click 'Analyze'"
    echo "3. Select an analysis mode"
    echo "4. Watch the AI extract insights!"
    echo ""
    echo "To stop the application: docker-compose down"
    echo ""
else
    echo "❌ Failed to start the application."
    echo "   Check the logs: docker-compose logs"
    exit 1
fi