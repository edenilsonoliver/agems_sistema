from django.contrib import admin
from .models import Instrumento, Obrigacao


class ObrigacaoInline(admin.TabularInline):
    model = Obrigacao
    extra = 1
    fields = ['titulo', 'tipo_obrigacao', 'clausula_referencia', 'recorrente', 'data_vencimento', 'status']


@admin.register(Instrumento)
class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo_instrumento', 'diretoria', 'get_entidades_display', 'status', 'data_inicio', 'data_fim']
    list_filter = ['tipo_instrumento', 'diretoria', 'status']
    search_fields = ['numero', 'objeto']
    filter_horizontal = ['entidades']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    inlines = [ObrigacaoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'tipo_instrumento', 'diretoria', 'entidades', 'status')
        }),
        ('Detalhes', {
            'fields': ('objeto', 'data_assinatura', 'data_inicio', 'data_fim', 'valor', 'arquivo')
        }),
        ('Revisão Tarifária', {
            'fields': ('periodicidade_revisao_tarifaria', 'data_proxima_revisao'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Obrigacao)
class ObrigacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'instrumento', 'tipo_obrigacao', 'clausula_referencia', 'recorrente', 'status', 'data_vencimento']
    list_filter = ['tipo_obrigacao', 'status', 'recorrente', 'instrumento__tipo_instrumento']
    search_fields = ['titulo', 'descricao', 'clausula_referencia', 'instrumento__numero']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'instrumento', 'tipo_obrigacao', 'clausula_referencia')
        }),
        ('Características', {
            'fields': ('recorrente', 'data_vencimento', 'dias_antecedencia_alerta')
        }),
        ('Status', {
            'fields': ('status', 'cumprida', 'data_cumprimento')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
