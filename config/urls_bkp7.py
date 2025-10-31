from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from dashboards.views import dashboard_principal
from acoes import views as acoes_views
from core.config_views import configuracoes
from usuarios import views as usuarios_views
from alertas import views as alertas_views

# Import adicional no topo
from core.core_views import (
    DiretoriaListView, DiretoriaCreateView, DiretoriaUpdateView, DiretoriaDeleteView,
    SubunidadeListView, SubunidadeCreateView, SubunidadeUpdateView, SubunidadeDeleteView,
    TipoEntidadeListView, TipoEntidadeCreateView, TipoEntidadeUpdateView, TipoEntidadeDeleteView,
    TipoServicoListView, TipoServicoCreateView, TipoServicoUpdateView, TipoServicoDeleteView,
    TipoInstrumentoListView, TipoInstrumentoCreateView, TipoInstrumentoUpdateView, TipoInstrumentoDeleteView,
    TipoObrigacaoListView, TipoObrigacaoCreateView, TipoObrigacaoUpdateView, TipoObrigacaoDeleteView,
    TipoAcaoListView, TipoAcaoCreateView, TipoAcaoUpdateView, TipoAcaoDeleteView,
)

# Instrumentos
from instrumentos.views import (
    InstrumentoListView, InstrumentoCreateView, InstrumentoUpdateView, InstrumentoDeleteView,
    tipo_instrumento_create, diretoria_create, arquivo_upload
)

# Entidades
from entidades.views import (
    EntidadeListView, EntidadeCreateView, EntidadeUpdateView, EntidadeDeleteView
)

# Ações e Tarefas
from acoes.views import (
    AcaoListView, AcaoCreateView, AcaoUpdateView, AcaoDeleteView,
    TarefaListView, TarefaCreateView, TarefaUpdateView, TarefaDeleteView
)

# ✅ KANBAN - Import das views do Kanban
from acoes import views_kanban

# Indicadores
from indicadores.views import (
    IndicadorListView, IndicadorCreateView, IndicadorUpdateView, IndicadorDeleteView
)

# Core
from core.views import ModernListView
from core.models import Diretoria, TipoEntidade, TipoServico, TipoInstrumento

# ✅ Importa novamente as views do core
from core.core_views import (
    DiretoriaListView, DiretoriaCreateView, DiretoriaUpdateView, DiretoriaDeleteView,
    TipoEntidadeListView, TipoEntidadeCreateView, TipoEntidadeUpdateView, TipoEntidadeDeleteView,
    TipoServicoListView, TipoServicoCreateView, TipoServicoUpdateView, TipoServicoDeleteView,
    TipoInstrumentoListView, TipoInstrumentoCreateView, TipoInstrumentoUpdateView, TipoInstrumentoDeleteView,
    TipoObrigacaoListView, TipoObrigacaoCreateView, TipoObrigacaoUpdateView, TipoObrigacaoDeleteView,
    TipoAcaoListView, TipoAcaoCreateView, TipoAcaoUpdateView, TipoAcaoDeleteView
)

