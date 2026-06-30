#!/bin/bash
set -e

echo "=========================================="
echo "  AGEMS - Sistema de Gestao Regulatoria"
echo "=========================================="
echo ""

# ==========================================
# Aguarda o banco de dados (PostgreSQL)
# ==========================================
if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]; then
  echo "Aguardando PostgreSQL (${DB_HOST}:${DB_PORT})..."
  python <<'PYCODE'
import socket, time, os
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
while True:
    try:
        socket.create_connection((host, port), timeout=3)
        print("PostgreSQL esta pronto!")
        break
    except OSError:
        print("Aguardando PostgreSQL...")
        time.sleep(2)
PYCODE
else
  echo "Usando banco de dados SQLite local"
fi

# ==========================================
# Aplicar migracoes
# ==========================================
echo ""
echo "Aplicando migracoes do banco de dados..."
python manage.py migrate --noinput

# ==========================================
# Coletar arquivos estaticos
# ==========================================
echo ""
echo "Coletando arquivos estaticos..."
python manage.py collectstatic --noinput

# ==========================================
# Configurar Grupos e Permissoes
# ==========================================
echo ""
echo "Configurando grupos e permissoes de acesso..."
python manage.py setup_permissions

# ==========================================
# Criar superusuario padrao (se nao existir)
# ==========================================
echo ""
echo "Verificando superusuario e sincronizando grupos..."

# Criar admin somente se a variavel DJANGO_SUPERUSER_PASSWORD estiver definida
# e o usuario ainda nao existir. Em producao com admin ja existente: ignorado.
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell <<EOF_ADMIN
from usuarios.models import Usuario
import os

if not Usuario.objects.filter(username='admin').exists():
    print("Criando superusuario admin...")
    Usuario.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@agems.ms.gov.br'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD'),
        first_name='Administrador',
        last_name='AGEMS',
        perfil=0
    )
    print("Superusuario criado com sucesso!")
else:
    print("Superusuario admin ja existe. Nenhuma alteracao realizada.")
EOF_ADMIN
else
  echo "DJANGO_SUPERUSER_PASSWORD nao definida - superusuario nao sera criado automaticamente."
fi

# Sincronizacao automatica de grupos para todos os usuarios
python manage.py shell <<EOF_GROUPS
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
Usuario = get_user_model()

groups_map = {1: 'Gestores', 2: 'Gestores', 3: 'Tecnicos', 4: 'Tecnicos', 5: 'Visualizadores'}
for user in Usuario.objects.all():
    if user.perfil in groups_map:
        group_name = groups_map[user.perfil]
        try:
            group = Group.objects.get(name=group_name)
            if group not in user.groups.all():
                user.groups.add(group)
                print(f"{user.username} -> grupo {group_name}")
        except Group.DoesNotExist:
            print(f"Grupo {group_name} nao encontrado para {user.username}")
EOF_GROUPS

# ==========================================
# Inicializacao concluida
# ==========================================
echo ""
echo "=========================================="
echo "  Sistema iniciado com sucesso!"
echo "=========================================="
echo ""
echo "Acesse: http://localhost:8000"
echo ""

# Executar comando padrao do container
exec "$@"
