# ===== ADMIN PARA GERENCIAR NOTIFICAÇÕES =====
from django.contrib import admin
from django.utils.html import format_html
from .models import Notificacao, PreferenciaNotificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'usuario',
        'tipo_badge',
        'titulo_truncado',
        'prioridade_badge',
        'lida_badge',
        'data_criacao',
    ]
    
    list_filter = [
        'tipo',
        'prioridade',
        'lida',
        'data_criacao',
    ]
    
    search_fields = [
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'titulo',
        'mensagem',
    ]
    
    readonly_fields = [
        'data_criacao',
        'data_leitura',
    ]
    
    fieldsets = (
        ('Destinatário', {
            'fields': ('usuario',)
        }),
        ('Conteúdo', {
            'fields': ('tipo', 'prioridade', 'titulo', 'mensagem', 'link')
        }),
        ('Entidades Relacionadas', {
            'fields': ('tarefa_id', 'obrigacao_id', 'instrumento_id'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('lida', 'data_leitura', 'data_expiracao')
        }),
        ('Metadados', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_como_lida', 'marcar_como_nao_lida', 'excluir_selecionadas']
    
    def tipo_badge(self, obj):
        cores = {
            'tarefa_atrasada': 'danger',
            'tarefa_vencendo_hoje': 'warning',
            'tarefa_a_vencer': 'info',
            'tarefa_nova': 'primary',
            'obrigacao_vencendo': 'warning',
        }
        cor = cores.get(obj.tipo, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            cor,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = 'Tipo'
    
    def prioridade_badge(self, obj):
        cores = {
            'baixa': 'secondary',
            'media': 'info',
            'alta': 'warning',
            'urgente': 'danger',
        }
        cor = cores.get(obj.prioridade, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            cor,
            obj.get_prioridade_display()
        )
    prioridade_badge.short_description = 'Prioridade'
    
    def lida_badge(self, obj):
        if obj.lida:
            return format_html('<span class="badge bg-success">✓ Lida</span>')
        return format_html('<span class="badge bg-secondary">○ Não lida</span>')
    lida_badge.short_description = 'Status'
    
    def titulo_truncado(self, obj):
        if len(obj.titulo) > 50:
            return obj.titulo[:50] + '...'
        return obj.titulo
    titulo_truncado.short_description = 'Título'
    
    def marcar_como_lida(self, request, queryset):
        count = 0
        for notif in queryset:
            notif.marcar_como_lida()
            count += 1
        self.message_user(request, f'{count} notificações marcadas como lidas.')
    marcar_como_lida.short_description = 'Marcar como lida'
    
    def marcar_como_nao_lida(self, request, queryset):
        count = 0
        for notif in queryset:
            notif.marcar_como_nao_lida()
            count += 1
        self.message_user(request, f'{count} notificações marcadas como não lidas.')
    marcar_como_nao_lida.short_description = 'Marcar como não lida'
    
    def excluir_selecionadas(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} notificações excluídas.')
    excluir_selecionadas.short_description = 'Excluir selecionadas'


@admin.register(PreferenciaNotificacao)
class PreferenciaNotificacaoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'notificar_tarefa_atrasada',
        'notificar_tarefa_vencendo',
        'notificar_obrigacao',
        'enviar_email',
        'tocar_som',
    ]
    
    list_filter = [
        'enviar_email',
        'frequencia_email',
        'tocar_som',
        'mostrar_toast',
    ]
    
    search_fields = [
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
    ]
    
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Tipos de Notificação', {
            'fields': (
                'notificar_tarefa_atrasada',
                'notificar_tarefa_vencendo',
                'notificar_tarefa_nova',
                'notificar_obrigacao',
                'notificar_comentario',
            )
        }),
        ('E-mail', {
            'fields': ('enviar_email', 'frequencia_email')
        }),
        ('Interface', {
            'fields': ('tocar_som', 'mostrar_toast')
        }),
    )

