# Docker image for Python sandbox server
# Builds a container with Python, UV package manager, and required dependencies

FROM python:3.11-slim

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Use UV for package management
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python packages using UV
COPY requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for HTTP server (if using Flask version)
EXPOSE 8000

# Run the MCP sandbox server
CMD ["python", "src/omcp_py/main.py"]
