
import os
import sys
import django
import re
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db.models import Q
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
import uuid

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario
from instrumentos.models import Instrumento, Obrigacao
from acoes.models import Acao
from core.models import Diretoria, Subunidade, TipoAcao, TipoInstrumento, TipoObrigacao
from alertas.models import Notificacao

def log_test(module, test_name, result, message=""):
    status = "[PASS]" if result else "[FAIL]"
    print(f"[{module}] {test_name}: {status}")
    if message:
        print(f"   > {message}")
    return result

def get_mock_request(factory, url, user, data=None):
    if data:
        request = factory.post(url, data)
    else:
        request = factory.get(url)
    request.user = user
    sm = SessionMiddleware(lambda r: None)
    sm.process_request(request)
    request.session.save()
    mm = MessageMiddleware(lambda r: None)
    mm.process_request(request)
    setattr(request, '_messages', FallbackStorage(request))
    return request

def run_automated_tests():
    print("=" * 60)
    print("AGEMS AUTOMATED PRE-DEPLOY SYSTEM TEST - VERSION ULTRA-PARANOID")
    print("=" * 60)
    
    factory = RequestFactory()
    
    # --- Módulo 0: Setup Usuarios ---
    try:
        # Garantir diretoria e subunidade de teste
        diretoria, _ = Diretoria.objects.get_or_create(sigla='TEST', defaults={'nome': 'Unidade de Teste'})
        sub_a, _ = Subunidade.objects.get_or_create(nome='Sub A', sigla='SA', diretoria=diretoria)
        sub_b, _ = Subunidade.objects.get_or_create(nome='Sub B', sigla='SB', diretoria=diretoria)
        
        # Criar/Garantir Técnicos
        t1, _ = Usuario.objects.get_or_create(username='test_t1', defaults={'perfil': 4, 'subunidade': sub_a, 'diretoria': diretoria})
        t2, _ = Usuario.objects.get_or_create(username='test_t2', defaults={'perfil': 4, 'subunidade': sub_a, 'diretoria': diretoria})
        t3, _ = Usuario.objects.get_or_create(username='test_t3', defaults={'perfil': 4, 'subunidade': sub_b, 'diretoria': diretoria})
        
        log_test("M0", "Setup Usuários", True, f"T1/T2 (Sub A), T3 (Sub B)")
    except Exception as e:
        log_test("M0", "Setup Usuários", False, f"Erro: {e}")
        return

    # --- Módulo 1: Setup Dados ---
    try:
        tipo_inst, _ = TipoInstrumento.objects.get_or_create(nome='Tipo Teste')
        tipo_obrig, _ = TipoObrigacao.objects.get_or_create(nome='Obrig Teste')
        
        inst = Instrumento.objects.create(
            numero=f"TEST-{uuid.uuid4().hex[:6]}",
            tipo_instrumento=tipo_inst,
            diretoria=diretoria,
            objeto="Objeto de Teste",
            data_assinatura="2024-01-01",
            data_inicio="2024-01-01",
            data_fim="2025-01-01"
        )
        inst.subunidades.add(sub_a) # Sub A é gestora desse instrumento
        
        obrig = Obrigacao.objects.create(
            titulo="Obrigação de Teste",
            descricao="...",
            instrumento=inst,
            tipo_obrigacao=tipo_obrig
        )
        
        acao = Acao.objects.create(
            nome="Ação de T1",
            obrigacao=obrig,
            responsavel=t1,
            data_inicio="2024-01-01",
            data_fim="2024-12-31"
        )
        acao.executores.add(t2)
        
        log_test("M1", "Setup Dados", True, f"Ação {acao.id} criada. Resp: T1, Exec: T2.")
    except Exception as e:
        log_test("M1", "Setup Dados", False, f"Erro: {e}")
        return

    # --- Módulo 2: Segurança (Testando as correções) ---
    print("\n--- Módulo 2: RBAC Fino (Correções Aplicadas) ---")
    
    # 2.1 Responsável (T1) Acessa full
    try:
        from acoes.views import AcaoUpdateView
        view = AcaoUpdateView()
        view.request = get_mock_request(factory, reverse('acao_edit', kwargs={'pk': acao.id}), t1)
        view.kwargs = {'pk': acao.id}
        view.object = acao
        f_kwargs = view.get_form_kwargs()
        log_test("M2.1", "Responsável T1 (Acesso Full)", not f_kwargs.get('executor_readonly'))
    except Exception as e:
        log_test("M2.1", "Responsável T1", False, f"Erro: {e}")

    # 2.2 Executor (T2) Acessa Read-Only
    try:
        view = AcaoUpdateView()
        view.request = get_mock_request(factory, reverse('acao_edit', kwargs={'pk': acao.id}), t2)
        view.kwargs = {'pk': acao.id}
        view.object = acao
        f_kwargs = view.get_form_kwargs()
        log_test("M2.2", "Executor T2 (ReadOnly)", f_kwargs.get('executor_readonly'))
    except Exception as e:
        log_test("M2.2", "Executor T2", False, f"Erro: {e}")

    # 2.3 Curioso (T3) Bloqueado (Instrumento não é da subunidade dele)
    try:
        view_func = AcaoUpdateView.as_view()
        response = view_func(get_mock_request(factory, reverse('acao_edit', kwargs={'pk': acao.id}), t3), pk=acao.id)
        # Deve ser bloqueado pelo dispatch (verifica_acesso_unidade)
        is_blocked = response.status_code == 302 and response.url == reverse('acao_list')
        log_test("M2.3", "Invasor T3 (Sub Diferente) - Bloqueio Global", is_blocked)
    except Exception as e:
        log_test("M2.3", "Invasor T3", False, f"Erro: {e}")

    # 2.4 "Invasor Amigo" (T4) Mesma subunidade mas não está na ação
    try:
        t4, _ = Usuario.objects.get_or_create(username='test_t4', defaults={'perfil': 4, 'subunidade': sub_a, 'diretoria': diretoria})
        view_func = AcaoUpdateView.as_view()
        response = view_func(get_mock_request(factory, reverse('acao_edit', kwargs={'pk': acao.id}), t4), pk=acao.id)
        # Deve ser bloqueado pelo dispatch (Verificação Secundária nova)
        is_blocked = response.status_code == 302 and response.url == reverse('acao_list')
        log_test("M2.4", "Colega T4 (Mesma Sub) - Bloqueio Individual", is_blocked)
    except Exception as e:
        log_test("M2.4", "Colega T4", False, f"Erro: {e}")

    print("\n" + "=" * 60)
    print("FINISHED")
    print("=" * 60)

if __name__ == "__main__":
    run_automated_tests()
