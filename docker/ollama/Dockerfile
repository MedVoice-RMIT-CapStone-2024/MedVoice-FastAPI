FROM ollama/ollama:latest

# Install nvidia-container-toolkit
RUN apt-get update && \
    apt-get install -y nvidia-container-toolkit

# Copy the pull-llm.sh script
COPY ./pull-llm.sh /pull-llm.sh
