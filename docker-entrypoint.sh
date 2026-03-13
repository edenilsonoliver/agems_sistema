#!/bin/bash
set -e

echo "=========================================="
echo "  ðŸš€ AGEMS - Sistema de GestÃ£o RegulatÃ³ria"
echo "=========================================="
echo ""

# ==========================================
# ðŸ•’ Aguarda o banco de dados (PostgreSQL)
# ==========================================
if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]; then
  echo "â³ Aguardando PostgreSQL (${DB_HOST}:${DB_PORT})..."
  python <<'PYCODE'
import socket, time, os
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
while True:
    try:
        socket.create_connection((host, port), timeout=3)
        print("âœ… PostgreSQL estÃ¡ pronto!")
        break
    except OSError:
        print("â³ Aguardando PostgreSQL...")
        time.sleep(2)
PYCODE
else
  echo "ðŸ’¾ Usando banco de dados SQLite local"
fi

# ==========================================
# ðŸ“¦ Aplicar migraÃ§Ãµes
# ==========================================
echo ""
echo "ðŸ“œ Aplicando migraÃ§Ãµes do banco de dados..."
python manage.py migrate --noinput

# ==========================================
# ðŸŽ¨ Coletar arquivos estÃ¡ticos
# ==========================================
echo ""
echo "ðŸŽ¨ Coletando arquivos estÃ¡ticos..."
python manage.py collectstatic --noinput

# ==========================================
# ðŸ›¡ï¸ Configurar Grupos e PermissÃµes
# ==========================================
echo ""
echo "ðŸ›¡ï¸ Configurando grupos e permissÃµes de acesso..."
python manage.py setup_permissions

# ==========================================
# ðŸ‘¤ Criar superusuÃ¡rio padrÃ£o (se nÃ£o existir)
# ==========================================
echo ""
echo "ðŸ‘¤ Verificando superusuÃ¡rio e sincronizando grupos..."
python manage.py shell <<EOF
from usuarios.models import Usuario
from django.contrib.auth.models import Group

# Criar superusuÃ¡rio admin se nÃ£o existir
if not Usuario.objects.filter(username='admin').exists():
    print("Criando superusuÃ¡rio admin...")
    admin = Usuario.objects.create_superuser(
        username='admin',
        email='admin@agems.ms.gov.br',
        password='admin123',
        first_name='Administrador',
        last_name='AGEMS',
        perfil=0
    )
    print("âœ… SuperusuÃ¡rio criado com sucesso!")
else:
    print("â„¹ï¸ SuperusuÃ¡rio admin jÃ¡ existe.")

# SincronizaÃ§Ã£o automÃ¡tica de grupos para todos os usuÃ¡rios
groups_map = {1: 'Gestores', 2: 'Gestores', 3: 'Tecnicos', 4: 'Tecnicos', 5: 'Visualizadores'}
for user in Usuario.objects.all():
    if user.perfil in groups_map:
        group_name = groups_map[user.perfil]
        try:
            group = Group.objects.get(name=group_name)
            if group not in user.groups.all():
                user.groups.add(group)
                print(f"âœ… {user.username} â†’ grupo {group_name}")
        except Group.DoesNotExist:
            print(f"âš ï¸ Grupo {group_name} nÃ£o encontrado para {user.username}")
EOF

# ==========================================
# âœ… InicializaÃ§Ã£o concluÃ­da
# ==========================================
echo ""
echo "=========================================="
echo "  âœ… Sistema iniciado com sucesso!"
echo "=========================================="
echo ""
echo "ðŸŒ Acesse: http://localhost:8000"
echo "ðŸ‘¤ UsuÃ¡rio: admin"
echo "ðŸ”‘ Senha: admin123"
echo ""

# Executar comando padrÃ£o do container
exec "$@"
