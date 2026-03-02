"""
Testes Funcionais — Módulo Ações (acoes)

Cobertura:
  - Criação de Ação com campos obrigatórios
  - Status inicial correto
  - Detecção de atraso
  - Validação de datas (clean)
  - Checklist + signal atualiza percentual e status
  - Signal propaga status para Obrigação (cumprida)
  - Cascade delete de ChecklistItems ao excluir Ação
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from acoes.models import Acao, ChecklistItem
from core.models import Diretoria, TipoAcao, TipoInstrumento, TipoObrigacao
from entidades.models import Entidade
from instrumentos.models import Instrumento, Obrigacao

User = get_user_model()

HOJE = date.today()
AMANHA = HOJE + timedelta(days=1)
ONTEM = HOJE - timedelta(days=1)
SEMANA_QUE_VEM = HOJE + timedelta(days=7)


def criar_fixtures():
    """Cria objetos auxiliares reutilizáveis (fixtures manuais)."""
    diretoria = Diretoria.objects.create(nome="Diretoria Teste", sigla="DT")
    tipo_entidade = __import__(
        "core.models", fromlist=["TipoEntidade"]
    ).TipoEntidade.objects.create(nome="Concessionária")
    tipo_servico = __import__(
        "core.models", fromlist=["TipoServico"]
    ).TipoServico.objects.create(nome="Saneamento")
    entidade = Entidade.objects.create(
        razao_social="Empresa Teste LTDA",
        cnpj="00.000.000/0001-00",
        tipo_entidade=tipo_entidade,
        tipo_servico=tipo_servico,
        endereco="Rua Teste, 1",
        cep="79000-000",
    )
    tipo_instrumento = TipoInstrumento.objects.create(nome="Contrato")
    instrumento = Instrumento.objects.create(
        numero="INSTR-TEST-001",
        tipo_instrumento=tipo_instrumento,
        diretoria=diretoria,
        objeto="Objetivo de teste",
        data_assinatura=HOJE,
        data_inicio=HOJE,
        data_fim=SEMANA_QUE_VEM,
    )
    instrumento.entidades.set([entidade])
    tipo_obrigacao = TipoObrigacao.objects.create(nome="Relatório")
    obrigacao = Obrigacao.objects.create(
        titulo="Obrigação de Teste",
        descricao="Desc",
        instrumento=instrumento,
        tipo_obrigacao=tipo_obrigacao,
        recorrente=False,
        data_vencimento=SEMANA_QUE_VEM,
    )
    usuario = User.objects.create_user(
        username="user_teste_acao",
        password="senha123",
        perfil=1,
        diretoria=diretoria,
    )
    return usuario, obrigacao


class AcaoFlowTests(TestCase):
    """Testes de fluxo completo do modelo Ação."""

    def setUp(self):
        self.usuario, self.obrigacao = criar_fixtures()

    def _criar_acao(self, **kwargs):
        defaults = dict(
            nome="Ação de Teste",
            obrigacao=self.obrigacao,
            responsavel=self.usuario,
            data_inicio=HOJE,
            data_fim=SEMANA_QUE_VEM,
        )
        defaults.update(kwargs)
        return Acao.objects.create(**defaults)

    # ------------------------------------------------------------------
    # T01 — Criação básica sem erros
    # ------------------------------------------------------------------
    def test_criar_acao_valida(self):
        """Ação com todos os campos obrigatórios deve ser salva sem exceção."""
        acao = self._criar_acao()
        self.assertIsNotNone(acao.pk)
        self.assertEqual(acao.nome, "Ação de Teste")

    # ------------------------------------------------------------------
    # T02 — Status inicial
    # ------------------------------------------------------------------
    def test_status_inicial_a_iniciar(self):
        """Nova Ação deve começar com status 'a_iniciar'."""
        acao = self._criar_acao()
        self.assertEqual(acao.status, "a_iniciar")

    # ------------------------------------------------------------------
    # T03 — Detecção de atraso
    # ------------------------------------------------------------------
    def test_acao_atrasada_retorna_true(self):
        """Ação com data_fim no passado e não finalizada deve ser detectada como atrasada."""
        acao = self._criar_acao(data_inicio=ONTEM - timedelta(days=2), data_fim=ONTEM)
        self.assertTrue(acao.esta_atrasada())

    def test_acao_no_prazo_nao_atrasada(self):
        """Ação com data_fim no futuro não deve ser detectada como atrasada."""
        acao = self._criar_acao()
        self.assertFalse(acao.esta_atrasada())

    # ------------------------------------------------------------------
    # T04 — Validação de datas (clean)
    # ------------------------------------------------------------------
    def test_clean_data_fim_antes_inicio_levanta_validationerror(self):
        """data_fim < data_inicio deve levantar ValidationError."""
        data_inicio = HOJE
        data_fim = ONTEM  # inválido
        with self.assertRaises(ValidationError):
            acao = Acao(
                nome="Ação Inválida",
                obrigacao=self.obrigacao,
                responsavel=self.usuario,
                data_inicio=data_inicio,
                data_fim=data_fim,
            )
            acao.full_clean()

    # ------------------------------------------------------------------
    # T05 — Checklist atualiza percentual via signal
    # ------------------------------------------------------------------
    def test_checklist_item_concluido_atualiza_percentual(self):
        """Marcar o único item do checklist como concluído → percentual_cumprido = 100."""
        acao = self._criar_acao()
        item = ChecklistItem.objects.create(acao=acao, nome="Etapa 1", concluido=False)

        item.concluido = True
        item.save()  # dispara signal checklist_item_changed

        acao.refresh_from_db()
        self.assertEqual(acao.percentual_cumprido, 100)

    def test_checklist_item_concluido_muda_status_para_finalizado(self):
        """100% de itens concluídos → status da Ação muda para 'finalizado'."""
        acao = self._criar_acao()
        item = ChecklistItem.objects.create(acao=acao, nome="Etapa 1", concluido=False)

        item.concluido = True
        item.save()

        acao.refresh_from_db()
        self.assertEqual(acao.status, "finalizado")

    # ------------------------------------------------------------------
    # T06 — Signal propaga status para Obrigação (não-recorrente + finalizada)
    # ------------------------------------------------------------------
    def test_signal_atualiza_obrigacao_para_cumprida(self):
        """Completar todas as ações de Obrigação não-recorrente → status Obrigação = 'cumprida'."""
        # Obrigacao não recorrente; data_vencimento no futuro
        acao = self._criar_acao()
        item = ChecklistItem.objects.create(acao=acao, nome="Etapa 1", concluido=False)

        item.concluido = True
        item.save()  # signal → atualizar_status_por_acoes()

        self.obrigacao.refresh_from_db()
        self.assertEqual(self.obrigacao.status, "cumprida")

    # ------------------------------------------------------------------
    # T07 — Cascade delete
    # ------------------------------------------------------------------
    def test_delecao_acao_remove_checklist_items(self):
        """Deletar Ação deve remover seus ChecklistItems em cascade."""
        acao = self._criar_acao()
        ChecklistItem.objects.create(acao=acao, nome="Item A")
        ChecklistItem.objects.create(acao=acao, nome="Item B")
        acao_pk = acao.pk

        acao.delete()

        self.assertEqual(ChecklistItem.objects.filter(acao_id=acao_pk).count(), 0)

    # ------------------------------------------------------------------
    # T08 — Duração em dias
    # ------------------------------------------------------------------
    def test_duracao_dias_correto(self):
        """Ação de 7 dias deve retornar duracao_dias() = 8 (início e fim inclusivos)."""
        acao = self._criar_acao(data_inicio=HOJE, data_fim=HOJE + timedelta(days=7))
        self.assertEqual(acao.duracao_dias(), 8)
