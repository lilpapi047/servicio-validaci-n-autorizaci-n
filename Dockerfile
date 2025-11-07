# ===============================
# 🔹 Etapa base: imagen liviana
# ===============================
FROM python:3.11-slim

# Evitar archivos .pyc y asegurar salida inmediata
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear carpeta de trabajo
WORKDIR /app
RUN useradd -m appuser

# Copiar solo dependencias primero (mejora cache build)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código (después de deps)
COPY . .

#Switch to non-root
USER appuser

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para iniciar la app con autoreload (útil en desarrollo)
CMD ["uvicorn", "servicio_validacion.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
