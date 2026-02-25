from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import Http404
from django.shortcuts import redirect


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
        # Não mexe na ordenação, apenas aplica o filtro de busca
        queryset = self.model.objects.all()

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
        
        # Prioriza list_url definido na View, senão tenta adivinhar
        list_url_attr = getattr(self, 'list_url', None)
        if list_url_attr:
            context['list_url'] = list_url_attr
        else:
            context['list_url'] = reverse_lazy(f'{self.model._meta.model_name}_list')
            
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
        
        # Prioriza list_url definido na View
        list_url_attr = getattr(self, 'list_url', None)
        if list_url_attr:
            context['list_url'] = list_url_attr
        else:
            context['list_url'] = reverse_lazy(f'{self.model._meta.model_name}_list')
            
        # Prioriza delete_url definido na View
        delete_url_attr = getattr(self, 'delete_url', None)
        if delete_url_attr:
            context['delete_url'] = delete_url_attr
        else:
            context['delete_url'] = reverse_lazy(f'{self.model._meta.model_name}_delete', args=[self.object.pk])

        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            try:
                list_url = reverse_lazy(f'{self.model._meta.model_name}_list')
            except:
                list_url = '/'
            
            messages.error(request, f'{self.model._meta.verbose_name.title()} não encontrado.')
            return redirect(list_url)
    
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
        
        # Prioriza list_url definido na View
        list_url_attr = getattr(self, 'list_url', None)
        if list_url_attr:
            context['list_url'] = list_url_attr
        else:
            context['list_url'] = reverse_lazy(f'{self.model._meta.model_name}_list')
            
        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            try:
                list_url = reverse_lazy(f'{self.model._meta.model_name}_list')
            except:
                list_url = '/'
            
            messages.error(request, f'{self.model._meta.verbose_name.title()} não encontrado.')
            return redirect(list_url)
    
    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o método post para tratar ProtectedError.
        Captura tentativas de exclusão de objetos protegidos por foreign keys.
        """
        from django.db.models.deletion import ProtectedError
        from django.shortcuts import redirect
        
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError as e:
            # Extrai informações sobre os objetos protegidos
            protected_objects = e.protected_objects
            count = len(protected_objects)
            
            # Mensagem amigável ao usuário
            messages.error(
                self.request,
                f'Não é possível excluir este {self.model._meta.verbose_name} '
                f'porque existem {count} registro(s) vinculado(s) a ele. '
                f'Remova as vinculações antes de excluir.'
            )
            
            # Redireciona para a lista
            return redirect(self.success_url)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'{self.model._meta.verbose_name.title()} excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
