FROM python:3.11-slim

# Install build deps and runtime libs for common wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install common packages used in sandboxes
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install pandas duckdb pg8000 psycopg2-binary

# Create a non-root user for safety
RUN useradd -m -u 1000 sandboxuser
USER sandboxuser
WORKDIR /home/sandboxuser

# Keep a sleep entrypoint so containers start idle and we can exec into them
ENTRYPOINT ["sleep", "infinity"]
