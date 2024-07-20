.PHONY: check
check:
	@which docker-compose > /dev/null && (echo "docker-compose is installed.") || echo "docker-compose is not installed. Please install it."
	@which docker > /dev/null && (echo "Docker is installed.") || echo "Docker is not installed. Please install it."
	@which python > /dev/null && (echo "Python is installed.") || echo "Python is not installed. Please install it. Ignore this if you have python3 installed"
	@test -f .env && (echo ".env file exists.") || echo ".env file is missing. Please see .env-placeholder.txt for reference add it."
	@test -f google-credentials.json && (echo "google-credentials.json file exists.") || echo "google-credentials.json file is missing. Please add it."
	@test -f ngrok.yml && (echo "ngrok.yml file exists.") || echo "ngrok.yml file is missing. Please see ngrok.yml-placeholder.txt for reference and add it."

.PHONY: setup
setup:
	which python3 > /dev/null && python3 -m venv venv || python -m venv venv
	source venv/bin/activate
	which poetry > /dev/null && poetry install || pip install -r requirements.txt
