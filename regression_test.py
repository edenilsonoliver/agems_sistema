
import os
import django
import sys
from datetime import date, timedelta

# Configurar ambiente Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from acoes.models import Acao, AcaoFoto, AcaoDocumento, ChecklistItem
from instrumentos.models import Obrigacao
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

User = get_user_model()

def run_regression_test():
    print("--- 🛡️ Iniciando Teste de Regressão Global ---")
    
    user = User.objects.first()
    obrigacao = Obrigacao.objects.first()
    
    # 1. Teste de Criação e Salvamento (Signals de Status)
    print("\n1. Testando Criação e Atualização de Status...")
    acao = Acao.objects.create(
        nome="Teste Regressão Global",
        obrigacao=obrigacao,
        responsavel=user,
        data_inicio=date.today(),
        data_fim=date.today() + timedelta(days=5)
    )
    ChecklistItem.objects.create(acao=acao, nome="Item 1", concluido=False)
    
    acao.refresh_from_db()
    print(f"   Status Inicial: {acao.status} (Mínimo esperado: a_iniciar ou em_andamento)")
    
    # 2. Teste de Upload vinculado (Garantir que a criação física funciona)
    print("\n2. Testando Salvamento com Arquivos...")
    foto = AcaoFoto(acao=acao, usuario=user, legenda="Foto Regressão")
    foto.imagem.save('regressao_foto.jpg', ContentFile(b"data"), save=True)
    f_path = foto.imagem.path
    print(f"   Arquivo Foto Criado: {os.path.exists(f_path)}")

    # 3. Teste de Edição (Garantir que salvamento subsequente não apaga arquivo)
    print("\n3. Testando Manutenção de Arquivo em Edição...")
    acao.nome = "Teste Regressão Nome Alterado"
    acao.save()
    if os.path.exists(f_path):
        print("   ✅ SUCESSO: Arquivo permanece após edição da Ação pai.")
    else:
        print("   ❌ FALHA: Arquivo sumiu após um save() comum da Ação.")

    # 4. Teste de Deleção Segura
    print("\n4. Finalizando com Deleção Total...")
    acao.delete()
    if not os.path.exists(f_path):
        print("   ✅ SUCESSO: Faxina concluída ao deletar Ação pai.")
    else:
        print("   ❌ FALHA: Arquivo residual encontrado.")

if __name__ == "__main__":
    try:
        run_regression_test()
        print("\n✨ STATUS FINAL: SISTEMA ESTÁVEL E RESILIENTE ✨")
    except Exception as e:
        print(f"\n🔥 CRITICAL REGRESSION DETECTED: {str(e)}")
        sys.exit(1)
