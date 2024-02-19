COMPOSE_FILE := docker-compose.yml
NETWORK_NAME := nexus
PROJECT_NAME := nexus

OS := $(shell uname -s)
DOCKER_COMPOSE_CMD := $(shell command -v docker-compose || echo "docker compose")

# Detect OS and set grep command accordingly
ifeq ($(OS),Linux)
    GREP_COMMAND := grep -q
else ifeq ($(OS),Darwin)
    GREP_COMMAND := grep -q
else
    GREP_COMMAND := findstr
endif

# Help target to display help screen
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install
install:  ## Install dependencies
	@pip install -r requirements.txt

# Prepare Docker network
.PHONY: prepare-network
prepare-network:
	@if ! docker network ls | $(GREP_COMMAND) $(NETWORK_NAME); then \
        echo "Creating network $(NETWORK_NAME)"; \
        docker network create $(NETWORK_NAME); \
    fi

# Docker Compose Commands
.PHONY: build
build: prepare-network  ## Build or rebuild services
	@$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) build

.PHONY: run
run: stop  ## Start containers
	@COMPOSE_PROJECT_NAME=$(PROJECT_NAME) $(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) up -d --build
	@COMPOSE_PROJECT_NAME=$(PROJECT_NAME) $(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) logs -f -t

.PHONY: stop
stop:  ## Stop and remove containers and networks
	@-docker container rm -f $(NETWORK_NAME) 2> /dev/null || true
	@$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) down --rmi all -v --remove-orphans

.PHONY: restart
restart: stop run  ## Restart all services

.PHONY: logs
logs:  ## View container logs
	@$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) logs

.PHONY: ps
ps:  ## List containers
	@$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) ps

.PHONY: shell
shell:  ## Access container shell
	@$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) exec $(NETWORK_NAME) /bin/sh

.PHONY: start
start:  ## Start application services
	@python3 main.py

.PHONY: test
test:  ## Run tests
	@pytest

.PHONY: lint
lint:  ## Lint Python code with Ruff
	@flake8 .

.PHONY: format
format:  ## Format Python code with Black and Isort
	@black .
	@isort .

.PHONY: pr-ready
pr-ready: lint test  ## Run tests and linting to make sure the PR is ready
