#!/bin/bash

# Real Madrid Soccer Analysis - Startup Script
# ADS599 Capstone Project

echo "⚽ Real Madrid Soccer Analysis - Starting Up..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: requirements.txt, Dockerfile, docker-compose.yml"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected - Using containerized environment"
    
    # Check if containers are already running
    if docker-compose ps | grep -q "real_madrid_analysis"; then
        echo "⚠️  Containers already running. Stopping them first..."
        docker-compose down
    fi
    
    echo "🚀 Starting Docker containers..."
    docker-compose up --build -d
    
    echo ""
    echo "✅ Analysis environment started successfully!"
    echo "📊 Access Jupyter Notebook at: http://localhost:8888"
    echo "📁 Navigate to: Main Notebook/Main_Analysis.ipynb"
    echo ""
    echo "🛑 To stop the environment, run: docker-compose down"
    
else
    echo "🐍 Docker not available - Using local Python environment"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Error: Python 3 is not installed"
        echo "   Please install Python 3.8+ and try again"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "🔧 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Install requirements
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    
    echo ""
    echo "✅ Local environment ready!"
    echo "🚀 Starting Jupyter Notebook..."
    echo ""
    echo "📊 Jupyter will open in your browser"
    echo "📁 Navigate to: Main Notebook/Main_Analysis.ipynb"
    echo ""
    echo "🛑 To stop Jupyter, press Ctrl+C in this terminal"
    
    # Start Jupyter
    jupyter notebook "Main Notebook/Main_Analysis.ipynb"
fi

echo ""
echo "🎉 Happy analyzing! ⚽📊"
