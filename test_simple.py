#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import TipoAcao
from acoes.models import Acao
from instrumentos.models import Obrigacao

User = get_user_model()

print("TESTE: Tratamento de ProtectedError")
print("=" * 50)

# Criar TipoAcao
tipo = TipoAcao.objects.create(nome="Teste Protecao")
print(f"TipoAcao criado: ID {tipo.id}")

# Criar Acao vinculada
obrigacao = Obrigacao.objects.first()
user = User.objects.filter(is_superuser=True).first()

if obrigacao and user:
    acao = Acao.objects.create(
        nome="Teste",
        obrigacao=obrigacao,
        tipo_acao=tipo,
        responsavel=user,
        data_inicio="2026-01-01",
        data_fim="2026-12-31"
    )
    print(f"Acao criada e vinculada ao TipoAcao {tipo.id}")
    
    # Testar exclusao via HTTP
    client = Client(enforce_csrf_checks=False)
    client.force_login(user)
    
    url = f'/tipos-acao/{tipo.id}/excluir/'
    response = client.post(url, follow=True)
    
    print(f"Status: {response.status_code}")
    print(f"URL final: {response.request['PATH_INFO']}")
    
    # Verificar se tipo ainda existe
    existe = TipoAcao.objects.filter(id=tipo.id).exists()
    print(f"TipoAcao ainda existe: {existe}")
    
    if response.status_code == 200 and existe:
        print("SUCESSO! Erro tratado corretamente")
    else:
        print("FALHA!")
    
    # Limpar
    acao.delete()
    tipo.delete()
    print("Dados de teste removidos")
else:
    print("ERRO: Faltam dados no banco")
