# This is the first stage, it is named requirements-stage
FROM python:3.11 as requirements-stage

# Here's where we will generate the file requirements.txt
WORKDIR /tmp

# Install poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files to the /tmp directory
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Generate the requirements.txt file
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# This is the final stage
FROM python:3.11 as final-stage

# Set the current working directory to /code
WORKDIR /code

# Copy the requirements.txt file from the requirements-stage to the /code directory
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# Install the package dependencies in the generated requirements.txt file
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app directory to the /code directory
COPY ./app /code/app

# Copy the static, assets, and audios directories to the /code directory
COPY ./static /code/static
COPY ./assets /code/assets
COPY ./audios /code/audios

# Set the environment variable to indicate that the application is running in Docker
ENV RUNNING_IN_DOCKER=true

# Set the command to use uvicorn to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]