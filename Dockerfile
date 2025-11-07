FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pytest

COPY . .

# Agregar la carpeta /app al PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["pytest", "tests"]