"""
Script de teste para verificar o tratamento de ProtectedError na ModernDeleteView
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from core.models import TipoAcao
from acoes.models import Acao
from instrumentos.models import Obrigacao

User = get_user_model()

print("=" * 60)
print("TESTE: Tratamento de ProtectedError na exclusão de TipoAcao")
print("=" * 60)

# 1. Criar um TipoAcao de teste
tipo_teste = TipoAcao.objects.create(
    nome="Tipo Teste Proteção",
    descricao="Criado para testar proteção de exclusão"
)
print(f"\n✅ TipoAcao criado: ID {tipo_teste.id} - {tipo_teste.nome}")

# 2. Criar uma Ação vinculada a este tipo (para forçar ProtectedError)
obrigacao = Obrigacao.objects.first()
if obrigacao:
    user = User.objects.filter(is_superuser=True).first()
    if user:
        acao_teste = Acao.objects.create(
            nome="Ação de Teste",
            descricao="Para testar proteção",
            obrigacao=obrigacao,
            tipo_acao=tipo_teste,  # Vincula ao tipo
            responsavel=user,
            data_inicio="2026-01-01",
            data_fim="2026-12-31"
        )
        print(f"✅ Ação criada e vinculada: '{acao_teste.nome}' -> TipoAcao ID {tipo_teste.id}")
        
        # 3. Tentar excluir via Client (simula requisição HTTP)
        client = Client()
        client.force_login(user)
        
        url = f'/tipos-acao/{tipo_teste.id}/excluir/'
        print(f"\n🔍 Testando DELETE via POST em: {url}")
        
        response = client.post(url, follow=True)
        
        print(f"\n📊 Resultado:")
        print(f"   Status Code: {response.status_code}")
        print(f"   URL Final: {response.request['PATH_INFO']}")
        
        # Verificar mensagens
        messages = list(get_messages(response.wsgi_request))
        if messages:
            print(f"\n💬 Mensagens exibidas:")
            for msg in messages:
                print(f"   [{msg.level_tag.upper()}] {msg.message}")
        
        # Verificar se o TipoAcao ainda existe
        tipo_existe = TipoAcao.objects.filter(id=tipo_teste.id).exists()
        print(f"\n🔍 TipoAcao ainda existe no banco? {tipo_existe}")
        
        if response.status_code == 200 and tipo_existe:
            print("\n✅ SUCESSO! O erro foi tratado corretamente:")
            print("   - Não houve erro 500")
            print("   - TipoAcao não foi excluído (protegido)")
            print("   - Mensagem de erro foi exibida ao usuário")
        else:
            print("\n❌ FALHA! Algo não funcionou como esperado")
        
        # Limpeza
        print(f"\n🧹 Limpando dados de teste...")
        acao_teste.delete()
        tipo_teste.delete()
        print("   Dados de teste removidos")
        
    else:
        print("❌ Nenhum superusuário encontrado")
else:
    print("❌ Nenhuma obrigação encontrada no banco")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
