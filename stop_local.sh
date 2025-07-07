#!/bin/bash
echo "🛑 Stopping ADS599 Capstone services..."
docker compose -f docker-compose.yml -f docker-compose.local.yml down
echo "✅ All services stopped"
