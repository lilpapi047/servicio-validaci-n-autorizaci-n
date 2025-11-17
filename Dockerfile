FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Comando por defecto
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]