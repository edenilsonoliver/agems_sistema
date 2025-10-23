# 🚀 AGEMS - Sistema de Gestão Regulatória

**Versão:** 2.0 | **Data:** Outubro 2025

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
- **Dashboard Executivo** - Visão geral com estatísticas e gráficos
- **Instrumentos** - Gestão de contratos, convênios e acordos
- **Obrigações** - Cadastro inline junto com instrumentos
- **Entidades** - Concessionárias, órgãos públicos e empresas
- **Ações** - Fiscalizações, análises, projetos e averiguações
- **Tarefas** - Gestão com responsáveis e executores
- **Indicadores** - Metas, valores ideais e conformidade
- **Documentos** - Upload múltiplo de arquivos
- **Alertas** - Sistema de notificações
- **Configurações** - Tipos, diretorias e serviços

### ✅ **Recursos Avançados**
- ✨ CRUD inline de tipos (criar/editar sem sair da tela)
- ✨ Sistema de abas (Dados Gerais, Obrigações, Arquivos)
- ✨ Upload múltiplo de arquivos
- ✨ Busca e filtros em todas as listagens
- ✨ Badges coloridos para status
- ✨ Interface moderna e responsiva
- ✨ Identidade visual AGEMS (azul #0066B3)
- ✨ Logo institucional

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
├── 📄 iniciar.ps1              # Script principal de inicialização
├── 📄 parar.ps1                # Para o sistema
├── 📄 reiniciar.ps1            # Reinicia o sistema
├── 📄 logs.ps1                 # Visualiza logs
├── 📄 backup.ps1               # Cria backup do banco
├── 📄 docker-compose.yml       # Configuração Docker
├── 📄 Dockerfile               # Imagem Docker
├── 📄 docker-entrypoint.sh     # Script de inicialização
├── 📄 requirements.txt         # Dependências Python
├── 📄 manage.py                # Django management
├── 📄 db.sqlite3               # Banco de dados (com admin criado)
├── 📂 config/                  # Configurações Django
├── 📂 core/                    # App principal
├── 📂 usuarios/                # Módulo de usuários
├── 📂 instrumentos/            # Módulo de instrumentos
├── 📂 entidades/               # Módulo de entidades
├── 📂 obrigacoes/              # Módulo de obrigações
├── 📂 acoes/                   # Módulo de ações
├── 📂 indicadores/             # Módulo de indicadores
├── 📂 alertas/                 # Módulo de alertas
├── 📂 documentos/              # Módulo de documentos
├── 📂 dashboards/              # Módulo de dashboards
├── 📂 templates/               # Templates HTML
└── 📂 static/                  # Arquivos estáticos (CSS, JS, imagens)
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

## 📄 Licença

Sistema desenvolvido exclusivamente para a **AGEMS - Agência de Regulação de Serviços Públicos de Mato Grosso do Sul**.

---

**Desenvolvido com ❤️ para a AGEMS**