# 🚫 Bloqueia o acesso direto ao Django Admin
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    # 🔒 Redireciona qualquer tentativa de /admin/ para o login moderno
    path('admin/', redirect_to_login, name='redirect_admin'),

    # Autenticação moderna
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboard
    path('', dashboard_principal, name='dashboard'),

    # Instrumentos
    path('instrumentos/', InstrumentoListView.as_view(), name='instrumento_list'),
    path('instrumentos/criar/', InstrumentoCreateView.as_view(), name='instrumento_create'),
    path('instrumentos/<int:pk>/editar/', InstrumentoUpdateView.as_view(), name='instrumento_edit'),
    path('instrumentos/<int:pk>/excluir/', InstrumentoDeleteView.as_view(), name='instrumento_delete'),

    # APIs CRUD Inline
    path('api/tipo-instrumento/criar/', tipo_instrumento_create, name='tipo_instrumento_create'),
    path('api/diretoria/criar/', diretoria_create, name='diretoria_create'),
    path('api/instrumento/<int:instrumento_id>/arquivo/upload/', arquivo_upload, name='arquivo_upload'),

    # Entidades
    path('entidades/', EntidadeListView.as_view(), name='entidade_list'),
    path('entidades/criar/', EntidadeCreateView.as_view(), name='entidade_create'),
    path('entidades/<int:pk>/editar/', EntidadeUpdateView.as_view(), name='entidade_edit'),
    path('entidades/<int:pk>/excluir/', EntidadeDeleteView.as_view(), name='entidade_delete'),

    # Ações
    path('acoes/', AcaoListView.as_view(), name='acao_list'),
    path('acoes/criar/', AcaoCreateView.as_view(), name='acao_create'),
    path('acoes/<int:pk>/editar/', AcaoUpdateView.as_view(), name='acao_edit'),
    path('acoes/<int:pk>/excluir/', AcaoDeleteView.as_view(), name='acao_delete'),

    # Tarefas
    path('tarefas/', TarefaListView.as_view(), name='tarefa_list'),
    path('tarefas/criar/', TarefaCreateView.as_view(), name='tarefa_create'),
    path('tarefas/<int:pk>/editar/', TarefaUpdateView.as_view(), name='tarefa_edit'),
    path('tarefas/<int:pk>/excluir/', TarefaDeleteView.as_view(), name='tarefa_delete'),

    # Calendário de Tarefas
    path('tarefas/calendario/', acoes_views.TarefaCalendarioView.as_view(), name='tarefa_calendario'),
    path('tarefas/json/', acoes_views.tarefas_json, name='tarefas_json'),

    # ===== KANBAN DE TAREFAS =====
    path('tarefas/kanban/', views_kanban.tarefa_kanban_view, name='tarefa_kanban'),
    path('tarefas/<int:pk>/update-status/', views_kanban.tarefa_update_status, name='tarefa_update_status'),
    path('tarefas/<int:pk>/edit-ajax/', views_kanban.tarefa_edit_ajax, name='tarefa_edit_ajax'),

    # Indicadores
    path('indicadores/', IndicadorListView.as_view(), name='indicador_list'),
    path('indicadores/criar/', IndicadorCreateView.as_view(), name='indicador_create'),
    path('indicadores/<int:pk>/editar/', IndicadorUpdateView.as_view(), name='indicador_edit'),
    path('indicadores/<int:pk>/excluir/', IndicadorDeleteView.as_view(), name='indicador_delete'),

    # Configurações
    path('configuracoes/', configuracoes, name='configuracoes'),

    # ✅ Core URLs restauradas
    path('diretorias/', DiretoriaListView.as_view(), name='diretoria_list'),
    path('diretorias/criar/', DiretoriaCreateView.as_view(), name='diretoria_create'),
    path('diretorias/<int:pk>/editar/', DiretoriaUpdateView.as_view(), name='diretoria_edit'),
    path('diretorias/<int:pk>/excluir/', DiretoriaDeleteView.as_view(), name='diretoria_delete'),

    # Entidades
    path('tipos-entidade/', TipoEntidadeListView.as_view(), name='tipoentidade_list'),
    path('tipos-entidade/criar/', TipoEntidadeCreateView.as_view(), name='tipoentidade_create'),
    path('tipos-entidade/<int:pk>/editar/', TipoEntidadeUpdateView.as_view(), name='tipoentidade_edit'),
    path('tipos-entidade/<int:pk>/excluir/', TipoEntidadeDeleteView.as_view(), name='tipoentidade_delete'),

    # Serviços
    path('tipos-servico/', TipoServicoListView.as_view(), name='tiposervico_list'),
    path('tipos-servico/criar/', TipoServicoCreateView.as_view(), name='tiposervico_create'),
    path('tipos-servico/<int:pk>/editar/', TipoServicoUpdateView.as_view(), name='tiposervico_edit'),
    path('tipos-servico/<int:pk>/excluir/', TipoServicoDeleteView.as_view(), name='tiposervico_delete'),

    # Tipos de Instrumentos
    path('tipos-instrumento/', TipoInstrumentoListView.as_view(), name='tipoinstrumento_list'),
    path('tipos-instrumento/criar/', TipoInstrumentoCreateView.as_view(), name='tipoinstrumento_create'),
    path('tipos-instrumento/<int:pk>/editar/', TipoInstrumentoUpdateView.as_view(), name='tipoinstrumento_edit'),
    path('tipos-instrumento/<int:pk>/excluir/', TipoInstrumentoDeleteView.as_view(), name='tipoinstrumento_delete'),

    # Tipos de Obrigações
    path('tipos-obrigacao/', TipoObrigacaoListView.as_view(), name='tipoobrigacao_list'),
    path('tipos-obrigacao/criar/', TipoObrigacaoCreateView.as_view(), name='tipoobrigacao_create'),
    path('tipos-obrigacao/<int:pk>/editar/', TipoObrigacaoUpdateView.as_view(), name='tipoobrigacao_edit'),
    path('tipos-obrigacao/<int:pk>/excluir/', TipoObrigacaoDeleteView.as_view(), name='tipoobrigacao_delete'),

    # Tipos de Ações
    path('tipos-acao/', TipoAcaoListView.as_view(), name='tipoacao_list'),
    path('tipos-acao/criar/', TipoAcaoCreateView.as_view(), name='tipoacao_create'),
    path('tipos-acao/<int:pk>/editar/', TipoAcaoUpdateView.as_view(), name='tipoacao_edit'),
    path('tipos-acao/<int:pk>/excluir/', TipoAcaoDeleteView.as_view(), name='tipoacao_delete'),

    # Usuários
    path('usuarios/', usuarios_views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/criar/', usuarios_views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', usuarios_views.UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('usuarios/<int:pk>/excluir/', usuarios_views.UsuarioDeleteView.as_view(), name='usuario_delete'),  

    # Subunidades
    path('subunidades/', SubunidadeListView.as_view(), name='subunidade_list'),
    path('subunidades/criar/', SubunidadeCreateView.as_view(), name='subunidade_create'),
    path('subunidades/<int:pk>/editar/', SubunidadeUpdateView.as_view(), name='subunidade_edit'),
    path('subunidades/<int:pk>/excluir/', SubunidadeDeleteView.as_view(), name='subunidade_delete'),

    # Filtro Obrigaçoes na tela de tarefa
   path('tarefas/obrigacoes/', acoes_views.get_obrigacoes_por_instrumento, name='get_obrigacoes_por_instrumento'),

   # Alertas do usuário
   path('alertas/', alertas_views.alertas_usuario, name='alertas_usuario'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

