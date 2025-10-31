# ===== URLS DO SISTEMA DE ALERTAS - VERSÃO 2 =====
from django.urls import path
from . import views

urlpatterns = [
    # Alertas do usuário (não lidas)
    path('', views.alertas_usuario, name='alertas_usuario'),
    
    # Marcar como lida
    path('<int:notificacao_id>/marcar-lida/', views.marcar_como_lida, name='marcar_notificacao_lida'),
    
    # Marcar todas como lidas
    path('marcar-todas-lidas/', views.marcar_todas_como_lidas, name='marcar_todas_notificacoes_lidas'),
    
    # Histórico (incluindo lidas)
    path('historico/', views.historico_notificacoes, name='historico_notificacoes'),
    
    # Preferências
    path('preferencias/', views.preferencias_notificacao, name='preferencias_notificacao'),
]

