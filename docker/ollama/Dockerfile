FROM ollama/ollama:latest

COPY ./pull-llm.sh /pull-llm.sh

# Expose a health check endpoint
COPY health_check.sh /usr/local/bin/health_check.sh
HEALTHCHECK CMD ["sh", "/usr/local/bin/health_check.sh"]