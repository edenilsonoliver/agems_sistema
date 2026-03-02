"""
Testes Funcionais — Módulo Usuários (usuarios)

Cobertura:
  - RBAC: perfil Admin (0) pode tudo
  - RBAC: Gestores (1, 2) podem editar entidade e instrumento
  - RBAC: Técnicos (3, 4) NÃO podem editar entidade nem instrumento
  - RBAC: Visualizador (5) não pode editar nada
  - Hierarquia: gestores só editam usuários da SUA diretoria
  - Hierarquia: pode_criar_usuario() por perfil
"""
from django.test import TestCase

from core.models import Diretoria, Subunidade
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioRBACTests(TestCase):
    """Testes das regras de controle de acesso (RBAC) no modelo Usuario."""

    def setUp(self):
        self.dir_a = Diretoria.objects.create(nome="Diretoria A", sigla="DA")
        self.dir_b = Diretoria.objects.create(nome="Diretoria B", sigla="DB")
        self.sub_a = Subunidade.objects.create(nome="Subunidade A", sigla="SA", diretoria=self.dir_a)
        self.sub_b = Subunidade.objects.create(nome="Subunidade B", sigla="SB", diretoria=self.dir_b)

        # Um usuário de cada perfil
        self.admin = User.objects.create_user(username="u_admin", password="x", perfil=0)
        self.gestor_diretor = User.objects.create_user(username="u_gestor1", password="x", perfil=1, diretoria=self.dir_a)
        self.gestor_assessor = User.objects.create_user(username="u_gestor2", password="x", perfil=2, diretoria=self.dir_a, subunidade=self.sub_a)
        self.tecnico_coord = User.objects.create_user(username="u_tec3", password="x", perfil=3, diretoria=self.dir_a, subunidade=self.sub_a)
        self.tecnico_exec = User.objects.create_user(username="u_tec4", password="x", perfil=4, diretoria=self.dir_a, subunidade=self.sub_a)
        self.visualizador = User.objects.create_user(username="u_vis5", password="x", perfil=5, diretoria=self.dir_a)

    # ------------------------------------------------------------------
    # T01 — Admin pode editar entidade, instrumento, ação e indicador
    # ------------------------------------------------------------------
    def test_admin_pode_editar_tudo(self):
        self.assertTrue(self.admin.pode_editar_entidade())
        self.assertTrue(self.admin.pode_editar_instrumento())
        self.assertTrue(self.admin.pode_editar_acao_tarefa())
        self.assertTrue(self.admin.pode_editar_indicador())

    # ------------------------------------------------------------------
    # T02 — Gestores podem editar entidade e instrumento
    # ------------------------------------------------------------------
    def test_gestor_diretor_pode_editar_entidade_e_instrumento(self):
        self.assertTrue(self.gestor_diretor.pode_editar_entidade())
        self.assertTrue(self.gestor_diretor.pode_editar_instrumento())

    def test_gestor_assessor_pode_editar_entidade_e_instrumento(self):
        self.assertTrue(self.gestor_assessor.pode_editar_entidade())
        self.assertTrue(self.gestor_assessor.pode_editar_instrumento())

    # ------------------------------------------------------------------
    # T03 — Técnicos NÃO podem editar entidade nem instrumento
    # ------------------------------------------------------------------
    def test_tecnico_coord_nao_pode_editar_entidade(self):
        self.assertFalse(self.tecnico_coord.pode_editar_entidade())
        self.assertFalse(self.tecnico_coord.pode_editar_instrumento())

    def test_tecnico_exec_nao_pode_editar_entidade(self):
        self.assertFalse(self.tecnico_exec.pode_editar_entidade())
        self.assertFalse(self.tecnico_exec.pode_editar_instrumento())

    # ------------------------------------------------------------------
    # T04 — Técnicos podem criar/editar ações
    # ------------------------------------------------------------------
    def test_tecnicos_podem_editar_acao(self):
        self.assertTrue(self.tecnico_coord.pode_editar_acao_tarefa())
        self.assertTrue(self.tecnico_exec.pode_editar_acao_tarefa())

    # ------------------------------------------------------------------
    # T05 — Visualizador não pode editar nada
    # ------------------------------------------------------------------
    def test_visualizador_nao_pode_editar_nada(self):
        self.assertFalse(self.visualizador.pode_editar_entidade())
        self.assertFalse(self.visualizador.pode_editar_instrumento())
        self.assertFalse(self.visualizador.pode_editar_indicador())

    def test_visualizador_pode_editar_acao_e_tarefa(self):
        """Visualizador não pode editar ação/tarefa."""
        self.assertFalse(self.visualizador.pode_editar_acao_tarefa())

    # ------------------------------------------------------------------
    # T06 — pode_criar_usuario() por perfil
    # ------------------------------------------------------------------
    def test_pode_criar_usuario_por_perfil(self):
        """Perfis 0-3 podem criar usuários; perfis 4 e 5 não."""
        self.assertTrue(self.admin.pode_criar_usuario())
        self.assertTrue(self.gestor_diretor.pode_criar_usuario())
        self.assertTrue(self.gestor_assessor.pode_criar_usuario())
        self.assertTrue(self.tecnico_coord.pode_criar_usuario())
        self.assertFalse(self.tecnico_exec.pode_criar_usuario())
        self.assertFalse(self.visualizador.pode_criar_usuario())

    # ------------------------------------------------------------------
    # T07 — Hierarquia de edição: gestor só edita usuário da SUA diretoria
    # ------------------------------------------------------------------
    def test_gestor_pode_editar_usuario_da_sua_diretoria(self):
        usuario_mesmo_dir = User.objects.create_user(
            username="u_sub_da", password="x", perfil=4, diretoria=self.dir_a, subunidade=self.sub_a
        )
        self.assertTrue(self.gestor_diretor.pode_editar_usuario(usuario_mesmo_dir))

    def test_gestor_nao_pode_editar_usuario_de_outra_diretoria(self):
        usuario_outra_dir = User.objects.create_user(
            username="u_sub_db", password="x", perfil=4, diretoria=self.dir_b, subunidade=self.sub_b
        )
        self.assertFalse(self.gestor_diretor.pode_editar_usuario(usuario_outra_dir))

    # ------------------------------------------------------------------
    # T08 — Permissão de diretoria por perfil
    # ------------------------------------------------------------------
    def test_admin_tem_permissao_em_qualquer_diretoria(self):
        self.assertTrue(self.admin.tem_permissao_diretoria(self.dir_a))
        self.assertTrue(self.admin.tem_permissao_diretoria(self.dir_b))

    def test_gestor_tem_permissao_apenas_na_sua_diretoria(self):
        self.assertTrue(self.gestor_diretor.tem_permissao_diretoria(self.dir_a))
        self.assertFalse(self.gestor_diretor.tem_permissao_diretoria(self.dir_b))
