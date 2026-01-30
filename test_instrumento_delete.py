#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.db import models
from instrumentos.models import Instrumento, Obrigacao
from core.models import TipoInstrumento, TipoObrigacao, Diretoria

User = get_user_model()

print("=" * 60)
print("TESTE: Exclusao de Instrumento com Obrigacoes")
print("=" * 60)

# Verificar se existe instrumento com obrigacoes
instrumentos_com_obrigacoes = Instrumento.objects.annotate(
    num_obrigacoes=models.Count('obrigacoes')
).filter(num_obrigacoes__gt=0).first()

if instrumentos_com_obrigacoes:
    print(f"\nInstrumento encontrado: {instrumentos_com_obrigacoes.numero}")
    print(f"Obrigacoes vinculadas: {instrumentos_com_obrigacoes.obrigacoes.count()}")
    
    # Testar exclusao via HTTP
    user = User.objects.filter(is_superuser=True).first()
    if user:
        client = Client(enforce_csrf_checks=False)
        client.force_login(user)
        
        url = f'/instrumentos/{instrumentos_com_obrigacoes.id}/excluir/'
        print(f"\nTestando DELETE em: {url}")
        
        response = client.post(url, follow=True)
        
        print(f"\nStatus: {response.status_code}")
        print(f"URL final: {response.request['PATH_INFO']}")
        
        # Verificar se instrumento ainda existe
        existe = Instrumento.objects.filter(id=instrumentos_com_obrigacoes.id).exists()
        print(f"Instrumento ainda existe: {existe}")
        
        if response.status_code == 200 and existe:
            print("\nSUCESSO! Erro tratado corretamente")
        else:
            print("\nFALHA! Precisa implementar tratamento")
    else:
        print("ERRO: Nenhum superusuario encontrado")
else:
    print("\nNenhum instrumento com obrigacoes encontrado")
    print("Criando cenario de teste...")
    
    # Criar dados de teste
    tipo_inst = TipoInstrumento.objects.first()
    tipo_obrig = TipoObrigacao.objects.first()
    diretoria = Diretoria.objects.first()
    user = User.objects.filter(is_superuser=True).first()
    
    if tipo_inst and tipo_obrig and diretoria and user:
        from django.db import models
        
        inst = Instrumento.objects.create(
            numero="TESTE-001",
            tipo_instrumento=tipo_inst,
            diretoria=diretoria,
            objeto="Teste de exclusao",
            data_assinatura="2026-01-01",
            data_inicio="2026-01-01",
            data_fim="2026-12-31"
        )
        print(f"Instrumento criado: {inst.numero}")
        
        obrig = Obrigacao.objects.create(
            titulo="Obrigacao Teste",
            descricao="Para testar protecao",
            instrumento=inst,
            tipo_obrigacao=tipo_obrig
        )
        print(f"Obrigacao criada e vinculada")
        
        # Testar exclusao
        client = Client(enforce_csrf_checks=False)
        client.force_login(user)
        
        url = f'/instrumentos/{inst.id}/excluir/'
        response = client.post(url, follow=True)
        
        print(f"\nStatus: {response.status_code}")
        existe = Instrumento.objects.filter(id=inst.id).exists()
        print(f"Instrumento ainda existe: {existe}")
        
        if response.status_code == 200 and existe:
            print("SUCESSO! Erro tratado")
        else:
            print("FALHA!")
        
        # Limpar
        obrig.delete()
        inst.delete()
        print("\nDados de teste removidos")
    else:
        print("ERRO: Faltam dados basicos no banco")

print("\n" + "=" * 60)
