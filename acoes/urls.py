
from django.urls import path
from . import views, views_kanban, views_json

urlpatterns = [
    # Manter rotas existentes que estavam provavelmente no urls principal (preciso verificar)
    # Mas como o arquivo não existia, vou assumir temporariamente que vou criar apenas as NOVAS rotas 
    # ou preciso mover as rotas antigas para cá se elas estiverem soltas.
    # PLANO: Definir apenas as JSON API routes aqui por enquanto para não quebrar o existente, 
    # a menos que eu ache onde as outras estão.
    
    # Rotas AJAX/JSON para Fotos
    path('acao/<int:pk>/foto/upload/', views_json.acao_foto_upload, name='acao_foto_upload'),
    path('foto/<int:foto_id>/delete/', views_json.acao_foto_delete, name='acao_foto_delete'),

    # Rotas AJAX/JSON para Documentos
    path('acao/<int:pk>/doc/upload/', views_json.acao_documento_upload, name='acao_documento_upload'),
    path('doc/<int:doc_id>/delete/', views_json.acao_documento_delete, name='acao_documento_delete'),

    # Rotas AJAX/JSON para Mapa (Fase 5)
    path('acao/<int:acao_id>/marcadores/', views.listar_marcadores_ajax, name='listar_marcadores_ajax'),
    path('acao/<int:acao_id>/marcador/salvar/', views.salvar_marcador_ajax, name='salvar_marcador_ajax'),
    path('marcador/<int:marcador_id>/deletar/', views.deletar_marcador_ajax, name='deletar_marcador_ajax'),
]
