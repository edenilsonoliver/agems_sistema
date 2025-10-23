from django.contrib import admin
from .models import Entidade


@admin.register(Entidade)
class EntidadeAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'cnpj', 'tipo_entidade', 'tipo_servico', 'status', 'cidade']
    list_filter = ['tipo_entidade', 'tipo_servico', 'status', 'estado']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj', 'representante_legal']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('razao_social', 'nome_fantasia', 'cnpj', 'tipo_entidade', 'tipo_servico', 'logo', 'status')
        }),
        ('Contato', {
            'fields': ('email', 'telefone', 'site')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Representante Legal', {
            'fields': ('representante_legal', 'cpf_representante', 'email_representante', 'telefone_representante')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
