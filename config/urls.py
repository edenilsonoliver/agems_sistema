from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from dashboards.views import dashboard_principal
from acoes import views as acoes_views
from core.config_views import configuracoes
from usuarios import views as usuarios_views
from usuarios.views import get_subunidades_por_diretoria
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
    tipo_instrumento_create, diretoria_create, arquivo_upload, arquivo_delete,
    importar_obrigacoes_csv
)

# Entidades
from entidades.views import (
    EntidadeListView, EntidadeCreateView, EntidadeUpdateView, EntidadeDeleteView
)

# Ações (Novo Fluxo Unificado)
from acoes.views import (
    AcaoListView, AcaoCreateView, AcaoUpdateView, AcaoDeleteView,
    AcaoCalendarioView, acoes_json, get_obrigacoes_por_instrumento
)

# ✅ KANBAN - Import das views do Kanban
from acoes import views_kanban

# Indicadores
from indicadores.views import (
    IndicadorListView, IndicadorCreateView, IndicadorUpdateView, IndicadorDeleteView
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
    
    # Adicionado para suportar Correcao de Bug Latente no VerificaSenhaTemporariaMixin do usuario
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

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
    path('api/arquivo/<int:arquivo_id>/excluir/', arquivo_delete, name='arquivo_delete'),
    path('api/obrigacoes/importar-csv/', importar_obrigacoes_csv, name='importar_obrigacoes_csv'),
    path('api/subunidades/', get_subunidades_por_diretoria, name='get_subunidades'),

    # Entidades
    path('entidades/', EntidadeListView.as_view(), name='entidade_list'),
    path('entidades/criar/', EntidadeCreateView.as_view(), name='entidade_create'),
    path('entidades/<int:pk>/editar/', EntidadeUpdateView.as_view(), name='entidade_edit'),
    path('entidades/<int:pk>/excluir/', EntidadeDeleteView.as_view(), name='entidade_delete'),

    # Ações Unificadas
    path('acoes/', AcaoListView.as_view(), name='acao_list'),
    path('acoes/criar/', AcaoCreateView.as_view(), name='acao_create'),
    path('acoes/<int:pk>/editar/', AcaoUpdateView.as_view(), name='acao_edit'),
    path('acoes/<int:pk>/excluir/', AcaoDeleteView.as_view(), name='acao_delete'),
    
    # Calendário e JSON de Ações
    path('acoes/calendario/', AcaoCalendarioView.as_view(), name='acao_calendario'),
    path('acoes/json/', acoes_json, name='acoes_json'),

    # ===== KANBAN DE AÇÕES =====
    path('acoes/kanban/', views_kanban.acao_kanban_view, name='acao_kanban'),
    path('acoes/<int:pk>/update-status/', views_kanban.acao_update_status, name='acao_update_status'),
    path('acoes/<int:pk>/edit-ajax/', views_kanban.acao_edit_ajax, name='acao_edit_ajax'),

    # Filtro Dinâmico de Obrigações
    path('acoes/obrigacoes/', get_obrigacoes_por_instrumento, name='get_obrigacoes_por_instrumento'),

    # ✅ Inclui as novas rotas de Mapa e APIs de Ações
    path('acoes/', include('acoes.urls')),

    # Indicadores
    path('indicadores/', IndicadorListView.as_view(), name='indicador_list'),
    path('indicadores/criar/', IndicadorCreateView.as_view(), name='indicador_create'),
    path('indicadores/<int:pk>/editar/', IndicadorUpdateView.as_view(), name='indicador_edit'),
    path('indicadores/<int:pk>/excluir/', IndicadorDeleteView.as_view(), name='indicador_delete'),

    # Configurações
    path('configuracoes/', configuracoes, name='configuracoes'),

    # ✅ Core URLs
    path('diretorias/', DiretoriaListView.as_view(), name='diretoria_list'),
    path('diretorias/criar/', DiretoriaCreateView.as_view(), name='diretoria_create'),
    path('diretorias/<int:pk>/editar/', DiretoriaUpdateView.as_view(), name='diretoria_edit'),
    path('diretorias/<int:pk>/excluir/', DiretoriaDeleteView.as_view(), name='diretoria_delete'),

    # Tipos
    path('tipos-entidade/', TipoEntidadeListView.as_view(), name='tipoentidade_list'),
    path('tipos-entidade/criar/', TipoEntidadeCreateView.as_view(), name='tipoentidade_create'),
    path('tipos-entidade/<int:pk>/editar/', TipoEntidadeUpdateView.as_view(), name='tipoentidade_edit'),
    path('tipos-entidade/<int:pk>/excluir/', TipoEntidadeDeleteView.as_view(), name='tipoentidade_delete'),

    path('tipos-servico/', TipoServicoListView.as_view(), name='tiposervico_list'),
    path('tipos-servico/criar/', TipoServicoCreateView.as_view(), name='tiposervico_create'),
    path('tipos-servico/<int:pk>/editar/', TipoServicoUpdateView.as_view(), name='tiposervico_edit'),
    path('tipos-servico/<int:pk>/excluir/', TipoServicoDeleteView.as_view(), name='tiposervico_delete'),

    path('tipos-instrumento/', TipoInstrumentoListView.as_view(), name='tipoinstrumento_list'),
    path('tipos-instrumento/criar/', TipoInstrumentoCreateView.as_view(), name='tipoinstrumento_create'),
    path('tipos-instrumento/<int:pk>/editar/', TipoInstrumentoUpdateView.as_view(), name='tipoinstrumento_edit'),
    path('tipos-instrumento/<int:pk>/excluir/', TipoInstrumentoDeleteView.as_view(), name='tipoinstrumento_delete'),

    path('tipos-obrigacao/', TipoObrigacaoListView.as_view(), name='tipoobrigacao_list'),
    path('tipos-obrigacao/criar/', TipoObrigacaoCreateView.as_view(), name='tipoobrigacao_create'),
    path('tipos-obrigacao/<int:pk>/editar/', TipoObrigacaoUpdateView.as_view(), name='tipoobrigacao_edit'),
    path('tipos-obrigacao/<int:pk>/excluir/', TipoObrigacaoDeleteView.as_view(), name='tipoobrigacao_delete'),

    path('tipos-acao/', TipoAcaoListView.as_view(), name='tipoacao_list'),
    path('tipos-acao/criar/', TipoAcaoCreateView.as_view(), name='tipoacao_create'),
    path('tipos-acao/<int:pk>/editar/', TipoAcaoUpdateView.as_view(), name='tipoacao_edit'),
    path('tipos-acao/<int:pk>/excluir/', TipoAcaoDeleteView.as_view(), name='tipoacao_delete'),

    # Usuários
    path('usuarios/perfil/', usuarios_views.UsuarioPerfilView.as_view(), name='usuario_perfil'),
    path('usuarios/', usuarios_views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/criar/', usuarios_views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', usuarios_views.UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('usuarios/<int:pk>/excluir/', usuarios_views.UsuarioDeleteView.as_view(), name='usuario_delete'),  

    # Subunidades
    path('subunidades/', SubunidadeListView.as_view(), name='subunidade_list'),
    path('subunidades/criar/', SubunidadeCreateView.as_view(), name='subunidade_create'),
    path('subunidades/<int:pk>/editar/', SubunidadeUpdateView.as_view(), name='subunidade_edit'),
    path('subunidades/<int:pk>/excluir/', SubunidadeDeleteView.as_view(), name='subunidade_delete'),


    # Georeferencias
    path('georeferencias/', include('georeferencias.urls')),

    # Alertas

    path('alertas/', include('alertas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
