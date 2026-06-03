from django.urls import path
from .views import (
    # Dashboards
    DashboardListView, DashboardDetailView,
    DashboardCreateView, DashboardUpdateView,
    # Datasets
    DatasetCreateView, DatasetUpdateView,
    # Fontes de Dados
    FonteDadosListView, FonteDadosCreateView,
    FonteDadosManageView,
    # Credenciais e Auth Flow
    renovar_token_view, testar_conexao_view,
    # Endpoints
    endpoint_criar, endpoint_editar,
    # API interna
    dataset_dados_api,
)

app_name = 'integracao_dados'

urlpatterns = [
    # ── Dashboards Analíticos ─────────────────────────────────────────────────
    path('dashboards/', DashboardListView.as_view(), name='dashboard_list'),
    path('dashboards/<int:pk>/', DashboardDetailView.as_view(), name='dashboard_detail'),
    path('dashboards/novo/', DashboardCreateView.as_view(), name='dashboard_create'),
    path('dashboards/<int:pk>/editar/', DashboardUpdateView.as_view(), name='dashboard_update'),

    # ── Datasets ──────────────────────────────────────────────────────────────
    path('datasets/novo/', DatasetCreateView.as_view(), name='dataset_create'),
    path('datasets/<int:pk>/editar/', DatasetUpdateView.as_view(), name='dataset_update'),

    # ── Fontes de Dados ───────────────────────────────────────────────────────
    path('fontes/', FonteDadosListView.as_view(), name='fontedados_list'),
    path('fontes/nova/', FonteDadosCreateView.as_view(), name='fontedados_create'),
    path('fontes/<int:pk>/', FonteDadosManageView.as_view(), name='fontedados_manage'),

    # ── Credenciais e Auth Flow ───────────────────────────────────────────────
    path('fontes/<int:pk>/testar-conexao/', testar_conexao_view, name='testar_conexao'),
    path('fontes/<int:fonte_pk>/renovar-token/', renovar_token_view, name='renovar_token'),

    # ── Endpoints (1 Fonte : N Endpoints) ────────────────────────────────────
    path('fontes/<int:fonte_pk>/endpoints/novo/', endpoint_criar, name='endpoint_criar'),
    path('endpoints/<int:pk>/editar/', endpoint_editar, name='endpoint_editar'),

    # ── API Interna ───────────────────────────────────────────────────────────
    path('api/datasets/<int:dataset_id>/dados/', dataset_dados_api, name='dataset_dados_api'),
]
