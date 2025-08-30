.PHONY: help install dev test lint format clean run docker-build docker-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install black isort mypy flake8

test: ## Run tests
	pytest tests/ -v --cov=.

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	mypy .

format: ## Format code
	black .
	isort .

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run: ## Run the application
	python run.py

docker-build: ## Build Docker image
	docker build -t bhiv-platform .

docker-run: ## Run Docker container
	docker run -p 8000:8000 bhiv-platform

deploy: ## Deploy to production
	./deploy.sh