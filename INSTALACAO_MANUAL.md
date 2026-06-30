# 🔧 AGEMS - Instalação Manual Passo a Passo

## Guia para Inicialização Manual do Sistema

Se o script `iniciar.ps1` não funcionar no seu ambiente, siga este guia passo a passo para iniciar o sistema manualmente.

---

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter:

1. ✅ **Windows 11** instalado
2. ✅ **Docker Desktop** instalado e **RODANDO**
3. ✅ **PowerShell** ou **CMD** disponível

---

## 📋 Passo a Passo - Comandos Manuais

### **Passo 1: Abrir Terminal**

1. Navegue até a pasta onde você extraiu o sistema
2. Clique com botão direito na pasta
3. Selecione **"Abrir no Terminal"** ou **"Open PowerShell window here"**

---

### **Passo 2: Verificar Docker**

Execute o comando:

```powershell
docker --version
```

**Resultado esperado:**
```
Docker version 24.x.x, build xxxxxxx
```

Se der erro, instale o Docker Desktop: https://www.docker.com/products/docker-desktop

---

### **Passo 3: Verificar se Docker está Rodando**

Execute:

```powershell
docker info
```

**Resultado esperado:**
- Deve mostrar informações do Docker (versão, containers, etc.)

**Se der erro:**
- Abra o Docker Desktop manualmente
- Aguarde até o ícone da baleia ficar estável na bandeja
- Tente novamente

---

### **Passo 4: Limpar Containers Antigos (Opcional)**

Execute:

```powershell
docker-compose down -v
```

**Resultado esperado:**
- Pode mostrar "no configuration file provided" se for a primeira vez (isso é normal)
- Ou mostrar que removeu containers antigos

---

### **Passo 5: Construir a Imagem Docker**

Execute:

```powershell
docker-compose build --no-cache
```

**Resultado esperado:**
- Vai baixar imagens base do Python
- Vai instalar dependências
- Pode levar 3-5 minutos na primeira vez
- Deve terminar com "Successfully built" e "Successfully tagged"

**Se der erro:**
- Verifique sua conexão com a internet
- Certifique-se de que o Docker Desktop está rodando
- Tente novamente

---

### **Passo 6: Iniciar os Containers**

Execute:

```powershell
docker-compose up -d
```

**Resultado esperado:**
```
Creating network "agems_sistema_final_agems_network" with driver "bridge"
Creating agems_web ... done
```

**O que esse comando faz:**
- Cria a rede Docker
- Inicia o container da aplicação
- Roda em segundo plano (flag `-d`)

---

### **Passo 7: Verificar se o Container está Rodando**

Execute:

```powershell
docker-compose ps
```

**Resultado esperado:**
```
Name              Command               State           Ports
------------------------------------------------------------------------
agems_web   /docker-entrypoint.sh ...   Up      0.0.0.0:8000->8000/tcp
```

**Status deve ser "Up"**

**Se o status for "Exit" ou "Restarting":**
- Veja os logs (próximo passo)

---

### **Passo 8: Ver os Logs (Se Necessário)**

Execute:

```powershell
docker-compose logs -f
```

**O que procurar:**
- Mensagens de erro em vermelho
- "System check identified no issues"
- "Listening at: http://0.0.0.0:8000"

**Para sair dos logs:**
- Pressione `Ctrl + C`

---

### **Passo 9: Aguardar Inicialização**

Aguarde **10-15 segundos** para o Django inicializar completamente.

---

### **Passo 10: Acessar o Sistema**

Abra seu navegador e acesse:

```
http://localhost:8000
```

**Credenciais:**
- **Usuário:** `admin`
- **Senha:** Defina via `DJANGO_SUPERUSER_PASSWORD` no `.env`

---

## 🎯 Comandos Úteis

### **Ver Status dos Containers**
```powershell
docker-compose ps
```

### **Ver Logs em Tempo Real**
```powershell
docker-compose logs -f
```

