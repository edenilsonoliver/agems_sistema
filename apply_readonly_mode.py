import os
import re

def create_backups():
    files = [
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\usuarios\models.py',
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\instrumentos\views.py',
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\entidades\views.py',
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\instrumentos\forms.py',
        r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\entidades\forms.py'
    ]
    for f in files:
        if os.path.exists(f):
            with open(f, 'rb') as src, open(f + '.bak_readonly', 'wb') as dst:
                dst.write(src.read())
            print(f"Backup criado: {f}.bak_readonly")

def update_user_model():
    path = r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\usuarios\models.py'
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Liberar acesso aos módulos para Perfil 4 e 3
    # Localizar: if self.perfil == 4: return modulo in ['acoes', 'tarefas', 'dashboard']
    old_p4 = "if self.perfil == 4:\n            return modulo in ['acoes', 'tarefas', 'dashboard']"
    new_p4 = "if self.perfil == 4:\n            return modulo in ['entidades', 'instrumentos', 'acoes', 'tarefas', 'dashboard']"
    
    # Localizar: if self.perfil == 3: return modulo not in ['entidades', 'instrumentos']
    old_p3 = "if self.perfil == 3:\n            return modulo not in ['entidades', 'instrumentos']"
    new_p3 = "if self.perfil == 3:\n            return modulo in ['entidades', 'instrumentos', 'acoes', 'tarefas', 'dashboard']"

    content = content.replace(old_p4, new_p4)
    content = content.replace(old_p3, new_p3)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Modelo de Usuário atualizado (Acesso liberado para visualização).")

def update_views_readonly(path, app_name, model_name):
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Alterar permissões para view_ nas views de Create/Update
    # Regex para capturar classes de Create e Update
    create_pattern = rf"class {model_name}CreateView\(PermissionRequiredMixin, ModernCreateView\):"
    update_pattern = rf"class {model_name}UpdateView\(PermissionRequiredMixin, ModernUpdateView\):"
    
    # Substituir permissão_required correspondente
    # Procuramos o permission_required logo abaixo da definição da classe
    content = re.sub(rf"({create_pattern}\s+)permission_required = '{app_name}\.add_{app_name}'", 
                     rf"\1permission_required = '{app_name}.view_{app_name}'", content)
    
    content = re.sub(rf"({update_pattern}\s+)permission_required = '{app_name}\.change_{app_name}'", 
                     rf"\1permission_required = '{app_name}.view_{app_name}'", content)

    # 2. Injetar lógica de readonly no get_form_kwargs e get_context_data
    method_insertion = f"""
    def get_readonly(self):
        # Admin e Gestores (0,1,2) podem editar. Outros (3,4,5) só visualizam.
        return self.request.user.perfil not in [0, 1, 2]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        # Garantir que o formset também receba readonly se necessário
        if 'formset' in context:
            # Especial para Instrumentos que tem ObrigacaoFormSet
            formset = context['formset']
            if self.get_readonly():
                for form in formset.forms:
                    for field in form.fields.values():
                        field.disabled = True
        return context
    
    def form_valid(self, form):
        if self.get_readonly():
             from django.contrib import messages
             messages.error(self.request, "Você não tem permissão para salvar alterações.")
             return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)
"""
    # Inserir antes de get_context_data ou no final das classes
    for pattern in [create_pattern, update_pattern]:
        if re.search(pattern, content):
            # Tentar inserir logo após o template_name
            # Procuramos por: template_name = '...'
            match = re.search(rf"({pattern}.*?template_name = '.*?')", content, re.DOTALL)
            if match:
                content = content.replace(match.group(1), match.group(1) + method_insertion)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Views de {model_name} atualizadas para modo readonly.")

def update_forms_readonly(path):
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Injetar processamento de readonly no __init__
    readonly_logic = """
    def __init__(self, *args, **kwargs):
        self.readonly = kwargs.pop('readonly', False)
        super().__init__(*args, **kwargs)
        if self.readonly:
            for field in self.fields.values():
                field.disabled = True
"""
    # Se já tiver __init__, precisamos ser cuidadosos.
    if 'def __init__(self,' in content:
        # Tenta injetar no início do __init__ existente
        content = re.sub(
            r"(def __init__\(self, \*args, \*\*kwargs\):)",
            r"\1\n        self.readonly = kwargs.pop('readonly', False)",
            content
        )
        # Tenta injetar o disabled logo após super().__init__
        content = re.sub(
            r"(super\(\)\.__init__\(.*?\))",
            r"\1\n        if self.readonly:\n            for field in self.fields.values():\n                field.disabled = True",
            content
        )
    else:
        # Se não tiver, adicionamos após a Meta ou widgets
        if 'class Meta:' in content:
            # Encontrar o fim do bloco Meta (aproximadamente)
            # Vamos achar o último item dos widgets ou fields
            match = re.search(r"(class Meta:.*?})", content, re.DOTALL)
            if match:
                content = content.replace(match.group(1), match.group(1) + "\n" + readonly_logic)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Formulário {os.path.basename(path)} atualizado para modo readonly.")

if __name__ == "__main__":
    create_backups()
    update_user_model()
    # Instrumentos
    update_views_readonly(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\instrumentos\views.py', 'instrumentos', 'Instrumento')
    update_forms_readonly(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\instrumentos\forms.py')
    # Entidades
    update_views_readonly(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\entidades\views.py', 'entidades', 'Entidade')
    update_forms_readonly(r'c:\Users\SAMSUNG\OneDrive\Documentos\agems_sistema\entidades\forms.py')
