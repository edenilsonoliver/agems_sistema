from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import IndicadorContratual, ValorIndicador
from django.urls import reverse_lazy


class IndicadorListView(ModernListView):
    model = IndicadorContratual
    template_name = 'indicadores/indicadorcontratual_list.html'
    icon = "bi bi-graph-up"
    create_url = 'indicador_create'
    search_fields = ['nome', 'descricao']


class IndicadorCreateView(ModernCreateView):
    model = IndicadorContratual
    fields = '__all__'
    success_url = reverse_lazy('indicador_list')


class IndicadorUpdateView(ModernUpdateView):
    model = IndicadorContratual
    fields = '__all__'
    success_url = reverse_lazy('indicador_list')


class IndicadorDeleteView(ModernDeleteView):
    model = IndicadorContratual
    success_url = reverse_lazy('indicador_list')
