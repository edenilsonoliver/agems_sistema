import os

def fix_access_control():
    # 1. Corrigir View de Configurações (Restringir ao Perfil 0)
    config_view_path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\core\config_views.py'
    if os.path.exists(config_view_path):
        with open(config_view_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Injetar verificação de perfil
        old_code = "@login_required\ndef configuracoes(request):"
        new_code = """@login_required
def configuracoes(request):
    # Apenas administradores (Perfil 0) podem acessar
    if request.user.perfil != 0:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "Acesso negado: apenas administradores podem acessar as configurações globais.")
        return redirect('dashboard')
"""
        if old_code in content and "request.user.perfil != 0" not in content:
            content = content.replace(old_code, new_code)
            with open(config_view_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("View de configurações protegida.")

    # 2. Corrigir Template Base (Ocultar engrenagem e links restritos)
    base_path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\base_modern.html'
    if os.path.exists(base_path):
        with open(base_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ocultar Configurações na Sidebar (mudar de <= 3 para == 0)
        content = content.replace('{% if user.is_authenticated and user.perfil <= 3 %}', '{% if user.is_authenticated and user.perfil == 0 %}')
        
        # Ocultar Configurações no Dropdown do Usuário
        old_dropdown = '<li><a class="dropdown-item" href="{% url \'configuracoes\' %}"><i\n                                    class="bi bi-gear me-2"></i>Configurações</a></li>'
        new_dropdown = '{% if user.perfil == 0 %}<li><a class="dropdown-item" href="{% url \'configuracoes\' %}"><i class="bi bi-gear me-2"></i>Configurações</a></li>{% endif %}'
        content = content.replace(old_dropdown, new_dropdown)

        with open(base_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Template base atualizado (UI restrita).")

    # 3. Corrigir Template de Entidade (Ocultar botão excluir)
    entidade_form_path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\templates\entidades\entidade_form.html'
    if os.path.exists(entidade_form_path):
        with open(entidade_form_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Envolver o botão de excluir na lógica readonly
        old_delete = """                        {% if object %}
                        <button type="button" class="btn btn-outline-danger ms-auto" data-bs-toggle="modal"
                            data-bs-target="#deleteModal">
                            <i class="bi bi-trash me-2"></i>
                            Excluir
                        </button>
                        {% endif %}"""
        new_delete = """                        {% if object and not readonly %}
                        <button type="button" class="btn btn-outline-danger ms-auto" data-bs-toggle="modal"
                            data-bs-target="#deleteModal">
                            <i class="bi bi-trash me-2"></i>
                            Excluir
                        </button>
                        {% endif %}"""
        if old_delete in content:
            content = content.replace(old_delete, new_delete)
            with open(entidade_form_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Botão de exclusão ocultado em Entidades.")

if __name__ == "__main__":
    fix_access_control()
