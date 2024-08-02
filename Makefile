.PHONY: check
check:
	@which docker-compose > /dev/null && (echo -e "docker-compose is installed\n.") || echo -e "docker-compose is not installed. Please install it. Ignore this if you have docker compose installed.\n"
	@which docker > /dev/null && (echo -e "Docker is installed\n.") || echo -e "Docker is not installed. Please install it.\n"
	@which python > /dev/null && (echo -e "Python is installed\n.") || echo -e "Python is not installed. Please install it. Ignore this if you have python3 installed.\n"
	@test -f .env && (echo -e ".env file exists\n.") || echo -e ".env file is missing. Please see .env-placeholder.txt for reference and add it.\n"
	@test -f google-credentials.json && (echo -e "google-credentials.json file exists\n.") || echo -e "google-credentials.json file is missing. Please add it.\n"
	@test -f ngrok.yml && (echo -e "ngrok.yml file exists\n.") || echo -e "ngrok.yml file is missing. Please see ngrok.yml-placeholder.txt for reference and add it.\n"

.PHONY: venv
venv:
	if [ -x $$(command -v apt-get) ]; then \
		if ! dpkg -l | grep -q python3.10-venv; then \
			sudo apt-get update && sudo apt-get install -y python3.10-venv; \
		fi; \
	fi
	if ! which python3 > /dev/null; then \
		echo -e "Python3 is not installed.\nPlease install Python3."; \
		exit 1; \
	fi
	if ! python3 -m venv venv; then \
		if [ -x $$(command -v apt-get) ]; then \
			sudo apt-get update && sudo apt-get install -y python3.10-venv; \
			python3 -m venv venv; \
		else \
			echo -e "You are not on Ubuntu.\nPlease install the 'python3.10-venv' package manually."; \
			exit 1; \
		fi; \
	fi
	source venv/bin/activate
