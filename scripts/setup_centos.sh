#!/bin/bash

# =================================================================
# AGEMS - Script de Preparação do Servidor CentOS
# =================================================================

# 1. Atualização do Sistema
echo "🔄 Atualizando o sistema..."
sudo yum update -y

# 2. Instalação de Utilitários
echo "📦 Instalando utilitários básicos..."
sudo yum install -y yum-utils git curl

# 3. Configuração do Repositório Docker
echo "🐳 Configurando repositório Docker..."
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 4. Instalação do Docker
echo "🐳 Instalando Docker e Docker Compose..."
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. Iniciar e Habilitar Docker
echo "🚀 Iniciando o serviço Docker..."
sudo systemctl start docker
sudo systemctl enable docker

# 6. Instalação do Portainer CE (Gestão e Orquestração)
echo "🚢 Instalando Portainer CE para gestão visual dos containers..."
sudo docker volume create portainer_data
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest

# 7. Configuração do Firewall (Opcional mas recomendado)
# echo "🛡️ Configurando Firewall..."
# sudo firewall-cmd --permanent --add-service=http
# sudo firewall-cmd --permanent --add-service=https
# sudo firewall-cmd --permanent --add-port=9443/tcp
# sudo firewall-cmd --reload

echo "✅ Servidor CentOS preparado com sucesso!"
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker compose version)"
echo "🚀 Portainer está rodando em: https://[IP-DO-SERVIDOR]:9443"
