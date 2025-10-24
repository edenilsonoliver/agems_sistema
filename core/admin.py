from django.contrib import admin
from .models import (
    Diretoria, TipoEntidade, TipoServico, 
    TipoInstrumento, TipoObrigacao, TipoAcao
)


@admin.register(Diretoria)
class DiretoriaAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome', 'diretor_responsavel', 'ativa']
    list_filter = ['ativa']
    search_fields = ['nome', 'sigla', 'diretor_responsavel']
    #inlines = [SubunidadeInline]
    ordering = ['sigla']

#class SubunidadeInline(admin.TabularInline):
 #   model = Subunidade
 #   extra = 1

@admin.register(TipoEntidade)
class TipoEntidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(TipoInstrumento)
class TipoInstrumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(TipoObrigacao)
class TipoObrigacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(TipoAcao)
class TipoAcaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']
