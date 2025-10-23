# ============================================================
# AGEMS - Sistema de Gestão Regulatória
# Script de Inicialização para Windows 11
# ============================================================

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Cores
$ColorTitle = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "White"

# Função para exibir cabeçalho
function Show-Header {
    Clear-Host
    Write-Host "============================================================" -ForegroundColor $ColorTitle
    Write-Host "  AGEMS - Sistema de Gestão Regulatória" -ForegroundColor $ColorTitle
    Write-Host "  Agência de Regulação de Serviços Públicos de MS" -ForegroundColor $ColorTitle
    Write-Host "============================================================" -ForegroundColor $ColorTitle
    Write-Host ""
}

# Função para verificar Docker
function Test-Docker {
    Write-Host "Verificando Docker Desktop..." -ForegroundColor $ColorWarning
    try {
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Docker instalado: $dockerVersion" -ForegroundColor $ColorSuccess
            
            # Verificar se Docker está rodando
            $dockerInfo = docker info 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Docker Desktop está rodando" -ForegroundColor $ColorSuccess
                return $true
            } else {
                Write-Host "✗ Docker Desktop não está rodando!" -ForegroundColor $ColorError
                Write-Host "  Por favor, inicie o Docker Desktop e tente novamente." -ForegroundColor $ColorWarning
                return $false
            }
        }
    } catch {
        Write-Host "✗ Docker não está instalado!" -ForegroundColor $ColorError
        Write-Host "  Baixe em: https://www.docker.com/products/docker-desktop" -ForegroundColor $ColorWarning
        return $false
    }
}

# Função para limpar containers antigos
function Remove-OldContainers {
    Write-Host ""
    Write-Host "Verificando containers antigos..." -ForegroundColor $ColorWarning
    
    $containers = docker ps -a --filter "name=agems" --format "{{.Names}}" 2>&1
    if ($containers) {
        Write-Host "Removendo containers antigos..." -ForegroundColor $ColorWarning
        docker-compose down -v 2>&1 | Out-Null
        Write-Host "✓ Containers antigos removidos" -ForegroundColor $ColorSuccess
    } else {
        Write-Host "✓ Nenhum container antigo encontrado" -ForegroundColor $ColorSuccess
    }
}

# Função para construir e iniciar
function Start-AGEMS {
    Write-Host ""
    Write-Host "Construindo e iniciando o sistema..." -ForegroundColor $ColorWarning
    Write-Host "Isso pode levar alguns minutos na primeira vez..." -ForegroundColor $ColorInfo
    Write-Host ""
    
    # Construir imagem
    docker-compose build --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ Erro ao construir a imagem Docker!" -ForegroundColor $ColorError
        return $false
    }
    
    Write-Host ""
    Write-Host "Iniciando containers..." -ForegroundColor $ColorWarning
    
    # Iniciar containers
    docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ Erro ao iniciar containers!" -ForegroundColor $ColorError
        return $false
    }
    
    return $true
}

# Função para aguardar sistema ficar pronto
function Wait-SystemReady {
    Write-Host ""
    Write-Host "Aguardando sistema inicializar..." -ForegroundColor $ColorWarning
    
    $maxAttempts = 30
    $attempt = 0
    $ready = $false
    
    while (-not $ready -and $attempt -lt $maxAttempts) {
        $attempt++
        Start-Sleep -Seconds 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $ready = $true
            }
        } catch {
            Write-Host "." -NoNewline -ForegroundColor $ColorInfo
        }
    }
    
    Write-Host ""
    return $ready
}

# Função para exibir informações de acesso
function Show-AccessInfo {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor $ColorSuccess
    Write-Host "  Sistema iniciado com sucesso!" -ForegroundColor $ColorSuccess
    Write-Host "============================================================" -ForegroundColor $ColorSuccess
    Write-Host ""
    Write-Host "Acesse o sistema em:" -ForegroundColor $ColorTitle
    Write-Host "  http://localhost:8000" -ForegroundColor $ColorInfo
    Write-Host ""
    Write-Host "Credenciais de acesso:" -ForegroundColor $ColorTitle
    Write-Host "  Usuário: admin" -ForegroundColor $ColorInfo
    Write-Host "  Senha:   admin123" -ForegroundColor $ColorInfo
    Write-Host ""
    Write-Host "Comandos úteis:" -ForegroundColor $ColorTitle
    Write-Host "  Parar sistema:     docker-compose down" -ForegroundColor $ColorInfo
    Write-Host "  Ver logs:          docker-compose logs -f" -ForegroundColor $ColorInfo
    Write-Host "  Reiniciar:         docker-compose restart" -ForegroundColor $ColorInfo
    Write-Host "  Status:            docker-compose ps" -ForegroundColor $ColorInfo
    Write-Host ""
}

# Função para abrir navegador
function Open-Browser {
    Write-Host "Abrindo navegador..." -ForegroundColor $ColorWarning
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
}

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

Show-Header

# Verificar Docker
if (-not (Test-Docker)) {
    Write-Host ""
    Write-Host "Pressione qualquer tecla para sair..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Limpar containers antigos
Remove-OldContainers

# Iniciar sistema
if (-not (Start-AGEMS)) {
    Write-Host ""
    Write-Host "Para ver os logs de erro, execute:" -ForegroundColor $ColorWarning
    Write-Host "  docker-compose logs" -ForegroundColor $ColorInfo
    Write-Host ""
    Write-Host "Pressione qualquer tecla para sair..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Aguardar sistema ficar pronto
if (Wait-SystemReady) {
    Show-AccessInfo
    Open-Browser
} else {
    Write-Host ""
    Write-Host "✗ Sistema não respondeu no tempo esperado" -ForegroundColor $ColorError
    Write-Host "  Verifique os logs com: docker-compose logs -f" -ForegroundColor $ColorWarning
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

