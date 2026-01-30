#!/usr/bin/env python
"""
Script de teste para validar a lógica de atualização:
Checklist → Ação → Obrigação
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from instrumentos.models import Instrumento, Obrigacao
from acoes.models import Acao, ChecklistItem
from core.models import TipoInstrumento, TipoObrigacao, Diretoria

User = get_user_model()

print("=" * 70)
print("TESTE: Validação da Lógica Checklist → Ação → Obrigação")
print("=" * 70)

# Buscar dados necessários
tipo_inst = TipoInstrumento.objects.first()
tipo_obrig = TipoObrigacao.objects.first()
diretoria = Diretoria.objects.first()
user = User.objects.filter(is_superuser=True).first()

if not all([tipo_inst, tipo_obrig, diretoria, user]):
    print("ERRO: Faltam dados básicos no banco")
    exit(1)

# Criar Instrumento de teste
hoje = date.today()
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

inst = Instrumento.objects.create(
    numero=f"TESTE-LOGICA-{timestamp}",
    tipo_instrumento=tipo_inst,
    diretoria=diretoria,
    objeto="Teste de lógica de atualização",
    data_assinatura=hoje,
    data_inicio=hoje,
    data_fim=hoje + timedelta(days=365)
)
print(f"\n✅ Instrumento criado: {inst.numero}")

# Criar Obrigação com data de vencimento futura
obrig = Obrigacao.objects.create(
    titulo="Obrigação Teste Lógica",
    descricao="Para testar atualização automática",
    instrumento=inst,
    tipo_obrigacao=tipo_obrig,
    data_vencimento=hoje + timedelta(days=30)
)
print(f"✅ Obrigação criada: {obrig.titulo}")
print(f"   Status inicial: {obrig.status}")
print(f"   Cumprida: {obrig.cumprida}")

# Criar 3 Ações vinculadas
acoes = []
for i in range(1, 4):
    acao = Acao.objects.create(
        nome=f"Ação Teste {i}",
        descricao=f"Ação {i} para teste",
        obrigacao=obrig,
        responsavel=user,
        data_inicio=hoje,
        data_fim=hoje + timedelta(days=20)
    )
    acoes.append(acao)
    print(f"✅ Ação {i} criada: {acao.nome}")

# Recarregar obrigação
obrig.refresh_from_db()
print(f"\n📊 Após criar ações:")
print(f"   Obrigação status: {obrig.status}")
print(f"   Percentual conclusão: {obrig.percentual_conclusao}%")

# Teste 1: Adicionar checklist à primeira ação
print("\n" + "=" * 70)
print("TESTE 1: Adicionar checklist e marcar itens")
print("=" * 70)

acao1 = acoes[0]
for i in range(1, 4):
    ChecklistItem.objects.create(
        acao=acao1,
        nome=f"Item checklist {i}",
        ordem=i
    )
print(f"✅ 3 itens de checklist adicionados à Ação 1")

acao1.refresh_from_db()
print(f"   Ação 1 percentual: {acao1.percentual_cumprido}%")
print(f"   Ação 1 status: {acao1.status}")

# Marcar 2 itens como concluídos
# Converter para lista para evitar lazy evaluation do QuerySet
itens = list(acao1.checklist_itens.all())
print(f"\n[TESTE] Marcando item 1 como concluído...")
itens[0].concluido = True
itens[0].save()

print(f"[TESTE] Marcando item 2 como concluído...")
itens[1].concluido = True
itens[1].save()

acao1.refresh_from_db()
obrig.refresh_from_db()
print(f"\n📊 Após marcar 2/3 itens:")
print(f"   Ação 1 percentual: {acao1.percentual_cumprido}%")
print(f"   Ação 1 status: {acao1.status}")
print(f"   Obrigação status: {obrig.status}")
print(f"   Obrigação percentual: {obrig.percentual_conclusao}%")

# Marcar último item
print(f"\n[TESTE] Marcando item 3 como concluído...")
itens[2].concluido = True
itens[2].save()

acao1.refresh_from_db()
obrig.refresh_from_db()
print(f"\n📊 Após marcar 3/3 itens:")
print(f"   Ação 1 percentual: {acao1.percentual_cumprido}%")
print(f"   Ação 1 status: {acao1.status}")
print(f"   Obrigação status: {obrig.status}")

# Teste 2: Finalizar todas as ações
print("\n" + "=" * 70)
print("TESTE 2: Finalizar todas as ações")
print("=" * 70)

for acao in acoes[1:]:
    acao.status = 'finalizado'
    acao.percentual_cumprido = 100
    acao.save()

obrig.refresh_from_db()
print(f"📊 Após finalizar todas as ações:")
print(f"   Obrigação status: {obrig.status}")
print(f"   Obrigação cumprida: {obrig.cumprida}")
print(f"   Obrigação data_cumprimento: {obrig.data_cumprimento}")
print(f"   Obrigação percentual: {obrig.percentual_conclusao}%")

if obrig.status == 'cumprida' and obrig.cumprida:
    print("   ✅ SUCESSO: Obrigação marcada como cumprida!")
else:
    print("   ❌ FALHA: Obrigação deveria estar cumprida")

# Teste 3: Testar data vencida
print("\n" + "=" * 70)
print("TESTE 3: Testar obrigação vencida")
print("=" * 70)

# Criar nova obrigação com data vencida
obrig_vencida = Obrigacao.objects.create(
    titulo="Obrigação Vencida Teste",
    descricao="Teste de vencimento",
    instrumento=inst,
    tipo_obrigacao=tipo_obrig,
    data_vencimento=hoje - timedelta(days=10)  # 10 dias atrás
)
print(f"✅ Obrigação com data vencida criada")

# Criar ação não finalizada
acao_vencida = Acao.objects.create(
    nome="Ação Atrasada",
    descricao="Teste",
    obrigacao=obrig_vencida,
    responsavel=user,
    data_inicio=hoje - timedelta(days=15),
    data_fim=hoje - timedelta(days=5)
)

obrig_vencida.refresh_from_db()
print(f"📊 Obrigação com data vencida:")
print(f"   Status: {obrig_vencida.status}")
print(f"   Data vencimento: {obrig_vencida.data_vencimento}")

if obrig_vencida.status == 'vencida':
    print("   ✅ SUCESSO: Obrigação marcada como vencida!")
else:
    print(f"   ❌ FALHA: Obrigação deveria estar vencida, mas está: {obrig_vencida.status}")

# Limpeza
print("\n" + "=" * 70)
print("Limpando dados de teste...")
print("=" * 70)

# Excluir ações primeiro (para evitar ProtectedError)
acao_vencida.delete()
for acao in acoes:
    acao.delete()

# Depois excluir obrigações
obrig_vencida.delete()
obrig.delete()

# Por fim, instrumento
inst.delete()
print("✅ Dados removidos")

print("\n" + "=" * 70)
print("TESTE CONCLUÍDO")
print("=" * 70)
