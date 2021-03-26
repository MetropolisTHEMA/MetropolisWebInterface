# Pull base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /metroweb

# Install dependencies
COPY Pipfile Pipfile.lock /metroweb/
RUN pip install pipenv && pipenv install --system

# Copy project
COPY . /metroweb/
