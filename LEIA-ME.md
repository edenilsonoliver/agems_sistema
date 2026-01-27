# 🚀 AGEMS - Sistema de Gestão Regulatória

**Versão:** v0.0.11 | **Data:** Janeiro 2026

Sistema completo de gestão de instrumentos regulatórios, obrigações, entidades e ações para a **AGEMS - Agência de Regulação de Serviços Públicos de Mato Grosso do Sul**.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- ✅ **Windows 11**
- ✅ **Docker Desktop** ([Download aqui](https://www.docker.com/products/docker-desktop))
- ✅ **PowerShell** (já vem instalado no Windows)

> **IMPORTANTE**: Após instalar o Docker Desktop, inicie-o e aguarde até que o ícone fique estável na bandeja do sistema.

---

## 🎯 Instalação Rápida (3 Passos)

### **Passo 1: Extrair o arquivo**
Descompacte o arquivo ZIP em uma pasta de sua escolha (ex: `C:\AGEMS`).

### **Passo 2: Abrir PowerShell**
Clique com botão direito na pasta do projeto e selecione:
- **"Abrir no Terminal"** ou
- **"Open PowerShell window here"**

### **Passo 3: Executar o script de inicialização**
Digite no PowerShell:
```powershell
.\iniciar.ps1
```

**Pronto!** O sistema será construído e iniciado automaticamente. O navegador abrirá na página de login.

---

## 🌐 Acesso ao Sistema

- **URL:** http://localhost:8000
- **Usuário:** `admin`
- **Senha:** `admin123`

---

## 🛠️ Scripts de Gerenciamento

O pacote inclui scripts PowerShell para facilitar o gerenciamento:

| Script | Comando | Descrição |
|--------|---------|-----------|
| **Iniciar** | `.\iniciar.ps1` | Constrói e inicia o sistema completo |
| **Parar** | `.\parar.ps1` | Para todos os containers |
| **Reiniciar** | `.\reiniciar.ps1` | Reinicia o sistema |
| **Ver Logs** | `.\logs.ps1` | Exibe logs em tempo real (Ctrl+C para sair) |
| **Backup** | `.\backup.ps1` | Cria backup do banco de dados |

---

## 📦 Funcionalidades Implementadas

### ✅ **Módulos Completos**
- **Dashboard Executivo** - Visão geral com estatísticas e gráficos dinâmicos
- **Entidades** - Concessionárias, órgãos públicos e empresas com gestão de logos
- **Instrumentos** - Gestão de contratos, convênios e acordos (NUP E-MS)
- **Obrigações** - Cadastro inline e **importação em massa via CSV**
- **Ações** - Nível executivo vinculado às obrigações (Fiscalizações, análises, projetos)
- **Checklist/Tarefas** - Reordenamento dinâmico (Drag-and-Drop) dentro das ações
- **Indicadores** - Metas, valores ideais e conformidade contratual
- **Documentos** - Upload múltiplo e gestão de arquivos por instrumento
- **Alertas** - Sistema de notificações automáticas
- **Configurações** - Gestão de tipos, diretorias e subunidades

### ✅ **Recursos Avançados**
- ✨ **Importação Inteligente:** Carga de obrigações via planilha CSV com detecção automática de delimitador (; ou ,)
- ✨ **Estrutura em 4 Níveis:** Instrumento -> Obrigação -> Ação -> Checklist
- ✨ **Drag-and-Drop:** Reordenamento visual de itens de checklist
- ✨ **Design Moderno:** Interface premium com gradientes, micro-animações e Sticky Footer
- ✨ **Padronização Visual:** Status "Em Andamento" em **Dourado Metálico** e "Encerrada" em **Vermelho**
- ✨ **Mascaramento Inteligente:** Campos de CNPJ e CEP com formatação automática
- ✨ **CRUD Inline:** Criação de tipos sem sair da tela principal
- ✨ **Identidade Visual MS:** Cores oficiais e logo institucional AGEMS

---

## 🎨 Identidade Visual

O sistema utiliza a identidade visual oficial da AGEMS:

- **Cor principal:** Azul #0066B3 (Governo de MS)
- **Logo:** AGEMS oficial
- **Design:** Moderno, limpo e responsivo

---

## 🔧 Solução de Problemas

### **Erro: "Docker is not running"**
1. Abra o Docker Desktop
2. Aguarde até aparecer "Docker Desktop is running"
3. Execute `.\iniciar.ps1` novamente

### **Erro de permissão no PowerShell**
Execute este comando uma vez (como Administrador):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Porta 8000 já está em uso**
Edite o arquivo `docker-compose.yml` e altere a porta:
```yaml
ports:
  - "8001:8000"  # Usar porta 8001
```

### **Sistema não carrega**
1. Verifique os logs: `.\logs.ps1`
2. Reinicie: `.\reiniciar.ps1`
3. Se persistir, reconstrua: `docker-compose up -d --build`

---

## 📁 Estrutura do Projeto

```
agems_regulatorio/
├── 📄 iniciar.ps1              # Script de inicialização automática
├── 📄 parar.ps1                # Script para desligar o sistema
├── 📄 reiniciar.ps1            # Script para reinicialização rápida
├── 📄 logs.ps1                 # Visualização de logs em tempo real
├── 📄 backup.ps1               # Script de backup de banco de dados
├── 📄 docker-compose.yml       # Orquestração de containers
├── 📄 Dockerfile               # Configuração da imagem Python 3.13
├── 📄 db.sqlite3               # Banco de dados principal
├── 📂 config/                  # Ajustes de sistema e segurança (Django)
├── 📂 core/                    # Núcleo da interface e views modernas
├── 📂 usuarios/                # Gestão de acessos e perfis
├── 📂 instrumentos/            # Contratos e Obrigações (Inlines)
├── 📂 acoes/                   # Execução, Checklist e Kanban
├── 📂 entidades/               # Concessionárias e Logos
├── 📂 indicadores/             # Gestão de metas e resultados
├── 📂 alertas/                 # Motor de notificações
├── 📂 documentos/              # Gestão documental
├── 📂 dashboards/              # Visões estatísticas
├── 📂 templates/               # Arquivos HTML (layout moderno)
├── 📂 static/                  # CSS (Metallic UI), JS e Imagens
└── 📂 backups/                 # Repositório de snapshots do banco
```

---

## 💾 Backup e Restauração

### **Criar Backup**
```powershell
.\backup.ps1
```
Os backups são salvos na pasta `backups/` com data e hora.

### **Restaurar Backup**
1. Pare o sistema: `.\parar.ps1`
2. Substitua o arquivo `db.sqlite3` pelo backup desejado
3. Inicie novamente: `.\iniciar.ps1`

---

## 🔐 Segurança

- ⚠️ **IMPORTANTE**: As credenciais padrão (`admin/admin123`) são para desenvolvimento local.
- ⚠️ Para uso em produção, altere imediatamente a senha do administrador.
- ⚠️ Configure variáveis de ambiente adequadas no arquivo `.env.local`.

---

## 📞 Suporte

Para problemas técnicos:
1. Verifique se o Docker Desktop está rodando
2. Consulte os logs: `.\logs.ps1`
3. Tente reiniciar: `.\reiniciar.ps1`
4. Reconstrua se necessário: `docker-compose up -d --build`

---

## 📊 Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.13 | Backend / Runtime |
| **Django** | 5.1.2 | Framework Web |
| **SQLite** | 3 | Banco de dados (Dev) |
| **PostgreSQL** | 16 | Banco de dados (Prod) |
| **Docker** | Latest | Containerização |
| **Bootstrap** | 5.3 | Frontend / UI |
| **Redis** | 5.0 | Cache & Mensageria |
| **Celery** | 5.4 | Tarefas em Segundo Plano |

---

**Desenvolvido com ❤️ para a AGEMS**

