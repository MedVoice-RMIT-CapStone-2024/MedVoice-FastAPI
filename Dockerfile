# This is the first stage, it is named builder
FROM python:3.10-slim as builder

RUN pip install --upgrade pip setuptools wheel

# Install and setup poetry config
RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /workspace/tmp

COPY pyproject.toml poetry.lock ./
# Poetry complains if there is no README file
RUN touch README.md

# Install all dependencies + remove poetry cache
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# This is the final stage
FROM python:3.10-slim as final-stage

ENV VIRTUAL_ENV=/workspace/tmp/.venv \
    PATH="/workspace/tmp/.venv/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Install netcat
RUN apt-get update && apt-get install -y netcat-traditional

# Set the current working directory to /workspace/code
WORKDIR /workspace/code

# Copy wait-for-it.sh
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copy all files and directories from the host to the Docker image
COPY . .

# Set the environment variable to indicate that the application is running in Docker
ENV RUNNING_IN_DOCKER=true
ENV NGROK_CONFIG_PATH /workspace/code/ngrok.yml
ENV GOOGLE_APPLICATION_CREDENTIALS /workspace/code/google-credentials.json

# Expose port 8000 and 11434
EXPOSE 8000 11434

# Set the command to use FastAPI to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]