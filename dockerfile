# Base image
FROM python:3.11-slim AS runtime

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Workdir inside container
WORKDIR /app

# System dependencies (for psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project code
COPY . .

# Expose FastAPI port
EXPOSE 8010

# Start Uvicorn with your current app path
CMD ["uvicorn", "API.app.main:app", "--host", "0.0.0.0", "--port", "8010"]
