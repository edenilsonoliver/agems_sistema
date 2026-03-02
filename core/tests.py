"""
Testes Funcionais — Core: Views de Autenticação e Controle de Acesso HTTP

Cobertura:
  - GET /login/ → HTTP 200 (acessível sem login)
  - POST login válido → redireciona para dashboard
  - POST login inválido → HTTP 200 (permanece na página)
  - GET /dashboard/ sem autenticação → redireciona para /login/
  - Admin → GET instrumento_list, entidade_list, acao_list → HTTP 200
  - Visualizador (perfil 5) → GET listagens → HTTP 200 (somente leitura)
  - Técnico executor (perfil 4) → GET acao_list e outras listagens → HTTP 200
  - Gestor (perfil 1) → GET instrumento_create → HTTP 200
  - Unauthenticated → rotas privadas → HTTP 302

Nota técnica:
  Os testes de view usam SESSION_ENGINE='cache' via override_settings para
  evitar o erro "no such table: django_session" no banco de teste SQLite —
  problema causado pela ordem de criação de tabelas durante o migrate de testes.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Diretoria

User = get_user_model()

# Configurações de sessão para testes (sem tabela no banco)
SESSION_OVERRIDE = {
    'SESSION_ENGINE': 'django.contrib.sessions.backends.cache',
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
}


def criar_usuario(username, perfil, password="senha123"):
    """Helper para criar diretoria e usuário."""
    diretoria, _ = Diretoria.objects.get_or_create(nome="Diretoria Views Test", sigla="DVT")
    return User.objects.create_user(
        username=username,
        password=password,
        perfil=perfil,
        diretoria=diretoria,
    )


@override_settings(**SESSION_OVERRIDE)
class AuthViewTests(TestCase):
    """Testes de autenticação via HTTP."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin_test",
            password="senha123",
            email="admin@test.com",
            perfil=0,
        )

    # ------------------------------------------------------------------
    # T01 — Página de login acessível sem autenticação
    # ------------------------------------------------------------------
    def test_login_view_acessivel_sem_autenticacao(self):
        """GET /login/ deve retornar HTTP 200."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # T02 — Login válido redireciona
    # ------------------------------------------------------------------
    def test_login_valido_redireciona(self):
        """POST com credenciais corretas deve redirecionar (HTTP 302)."""
        response = self.client.post(
            reverse("login"),
            {"username": "admin_test", "password": "senha123"},
        )
        self.assertIn(response.status_code, [302, 301])

    # ------------------------------------------------------------------
    # T03 — Login inválido não redireciona
    # ------------------------------------------------------------------
    def test_login_invalido_nao_redireciona(self):
        """POST com senha errada deve retornar HTTP 200 (formulário com erro)."""
        response = self.client.post(
            reverse("login"),
            {"username": "admin_test", "password": "senhaerrada"},
        )
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # T04 — Dashboard sem autenticação redireciona para login
    # ------------------------------------------------------------------
    def test_dashboard_sem_login_redireciona(self):
        """GET / sem autenticação deve redirecionar para login."""
        response = self.client.get(reverse("dashboard"))
        self.assertIn(response.status_code, [302, 301])

    # ------------------------------------------------------------------
    # T05 — Admin acessa listagens sem erro
    # ------------------------------------------------------------------
    def test_admin_acessa_instrumento_list(self):
        """Admin deve acessar /instrumentos/ com HTTP 200."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse("instrumento_list"))
        self.assertEqual(response.status_code, 200)

    def test_admin_acessa_entidade_list(self):
        """Admin deve acessar /entidades/ com HTTP 200."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse("entidade_list"))
        self.assertEqual(response.status_code, 200)

    def test_admin_acessa_acao_list(self):
        """Admin deve acessar /acoes/ com HTTP 200."""
        self.client.force_login(self.admin)
        response = self.client.get(reverse("acao_list"))
        self.assertEqual(response.status_code, 200)


@override_settings(**SESSION_OVERRIDE)
class AccessControlViewTests(TestCase):
    """Testes de controle de acesso HTTP por perfil de usuário."""

    def setUp(self):
        self.visualizador = criar_usuario("vis_test", perfil=5)
        self.tecnico_exec = criar_usuario("tec_exec_test", perfil=4)
        self.gestor = criar_usuario("gestor_test", perfil=1)

        # Atribui permissões diretas (sem depender de auth.Group)
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from entidades.models import Entidade
        from instrumentos.models import Instrumento
        from acoes.models import Acao

        def add_perm(user, model, codename):
            ct = ContentType.objects.get_for_model(model)
            perm = Permission.objects.filter(codename=codename, content_type=ct).first()
            if perm:
                user.user_permissions.add(perm)

        # Visualizador: apenas view
        for model in [Entidade, Instrumento, Acao]:
            add_perm(self.visualizador, model, f'view_{model.__name__.lower()}')

        # Técnico executor: view+add+change em Acao, view em Entidade/Instrumento
        for action in ['view', 'add', 'change']:
            add_perm(self.tecnico_exec, Acao, f'{action}_acao')
        add_perm(self.tecnico_exec, Entidade, 'view_entidade')
        add_perm(self.tecnico_exec, Instrumento, 'view_instrumento')

        # Gestor: CRUD completo
        for model in [Entidade, Instrumento, Acao]:
            for action in ['view', 'add', 'change', 'delete']:
                add_perm(self.gestor, model, f'{action}_{model.__name__.lower()}')

    # ------------------------------------------------------------------
    # T06 — Visualizador acessa listagens (somente leitura)
    # ------------------------------------------------------------------
    def test_visualizador_acessa_entidade_list(self):
        """Visualizador deve acessar lista de entidades com HTTP 200."""
        self.client.force_login(self.visualizador)
        response = self.client.get(reverse("entidade_list"))
        self.assertEqual(response.status_code, 200)

    def test_visualizador_acessa_instrumento_list(self):
        """Visualizador deve acessar lista de instrumentos com HTTP 200."""
        self.client.force_login(self.visualizador)
        response = self.client.get(reverse("instrumento_list"))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # T07 — Técnico acessa lista de ações
    # ------------------------------------------------------------------
    def test_tecnico_acessa_acao_list(self):
        """Técnico executor deve acessar lista de ações com HTTP 200."""
        self.client.force_login(self.tecnico_exec)
        response = self.client.get(reverse("acao_list"))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # T08 — Gestor cria instrumento
    # ------------------------------------------------------------------
    def test_gestor_acessa_instrumento_create(self):
        """Gestor deve acessar formulário de criação de instrumento (HTTP 200)."""
        self.client.force_login(self.gestor)
        response = self.client.get(reverse("instrumento_create"))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # T09 — Unauthenticated → rotas privadas redirecionam
    # ------------------------------------------------------------------
    def test_unauthenticated_instrumento_list_redireciona(self):
        """Acesso sem login à lista de instrumentos deve redirecionar."""
        response = self.client.get(reverse("instrumento_list"))
        self.assertIn(response.status_code, [302, 301])

    def test_unauthenticated_acao_list_redireciona(self):
        """Acesso sem login à lista de ações deve redirecionar."""
        response = self.client.get(reverse("acao_list"))
        self.assertIn(response.status_code, [302, 301])
