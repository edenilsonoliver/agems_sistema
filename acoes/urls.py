
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

    # Rotas AJAX/JSON para Conformidades (Fase 5)
    path('acao/<int:acao_id>/conformidades/data/', views.conformidades_data_ajax, name='conformidades_data_ajax'),
    path('conformidades/item/status/update/', views.update_item_status_ajax, name='update_item_status_ajax'),
    path('conformidades/item/constatacao/add/', views.add_constatacao_ajax, name='add_constatacao_ajax'),
    path('conformidades/constatacao/remove/', views.remove_constatacao_ajax, name='remove_constatacao_ajax'),
    path('conformidades/item/foto/upload/', views.upload_foto_item_ajax, name='upload_foto_item_ajax'),
    path('conformidades/foto/update-legenda/', views.update_foto_legenda_ajax, name='update_foto_legenda_ajax'),
    path('conformidades/item/rename/', views.rename_item_ajax, name='rename_item_ajax'),
    
    # Gerenciamento de Templates e Grupos
    path('conformidades/templates/list/', views.listar_templates_ajax, name='listar_templates_ajax'),
    path('acao/<int:acao_id>/conformidades/aplicar-template/', views.aplicar_template_ajax, name='aplicar_template_ajax'),
    path('acao/<int:acao_id>/conformidades/salvar-template/', views.salvar_como_template_ajax, name='salvar_como_template_ajax'),
    path('acao/<int:acao_id>/conformidades/grupo/criar/', views.criar_grupo_ajax, name='criar_grupo_ajax'),
    path('conformidades/grupo/renomear/', views.renomear_grupo_ajax, name='renomear_grupo_ajax'),
    path('conformidades/grupo/remover/', views.remover_grupo_ajax, name='remover_grupo_ajax'),
    path('conformidades/item/adicionar/', views.adicionar_item_ajax, name='adicionar_item_ajax'),
    path('conformidades/item/remover/', views.remover_item_ajax, name='remover_item_ajax'),
    path('acao/<int:acao_id>/conformidades/remover-todas/', views.remover_todas_conformidades_ajax, name='remover_todas_conformidades_ajax'),
    path('conformidades/grupos/reordenar/', views.reordenar_grupos_ajax, name='reordenar_grupos_ajax'),
    path('conformidades/itens/reordenar/', views.reordenar_itens_ajax, name='reordenar_itens_ajax'),
    path('conformidades/template/salvar-direto/', views.salvar_template_direto_ajax, name='salvar_template_direto_ajax'),
    path('instrumento/<int:instrumento_id>/obrigacoes/', views.listar_obrigacoes_instrumento_ajax, name='listar_obrigacoes_instrumento_ajax'),

    # Gestão de Templates (Página dedicada)
    path('conformidades/templates/', views.template_list, name='template_list'),
    path('conformidades/template/create/', views.template_create, name='template_create'),
    path('conformidades/template/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('conformidades/template/item/add/', views.template_add_item_ajax, name='template_add_item_ajax'),
    path('conformidades/template/item/remove/', views.template_remove_item_ajax, name='template_remove_item_ajax'),
    path('conformidades/template/item/rename/', views.template_rename_item_ajax, name='template_rename_item_ajax'),
    path('conformidades/template/<int:pk>/delete/', views.template_delete_ajax, name='template_delete_ajax'),

    # Modal de seleção de tipo de ação (carregado via fetch no botão Adicionar)
    path('tipo-seletor/', views.acao_tipo_selector, name='acao_tipo_selector'),
]
