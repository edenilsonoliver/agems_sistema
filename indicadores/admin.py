from django.contrib import admin
from .models import IndicadorContratual, ValorIndicador, ImportacaoIndicadores


@admin.register(IndicadorContratual)
class IndicadorContratualAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'tipo', 'unidade_medida', 'ativo']
    list_filter = ['tipo', 'forma_visualizacao', 'ativo']
    search_fields = ['codigo', 'nome', 'descricao']
    ordering = ['ordem_exibicao', 'nome']


@admin.register(ValorIndicador)
class ValorIndicadorAdmin(admin.ModelAdmin):
    list_display = ['indicador', 'contrato', 'periodo_referencia', 'valor', 'valor_meta']
    list_filter = ['indicador', 'contrato']
    search_fields = ['indicador__nome', 'contrato__numero']
    date_hierarchy = 'periodo_referencia'


@admin.register(ImportacaoIndicadores)
class ImportacaoIndicadoresAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'status', 'total_registros', 'registros_sucesso', 'data_importacao']
    list_filter = ['status']
    date_hierarchy = 'data_importacao'
    readonly_fields = ['total_registros', 'registros_sucesso', 'registros_erro', 'log_erros']
