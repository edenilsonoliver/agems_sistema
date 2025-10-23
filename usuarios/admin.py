from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administração customizada para o modelo Usuario."""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'perfil', 'ativo', 'is_staff']
    list_filter = ['perfil', 'ativo', 'is_staff', 'is_superuser']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações AGEMS', {
            'fields': ('perfil', 'cargo', 'setor', 'telefone', 'concessionaria', 'ativo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações AGEMS', {
            'fields': ('perfil', 'cargo', 'setor', 'telefone', 'concessionaria', 'ativo')
        }),
    )
