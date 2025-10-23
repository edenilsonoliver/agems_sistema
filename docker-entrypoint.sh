#!/bin/bash
set -e

echo "=========================================="
echo "  🚀 AGEMS - Sistema de Gestão Regulatória"
echo "=========================================="
echo ""

# ==========================================
# 🕒 Aguarda o banco de dados (PostgreSQL)
# ==========================================
if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]; then
  echo "⏳ Aguardando PostgreSQL (${DB_HOST}:${DB_PORT})..."
  python <<'PYCODE'
import socket, time, os
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
while True:
    try:
        socket.create_connection((host, port), timeout=3)
        print("✅ PostgreSQL está pronto!")
        break
    except OSError:
        print("⏳ Aguardando PostgreSQL...")
        time.sleep(2)
PYCODE
else
  echo "💾 Usando banco de dados SQLite local"
fi

# ==========================================
# 📦 Aplicar migrações
# ==========================================
echo ""
echo "📜 Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# ==========================================
# 🎨 Coletar arquivos estáticos
# ==========================================
echo ""
echo "🎨 Coletando arquivos estáticos..."
#python manage.py collectstatic --noinput --clear
python manage.py collectstatic --noinput

# ==========================================
# 👤 Criar superusuário padrão (se não existir)
# ==========================================
echo ""
echo "👤 Verificando superusuário..."
python manage.py shell <<EOF
from usuarios.models import Usuario
if not Usuario.objects.filter(username='admin').exists():
    print("Criando superusuário admin...")
    Usuario.objects.create_superuser(
        username='admin',
        email='admin@agems.ms.gov.br',
        password='admin123',
        nome_completo='Administrador AGEMS',
        perfil='ADMINISTRADOR'
    )
    print("✅ Superusuário criado com sucesso!")
else:
    print("ℹ️ Superusuário admin já existe.")
EOF

# ==========================================
# ✅ Inicialização concluída
# ==========================================
echo ""
echo "=========================================="
echo "  ✅ Sistema iniciado com sucesso!"
echo "=========================================="
echo ""
echo "🌐 Acesse: http://localhost:8000"
echo "👤 Usuário: admin"
echo "🔑 Senha: admin123"
echo ""

# Executar comando padrão do container
exec "$@"
