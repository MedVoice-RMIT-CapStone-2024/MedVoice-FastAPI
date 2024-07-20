.PHONY: check
check:
	@which docker-compose > /dev/null && (echo "docker-compose is installed.") || (echo "docker-compose is not installed. Please install it." && exit 1)
	@which docker > /dev/null && (echo "Docker is installed.") || (echo "Docker is not installed. Please install it." && exit 1)
	@which python > /dev/null && (echo "Python is installed.") || (echo "Python is not installed. Please install it. Ignore this if you have python3 installed" && exit 1)
	@test -f .env && (echo ".env file exists.") || (echo ".env file is missing. Please add it." && exit 1)
	@test -f google-credentials.json && (echo "google-credentials.json file exists.") || (echo "google-credentials.json file is missing. Please add it." && exit 1)

.PHONY: setup
setup:
	which python3 > /dev/null python3 -m venv venv || python -m venv venv
	source venv/bin/activate
	which poetry > /dev/null && poetry install || pip install -r requirements.txt
