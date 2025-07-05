# Makefile for ADS599 Capstone Soccer Intelligence System Docker Operations
# Provides convenient commands for building, deploying, and managing the containerized system

.PHONY: help build up down restart logs shell clean test validate deploy

# Default target
.DEFAULT_GOAL := help

# Configuration
COMPOSE_FILE := docker-compose.yml
COMPOSE_DEV_FILE := docker-compose.override.yml
PROJECT_NAME := soccer-intelligence
SERVICE_NAME := soccer-intelligence

# Environment variables
ENV_FILE := .env
API_KEYS_FILE := config/api_keys.yaml

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Help target
help: ## Show this help message
	@echo "$(BLUE)ADS599 Capstone Soccer Intelligence System - Docker Operations$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Environment profiles:$(NC)"
	@echo "  $(YELLOW)production$(NC)        Default production environment"
	@echo "  $(YELLOW)development$(NC)       Development with additional tools"
	@echo "  $(YELLOW)scaling$(NC)           Production with worker scaling"
	@echo "  $(YELLOW)monitoring$(NC)        Production with monitoring tools"

# Setup targets
setup: ## Setup environment files from templates
	@echo "$(BLUE)Setting up environment configuration...$(NC)"
	@if [ ! -f $(ENV_FILE) ]; then \
		cp .env.template $(ENV_FILE); \
		echo "$(GREEN)Created $(ENV_FILE) from template$(NC)"; \
		echo "$(YELLOW)Please edit $(ENV_FILE) and add your API keys$(NC)"; \
	else \
		echo "$(YELLOW)$(ENV_FILE) already exists$(NC)"; \
	fi
	@if [ ! -f $(API_KEYS_FILE) ]; then \
		cp config/api_keys_template.yaml $(API_KEYS_FILE); \
		echo "$(GREEN)Created $(API_KEYS_FILE) from template$(NC)"; \
		echo "$(YELLOW)Please edit $(API_KEYS_FILE) and add your API keys$(NC)"; \
	else \
		echo "$(YELLOW)$(API_KEYS_FILE) already exists$(NC)"; \
	fi

check-env: ## Check if environment files exist
	@echo "$(BLUE)Checking environment configuration...$(NC)"
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(RED)Error: $(ENV_FILE) not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f $(API_KEYS_FILE) ]; then \
		echo "$(RED)Error: $(API_KEYS_FILE) not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Environment configuration found$(NC)"

# Build targets
build: check-env ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

build-prod: check-env ## Build production image only
	@echo "$(BLUE)Building production image...$(NC)"
	docker-compose build --target production $(SERVICE_NAME)

build-dev: check-env ## Build development image only
	@echo "$(BLUE)Building development image...$(NC)"
	docker-compose build --target development $(SERVICE_NAME)

build-no-cache: check-env ## Build images without cache
	@echo "$(BLUE)Building Docker images without cache...$(NC)"
	docker-compose build --no-cache

# Deployment targets
up: check-env ## Start all services (production)
	@echo "$(BLUE)Starting production services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started successfully$(NC)"
	@make status

up-dev: check-env ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose --profile development up -d
	@echo "$(GREEN)Development environment started$(NC)"
	@echo "$(YELLOW)Available services:$(NC)"
	@echo "  - Jupyter Lab: http://localhost:8888 (token: soccer-intelligence-dev)"
	@echo "  - Streamlit: http://localhost:8501"
	@echo "  - FastAPI: http://localhost:8000"
	@echo "  - pgAdmin: http://localhost:8080 (admin@soccerapp.com / admin123)"
	@echo "  - Redis Commander: http://localhost:8081"
	@make status

up-scaling: check-env ## Start with worker scaling
	@echo "$(BLUE)Starting services with worker scaling...$(NC)"
	docker-compose --profile scaling up -d
	@make status

up-monitoring: check-env ## Start with monitoring
	@echo "$(BLUE)Starting services with monitoring...$(NC)"
	docker-compose --profile monitoring up -d
	@echo "$(GREEN)Monitoring services started$(NC)"
	@echo "$(YELLOW)Available monitoring:$(NC)"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3000 (admin / admin123)"
	@make status

down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	docker-compose --profile development --profile scaling --profile monitoring down
	@echo "$(GREEN)All services stopped$(NC)"

restart: ## Restart main application service
	@echo "$(BLUE)Restarting $(SERVICE_NAME)...$(NC)"
	docker-compose restart $(SERVICE_NAME)
	@echo "$(GREEN)Service restarted$(NC)"

# Status and monitoring targets
status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

logs: ## Show logs for main service
	@echo "$(BLUE)Showing logs for $(SERVICE_NAME):$(NC)"
	docker-compose logs -f --tail=100 $(SERVICE_NAME)

logs-all: ## Show logs for all services
	@echo "$(BLUE)Showing logs for all services:$(NC)"
	docker-compose logs -f --tail=50

health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	@docker-compose exec $(SERVICE_NAME) python -c "
import sys
sys.path.append('src')
try:
    from soccer_intelligence.utils.config import Config
    config = Config()
    print('✓ Configuration loaded successfully')
except Exception as e:
    print(f'✗ Configuration error: {e}')
    sys.exit(1)
" && echo "$(GREEN)Health check passed$(NC)" || echo "$(RED)Health check failed$(NC)"

# Access targets
shell: ## Access main container shell
	@echo "$(BLUE)Accessing $(SERVICE_NAME) shell...$(NC)"
	docker-compose exec $(SERVICE_NAME) bash

