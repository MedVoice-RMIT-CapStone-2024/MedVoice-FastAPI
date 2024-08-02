.PHONY: check
check:
	@which docker-compose > /dev/null && echo "docker-compose is installed." || echo "docker-compose is not installed. Please install it. Ignore this if you have docker compose installed."
	@which docker > /dev/null && echo "Docker is installed." || echo "Docker is not installed. Please install it."
	@which python > /dev/null && echo "Python is installed." || echo "Python is not installed. Please install it. Ignore this if you have python3 installed."
	@test -f .env && echo ".env file exists." || echo ".env file is missing. Please see .env-placeholder.txt for reference and add it."
	@test -f google-credentials.json && echo "google-credentials.json file exists." || echo "google-credentials.json file is missing. Please add it."
	@test -f ngrok.yml && echo "ngrok.yml file exists." || echo "ngrok.yml file is missing. Please see ngrok.yml-placeholder.txt for reference and add it."

.PHONY: venv
venv:
	if [ -x $$(command -v apt-get) ]; then \
		if ! dpkg -l | grep -q python3.10-venv; then \
			sudo apt-get update && sudo apt-get install -y python3.10-venv; \
		fi; \
	fi
	if ! which python3 > /dev/null; then \
		echo "Python3 is not installed. Please install Python3."; \
		exit 1; \
	fi
	if ! python3 -m venv venv; then \
		if [ -x $$(command -v apt-get) ]; then \
			sudo apt-get update && sudo apt-get install -y python3.10-venv; \
			python3 -m venv venv; \
		else \
			echo "You are not on Ubuntu. Please install the 'python3.10-venv' package manually."; \
			exit 1; \
		fi; \
	fi
	source venv/bin/activate
