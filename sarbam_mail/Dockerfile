# syntax=docker/dockerfile:1

FROM python:3.10-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN python3 -m pip install --upgrade pip

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --noinput


# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD gunicorn 'sarbam_mail.wsgi' --bind=0.0.0.0:8000