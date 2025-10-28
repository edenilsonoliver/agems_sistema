"""
URLs para adicionar ao urls.py do app acoes.

Adicione estas rotas ao seu arquivo acoes/urls.py existente:
"""

from django.urls import path
from . import views_kanban

# Adicionar estas URLs ao urlpatterns existente
urlpatterns_kanban = [
    # Visualização Kanban
    path('tarefas/kanban/', views_kanban.tarefa_kanban_view, name='tarefa_kanban'),
    
    # Endpoint para atualizar status via drag & drop
    path('tarefas/<int:pk>/update-status/', views_kanban.tarefa_update_status, name='tarefa_update_status'),
    
    # Endpoint para carregar formulário no modal
    path('tarefas/<int:pk>/edit-ajax/', views_kanban.tarefa_edit_ajax, name='tarefa_edit_ajax'),
]

# ===== INSTRUÇÕES DE INSTALAÇÃO =====
# 
# 1. Abra o arquivo acoes/urls.py
# 
# 2. Adicione o import:
#    from . import views_kanban
# 
# 3. Adicione as rotas ao urlpatterns existente:
#    urlpatterns = [
#        # ... suas rotas existentes ...
#        
#        # Kanban
#        path('tarefas/kanban/', views_kanban.tarefa_kanban_view, name='tarefa_kanban'),
#        path('tarefas/<int:pk>/update-status/', views_kanban.tarefa_update_status, name='tarefa_update_status'),
#        path('tarefas/<int:pk>/edit-ajax/', views_kanban.tarefa_edit_ajax, name='tarefa_edit_ajax'),
#    ]

