# Imagen base ligera de Python
FROM python:3.11-slim

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde correrá FastAPI
EXPOSE 8000

# Comando para iniciar la app con Uvicorn
CMD ["uvicorn", "servicio_validacion.main:app", "--host", "0.0.0.0", "--port", "8000"]
