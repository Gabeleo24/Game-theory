#!/bin/bash

# ADS599 Capstone - Local Startup Script

echo "🚀 Starting ADS599 Capstone Soccer Intelligence System locally..."

# Start all services
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d

echo ""
echo "✅ Services started! Access points:"
echo ""
echo "📊 Jupyter Lab: http://localhost:8888"
echo "   Token: local_secure_token_2024"
echo ""
echo "🗄️ pgAdmin: http://localhost:8080"
echo "   Email: admin@admin.com"
echo "   Password: admin"
echo ""
echo "📓 Notebooks: ./notebooks/"
echo ""
echo "🔧 Management commands:"
echo "   ./start_local.sh          # Start all services"
echo "   ./stop_local.sh           # Stop all services"
echo "   ./status_local.sh         # Check service status"
echo ""
