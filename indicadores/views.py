from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import IndicadorContratual, ValorIndicador
from django.urls import reverse_lazy


class IndicadorListView(PermissionRequiredMixin, ModernListView):

    permission_required = 'indicadores.view_indicadorcontratual'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade.")
            return redirect('dashboard')
        return super().handle_no_permission()

    model = IndicadorContratual
    template_name = 'indicadores/indicadorcontratual_list.html'
    icon = "bi bi-graph-up"
    create_url = 'indicador_create'
    list_url = 'indicador_list'
    search_fields = ['nome', 'descricao']


class IndicadorCreateView(PermissionRequiredMixin, ModernCreateView):

    permission_required = 'indicadores.add_indicadorcontratual'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade.")
            return redirect('dashboard')
        return super().handle_no_permission()

    model = IndicadorContratual
    fields = '__all__'
    success_url = reverse_lazy('indicador_list')
    list_url = reverse_lazy('indicador_list')


class IndicadorUpdateView(PermissionRequiredMixin, ModernUpdateView):

    permission_required = 'indicadores.change_indicadorcontratual'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade.")
            return redirect('dashboard')
        return super().handle_no_permission()

    model = IndicadorContratual
    fields = '__all__'
    success_url = reverse_lazy('indicador_list')
    list_url = reverse_lazy('indicador_list')


class IndicadorDeleteView(PermissionRequiredMixin, ModernDeleteView):

    permission_required = 'indicadores.delete_indicadorcontratual'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Você não possui permissão para acessar esta funcionalidade.")
            return redirect('dashboard')
        return super().handle_no_permission()

    model = IndicadorContratual
    success_url = reverse_lazy('indicador_list')
