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
python manage.py collectstatic --noinput

# ==========================================
# 🛡️ Configurar Grupos e Permissões
# ==========================================
echo ""
echo "🛡️ Configurando grupos e permissões de acesso..."
python manage.py setup_permissions

# ==========================================
# 👤 Criar superusuário padrão (se não existir)
# ==========================================
echo ""
echo "👤 Verificando superusuário e sincronizando grupos..."
python manage.py shell <<EOF
from usuarios.models import Usuario
from django.contrib.auth.models import Group

# Criar superusuário admin se não existir
if not Usuario.objects.filter(username='admin').exists():
    print("Criando superusuário admin...")
    admin = Usuario.objects.create_superuser(
        username='admin',
        email='admin@agems.ms.gov.br',
        password='admin123',
        first_name='Administrador',
        last_name='AGEMS',
        perfil=0
    )
    print("✅ Superusuário criado com sucesso!")
else:
    print("ℹ️ Superusuário admin já existe.")

# Sincronização automática de grupos para todos os usuários
groups_map = {1: 'Gestores', 2: 'Gestores', 3: 'Tecnicos', 4: 'Tecnicos', 5: 'Visualizadores'}
for user in Usuario.objects.all():
    if user.perfil in groups_map:
        group_name = groups_map[user.perfil]
        try:
            group = Group.objects.get(name=group_name)
            if group not in user.groups.all():
                user.groups.add(group)
                print(f"✅ {user.username} → grupo {group_name}")
        except Group.DoesNotExist:
            print(f"⚠️ Grupo {group_name} não encontrado para {user.username}")
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
