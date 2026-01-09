from django.contrib import admin
from .models import Acao, ChecklistItem


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1


@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'obrigacao', 'responsavel', 
        'status', 'percentual_cumprido', 'data_fim', 'prioridade'
    ]
    list_filter = ['status', 'tipo_acao', 'prioridade', 'responsavel']
    search_fields = ['nome', 'descricao', 'obrigacao__titulo']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    filter_horizontal = ['executores', 'acoes_predecessoras']
    date_hierarchy = 'data_inicio'
    inlines = [ChecklistItemInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'obrigacao', 'tipo_acao', 'responsavel')
        }),
        ('Status e Progresso', {
            'fields': ('status', 'percentual_cumprido', 'prioridade')
        }),
        ('Prazos e Periodicidade', {
            'fields': ('data_inicio', 'data_fim', 'data_conclusao', 'periodicidade')
        }),
        ('Alertas e Dependências', {
            'fields': ('dias_antecedencia_alerta', 'acoes_predecessoras')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Atualizar status automaticamente após salvar se necessário
        # obj.verificar_status_automatico() # Já fazemos no model se preferir
