import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from usuarios.models import Usuario
from django.contrib.auth.models import Permission

username = 'teste_tecnico'
try:
    user = Usuario.objects.get(username=username)
    print(f"Usuário: {user.username}")
    print(f"Perfil: {user.perfil} ({user.get_perfil_display()})")
    print(f"Diretoria: {user.diretoria}")
    print(f"Subunidade: {user.subunidade}")
    print(f"É Superusuário? {user.is_superuser}")
    print(f"É Staff? {user.is_staff}")
    
    print("\nPermissões Diretas:")
    for perm in user.user_permissions.all():
        print(f" - {perm.codename}")
        
    print("\nPermissões de Grupos:")
    for group in user.groups.all():
        print(f" Grupo: {group.name}")
        for perm in group.permissions.all():
            print(f"  - {perm.codename}")
            
    print("\nPermissões Totais (has_perm('instrumentos.change_instrumento')):")
    print(f" Resultado: {user.has_perm('instrumentos.change_instrumento')}")

except Usuario.DoesNotExist:
    print(f"Usuário {username} não encontrado.")
except Exception as e:
    print(f"Erro: {e}")
