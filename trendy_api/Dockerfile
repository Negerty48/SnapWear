# Usamos una imagen oficial de Python ligera
FROM python:3.10-slim

# Evita que Python genere archivos .pyc y asegura que la consola escupa logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos dependencias del sistema necesarias para compilar OpenCV (que usa YOLO) y Psycopg2
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Creamos el directorio de trabajo
WORKDIR /code

# Copiamos primero los requirements para aprovechar la caché de Docker
COPY ./requirements.txt /code/requirements.txt

# Instalamos las librerías de Python
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copiamos todo el resto del código y los modelos
COPY ./app /code/app
COPY ./data /code/data

# Exponemos el puerto 80 (El estándar para web/APIs)
EXPOSE 80

# Comando para arrancar el servidor web
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]