from django.urls import path
from . import views

app_name = 'georeferencias'

urlpatterns = [
    # Funcionalidades de Gestão (para o dashboard)
    path('', views.CamadaListView.as_view(), name='camada_list'),
    path('criar/', views.CamadaCreateView.as_view(), name='camada_create'),
    path('<int:pk>/editar/', views.CamadaUpdateView.as_view(), name='camada_update'),
    path('<int:pk>/excluir/', views.CamadaDeleteView.as_view(), name='camada_delete'),

    # APIs JSON (consumidas pelo mapa)
    path('api/camadas/', views.api_list_camadas, name='api_list_camadas'),
    path('api/camada/<int:camada_id>/pontos/', views.api_get_pontos_camada, name='api_get_pontos_camada'),
]