shell-db: ## Access database shell
	@echo "$(BLUE)Accessing PostgreSQL shell...$(NC)"
	docker-compose exec postgres psql -U soccerapp -d soccer_intelligence

shell-redis: ## Access Redis shell
	@echo "$(BLUE)Accessing Redis shell...$(NC)"
	docker-compose exec redis redis-cli

# Workflow targets
validate: check-env ## Run quick validation workflow
	@echo "$(BLUE)Running validation workflow...$(NC)"
	./docker/scripts/run-workflows.sh quick

collect: check-env ## Run data collection workflow
	@echo "$(BLUE)Running data collection workflow...$(NC)"
	./docker/scripts/run-workflows.sh collection

analyze: check-env ## Run analysis workflow
	@echo "$(BLUE)Running analysis workflow...$(NC)"
	./docker/scripts/run-workflows.sh analysis

shapley: check-env ## Run Shapley value analysis
	@echo "$(BLUE)Running Shapley value analysis...$(NC)"
	./docker/scripts/run-workflows.sh shapley

multi-season: check-env ## Run multi-season comparative analysis
	@echo "$(BLUE)Running multi-season analysis...$(NC)"
	./docker/scripts/run-workflows.sh multi-season

full-workflow: check-env ## Run complete workflow (collection + analysis)
	@echo "$(BLUE)Running complete workflow...$(NC)"
	./docker/scripts/run-workflows.sh full

# Scaling targets
scale-collectors: check-env ## Scale data collection workers
	@echo "$(BLUE)Scaling data collection workers...$(NC)"
	docker-compose up -d --scale data-collector=3

scale-analyzers: check-env ## Scale analysis workers
	@echo "$(BLUE)Scaling analysis workers...$(NC)"
	docker-compose up -d --scale analysis-worker=2

scale-down: check-env ## Scale down all workers
	@echo "$(BLUE)Scaling down workers...$(NC)"
	docker-compose up -d --scale data-collector=1 --scale analysis-worker=1

# Optimization targets
optimize: ## Run container optimization
	@echo "$(BLUE)Running container optimization...$(NC)"
	./docker/scripts/optimize-container.sh

monitor: ## Start performance monitoring
	@echo "$(BLUE)Starting performance monitoring...$(NC)"
	docker-compose exec $(SERVICE_NAME) python scripts/monitor-performance.py

# Data management targets
backup: ## Backup data volumes
	@echo "$(BLUE)Backing up data volumes...$(NC)"
	@mkdir -p backups
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	docker run --rm -v soccer-intelligence-postgres-data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/postgres_$$DATE.tar.gz /data; \
	tar czf backups/app_data_$$DATE.tar.gz data/ logs/; \
	echo "$(GREEN)Backup completed: backups/postgres_$$DATE.tar.gz and backups/app_data_$$DATE.tar.gz$(NC)"

restore-db: ## Restore database from backup (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)Error: Please specify BACKUP_FILE variable$(NC)"; \
		echo "$(YELLOW)Usage: make restore-db BACKUP_FILE=backups/postgres_20240101_120000.tar.gz$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(BACKUP_FILE)...$(NC)"
	docker run --rm -v soccer-intelligence-postgres-data:/data -v $(PWD):/backup alpine tar xzf /backup/$(BACKUP_FILE) -C /
	@echo "$(GREEN)Database restored from $(BACKUP_FILE)$(NC)"

clear-cache: ## Clear Redis cache
	@echo "$(BLUE)Clearing Redis cache...$(NC)"
	docker-compose exec redis redis-cli FLUSHALL
	@echo "$(GREEN)Cache cleared$(NC)"

# Testing targets
test: check-env ## Run tests in container
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose run --rm $(SERVICE_NAME) python -m pytest tests/ -v

test-api: check-env ## Test API connectivity
	@echo "$(BLUE)Testing API connectivity...$(NC)"
	docker-compose run --rm $(SERVICE_NAME) python -c "
import sys
sys.path.append('src')
from soccer_intelligence.data_collection.api_football import APIFootballClient
client = APIFootballClient()
print('✓ API client initialized successfully')
"

test-db: check-env ## Test database connectivity
	@echo "$(BLUE)Testing database connectivity...$(NC)"
	docker-compose exec $(SERVICE_NAME) python -c "
import psycopg2
import os
conn = psycopg2.connect(
    host='postgres',
    database='soccer_intelligence',
    user='soccerapp',
    password='soccerpass123'
)
print('✓ Database connection successful')
"

# Cleanup targets
clean: ## Remove stopped containers and unused images
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker-compose down --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

clean-all: ## Remove all containers, images, and volumes (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will remove all containers, images, and volumes!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Removing all Docker resources...$(NC)"
	docker-compose down --volumes --remove-orphans
	docker system prune -a -f --volumes
	@echo "$(GREEN)All Docker resources removed$(NC)"

clean-data: ## Remove application data (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will remove all application data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Removing application data...$(NC)"
	rm -rf data/ logs/
	@echo "$(GREEN)Application data removed$(NC)"

# Development targets
dev-setup: setup up-dev ## Complete development setup
	@echo "$(GREEN)Development environment setup completed!$(NC)"

prod-deploy: setup build up ## Complete production deployment
	@echo "$(GREEN)Production deployment completed!$(NC)"

# Quick commands
quick-start: setup build up validate ## Quick start with validation
	@echo "$(GREEN)Quick start completed successfully!$(NC)"

quick-dev: setup build up-dev ## Quick development start
	@echo "$(GREEN)Quick development environment ready!$(NC)"
