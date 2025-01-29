# syntax=docker/dockerfile:1

FROM python:3.10-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Grant the 'appuser' ownership of the /app directory.
RUN chown -R appuser:appuser /app

COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN python3 -m pip install --upgrade pip

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Give 'appuser' permissions on the pip cache (if used)
RUN chown -R appuser:appuser /root/.cache

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD gunicorn 'sarbam_mail.wsgi' --bind=0.0.0.0:8000