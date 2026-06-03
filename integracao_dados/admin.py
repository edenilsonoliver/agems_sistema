from django.contrib import admin
from .models import (
    FonteDados, CredencialFonte, Endpoint, Snapshot, 
    Dataset, Dashboard, Widget, VinculoObrigacao, CompartilhamentoAnalitico
)

@admin.register(FonteDados)
class FonteDadosAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'diretoria', 'status_integracao', 'frequencia_minutos')
    list_filter = ('tipo', 'status_integracao', 'diretoria')
    search_fields = ('nome', 'url_base')

@admin.register(CredencialFonte)
class CredencialFonteAdmin(admin.ModelAdmin):
    list_display = ('fonte', 'usuario_api', 'data_expiracao')

@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fonte', 'metodo_http', 'ativo')
    list_filter = ('metodo_http', 'ativo', 'fonte')

@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'data_hora', 'status', 'quantidade_registros', 'tempo_execucao_ms')
    list_filter = ('status', 'endpoint')
    date_hierarchy = 'data_hora'

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('nome', 'diretoria_proprietaria', 'versao', 'data_atualizacao')
    list_filter = ('diretoria_proprietaria',)
    search_fields = ('nome',)

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('nome', 'diretoria_proprietaria', 'criador')
    list_filter = ('diretoria_proprietaria',)
    search_fields = ('nome',)

@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'dashboard', 'tipo', 'ordem')
    list_filter = ('tipo', 'dashboard')

@admin.register(VinculoObrigacao)
class VinculoObrigacaoAdmin(admin.ModelAdmin):
    list_display = ('obrigacao', 'dashboard', 'dataset', 'tipo_vinculo')
    list_filter = ('tipo_vinculo',)

@admin.register(CompartilhamentoAnalitico)
class CompartilhamentoAnaliticoAdmin(admin.ModelAdmin):
    list_display = ('dashboard', 'diretoria_destino', 'nivel_acesso', 'data_expiracao')
    list_filter = ('nivel_acesso', 'diretoria_destino')
