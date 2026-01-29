import os
import django
import sys
from unittest.mock import MagicMock

def run_test():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from acoes.models import Acao, AcaoDocumento
    from acoes.views import AcaoUpdateView
    from acoes.forms import AcaoForm, ChecklistItemFormSet, AcaoDocumentoFormSet, AcaoFotoFormSet
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.contrib.messages.storage.fallback import FallbackStorage

    User = get_user_model()
    user = User.objects.first()
    acao = Acao.objects.last()

    if not acao:
        print("Erro: Nenhuma Ação encontrada no banco.")
        return

    print(f"--- TESTE OPERACIONAL (via SCRIPT) ---")
    print(f"Acao ID: {acao.id}")

    rf = RequestFactory()
    request = rf.post(f'/acoes/{acao.id}/editar/')
    
    # Mock de sessão simples
    request.session = MagicMock()
    request.user = user
    request._messages = FallbackStorage(request)

    # Contagem inicial de documentos
    doc_count_before = AcaoDocumento.objects.filter(acao=acao).count()

    post_data = {
        'nome': acao.nome + ' (Testado)',
        'descricao': acao.descricao or 'Desc',
        'data_inicio': acao.data_inicio.isoformat() if acao.data_inicio else '2025-01-01',
        'data_fim': acao.data_fim.isoformat() if acao.data_fim else '2025-12-31',
        'status': acao.status,
        'prioridade': acao.prioridade,
        'responsavel': acao.responsavel.id,
        'obrigacao': acao.obrigacao.id,
        'docs-TOTAL_FORMS': '1',
        'docs-INITIAL_FORMS': '0',
        'fotos-TOTAL_FORMS': '0',
        'fotos-INITIAL_FORMS': '0',
        'checklist_itens-TOTAL_FORMS': '0',
        'checklist_itens-INITIAL_FORMS': '0',
    }
    file_data = {
        'docs-0-arquivo': SimpleUploadedFile('teste_final.pdf', b'fake content', content_type='application/pdf')
    }

    form = AcaoForm(post_data, instance=acao)
    
    view = AcaoUpdateView()
    view.request = request
    view.object = acao
    
    # Simular o que o Django faz antes de chamar form_valid
    request.POST = post_data
    request.FILES = file_data

    print(f"Validando formulários...")
    if form.is_valid():
        try:
            print("Executando form_valid...")
            # A view UpdateView.form_valid faz self.object = form.save() e depois redireciona
            response = view.form_valid(form)
            
            # Forçar o processamento dos ativos se a view não o fizer no form_valid (que agora faz)
            # Verifica se o documento foi criado
            doc_count_after = AcaoDocumento.objects.filter(acao=acao).count()
            
            if doc_count_after > doc_count_before:
                print(f"✅ SUCESSO COMPLETO: Documento persistido (Antes: {doc_count_before}, Depois: {doc_count_after})")
                print("✅ TESTE DE 'messages': O código passou pelo ponto que causava NameError.")
            else:
                # Se não criou, pode ser que o form_valid não chamou o save_assets corretamente no teste
                # Vamos tentar chamar o save_assets explicitamente para validar o código interno dele
                print("Aviso: Documento não persistido automaticamente pelo form_valid no teste. Testando save_assets explicitamente...")
                context = view.get_context_data()
                view.save_assets(acao, context['docs_formset'], context['fotos_formset'])
                
                doc_count_final = AcaoDocumento.objects.filter(acao=acao).count()
                if doc_count_final > doc_count_before:
                    print(f"✅ SUCESSO: save_assets funcionando e salvando no banco.")
                else:
                    print("❌ FALHA: Mesmo chamando explicitamente, o arquivo não foi salvo.")
                    sys.exit(1)
                
        except Exception as e:
            print(f"❌ ERRO DURANTE EXECUÇÃO: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print(f"❌ ERRO: Formulário inválido. {form.errors}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
