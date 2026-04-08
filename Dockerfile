FROM python:3.11-slim

# Install uv directly into the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies for Linux using uv's resolution
RUN uv sync --frozen --no-dev

# Copy application source code
COPY . .

# Run the cron job via uv
CMD ["uv", "run", "python", "main.py"]
