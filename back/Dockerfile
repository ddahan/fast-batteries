##########################################################################################
# stage: requirements
##########################################################################################

# Use a specific Python version as the base image for requirements
FROM python:3.13.2-bookworm as requirements-stage

# Set the working directory inside the container
WORKDIR /tmp

# Install Poetry for dependency management
RUN pip install poetry

# Copy only the Poetry configuration files to leverage Docker caching for dependencies
COPY ./pyproject.toml ./poetry.lock /tmp/

# Check
RUN poetry --version && poetry check && poetry lock

# Export dependencies from Poetry to a requirements.txt file for later use
# This helps avoid installing Poetry in the final image
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --verbose

##########################################################################################
# stage: final image build 
##########################################################################################

# Use a clean Python base image for the final build
FROM python:3.13.2-bookworm

# Set the working directory for the application code
WORKDIR /code

# Copy the generated requirements.txt from the requirements stage
# This avoids including Poetry in the final image, reducing image size
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# Install dependencies from requirements.txt
# --no-cache-dir prevents caching, reducing the final image size
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy useful files to the container
COPY ./app /code/app
COPY ./public /code/public
COPY ./migrations /code/migrations
COPY alembic.ini /code/alembic.ini

# Set environment variables for the Python application
ENV PYTHONPATH=/code
ENV PYTHONUNBUFFERED=1

# NOTE: CMD command is omitted here, the Docker Compose file handles it, as the image
# is used multiple times with different start command.
