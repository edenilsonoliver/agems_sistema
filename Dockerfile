# ===============================
#   AGEMS - Sistema Regulatória
#   Dockerfile atualizado
# ===============================

# Imagem base leve
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Evita criação de .pyc e garante logs no console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema (incluindo netcat e libmagic)
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    build-essential \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . /app

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Concede permissão de execução ao entrypoint
RUN chmod +x /app/docker-entrypoint.sh

# Expõe a porta padrão do Django
EXPOSE 8000

# Define o entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando padrão (No desenvolvimento usa runserver, em produção o docker-compose.prod.yml sobrescreve para gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
