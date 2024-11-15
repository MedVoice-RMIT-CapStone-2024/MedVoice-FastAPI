
SHELL := /bin/bash

# Variables
NGROK_CONFIG_PATH := /home/laansdole/.config/ngrok/ngrok.yml
NGROK_EXAMPLE_FILE := $(NGROK_CONFIG_PATH).example

.PHONY: venv
venv:
	# Ensure Python3 and virtual environment
	@which python3 > /dev/null && python3 -m venv venv || python -m venv venv
	@echo "Setting up virtual environment and installing dependencies..."
	@bash -c "source venv/bin/activate && pip install -r requirements.txt"
	@echo "Dependencies installed successfully."

.PHONY: check
check:
	@which docker-compose > /dev/null && (echo "docker-compose is installed.") || echo "docker-compose is not installed. Please install it."
	@which docker > /dev/null && (echo "Docker is installed.") || echo "Docker is not installed. Please install it."
	@which python > /dev/null && (echo "Python is installed.") || echo "Python is not installed. Please install it. Ignore this if you have python3 installed"
	@which ngrok > /dev/null && (echo "ngrok is installed.") || echo "ngrok is not installed. Please install it."
	@test -f .env && (echo ".env file exists.") || echo ".env file is missing. Please see .env.local.example for reference add it."
	@test -f google-credentials.json && (echo "google-credentials.json file exists.") || echo "google-credentials.json file is missing. Please add it."
	@test -f ngrok.yml && (echo "ngrok.yml file exists.") || echo "ngrok.yml file is missing. Please see ngrok.yml.example for reference and add it."
	@which ngrok > /dev/null && (echo "ngrok is installed.") || echo "ngrok is not installed. Please install it."

.PHONY: setup-ngrok
setup-ngrok: setup_ngrok

# Ensure required environment variables are set
.PHONY: check_ngrok_env
check_ngrok_env:
	@if [ -z "$(NGROK_AUTH_TOKEN)" ]; then echo "Error: NGROK_AUTH_TOKEN is not set"; exit 1; fi
	@if [ -z "$(NGROK_API_KEY)" ]; then echo "Error: NGROK_API_KEY is not set"; exit 1; fi
	@if [ -z "$(NGROK_EDGE)" ]; then echo "Error: NGROK_EDGE is not set"; exit 1; fi

# Setup ngrok.yml
.PHONY: setup_ngrok
setup_ngrok: check_ngrok_env
	@echo "Checking ngrok configuration file path..."
	@NGROK_FILE=$$(ngrok config check 2>&1 | grep "Valid configuration file at" | awk '{print $$5}'); \
	if [ -z "$$NGROK_FILE" ]; then \
		echo "Error: Unable to find ngrok configuration file path."; \
		exit 1; \
	fi; \
	if [ ! -f "$(NGROK_EXAMPLE_FILE)" ]; then \
		echo "Error: Example file $(NGROK_EXAMPLE_FILE) does not exist."; \
		exit 1; \
	fi; \
	echo "Replacing placeholders in $$NGROK_FILE..."; \
	sed -e "s|\$${NGROK_AUTH_TOKEN}|$(NGROK_AUTH_TOKEN)|g" \
	    -e "s|\$${NGROK_API_KEY}|$(NGROK_API_KEY)|g" \
	    -e "s|\$${NGROK_EDGE}|$(NGROK_EDGE)|g" \
	    "$(NGROK_EXAMPLE_FILE)" > "$$NGROK_FILE"; \
	echo "Setup complete: $$NGROK_FILE"
