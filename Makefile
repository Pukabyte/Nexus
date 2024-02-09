# Makefile for managing Docker Compose for the project

# Variables
COMPOSE_FILE := docker-compose.yml
NETWORK_NAME := nexus

# Help
.PHONY: help
help:  ## Display this help screen
    @grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Detect OS and set commands accordingly
OS := $(shell uname -s)
ifeq ($(OS),Linux)
    GREP_COMMAND := grep -q
else ifeq ($(OS),Darwin)
    GREP_COMMAND := grep -q
else
    GREP_COMMAND := findstr
endif

# Detect Docker Compose command
DOCKER_COMPOSE_CMD := $(shell command -v docker-compose || echo "docker compose")

# Check if the network exists, and if not, create it
.PHONY: prepare-network
prepare-network:
	@if ! docker network ls | $(GREP_COMMAND) $(NETWORK_NAME); then \
        echo "Creating network $(NETWORK_NAME)"; \
        docker network create $(NETWORK_NAME); \
    fi

# Docker Compose Commands
.PHONY: build
build: prepare-network  ## Build or rebuild services from local compose
	$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) build

.PHONY: run
run: stop  ## Create and start containers from local compose
	@COMPOSE_PROJECT_NAME=mycustomproject $(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) up -d --build
	@COMPOSE_PROJECT_NAME=mycustomproject $(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) logs -f -t

.PHONY: stop
stop:  ## Stop and remove containers, networks, and images from local compose
	@-docker container rm -f nexus 2> /dev/null || true
	@$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) down --rmi all -v --remove-orphans

.PHONY: restart
restart: stop run  ## Restart all services from local compose

.PHONY: logs
logs:  ## View output from containers from local compose
	$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) logs

.PHONY: ps
ps:  ## List containers from local compose
	$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) ps

.PHONY: shell
shell:  ## Access the container's shell
	$(DOCKER_COMPOSE_CMD) -f $(COMPOSE_FILE) exec nexus /bin/sh

.PHONY: start
start: ## Start services from python
	python3 main.py

.PHONY: test
test: ## Run Pytests
	pytest -vv