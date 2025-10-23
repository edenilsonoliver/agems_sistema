# 🚀 AGEMS - Sistema de Gestão Regulatória

**Versão 2.1 - Outubro 2025**

Sistema completo de gestão de instrumentos regulatórios, obrigações, entidades e ações para a **AGEMS - Agência de Regulação de Serviços Públicos de Mato Grosso do Sul**.

---

## 📦 Instalação Rápida

### **Opção 1: Script Automatizado (Recomendado)**

1. Extraia o arquivo ZIP
2. Abra PowerShell na pasta
3. Execute: `.\iniciar.ps1`
4. Aguarde e acesse: `http://localhost:8000`

### **Opção 2: Manual (Se o script não funcionar)**

Siga o guia detalhado em: **`INSTALACAO_MANUAL.md`**

---

## 🔑 Credenciais de Acesso

- **URL:** http://localhost:8000
- **Usuário:** `admin`
- **Senha:** `admin123`

---

## 📋 Pré-requisitos

- ✅ Windows 11
- ✅ Docker Desktop ([Download](https://www.docker.com/products/docker-desktop))
- ✅ PowerShell (já vem no Windows)

---

## 🎯 Módulos Implementados

### **9 Módulos Completos**

1. **Usuários** - Gestão com perfis (Administrador, Gestor, Analista, Consulta)
2. **Entidades** - Concessionárias e órgãos públicos com logo
3. **Instrumentos** - Contratos, convênios, acordos com NUP (E-MS)
4. **Obrigações** - Vinculadas aos instrumentos (gerenciadas inline)
5. **Ações** - Fiscalizações, análises, projetos, averiguações
6. **Indicadores** - Metas, valores ideais e conformidade
7. **Alertas** - Sistema de notificações
8. **Documentos** - Upload múltiplo de arquivos
9. **Dashboards** - Visão executiva com estatísticas

### **Recursos Especiais**

- ✨ Sistema de abas (Dados Gerais, Obrigações, Arquivos)
- ✨ CRUD inline de tipos (criar/editar sem sair da tela)
- ✨ Upload múltiplo de arquivos por instrumento
- ✨ Busca e filtros em todas as listagens
- ✨ Badges coloridos para status
- ✨ Interface responsiva (mobile-friendly)
- ✨ Identidade visual AGEMS (azul #0066B3)
- ✨ Logo institucional integrado

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
agems_sistema_final/
├── 📄 README.md                  # Este arquivo
├── 📄 INSTALACAO_MANUAL.md       # Guia passo a passo manual
├── 📄 iniciar.ps1                # ⭐ Script de inicialização
├── 📄 parar.ps1                  # Parar sistema
├── 📄 reiniciar.ps1              # Reiniciar sistema
├── 📄 logs.ps1                   # Ver logs
├── 📄 backup.ps1                 # Fazer backup
├── 📄 docker-compose.yml         # Configuração Docker
├── 📄 Dockerfile                 # Imagem Docker
├── 📄 db.sqlite3                 # ⭐ Banco de dados
├── 📄 manage.py                  # Django CLI
├── 📄 requirements.txt           # Dependências Python
├── 📂 config/                    # Configurações Django
├── 📂 usuarios/                  # Módulo usuários
├── 📂 entidades/                 # Módulo entidades
├── 📂 instrumentos/              # Módulo instrumentos
├── 📂 acoes/                     # Módulo ações
├── 📂 indicadores/               # Módulo indicadores
├── 📂 alertas/                   # Módulo alertas
├── 📂 documentos/                # Módulo documentos
├── 📂 dashboards/                # Módulo dashboards
├── 📂 fiscalizacao/              # Módulo fiscalização
├── 📂 core/                      # App principal
├── 📂 templates/                 # Templates HTML
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
docker-compose restart

# Reconstruir do zero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 🐛 Solução de Problemas

### **Script iniciar.ps1 não funciona?**
- Consulte o arquivo **`INSTALACAO_MANUAL.md`** para comandos passo a passo

### **Erro de permissão no PowerShell?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Docker não está rodando?**
- Abra o Docker Desktop manualmente
- Aguarde até o ícone ficar estável
- Tente novamente

### **Porta 8000 ocupada?**
- Edite `docker-compose.yml`
- Altere `"8000:8000"` para `"8001:8000"`
- Acesse em `http://localhost:8001`

### **Sistema não carrega?**
```powershell
# Ver logs para identificar erro
.\logs.ps1

# Ou manualmente
docker-compose logs -f
```

---

## 🎨 Identidade Visual

O sistema utiliza a identidade visual oficial da AGEMS:

- **Cor principal:** Azul #0066B3 (Governo de MS)
- **Logo:** AGEMS oficial
- **Design:** Moderno, limpo e responsivo

---

## 💾 Backup e Restauração

### **Criar Backup**
```powershell
.\backup.ps1
```
Os backups são salvos em `backups/` com data e hora.

### **Restaurar Backup**
1. Pare o sistema: `.\parar.ps1`
2. Substitua `db.sqlite3` pelo backup desejado
3. Inicie: `.\iniciar.ps1`

---

## 🔐 Segurança

⚠️ **IMPORTANTE:**
- As credenciais padrão (`admin/admin123`) são para desenvolvimento local
- Para produção, altere imediatamente a senha do administrador
- Configure variáveis de ambiente adequadas

---

## 📊 Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11 | Backend |
| Django | 5.2 | Framework web |
| SQLite | 3 | Banco de dados |
| Docker | Latest | Containerização |
| Bootstrap | 5 | Frontend |
| Gunicorn | Latest | Servidor WSGI |

---

## ✅ Correções Implementadas (14/14)

### **ENTIDADES**
- ✅ CRUD inline de tipos de entidade
- ✅ CRUD inline de tipos de serviço
- ✅ Upload de logo da entidade
- ✅ Campo "Diretoria Responsável"

### **INSTRUMENTOS**
- ✅ Sistema de abas (Dados Gerais, Obrigações, Arquivos)
- ✅ CRUD inline de tipos de instrumento
- ✅ Campo NUP (E-MS)
- ✅ Upload múltiplo de arquivos
- ✅ Redirecionamento para edição após salvar

### **OBRIGAÇÕES**
- ✅ Formset inline (salvar junto com instrumento)
- ✅ Campo "Instrumento" oculto no formulário
- ✅ Menu "Obrigações" removido da sidebar
- ✅ CRUD inline de tipos de obrigação

### **IDENTIDADE VISUAL**
- ✅ Cores AGEMS (#0066B3)
- ✅ Logo institucional

---

## 📞 Suporte

Para problemas técnicos:

1. Consulte **`INSTALACAO_MANUAL.md`**
2. Execute `.\logs.ps1` para ver erros
3. Verifique se Docker Desktop está rodando
4. Tente reiniciar com `.\reiniciar.ps1`

---

## 📄 Licença

Sistema desenvolvido exclusivamente para a **AGEMS - Agência de Regulação de Serviços Públicos de Mato Grosso do Sul**.

---

**Desenvolvido com dedicação para a AGEMS** ❤️  
**Versão:** 2.1  
**Data:** Outubro 2025  
**Status:** ✅ PRONTO PARA USO

