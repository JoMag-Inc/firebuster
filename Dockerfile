# Start with a bare-bones Python 3.13 computer.
FROM python:3.14-slim

# Don't create extra junk files while running Python.
ENV PYTHONDONTWRITEBYTECODE=1
# Show log messages right away (don't buffer them).
ENV PYTHONUNBUFFERED=1

# Create a folder called /app inside the container to hold our code.
WORKDIR /app

# Install git and clean up extra files to keep the image small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install uv, the tool we use to manage Python packages.
RUN pip install --no-cache-dir uv

# Copy the list of our dependencies from the computer into the container.
COPY pyproject.toml uv.lock README.md ./

# Install all the Python packages our app needs.
RUN uv sync --locked --no-dev

# Copy our actual application code into the container.
COPY app ./app
COPY database/alembic.ini ./
COPY database/migrations ./migrations
# Tell Docker this app listens on port 8000.
EXPOSE 8000

# When the container starts, run our app.
CMD ["uv", "run", "python", "-m", "app.main"]