### **Parar o Sistema**
```powershell
docker-compose down
```

### **Reiniciar o Sistema**
```powershell
docker-compose restart
```

### **Parar e Remover Tudo (Incluindo Volumes)**
```powershell
docker-compose down -v
```

### **Reconstruir do Zero**
```powershell
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### **Limpeza de Cache (Se o layout parecer quebrado)**
Se após uma atualização as cores ou o layout não mudarem:
1. Pressione `Ctrl + F5` no seu navegador.
2. Isso forçará a limpeza do cache de CSS/JS e carregará as novas definições "Metallic Gold".

---

## 🐛 Solução de Problemas Comuns

### **Problema 1: "docker: command not found"**

**Causa:** Docker não está instalado ou não está no PATH

**Solução:**
1. Instale o Docker Desktop
2. Reinicie o computador
3. Tente novamente

---

### **Problema 2: "Cannot connect to the Docker daemon"**

**Causa:** Docker Desktop não está rodando

**Solução:**
1. Abra o Docker Desktop manualmente
2. Aguarde até inicializar completamente
3. Tente novamente

---

### **Problema 3: "port is already allocated"**

**Causa:** Porta 8000 já está em uso

**Solução 1 - Parar o que está usando a porta:**
```powershell
# Descobrir o que está usando a porta
netstat -ano | findstr :8000

# Matar o processo (substitua PID pelo número encontrado)
taskkill /PID <PID> /F
```

**Solução 2 - Usar outra porta:**
1. Edite o arquivo `docker-compose.yml`
2. Encontre a linha: `- "8000:8000"`
3. Altere para: `- "8001:8000"`
4. Salve e execute `docker-compose up -d` novamente
5. Acesse em `http://localhost:8001`

---

### **Problema 4: Container inicia mas logo para**

**Causa:** Erro na aplicação Django

**Solução:**
```powershell
# Ver os logs completos
docker-compose logs

# Ver apenas erros
docker-compose logs | Select-String "error" -CaseSensitive
```

Procure por mensagens de erro e corrija conforme indicado.

---

### **Problema 5: "No configuration file provided"**

**Causa:** Você não está na pasta correta

**Solução:**
1. Certifique-se de estar na pasta onde está o arquivo `docker-compose.yml`
2. Execute `ls` ou `dir` para verificar
3. Deve aparecer: `docker-compose.yml`, `Dockerfile`, `manage.py`, etc.

---

### **Problema 6: Página não carrega (localhost:8000 não responde)**

**Causa:** Sistema ainda está inicializando ou houve erro

**Solução:**
```powershell
# 1. Verificar se container está rodando
docker-compose ps

# 2. Ver os logs
docker-compose logs -f

# 3. Aguardar mais tempo (até 30 segundos)

# 4. Se persistir, reiniciar
docker-compose restart
```

---

## 📊 Verificação Final

Após seguir todos os passos, você deve ter:

✅ Docker Desktop rodando  
✅ Container `agems_web` com status "Up"  
✅ Sistema acessível em `http://localhost:8000`  
✅ Login funcionando com as credenciais definidas no `.env`  

---

## 🆘 Ainda com Problemas?

Se mesmo seguindo este guia você ainda tiver problemas:

1. **Copie os logs completos:**
   ```powershell
   docker-compose logs > logs.txt
   ```

2. **Verifique o arquivo `logs.txt` gerado**

3. **Procure por linhas com "ERROR", "CRITICAL" ou "Exception"**

4. **Anote a mensagem de erro exata**

---

## 📝 Comandos Resumidos (Copiar e Colar)

Para iniciar o sistema do zero:

```powershell
# 1. Limpar tudo
docker-compose down -v

# 2. Construir
docker-compose build --no-cache

# 3. Iniciar
docker-compose up -d

# 4. Ver logs
docker-compose logs -f

# 5. Aguardar 15 segundos e acessar http://localhost:8000
```

---

**Boa sorte!** 🚀

