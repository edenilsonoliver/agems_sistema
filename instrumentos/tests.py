"""
Testes Funcionais — Módulo Instrumentos (instrumentos)

Cobertura:
  - Criação de Instrumento válido
  - Validação data_fim < data_inicio (clean)
  - Status automático Obrigação: vencida por prazo
  - Status automático Obrigação: cumprida (não-recorrente + ações finalizadas)
  - Status manual não é sobrescrito por save simples
  - Percentual de atendimento manual independente do status
"""
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import Diretoria, TipoInstrumento, TipoObrigacao, TipoEntidade, TipoServico
from entidades.models import Entidade
from instrumentos.models import Instrumento, Obrigacao

HOJE = date.today()
AMANHA = HOJE + timedelta(days=1)
ONTEM = HOJE - timedelta(days=1)
SEMANA_QUE_VEM = HOJE + timedelta(days=7)


def criar_base():
    """Cria estrutura básica reutilizável para os testes de Instrumento."""
    diretoria = Diretoria.objects.create(nome="Dir. Instrumento Teste", sigla="DIT")
    tipo_entidade = TipoEntidade.objects.create(nome="Órgão Público")
    tipo_servico = TipoServico.objects.create(nome="Gás")
    entidade = Entidade.objects.create(
        razao_social="Entidade Base LTDA",
        cnpj="11.111.111/0001-11",
        tipo_entidade=tipo_entidade,
        tipo_servico=tipo_servico,
        endereco="Av. Teste, 100",
        cep="79000-001",
    )
    tipo_instrumento = TipoInstrumento.objects.create(nome="Convênio")
    return diretoria, entidade, tipo_instrumento


class InstrumentoFlowTests(TestCase):
    """Testes de fluxo e validação do modelo Instrumento."""

    def setUp(self):
        self.diretoria, self.entidade, self.tipo_instrumento = criar_base()

    def _criar_instrumento(self, **kwargs):
        defaults = dict(
            numero="CONV-TEST-001",
            tipo_instrumento=self.tipo_instrumento,
            diretoria=self.diretoria,
            objeto="Objeto do convênio de teste",
            data_assinatura=HOJE,
            data_inicio=HOJE,
            data_fim=SEMANA_QUE_VEM,
        )
        defaults.update(kwargs)
        inst = Instrumento.objects.create(**defaults)
        inst.entidades.set([self.entidade])
        return inst

    # ------------------------------------------------------------------
    # T01 — Criação válida
    # ------------------------------------------------------------------
    def test_criar_instrumento_valido(self):
        """Instrumento com campos obrigatórios deve ser salvo sem exceção."""
        inst = self._criar_instrumento()
        self.assertIsNotNone(inst.pk)
        self.assertEqual(inst.numero, "CONV-TEST-001")
        self.assertEqual(inst.status, "vigente")

    # ------------------------------------------------------------------
    # T02 — Validação de datas (clean)
    # ------------------------------------------------------------------
    def test_clean_data_fim_antes_inicio_levanta_validationerror(self):
        """data_fim < data_inicio deve levantar ValidationError."""
        with self.assertRaises(ValidationError):
            inst = Instrumento(
                numero="CONV-INVALIDO-001",
                tipo_instrumento=self.tipo_instrumento,
                diretoria=self.diretoria,
                objeto="Inválido",
                data_assinatura=HOJE,
                data_inicio=HOJE,
                data_fim=ONTEM,
            )
            inst.full_clean()

    # ------------------------------------------------------------------
    # T03 — Número único do instrumento
    # ------------------------------------------------------------------
    def test_numero_duplicado_levanta_erro(self):
        """Dois instrumentos com o mesmo número devem falhar na validação."""
        self._criar_instrumento(numero="CONV-UNICO-001")
        with self.assertRaises(Exception):
            self._criar_instrumento(numero="CONV-UNICO-001")


