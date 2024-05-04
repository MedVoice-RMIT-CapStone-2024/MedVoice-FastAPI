# This is the first stage, it is named requirements-stage
FROM python:3.9 as requirements-stage

# Here's where we will generate the file requirements.txt
WORKDIR /tmp

# Copy the pyproject.toml and poetry.lock files to the /tmp directory
RUN pip install poetry

# Generate the requirements.txt file
COPY ./pyproject.toml ./poetry.lock* /tmp/

# This is the final stage, anything here will be preserved in the final container image
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# 
FROM python:3.9

# Set the current working directory to /code
WORKDIR /code

# Copy the requirements.txt file to the /code directory
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# Install the package dependencies in the generated requirements.txt file
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app directory to the /code directory
COPY ./app /code/app

# Define environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/code/app/service-account-file.json

# Set the command to use fastapi run, which uses Uvicorn underneath
CMD ["fastapi", "run", "app/main.py", "--port", "80"]