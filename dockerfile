# Imagen base ligera de Python
FROM python:3.11-slim

# Evitar bytecode y habilitar logs instantáneos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y cambiar a directorio de trabajo
WORKDIR /app

# Crear usuario sin privilegios
RUN useradd -m appuser

# Copiar solo dependencias primero (para aprovechar caché)
COPY requirements.txt .

# Instalar dependencias del proyecto
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Cambiar al usuario no root
USER appuser

# Exponer el puerto donde correrá FastAPI
EXPOSE 8030

ENV PYTHONPATH=/app

# Comando por defecto: iniciar FastAPI
CMD ["uvicorn", "services.auth_service.main:app", "--host", "0.0.0.0", "--port", "8030"]