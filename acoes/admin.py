from django.contrib import admin
from .models import Acao, Tarefa


class TarefaInline(admin.TabularInline):
    model = Tarefa
    extra = 1
    fields = ['nome', 'responsavel', 'status', 'percentual_cumprido', 'data_inicio', 'data_fim', 'prioridade']
    readonly_fields = []


@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'obrigacao', 'tipo_acao', 'responsavel', 
        'status', 'percentual_cumprido', 'data_fim_prevista', 'periodicidade'
    ]
    list_filter = ['status', 'tipo_acao', 'periodicidade', 'responsavel']
    search_fields = ['nome', 'descricao', 'obrigacao__titulo']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    date_hierarchy = 'data_fim_prevista'
    inlines = [TarefaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'obrigacao', 'tipo_acao', 'responsavel')
        }),
        ('Status e Progresso', {
            'fields': ('status', 'percentual_cumprido')
        }),
        ('Periodicidade e Prazos', {
            'fields': (
                'periodicidade', 
                'data_inicio', 
                'data_fim_prevista', 
                'data_fim_real'
            )
        }),
        ('Alertas', {
            'fields': ('dias_antecedencia_alerta',)
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
        # Atualizar status automaticamente após salvar
        obj.verificar_status_automatico()


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'acao', 'responsavel', 'status', 
        'percentual_cumprido', 'data_inicio', 'data_fim', 'prioridade'
    ]
    list_filter = ['status', 'prioridade', 'responsavel', 'acao__tipo_acao']
    search_fields = ['nome', 'descricao', 'acao__nome']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    filter_horizontal = ['executores', 'tarefas_predecessoras']
    date_hierarchy = 'data_inicio'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'acao')
        }),
        ('Responsabilidade', {
            'fields': ('responsavel', 'executores')
        }),
        ('Status e Progresso', {
            'fields': ('status', 'percentual_cumprido', 'prioridade')
        }),
        ('Datas (Gráfico de Gantt)', {
            'fields': ('data_inicio', 'data_fim', 'data_conclusao')
        }),
        ('Dependências', {
            'fields': ('tarefas_predecessoras',),
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
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Atualizar status automaticamente após salvar
        obj.verificar_status_automatico()
