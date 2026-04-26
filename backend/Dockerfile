FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias do sistema para pyserial 
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pi install  --no-cache-dir -r requirements.txt

# Copiar o codigo do backend
COPY app.py .

# Expor a porta do flask
EXPOSE 5000

# Comando para rodar o backend
CMD {"python", "app.py"}


