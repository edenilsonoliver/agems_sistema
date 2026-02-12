from django.contrib import admin
from .models import CamadaReferencia, PontoReferencia

class PontoReferenciaInline(admin.TabularInline):
    model = PontoReferencia
    extra = 0
    fields = ('nome', 'latitude', 'longitude', 'descricao')
    # readonly_fields = ('latitude', 'longitude') # Pode ser útil proteger

@admin.register(CamadaReferencia)
class CamadaReferenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'pontos_count', 'data_criacao', 'criado_por')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    inlines = [PontoReferenciaInline]
    
    def pontos_count(self, obj):
        return obj.pontos.count()
    pontos_count.short_description = 'Qtd Pontos'

@admin.register(PontoReferencia)
class PontoReferenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'camada', 'latitude', 'longitude')
    list_filter = ('camada',)
    search_fields = ('nome', 'descricao', 'camada__nome')
