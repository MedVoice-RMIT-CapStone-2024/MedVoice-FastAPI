
SHELL := /bin/bash

# Variables
NGROK_CONFIG_PATH := /home/laansdole/.config/ngrok/ngrok.yml
NGROK_EXAMPLE_FILE := $(NGROK_CONFIG_PATH).example

# Load environment variables from .env
ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: venv
venv:
	# Ensure Python3 and virtual environment
	@which python3 > /dev/null && python3 -m venv venv || python -m venv venv
	@echo "Setting up virtual environment and installing dependencies..."
	@bash -c "source venv/bin/activate && pip install -r requirements.txt"
	@echo "Dependencies installed successfully."

.PHONY: up
up:
	@if command -v docker-compose >/dev/null 2>&1; then \
		echo "Using docker-compose..."; \
		docker-compose up --build --scale worker=1; \
	else \
		echo "Using docker compose..."; \
		docker compose up --build --scale worker=1; \
	fi
	@echo "Project started."

.PHONY: check
check:
	@echo "Checking system dependencies and required files..."
	@echo ""
	@which docker-compose > /dev/null && echo "✔ docker-compose is installed." || echo "✘ docker-compose is not installed. Please install it."
	@echo ""
	@which docker > /dev/null && echo "✔ Docker is installed." || echo "✘ Docker is not installed. Please install it."
	@echo ""
	@which python > /dev/null && echo "✔ Python is installed." || echo "✘ Python is not installed. Please install it. Ignore this if you have python3 installed."
	@echo ""
	@which ngrok > /dev/null && echo "✔ ngrok is installed." || echo "✘ ngrok is not installed. Please install it."
	@echo ""
	@test -f .env && echo "✔ .env file exists." || echo "✘ .env file is missing. Please see .env.example for reference and add it."
	@echo ""
	@test -f google-credentials.json && echo "✔ google-credentials.json file exists." || echo "✘ google-credentials.json file is missing. Please add it."
	@echo ""
	@test -f ngrok.yml && echo "✔ ngrok.yml file exists." || echo "✘ ngrok.yml file is missing. Please see ngrok.example.example for reference and add it."
	@echo ""
	@echo "System check complete. If you are running the project in Ubuntu, run make install to setup the project."

.PHONY: install
install: 
	@echo "Running installation script..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh

# Setup ngrok.yml
.PHONY: ngrok
ngrok:
	@echo "Setting up ngrok environment variables..."
	@export NGROK_AUTH_TOKEN=$$(grep -m 1 '^NGROK_AUTH_TOKEN=' .env | cut -d '=' -f2 | xargs); \
	export NGROK_API_KEY=$$(grep -m 1 '^NGROK_API_KEY=' .env | cut -d '=' -f2 | xargs); \
	export NGROK_EDGE=$$(grep -m 1 '^NGROK_EDGE=' .env | cut -d '=' -f2 | xargs); \
	export NGROK_CONFIG_PATH=$$(ngrok config check 2>&1 | grep "Valid configuration file at" | awk '{print $$5}'); \
	if [ -z "$$NGROK_CONFIG_PATH" ]; then \
		echo "Error: Unable to find ngrok configuration file path."; \
		exit 1; \
	fi; \
	if [ ! -f "ngrok.example.yml" ]; then \
		echo "Error: ngrok.example.yml does not exist in the root directory."; \
		exit 1; \
	fi; \
	echo "Copying and configuring ngrok.yml..."; \
	ngrok config add-authtoken $${NGROK_AUTH_TOKEN}
	@sed -e "s|\$${NGROK_AUTH_TOKEN}|$$NGROK_AUTH_TOKEN|g" \
	    -e "s|\$${NGROK_API_KEY}|$$NGROK_API_KEY|g" \
	    -e "s|\$${NGROK_EDGE}|$$NGROK_EDGE|g" \
	    "ngrok.example.yml" > "$$NGROK_CONFIG_PATH"; \
	echo "Ngrok configuration setup complete: $$NGROK_CONFIG_PATH"
