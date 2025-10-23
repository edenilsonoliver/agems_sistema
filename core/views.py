from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy


class ModernListView(LoginRequiredMixin, ListView):
    """View genérica para listagens modernas"""
    template_name = 'components/list_view.html'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = getattr(self, 'title', self.model._meta.verbose_name_plural.title())
        context['subtitle'] = getattr(self, 'subtitle', f'Gerenciar {self.model._meta.verbose_name_plural}')
        context['icon'] = getattr(self, 'icon', 'bi bi-list')
        context['singular_name'] = self.model._meta.verbose_name.title()
        context['create_url'] = getattr(self, 'create_url', f'{self.model._meta.model_name}_create')
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q')
        if search and hasattr(self, 'search_fields'):
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': search})
            queryset = queryset.filter(query)
        return queryset


class ModernCreateView(LoginRequiredMixin, CreateView):
    """View genérica para criação moderna"""
    template_name = 'components/form_view.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Adicionar {self.model._meta.verbose_name.title()}'
        context['icon'] = getattr(self, 'icon', 'bi bi-plus-circle')
        context['module_name'] = self.model._meta.verbose_name_plural.title()
        context['list_url'] = getattr(self, 'list_url', f'{self.model._meta.model_name}_list')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'{self.model._meta.verbose_name.title()} criado com sucesso!')
        return super().form_valid(form)


class ModernUpdateView(LoginRequiredMixin, UpdateView):
    """View genérica para edição moderna"""
    template_name = 'components/form_view.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Editar {self.model._meta.verbose_name.title()}'
        context['icon'] = getattr(self, 'icon', 'bi bi-pencil')
        context['module_name'] = self.model._meta.verbose_name_plural.title()
        context['list_url'] = getattr(self, 'list_url', f'{self.model._meta.model_name}_list')
        context['delete_url'] = getattr(self, 'delete_url', f'{self.model._meta.model_name}_delete')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'{self.model._meta.verbose_name.title()} atualizado com sucesso!')
        return super().form_valid(form)


class ModernDeleteView(LoginRequiredMixin, DeleteView):
    """View genérica para exclusão moderna"""
    template_name = 'components/confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Excluir {self.model._meta.verbose_name.title()}'
        context['icon'] = 'bi bi-trash'
        context['module_name'] = self.model._meta.verbose_name_plural.title()
        context['list_url'] = getattr(self, 'list_url', f'{self.model._meta.model_name}_list')
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'{self.model._meta.verbose_name.title()} excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
