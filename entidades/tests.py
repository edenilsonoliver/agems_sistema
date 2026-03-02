"""
Testes Funcionais — Módulo Entidades (entidades)

Cobertura:
  - Criação de Entidade válida
  - CNPJ deve ser único (IntegrityError em duplicata)
  - get_logo_url() retorna placeholder quando sem logo
"""
from django.db import IntegrityError
from django.test import TestCase

from core.models import TipoEntidade, TipoServico
from entidades.models import Entidade


def criar_tipo_base():
    tipo_entidade = TipoEntidade.objects.create(nome="Permissionária")
    tipo_servico = TipoServico.objects.create(nome="Energia Elétrica")
    return tipo_entidade, tipo_servico


class EntidadeFlowTests(TestCase):
    """Testes de fluxo e validação do modelo Entidade."""

    def setUp(self):
        self.tipo_entidade, self.tipo_servico = criar_tipo_base()

    def _criar_entidade(self, cnpj="22.222.222/0001-22", razao_social="Entidade Teste LTDA"):
        return Entidade.objects.create(
            razao_social=razao_social,
            cnpj=cnpj,
            tipo_entidade=self.tipo_entidade,
            tipo_servico=self.tipo_servico,
            endereco="Rua das Flores, 50",
            cep="79000-100",
        )

    # ------------------------------------------------------------------
    # T01 — Criação válida
    # ------------------------------------------------------------------
    def test_criar_entidade_valida(self):
        """Entidade com campos obrigatórios deve ser salva sem exceção."""
        entidade = self._criar_entidade()
        self.assertIsNotNone(entidade.pk)
        self.assertEqual(entidade.razao_social, "Entidade Teste LTDA")
        self.assertEqual(entidade.status, "ativa")

    # ------------------------------------------------------------------
    # T02 — CNPJ único
    # ------------------------------------------------------------------
    def test_cnpj_duplicado_levanta_integrityerror(self):
        """Dois registros com mesmo CNPJ devem falhar com IntegrityError."""
        self._criar_entidade(cnpj="33.333.333/0001-33")
        with self.assertRaises(IntegrityError):
            self._criar_entidade(cnpj="33.333.333/0001-33", razao_social="Outro Nome LTDA")

    # ------------------------------------------------------------------
    # T03 — Logo placeholder
    # ------------------------------------------------------------------
    def test_get_logo_url_retorna_placeholder_sem_logo(self):
        """Entidade sem logo deve retornar URL de placeholder, não levantar exceção."""
        entidade = self._criar_entidade()
        url = entidade.get_logo_url()
        self.assertIsNotNone(url)
        self.assertIn("placeholder", url)

    # ------------------------------------------------------------------
    # T04 — __str__ retorna razão social + tipo
    # ------------------------------------------------------------------
    def test_str_contém_razao_social(self):
        """__str__ deve conter a razão social da entidade."""
        entidade = self._criar_entidade()
        self.assertIn("Entidade Teste LTDA", str(entidade))

    # ------------------------------------------------------------------
    # T05 — Status padrão é ativa
    # ------------------------------------------------------------------
    def test_status_padrao_e_ativo(self):
        """Entidade nova deve ter status 'ativa' por padrão."""
        entidade = self._criar_entidade(cnpj="44.444.444/0001-44")
        self.assertEqual(entidade.status, "ativa")
