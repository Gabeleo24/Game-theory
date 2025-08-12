# Real Madrid Soccer Analysis - Docker Container
# ADS599 Capstone Project

# Use official Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV JUPYTER_ENABLE_LAB=yes

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p "Main Notebook/Images" && \
    mkdir -p "Main Notebook/Code Library"

# Set permissions
RUN chmod -R 755 "Main Notebook/Code Library" && \
    chmod -R 755 "Main Notebook/Images"

# Expose Jupyter port
EXPOSE 8888

# Create a non-root user for security
RUN useradd -m -s /bin/bash jupyter && \
    chown -R jupyter:jupyter /app
USER jupyter

# Set the default command to start Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
