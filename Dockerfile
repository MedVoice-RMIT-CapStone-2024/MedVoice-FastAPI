# This is the first stage, it is named requirements-stage
FROM python:3.11 as requirements-stage

# Here's where we will generate the file requirements.txt
WORKDIR /workspace/tmp

# Install poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files to the /workspace/tmp directory
COPY ./pyproject.toml ./poetry.lock* /workspace/tmp/

# Generate the requirements.txt file
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# This is the final stage
FROM python:3.11 as final-stage

# Set the current working directory to /workspace/code
WORKDIR /workspace/code

# Copy the requirements.txt file from the requirements-stage to the /workspace/code directory
COPY --from=requirements-stage /workspace/tmp/requirements.txt /workspace/code/requirements.txt

# Install the package dependencies in the generated requirements.txt file
RUN pip install --no-cache-dir --upgrade -r /workspace/code/requirements.txt

# Copy the app directory to the /workspace/code directory
COPY ./app /workspace/code/app

# Copy the static, assets, and audios directories to the /workspace/code directory
COPY ./static /workspace/code/static
COPY ./assets /workspace/code/assets
COPY ./audios /workspace/code/audios

# Set the environment variable to indicate that the application is running in Docker
ENV RUNNING_IN_DOCKER=true

# Set the command to use uvicorn to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
