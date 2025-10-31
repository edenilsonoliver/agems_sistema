from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from core.models import Diretoria, Subunidade

User = get_user_model()


class UsuarioCreateForm(forms.ModelForm):
    """Formulário para criação de usuário com senha"""
    
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma senha forte'
        }),
        help_text='Mínimo 8 caracteres, incluindo letras e números'
    )
    
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha novamente'
        }),
        help_text='Digite a mesma senha para confirmação'
    )
    
    senha_temporaria = forms.BooleanField(
        label='Senha Temporária',
        required=False,
        initial=True,
        help_text='Se marcado, usuário será obrigado a trocar a senha no primeiro acesso',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'perfil',
            'diretoria',
            'subunidade',
            'cargo',
            'telefone',
            'is_active',
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Login do usuário'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@agems.ms.gov.br'
            }),
            'perfil': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_perfil'
            }),
            'diretoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_diretoria'
            }),
            'subunidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_subunidade'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Analista, Coordenador'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(67) 99999-9999'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'username': 'Nome de Usuário (Login)',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'perfil': 'Perfil de Acesso',
            'diretoria': 'Diretoria',
            'subunidade': 'Subunidade',
            'cargo': 'Cargo',
            'telefone': 'Telefone',
            'is_active': 'Usuário Ativo',
        }
        help_texts = {
            'username': 'Nome único para login no sistema',
            'email': 'E-mail institucional do usuário',
            'perfil': 'Define o nível de acesso e permissões',
            'diretoria': 'Obrigatório para perfis 1-5',
            'subunidade': 'Obrigatório para perfis 2, 3 e 4',
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Tornar campos obrigatórios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Filtrar perfis disponíveis baseado no usuário logado
        if self.request_user:
            if self.request_user.perfil == 1:  # Diretoria
                # Diretoria só pode criar perfis 2, 3, 4
                self.fields['perfil'].choices = [
                    (2, 'Assessoria'),
                    (3, 'Coordenação'),
                    (4, 'Usuário Comum'),
                ]
                # Filtrar apenas sua diretoria
                self.fields['diretoria'].queryset = Diretoria.objects.filter(id=self.request_user.diretoria.id)
                self.fields['diretoria'].initial = self.request_user.diretoria
                # Filtrar subunidades da sua diretoria
                if self.request_user.diretoria:
                    self.fields['subunidade'].queryset = Subunidade.objects.filter(diretoria=self.request_user.diretoria)
            
            elif self.request_user.perfil in [2, 3]:  # Assessoria ou Coordenação
                # Podem criar apenas usuários comuns
                self.fields['perfil'].choices = [(4, 'Usuário Comum')]
                # Fixar na sua subunidade
                if self.request_user.subunidade:
                    self.fields['diretoria'].queryset = Diretoria.objects.filter(id=self.request_user.subunidade.diretoria.id)
                    self.fields['diretoria'].initial = self.request_user.subunidade.diretoria
                    self.fields['subunidade'].queryset = Subunidade.objects.filter(id=self.request_user.subunidade.id)
                    self.fields['subunidade'].initial = self.request_user.subunidade
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Validar força da senha
        if len(password1) < 8:
            raise ValidationError('A senha deve ter no mínimo 8 caracteres.')
        
        if password1.isdigit():
            raise ValidationError('A senha não pode conter apenas números.')
        
        if password1.isalpha():
            raise ValidationError('A senha deve conter pelo menos um número.')
        
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('As senhas não coincidem.')
        
        return password2
    
    def clean(self):
        cleaned_data = super().clean()
        perfil = cleaned_data.get('perfil')
        diretoria = cleaned_data.get('diretoria')
        subunidade = cleaned_data.get('subunidade')
        
        # Validar diretoria obrigatória para perfis 1-5
        if perfil in [1, 2, 3, 4, 5] and not diretoria:
            self.add_error('diretoria', 'Diretoria é obrigatória para este perfil.')
        
        # Validar subunidade obrigatória para perfis 2, 3, 4
        if perfil in [2, 3, 4] and not subunidade:
            self.add_error('subunidade', 'Subunidade é obrigatória para este perfil.')
        
        # Validar se subunidade pertence à diretoria
        if subunidade and diretoria and subunidade.diretoria != diretoria:
            self.add_error('subunidade', 'A subunidade deve pertencer à diretoria selecionada.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.senha_temporaria = self.cleaned_data.get('senha_temporaria', True)
        
        if commit:
            user.save()
        
        return user


class UsuarioUpdateForm(forms.ModelForm):
    """Formulário para edição de usuário (sem senha)"""
    
    alterar_senha = forms.BooleanField(
        label='Alterar Senha',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_alterar_senha'}),
        help_text='Marque para definir uma nova senha'
    )
    
    password1 = forms.CharField(
        label='Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma nova senha',
            'id': 'id_password1'
        }),
        help_text='Mínimo 8 caracteres, incluindo letras e números'
    )
    
    password2 = forms.CharField(
        label='Confirmar Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha novamente',
            'id': 'id_password2'
        }),
        help_text='Digite a mesma senha para confirmação'
    )
    
    senha_temporaria = forms.BooleanField(
        label='Forçar Troca de Senha',
        required=False,
        help_text='Se marcado, usuário será obrigado a trocar a senha no próximo acesso',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'perfil',
            'diretoria',
            'subunidade',
            'cargo',
            'telefone',
            'is_active',
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'perfil': forms.Select(attrs={'class': 'form-select', 'id': 'id_perfil'}),
            'diretoria': forms.Select(attrs={'class': 'form-select', 'id': 'id_diretoria'}),
            'subunidade': forms.Select(attrs={'class': 'form-select', 'id': 'id_subunidade'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nome de Usuário (Login)',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'perfil': 'Perfil de Acesso',
            'diretoria': 'Diretoria',
            'subunidade': 'Subunidade',
            'cargo': 'Cargo',
            'telefone': 'Telefone',
            'is_active': 'Usuário Ativo',
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Tornar campos obrigatórios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Filtrar perfis disponíveis baseado no usuário logado
        if self.request_user and self.request_user.perfil != 0:
            if self.request_user.perfil == 1:  # Diretoria
                self.fields['perfil'].choices = [
                    (2, 'Assessoria'),
                    (3, 'Coordenação'),
                    (4, 'Usuário Comum'),
                ]
            elif self.request_user.perfil in [2, 3]:  # Assessoria ou Coordenação
                self.fields['perfil'].choices = [(4, 'Usuário Comum')]
    
    def clean(self):
        cleaned_data = super().clean()
        alterar_senha = cleaned_data.get('alterar_senha')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        perfil = cleaned_data.get('perfil')
        diretoria = cleaned_data.get('diretoria')
        subunidade = cleaned_data.get('subunidade')
        
        # Validar senhas se alterar_senha estiver marcado
        if alterar_senha:
            if not password1:
                self.add_error('password1', 'Digite a nova senha.')
            elif len(password1) < 8:
                self.add_error('password1', 'A senha deve ter no mínimo 8 caracteres.')
            elif password1.isdigit():
                self.add_error('password1', 'A senha não pode conter apenas números.')
            elif password1.isalpha():
                self.add_error('password1', 'A senha deve conter pelo menos um número.')
            
            if password1 and password2 and password1 != password2:
                self.add_error('password2', 'As senhas não coincidem.')
        
        # Validar diretoria obrigatória para perfis 1-5
        if perfil in [1, 2, 3, 4, 5] and not diretoria:
            self.add_error('diretoria', 'Diretoria é obrigatória para este perfil.')
        
        # Validar subunidade obrigatória para perfis 2, 3, 4
        if perfil in [2, 3, 4] and not subunidade:
            self.add_error('subunidade', 'Subunidade é obrigatória para este perfil.')
        
        # Validar se subunidade pertence à diretoria
        if subunidade and diretoria and subunidade.diretoria != diretoria:
            self.add_error('subunidade', 'A subunidade deve pertencer à diretoria selecionada.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Alterar senha se solicitado
        if self.cleaned_data.get('alterar_senha') and self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
            user.senha_temporaria = self.cleaned_data.get('senha_temporaria', False)
        
        if commit:
            user.save()
        
        return user

