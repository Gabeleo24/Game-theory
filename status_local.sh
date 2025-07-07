#!/bin/bash
echo "📊 ADS599 Capstone Service Status:"
echo ""
docker compose -f docker-compose.yml -f docker-compose.local.yml ps
echo ""
echo "🔗 Access URLs:"
echo "📊 Jupyter Lab: http://localhost:8888"
echo "🗄️ pgAdmin: http://localhost:8080"
