#!/bin/bash
set -e

echo "🚀 Iniciando AGEMS - Sistema de Gestão Regulatória"

# Aguardar o banco de dados estar pronto
echo "⏳ Aguardando PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "✅ PostgreSQL está pronto!"

# Executar migrações
echo "📦 Executando migrações do banco de dados..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@agems.ms.gov.br', 'admin123')
    print('✅ Superusuário criado: admin / admin123')
else:
    print('✅ Superusuário já existe')
END

# Carregar dados iniciais se necessário
echo "📊 Verificando dados iniciais..."
python manage.py shell << END
from core.models import Diretoria, TipoInstrumento, TipoObrigacao, TipoAcao, TipoEntidade, TipoServico

# Diretorias
if Diretoria.objects.count() == 0:
    Diretoria.objects.create(sigla='DGE', nome='Diretoria de Gás e Energia')
    Diretoria.objects.create(sigla='DSA', nome='Diretoria de Saneamento')
    Diretoria.objects.create(sigla='DRF', nome='Diretoria de Regulação Financeira')
    print('✅ Diretorias criadas')

# Tipos de Instrumento
if TipoInstrumento.objects.count() == 0:
    TipoInstrumento.objects.create(nome='Contrato de Concessão')
    TipoInstrumento.objects.create(nome='Convênio')
    TipoInstrumento.objects.create(nome='Acordo de Cooperação Técnica')
    TipoInstrumento.objects.create(nome='Termo de Ajustamento de Conduta')
    print('✅ Tipos de Instrumento criados')

# Tipos de Obrigação
if TipoObrigacao.objects.count() == 0:
    TipoObrigacao.objects.create(nome='Obrigação Contratual')
    TipoObrigacao.objects.create(nome='Obrigação Regulatória')
    TipoObrigacao.objects.create(nome='Obrigação Legal')
    print('✅ Tipos de Obrigação criados')

# Tipos de Ação
if TipoAcao.objects.count() == 0:
    TipoAcao.objects.create(nome='Fiscalização')
    TipoAcao.objects.create(nome='Análise')
    TipoAcao.objects.create(nome='Projeto')
    TipoAcao.objects.create(nome='Averiguação')
    print('✅ Tipos de Ação criados')

# Tipos de Entidade
if TipoEntidade.objects.count() == 0:
    TipoEntidade.objects.create(nome='Concessionária')
    TipoEntidade.objects.create(nome='Permissionária')
    TipoEntidade.objects.create(nome='Órgão Público')
    TipoEntidade.objects.create(nome='Empresa Privada')
    print('✅ Tipos de Entidade criados')

# Tipos de Serviço
if TipoServico.objects.count() == 0:
    TipoServico.objects.create(nome='Gás Canalizado')
    TipoServico.objects.create(nome='Energia Elétrica')
    TipoServico.objects.create(nome='Água e Esgoto')
    TipoServico.objects.create(nome='Resíduos Sólidos')
    print('✅ Tipos de Serviço criados')

print('✅ Dados iniciais verificados')
END

echo "🎉 AGEMS está pronto para uso!"
echo "📍 Acesse: http://localhost:8000"
echo "👤 Usuário: admin | Senha: admin123"
echo ""

# Executar comando passado como argumento
exec "$@"