class ObrigacaoStatusTests(TestCase):
    """Testes das regras automáticas de status da Obrigação."""

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.diretoria, self.entidade, self.tipo_instrumento = criar_base()
        self.instrumento = Instrumento.objects.create(
            numero="INST-OBRIG-001",
            tipo_instrumento=self.tipo_instrumento,
            diretoria=self.diretoria,
            objeto="Instrumento para testar Obrigações",
            data_assinatura=HOJE,
            data_inicio=HOJE,
            data_fim=SEMANA_QUE_VEM,
        )
        self.instrumento.entidades.set([self.entidade])
        self.tipo_obrigacao = TipoObrigacao.objects.create(nome="Prestação de Contas")
        self.usuario = User.objects.create_user(
            username="user_obrig_test",
            password="senha123",
            perfil=1,
            diretoria=self.diretoria,
        )

    def _criar_obrigacao(self, **kwargs):
        defaults = dict(
            titulo="Obrigação Teste Status",
            descricao="Desc",
            instrumento=self.instrumento,
            tipo_obrigacao=self.tipo_obrigacao,
            recorrente=False,
            data_vencimento=SEMANA_QUE_VEM,
        )
        defaults.update(kwargs)
        return Obrigacao.objects.create(**defaults)

    # ------------------------------------------------------------------
    # T04 — Status automático: vencida
    # ------------------------------------------------------------------
    def test_status_vencida_quando_prazo_passado(self):
        """Obrigação com data_vencimento no passado → atualizar_status_por_acoes() define 'vencida'."""
        obrigacao = self._criar_obrigacao(data_vencimento=ONTEM)
        obrigacao.atualizar_status_por_acoes()
        obrigacao.refresh_from_db()
        self.assertEqual(obrigacao.status, "vencida")

    # ------------------------------------------------------------------
    # T05 — Status automático: cumprida (não-recorrente + ações finalizadas)
    # ------------------------------------------------------------------
    def test_status_cumprida_quando_acoes_finalizadas(self):
        """Obrigação não-recorrente com todas as ações finalizadas → status = 'cumprida'."""
        from acoes.models import Acao
        obrigacao = self._criar_obrigacao()
        acao = Acao.objects.create(
            nome="Ação Finalizada",
            obrigacao=obrigacao,
            responsavel=self.usuario,
            data_inicio=HOJE,
            data_fim=SEMANA_QUE_VEM,
            status="finalizado",
        )
        obrigacao.atualizar_status_por_acoes()
        obrigacao.refresh_from_db()
        self.assertEqual(obrigacao.status, "cumprida")

    # ------------------------------------------------------------------
    # T06 — Status recorrente não muda para cumprida automaticamente
    # ------------------------------------------------------------------
    def test_obrigacao_recorrente_nao_muda_para_cumprida(self):
        """Obrigação recorrente não deve ter status definido como 'cumprida' automaticamente."""
        from acoes.models import Acao
        obrigacao = self._criar_obrigacao(recorrente=True)
        Acao.objects.create(
            nome="Ação Finalizada Recorrente",
            obrigacao=obrigacao,
            responsavel=self.usuario,
            data_inicio=HOJE,
            data_fim=SEMANA_QUE_VEM,
            status="finalizado",
        )
        obrigacao.atualizar_status_por_acoes()
        obrigacao.refresh_from_db()
        self.assertNotEqual(obrigacao.status, "cumprida")

    # ------------------------------------------------------------------
    # T07 — Status manual não é sobrescrito por save() simples
    # ------------------------------------------------------------------
    def test_status_manual_nao_sobrescrito_por_save(self):
        """Salvar Obrigação sem chamar atualizar_status_por_acoes() não altera status manual."""
        obrigacao = self._criar_obrigacao()
        # Define status manualmente
        obrigacao.status = "em_andamento"
        obrigacao.save(update_fields=["status", "data_atualizacao"])

        # Salva novamente SEM chamar atualizar_status
        obrigacao.titulo = "Título Editado"
        obrigacao.save(update_fields=["titulo", "data_atualizacao"])
        obrigacao.refresh_from_db()

        self.assertEqual(obrigacao.status, "em_andamento")

    # ------------------------------------------------------------------
    # T08 — Percentual de atendimento manual
    # ------------------------------------------------------------------
    def test_percentual_atendimento_pode_ser_editado(self):
        """Percentual de atendimento deve ser salvo e recuperado sem alterar status."""
        obrigacao = self._criar_obrigacao()
        obrigacao.percentual_atendimento = 75
        obrigacao.save(update_fields=["percentual_atendimento", "data_atualizacao"])
        obrigacao.refresh_from_db()
        self.assertEqual(obrigacao.percentual_atendimento, 75)
        # Status não deve ter mudado
        self.assertEqual(obrigacao.status, "pendente")
