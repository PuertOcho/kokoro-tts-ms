FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para Kokoro v1.0
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    espeak-ng \
    libespeak-ng-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install -r requirements.txt

# IMPORTANTE: Resolver conflicto onnxruntime vs onnxruntime-gpu
# Reinstalar onnxruntime-gpu para asegurar que tenga prioridad sobre onnxruntime
RUN pip install --force-reinstall onnxruntime-gpu

# Copiar código de la aplicación
COPY app.py .

# Crear directorios necesarios
RUN mkdir -p /app/models /app/debug_audio

# Copiar modelos (se montan como volumen en docker-compose)
# Los modelos se copiarán desde el host

# Exponer puerto
EXPOSE 5002

# Variables de entorno por defecto
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5002
ENV DEFAULT_LANGUAGE=es
ENV DEFAULT_VOICE=ef_dora
ENV DEBUG_AUDIO=true

# Comando para ejecutar la aplicación
CMD ["python", "app.py"] 