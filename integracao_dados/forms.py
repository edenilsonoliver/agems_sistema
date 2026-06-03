from django import forms
from .models import Dashboard, Dataset, FonteDados, Endpoint, Widget


# ──────────────────────────────────────────────────────────────────────────────
# FONTE DE DADOS — Focado em: Identidade + Estratégia de Auth + Config Global
# A gestão de Credenciais e Endpoints ficam em telas próprias (UX limpa)
# ──────────────────────────────────────────────────────────────────────────────
class FonteDadosForm(forms.ModelForm):
    class Meta:
        model = FonteDados
        fields = [
            'nome', 'tipo', 'diretoria', 'url_base', 'metodo_autenticacao',
            'auth_url_relativa', 'auth_metodo', 'auth_content_type',
            'auth_token_key', 'auth_payload_extra',
            'status_integracao', 'responsavel_tecnico',
            'frequencia_minutos', 'timeout_segundos',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: API MSGás Produção'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'diretoria': forms.Select(attrs={'class': 'form-select'}),
            'url_base': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://api.exemplo.com.br'}),
            'metodo_autenticacao': forms.Select(attrs={'class': 'form-select', 'id': 'id_metodo_autenticacao'}),
            'auth_url_relativa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/oauth/token'}),
            'auth_metodo': forms.Select(attrs={'class': 'form-select'}),
            'auth_content_type': forms.TextInput(attrs={'class': 'form-control'}),
            'auth_token_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'access_token'}),
            'auth_payload_extra': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 3,
                                                         'placeholder': '{"grant_type": "password"}'}),
            'responsavel_tecnico': forms.TextInput(attrs={'class': 'form-control'}),
            'frequencia_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'timeout_segundos': forms.NumberInput(attrs={'class': 'form-control'}),
            'status_integracao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'metodo_autenticacao': 'Estratégia de Autenticação',
            'auth_url_relativa': 'URL do Endpoint de Login (relativa)',
            'auth_metodo': 'Método HTTP do Login',
            'auth_content_type': 'Content-Type do Login',
            'auth_token_key': 'Chave do Token na Resposta JSON',
            'auth_payload_extra': 'Payload Extra de Login (JSON)',
        }

    def clean_auth_payload_extra(self):
        import json
        data = self.cleaned_data.get('auth_payload_extra')
        if not data:
            return {}
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("O campo deve conter um JSON válido.")
        return data

# ──────────────────────────────────────────────────────────────────────────────
# CREDENCIAL — Formulário isolado, campos sensíveis jamais são pré-preenchidos
# ──────────────────────────────────────────────────────────────────────────────
class CredencialFonteForm(forms.Form):
    """
    Formulário standalone para atualizar credenciais de uma FonteDados.
    NÃO usa ModelForm para evitar que campos criptografados sejam expostos
    no HTML ou logs de debug do Django.
    """
    usuario_api = forms.CharField(
        label='Usuário / Client ID',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'usuário de acesso à API',
        })
    )
    senha_api = forms.CharField(
        label='Senha / Client Secret',
        max_length=200,
        required=False,
        widget=forms.PasswordInput(render_value=True, attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': '••••••••',
        })
    )
    token_manual = forms.CharField(
        label='Token Estático (Bearer/API Key)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 3,
            'placeholder': 'Cole aqui o token se não for usar renovação automática (Bearer/API Key).',
            'autocomplete': 'off',
        }),
        help_text='Deixe em branco para usar renovação automática (JWT/OAuth). '
                  'Preenchido apenas para Bearer Token ou API Key estáticos.'
    )
    api_key_header = forms.CharField(
        label='Nome do Header da API Key',
        max_length=100,
        required=False,
        initial='X-API-Key',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'X-API-Key'}),
        help_text='Obrigatório apenas quando a estratégia for API Key.'
    )
    headers_customizados = forms.CharField(
        label='Headers Fixos Globais (JSON)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 3,
            'placeholder': '{"Accept": "application/json", "X-Client-ID": "agems"}',
        }),
        help_text='Headers enviados em TODAS as requisições desta fonte.'
    )

    def clean_headers_customizados(self):
        raw = self.cleaned_data.get('headers_customizados', '').strip()
        if not raw:
            return {}
        import json
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise forms.ValidationError("Os headers devem ser um objeto JSON (chave: valor).")
            return parsed
        except json.JSONDecodeError:
            raise forms.ValidationError("JSON inválido. Exemplo correto: {\"Content-Type\": \"application/json\"}")

    def clean_token_manual(self):
        return self.cleaned_data.get('token_manual', '').strip()


# ──────────────────────────────────────────────────────────────────────────────
# ENDPOINT — Formulário independente, vinculado à Fonte pelo view
# ──────────────────────────────────────────────────────────────────────────────
class EndpointForm(forms.ModelForm):
    class Meta:
        model = Endpoint
        fields = ['nome', 'url_relativa', 'metodo_http', 'content_type',
                  'parametros_default', 'headers_override', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Contratos Ativos'}),
            'url_relativa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '/api/v1/contratos'}),
            'metodo_http': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.TextInput(attrs={'class': 'form-control'}),
            'parametros_default': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 'rows': 3,
                'placeholder': '{"status": "ativo", "page_size": 100}',
            }),
            'headers_override': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 'rows': 2,
                'placeholder': '{"X-Custom-Header": "valor"}',
            }),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'url_relativa': 'URL Relativa',
            'parametros_default': 'Parâmetros / Body (JSON)',
            'headers_override': 'Headers Extras (sobrepõe globais)',
        }


# ──────────────────────────────────────────────────────────────────────────────
# DATASET E DASHBOARD — sem alteração em relação ao anterior
# ──────────────────────────────────────────────────────────────────────────────
class DatasetForm(forms.ModelForm):
    arquivo_importacao = forms.FileField(
        label="Importar Arquivo (JSON)",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.json'}),
        help_text="Suba um arquivo .json com lista de objetos para preencher os dados automaticamente."
    )

    class Meta:
        model = Dataset
        fields = ['nome', 'descricao', 'diretoria_proprietaria', 'responsavel', 'dados', 'schema']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'diretoria_proprietaria': forms.Select(attrs={'class': 'form-select'}),
            'responsavel': forms.Select(attrs={'class': 'form-select'}),
            'dados': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 5}),
            'schema': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 3}),
        }


class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = ['nome', 'descricao', 'diretoria_proprietaria', 'criador', 'configuracao_layout']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'diretoria_proprietaria': forms.Select(attrs={'class': 'form-select'}),
            'criador': forms.Select(attrs={'class': 'form-select'}),
            'configuracao_layout': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 3}),
        }


class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        fields = ['dashboard', 'dataset', 'titulo', 'tipo', 'configuracao', 'ordem']
        widgets = {
            'dashboard': forms.Select(attrs={'class': 'form-select'}),
            'dataset': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'configuracao': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 4}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }
