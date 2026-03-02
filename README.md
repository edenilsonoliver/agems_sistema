# 🚀 AGEMS - Sistema de Gestão Regulatória

**Versão 3.0 - Fevereiro 2026**

Sistema completo de **Gestão de Instrumentos Jurídicos, Regulamentação e Fiscalização de Entidades Reguladas** da **AGEMS - Agência de Regulação de Serviços Públicos de Mato Grosso do Sul**.

---

## 📦 Instalação Rápida

### **Opção 1: Script Automatizado (Recomendado)**

1. Extraia o arquivo ZIP
2. Abra PowerShell na pasta
3. Execute: `.\iniciar.ps1`
4. Aguarde e acesse: `http://localhost:8000`

### **Opção 2: Manual**

Siga o guia detalhado em: **`INSTALACAO_MANUAL.md`**

---

## 🔑 Credenciais de Acesso

- **URL:** http://localhost:8000
- **Usuário:** `admin`
- **Senha:** `admin123`

> ⚠️ Alterar senha do administrador imediatamente em produção.

---

## 📋 Pré-requisitos

- ✅ Windows 11
- ✅ Docker Desktop ([Download](https://www.docker.com/products/docker-desktop))
- ✅ PowerShell (já vem no Windows)

---

## 🎯 Módulos Implementados

### **10 Módulos Completos**

| # | Módulo | Descrição |
|---|--------|-----------|
| 1 | **Usuários** | Gestão com 5 perfis hierárquicos de acesso |
| 2 | **Entidades** | Concessionárias, Permissionárias e Entidades Reguladas |
| 3 | **Instrumentos** | Contratos, Convênios, Acordos com NUP (E-MS) |
| 4 | **Obrigações** | Vinculadas aos instrumentos (gerenciadas inline) |
| 5 | **Ações** | Fiscalizações, análises, projetos, averiguações |
| 6 | **Indicadores** | Metas, valores ideais e conformidade contratual |
| 7 | **Mapas/Geo** | Camadas KML, mapa de fiscalização por ocorrência |
| 8 | **Documentos** | Upload múltiplo com validação MIME |
| 9 | **Fotos** | Registro fotográfico de campo com GPS |
| 10 | **Painel** | Painel de Acompanhamento com gráficos e estatísticas |

---

## 🔐 Controle de Acesso por Perfil

O sistema implementa **Controle de Acesso Baseado em Funções (RBAC)** com 4 perfis mapeados para Grupos de Permissão do Django. Para detalhes completos, consulte [PERFIS_ACESSO.md](./PERFIS_ACESSO.md).

| Perfil | Grupo | Foco | Permissões Chave |
|--------|-------|------|-----------------|
| **Administrador** | *Superuser* | Sistema/TI | Acesso total e irrestrito (inclui `/admin` e configurações globais) |
| **Gestor** (Perfil 1-2) | `Gestores` | Gerência | CRUD completo de Entidades, Instrumentos, Obrigações e Ações. Gerencia Usuários |
| **Técnico** (Perfil 3-4) | `Tecnicos` | Execução | Pode criar e editar Ações. **Não pode excluir**. Vê apenas suas próprias tarefas (filtrado por Responsável/Executor). Somente leitura em Entidades e Instrumentos |
| **Visualizador** (Perfil 5) | `Visualizadores` | Auditoria | Somente leitura em todo o sistema. Sem botões de Criar/Editar/Excluir |

### **Comportamento para Acesso Restrito**
- Usuários sem permissão de edição veem formulários em **Modo de Visualização** (banner azul, campos desabilitados)
- Tentativas de exclusão sem permissão resultam em **redirecionamento com mensagem amigável** — sem erro 403
- Botões de ação (Salvar, Excluir) são ocultados automaticamente

### **Mapeamento Técnico**

```
perfil 1 ou 2  →  Grupo 'Gestores'   (add/change/delete/view nos modelos principais)
perfil 3 ou 4  →  Grupo 'Tecnicos'   (add/change/view em Acao; view em Entidade/Instrumento/Obrigacao)
perfil 5       →  Grupo 'Visualizadores' (view em todos os modelos)
```

---

## 📊 Regras de Negócio — Obrigações

### **Percentual de Atendimento (% ATEND.)**
- Definido **manualmente** pelo Gestor ou Diretor responsável
- Valor entre 0 e 100 — editável diretamente na tabela de obrigações do instrumento

### **Status Automático (editável)**
| Condição | Status Automático |
|----------|------------------|
| Data de vencimento ultrapassada | `Vencida` (prioritário) |
| Não recorrente + todas as ações finalizadas | `Cumprida` |
| Demais casos | Controlado manualmente |

> O usuário pode sobrescrever o status a qualquer momento.

---

## 🛠️ Scripts PowerShell Incluídos

| Script | Comando | Descrição |
|--------|---------|-----------|
| **Iniciar** | `.\iniciar.ps1` | Inicia o sistema completo |
| **Parar** | `.\parar.ps1` | Para todos os containers |
| **Reiniciar** | `.\reiniciar.ps1` | Reinicia o sistema |
| **Ver Logs** | `.\logs.ps1` | Exibe logs em tempo real |
| **Backup** | `.\backup.ps1` | Cria backup do banco de dados |

---

## 📁 Estrutura do Projeto

```
agems_sistema/
├── 📄 README.md
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📄 manage.py
├── 📄 requirements.txt
├── 📂 config/                    # Configurações Django
├── 📂 core/                      # App principal, views base, modelos de domínio
├── 📂 usuarios/                  # Módulo usuários e perfis
├── 📂 entidades/                 # Módulo entidades reguladas
├── 📂 instrumentos/              # Módulo instrumentos e obrigações
├── 📂 acoes/                     # Módulo ações de fiscalização
├── 📂 indicadores/               # Módulo indicadores contratuais
├── 📂 georeferencias/            # Módulo mapas e camadas KML
├── 📂 templates/                 # Templates HTML por módulo
├── 📂 static/                    # CSS, JS, imagens
└── 📂 backups/                   # Backups do banco
```

---

## 🔧 Comandos Docker Úteis

```powershell
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Parar o sistema
docker-compose down

# Reiniciar o sistema
docker-compose restart web

# Rodar validação do Django
docker-compose exec web python manage.py check
```

---

## 🐛 Solução de Problemas

### **Porta 8000 ocupada?**
- Edite `docker-compose.yml`
- Altere `"8000:8000"` para `"8001:8000"`

### **Sistema não carrega?**
```powershell
docker-compose logs -f
```

### **Erro de permissão no PowerShell?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📊 Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11 | Backend |
| Django | 5.x | Framework web |
| PostgreSQL | 15 | Banco de dados |
| Docker | Latest | Containerização |
| Bootstrap | 5 | Frontend |
| Leaflet.js | 1.9 | Mapas interativos |
| Chart.js | Latest | Gráficos no Painel |
| Gunicorn | Latest | Servidor WSGI |

---

## 💾 Backup e Restauração

```powershell
# Criar backup
.\backup.ps1

# Restaurar: substituir volume do PostgreSQL pelo backup desejado
```

---

## 🎨 Identidade Visual

- **Cor principal:** Azul `#0066B3` (Governo de MS)
- **Logo:** AGEMS oficial
- **Design:** Moderno, responsivo, com suporte a dispositivos móveis

---

## 📄 Licença

Sistema desenvolvido exclusivamente para a **AGEMS - Agência de Regulação de Serviços Públicos de Mato Grosso do Sul**.

---

**Versão:** 3.0 | **Data:** Fevereiro 2026 | **Status:** ✅ Em Produção
