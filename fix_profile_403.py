import os

def fix_profile_and_acess():
    # 1. Adicionar view de perfil em usuarios/views.py
    views_path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\usuarios\views.py'
    if os.path.exists(views_path):
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "class UsuarioPerfilView" not in content:
            profile_view_code = """
class UsuarioPerfilView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioUpdateForm
    template_name = 'usuarios/usuario_perfil.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Meu Perfil',
            'subtitle': 'Visualize e atualize seus dados cadastrais',
            'icon': 'bi bi-person-circle',
            'form_title': 'Dados do Meu Perfil',
        })
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Usuários comuns não podem alterar o próprio perfil ou diretoria
        if self.request.user.perfil != 0:
            if 'perfil' in form.fields: form.fields['perfil'].disabled = True
            if 'diretoria' in form.fields: form.fields['diretoria'].disabled = True
            if 'subunidade' in form.fields: form.fields['subunidade'].disabled = True
            if 'username' in form.fields: form.fields['username'].disabled = True
        return form

    def form_valid(self, form):
        messages.success(self.request, "Perfil atualizado com sucesso!")
        return super().form_valid(form)
"""
            content += profile_view_code
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("View de perfil adicionada.")

    # 2. Adicionar rota no config/urls.py
    urls_path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\config\urls.py'
    if os.path.exists(urls_path):
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "name='usuario_perfil'" not in content:
            # Inserir antes das rotas de usuários
            marker = "path('usuarios/', usuarios_views.UsuarioListView.as_view(), name='usuario_list'),"
            new_route = "path('usuarios/perfil/', usuarios_views.UsuarioPerfilView.as_view(), name='usuario_perfil'),\n    "
            content = content.replace(marker, new_route + marker)
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Rota de perfil adicionada.")

    # 3. Criar template de perfil (copiando do form_view simples)
    profile_template_dir = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\usuarios'
    profile_template_path = os.path.join(profile_template_dir, 'usuario_perfil.html')
    template_content = """{% extends 'base_modern.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="page-header">
    <h1 class="page-title">
        <i class="{{icon}} me-2"></i>
        {{title}}
    </h1>
    <p class="page-subtitle">{{subtitle}}</p>
</div>

<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card border-0 shadow-sm">
            <div class="card-body p-4">
                <form method="post">
                    {% csrf_token %}
                    <div class="row">
                        <div class="col-12">
                            {{ form|crispy }}
                        </div>
                    </div>
                    <div class="mt-4 d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save me-2"></i>Salvar Alterações
                        </button>
                        <a href="{% url 'dashboard' %}" class="btn btn-outline-secondary">Cancelar</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    if not os.path.exists(profile_template_path):
        with open(profile_template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print("Template de perfil criado.")

    # 4. Ajustar base_modern.html para o novo link de perfil
    base_path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\base_modern.html'
    if os.path.exists(base_path):
        with open(base_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Localizar o clique no avatar/perfil no dropdown
        # Originalmente não tinha link, vamos adicionar um item "Meu Perfil"
        old_mark = '<ul class="dropdown-menu dropdown-menu-end">'
        new_item = '<li><a class="dropdown-item" href="{% url \'usuario_perfil\' %}"><i class="bi bi-person-circle me-2"></i>Meu Perfil</a></li>\n                        '
        if old_mark in content and "usuario_perfil" not in content:
            content = content.replace(old_mark, old_mark + "\n                        " + new_item)
            
        with open(base_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Link de perfil adicionado ao cabeçalho.")

if __name__ == "__main__":
    fix_profile_and_acess()
