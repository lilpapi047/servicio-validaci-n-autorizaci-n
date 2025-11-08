#Funcion
FROM python:3.11.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pytest

COPY . .

# Agregar la carpeta /app al PYTHONPATH
ENV PYTHONPATH=/app

CMD ["pytest", "tests"]