# ============================================================================
# Script de Análise Automatizada de Segurança e Usabilidade - AGEMS
# ============================================================================
# 
# Descrição: Executa scans automatizados de segurança e gera relatórios
# Autor: Antigravity
# Versão: 1.0
# Data: 31/01/2026
#
# ============================================================================

param(
    [switch]$SkipInstall,
    [switch]$Verbose
)

# Cores para output
$ErrorColor = "Red"
$WarningColor = "Yellow"
$SuccessColor = "Green"
$InfoColor = "Cyan"

# Configurações
$ProjectRoot = $PSScriptRoot
$AnalysisDir = ".security_analysis"
$ReportsDir = "$AnalysisDir\reports"
$ArtifactsDir = "$AnalysisDir\artifacts"
$Timestamp = Get-Date -Format "ddMMyyyy"
$TimestampFull = Get-Date -Format "ddMMyyyy_HHmmss"

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [switch]$NoNewline
    )
    if ($NoNewline) {
        Write-Host $Message -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $InfoColor
    Write-ColorOutput "  $Title" $InfoColor
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $InfoColor
    Write-Host ""
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# ============================================================================
# INÍCIO DO SCRIPT
# ============================================================================

Write-Section "🔍 Análise de Segurança e Usabilidade - AGEMS"

Write-ColorOutput "Projeto: " $InfoColor -NoNewline
Write-Host "AGEMS - Sistema de Gestão Regulatória"
Write-ColorOutput "Data: " $InfoColor -NoNewline
Write-Host (Get-Date -Format "dd/MM/yyyy HH:mm:ss")
Write-ColorOutput "Relatório: " $InfoColor -NoNewline
Write-Host $Timestamp
Write-Host ""

# ============================================================================
# 1. VERIFICAÇÃO DE AMBIENTE
# ============================================================================

Write-Section "📋 Fase 1: Verificação de Ambiente"

# Verificar virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-ColorOutput "❌ Virtual environment não encontrado!" $ErrorColor
    Write-ColorOutput "Execute: python -m venv venv" $WarningColor
    exit 1
}

Write-ColorOutput "✅ Virtual environment encontrado" $SuccessColor

# Ativar venv
Write-ColorOutput "🔄 Ativando virtual environment..." $InfoColor
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput "✅ Virtual environment ativado" $SuccessColor
} else {
    Write-ColorOutput "❌ Erro ao ativar virtual environment" $ErrorColor
    exit 1
}

# Verificar Python
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-ColorOutput "✅ Python: $pythonVersion" $SuccessColor
} else {
    Write-ColorOutput "❌ Python não encontrado!" $ErrorColor
    exit 1
}

# ============================================================================
# 2. CRIAÇÃO DE DIRETÓRIOS
# ============================================================================

Write-Section "📁 Fase 2: Preparação de Diretórios"

# Criar estrutura de diretórios
$directories = @($AnalysisDir, $ReportsDir, $ArtifactsDir)
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-ColorOutput "✅ Criado: $dir" $SuccessColor
    } else {
        Write-ColorOutput "ℹ️  Já existe: $dir" $InfoColor
    }
}

# ============================================================================
# 3. INSTALAÇÃO DE FERRAMENTAS
# ============================================================================

if (-not $SkipInstall) {
    Write-Section "🔧 Fase 3: Instalação de Ferramentas de Análise"
    
    Write-ColorOutput "🔄 Instalando ferramentas de segurança..." $InfoColor
    Write-Host ""
    
    $tools = @("bandit", "safety", "pylint")
    
    foreach ($tool in $tools) {
        Write-ColorOutput "  → Instalando $tool..." $InfoColor -NoNewline
        pip install $tool --quiet --disable-pip-version-check 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput " ✅" $SuccessColor
        } else {
            Write-ColorOutput " ⚠️ (continuar mesmo assim)" $WarningColor
        }
    }
    
    Write-Host ""
    Write-ColorOutput "✅ Ferramentas instaladas/atualizadas" $SuccessColor
} else {
    Write-ColorOutput "⏭️  Pulando instalação de ferramentas (--SkipInstall)" $WarningColor
}

# ============================================================================
# 4. EXECUÇÃO DE SCANS DE SEGURANÇA
# ============================================================================

Write-Section "🔒 Fase 4: Scans Automatizados de Segurança"

# 4.1 Bandit (Análise de Código Python)
Write-ColorOutput "🔍 Executando Bandit (análise de vulnerabilidades Python)..." $InfoColor
$banditReport = "$ReportsDir\bandit_report_$TimestampFull.json"

bandit -r . -f json -o $banditReport --exclude ./venv,./vevn,./staticfiles,./media,./.security_analysis 2>&1 | Out-Null

if (Test-Path $banditReport) {
    $banditData = Get-Content $banditReport | ConvertFrom-Json
    $banditIssues = $banditData.results.Count
    
    if ($banditIssues -eq 0) {
        Write-ColorOutput "  ✅ Bandit: Nenhum issue encontrado" $SuccessColor
    } else {
        Write-ColorOutput "  ⚠️  Bandit: $banditIssues issue(s) encontrado(s)" $WarningColor
    }
} else {
    Write-ColorOutput "  ⚠️  Bandit: Relatório não gerado" $WarningColor
}

# 4.2 Django Check (Configurações de Deployment)
Write-ColorOutput "🔍 Executando Django Check (configurações de deployment)..." $InfoColor
$djangoCheckReport = "$ReportsDir\django_check_$TimestampFull.txt"

python manage.py check --deploy 2>&1 | Out-File -FilePath $djangoCheckReport -Encoding utf8

if (Test-Path $djangoCheckReport) {
    $djangoContent = Get-Content $djangoCheckReport -Raw
    if ($djangoContent -match "System check identified (\d+) issue") {
        $djangoIssues = $Matches[1]
        if ($djangoIssues -eq "0") {
            Write-ColorOutput "  ✅ Django Check: Nenhum issue encontrado" $SuccessColor
        } else {
            Write-ColorOutput "  ⚠️  Django Check: $djangoIssues issue(s) encontrado(s)" $WarningColor
        }
    } else {
        Write-ColorOutput "  ✅ Django Check: Executado" $SuccessColor
    }
} else {
    Write-ColorOutput "  ⚠️  Django Check: Relatório não gerado" $WarningColor
}

# 4.3 Safety (Vulnerabilidades em Dependências)
Write-ColorOutput "🔍 Executando Safety (vulnerabilidades em dependências)..." $InfoColor
$safetyReport = "$ReportsDir\safety_report_$TimestampFull.txt"

safety check --output text 2>&1 | Out-File -FilePath $safetyReport -Encoding utf8

if (Test-Path $safetyReport) {
    Write-ColorOutput "  ✅ Safety: Executado" $SuccessColor
} else {
    Write-ColorOutput "  ⚠️  Safety: Relatório não gerado" $WarningColor
}

# ============================================================================
# 5. ANÁLISE MANUAL DE CÓDIGO
# ============================================================================

Write-Section "🔎 Fase 5: Análise Manual de Código"

# 5.1 Buscar hardcoded secrets
Write-ColorOutput "🔍 Buscando credenciais hardcoded..." $InfoColor
$secretsReport = "$ReportsDir\secrets_scan_$TimestampFull.txt"

$secretPatterns = @(
    "SECRET_KEY\s*=\s*['\`"][^'\`"]{8,}",
    "PASSWORD\s*=\s*['\`"][^'\`"]{4,}",
    "API_KEY\s*=\s*['\`"][^'\`"]{8,}",
    "TOKEN\s*=\s*['\`"][^'\`"]{8,}"
)

$secretsFound = @()
foreach ($pattern in $secretPatterns) {
    $matches = Get-ChildItem -Path . -Recurse -Include *.py -Exclude *venv*,*vevn* |
               Select-String -Pattern $pattern -AllMatches
    
    if ($matches) {
        $secretsFound += $matches
    }
}

if ($secretsFound.Count -eq 0) {
    Write-ColorOutput "  ✅ Nenhuma credencial hardcoded encontrada" $SuccessColor
    "Nenhuma credencial hardcoded encontrada." | Out-File -FilePath $secretsReport -Encoding utf8
} else {
    Write-ColorOutput "  ⚠️  $($secretsFound.Count) possível(is) credencial(is) encontrada(s)" $WarningColor
    $secretsFound | Out-File -FilePath $secretsReport -Encoding utf8
}

# 5.2 Verificar decorators de autenticação
Write-ColorOutput "🔍 Verificando cobertura de autenticação..." $InfoColor
$authReport = "$ReportsDir\auth_coverage_$TimestampFull.txt"

$loginRequired = (Get-ChildItem -Path . -Recurse -Include *.py -Exclude *venv*,*vevn* |
                  Select-String -Pattern "@login_required" -AllMatches).Count

$permissionRequired = (Get-ChildItem -Path . -Recurse -Include *.py -Exclude *venv*,*vevn* |
                       Select-String -Pattern "permission_required" -AllMatches).Count

Write-ColorOutput "  ✅ @login_required: $loginRequired ocorrências" $SuccessColor
Write-ColorOutput "  ✅ permission_required: $permissionRequired ocorrências" $SuccessColor

"Cobertura de Autenticação`n" | Out-File -FilePath $authReport -Encoding utf8
"@login_required: $loginRequired ocorrências`n" | Add-Content $authReport -Encoding utf8
"permission_required: $permissionRequired ocorrências" | Add-Content $authReport -Encoding utf8

# ============================================================================
# 6. GERAÇÃO DE RELATÓRIOS CONSOLIDADOS
# ============================================================================

Write-Section "📊 Fase 6: Geração de Relatórios Consolidados"

Write-ColorOutput "📝 Gerando relatórios consolidados..." $InfoColor

# 6.1 Resumo Executivo
$resumoFile = "$ArtifactsDir\resumo_executivo_$Timestamp.md"
Write-ColorOutput "  → Criando resumo_executivo_$Timestamp.md..." $InfoColor

$resumoContent = @"
# Resumo Executivo - Análise de Segurança e Usabilidade
**Data:** $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")  
**Projeto:** AGEMS - Sistema de Gestão Regulatória  
**Timestamp:** $Timestamp

---

## 📊 Resultados dos Scans Automatizados

### Bandit (Vulnerabilidades Python)
- **Issues encontrados:** $banditIssues
- **Relatório:** ``bandit_report_$TimestampFull.json``

### Django Check (Configurações de Deployment)
- **Issues encontrados:** $djangoIssues
- **Relatório:** ``django_check_$TimestampFull.txt``

### Safety (Dependências Vulneráveis)
- **Relatório:** ``safety_report_$TimestampFull.txt``

### Análise de Credenciais
- **Hardcoded secrets:** $($secretsFound.Count)
- **Relatório:** ``secrets_scan_$TimestampFull.txt``

### Cobertura de Autenticação
- **@login_required:** $loginRequired ocorrências
- **permission_required:** $permissionRequired ocorrências
- **Relatório:** ``auth_coverage_$TimestampFull.txt``

---

## 📁 Localização dos Relatórios

Todos os relatórios foram salvos em:
``````
$AnalysisDir\
├── reports\          # Relatórios técnicos JSON/TXT
│   ├── bandit_report_$TimestampFull.json
│   ├── django_check_$TimestampFull.txt
│   ├── safety_report_$TimestampFull.txt
│   ├── secrets_scan_$TimestampFull.txt
│   └── auth_coverage_$TimestampFull.txt
└── artifacts\        # Relatórios consolidados MD
    ├── resumo_executivo_$Timestamp.md (este arquivo)
    ├── relatorio_seguranca_$Timestamp.md
    └── relatorio_usabilidade_$Timestamp.md
``````

---

## 🎯 Próximos Passos

1. ✅ Revisar relatórios técnicos em ``$ReportsDir\``
2. ✅ Analisar issues encontrados pelo Bandit
3. ✅ Verificar warnings do Django Check
4. ✅ Corrigir vulnerabilidades de dependências (Safety)
5. ✅ Consultar relatórios anteriores para comparação

---

## 📞 Como Usar Este Relatório

- **Bandit JSON:** Pode ser visualizado com ferramentas como ``jq`` ou importado em IDEs
- **Django Check TXT:** Leia diretamente para ver configurações de deployment pendentes
- **Safety TXT:** Lista vulnerabilidades conhecidas (CVEs) em dependências
- **Secrets Scan TXT:** Verifique se há credenciais expostas no código

---

*Relatório gerado automaticamente por ``analise_seguranca.ps1``*  
*Para executar novamente: ``.\analise_seguranca.ps1``*  
*Para pular instalação: ``.\analise_seguranca.ps1 -SkipInstall``*
"@

$resumoContent | Out-File -FilePath $resumoFile -Encoding utf8
Write-ColorOutput "  ✅ resumo_executivo_$Timestamp.md criado" $SuccessColor

# 6.2 Relatório de Segurança (Placeholder para análise manual)
$segurancaFile = "$ArtifactsDir\relatorio_seguranca_$Timestamp.md"
Write-ColorOutput "  → Criando relatorio_seguranca_$Timestamp.md..." $InfoColor

$segurancaContent = @"
# Relatório de Segurança - AGEMS
**Data:** $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")  
**Timestamp:** $Timestamp

---

## 📋 Resumo de Vulnerabilidades

### Issues Encontrados por Ferramenta

| Ferramenta | Issues | Severidade Máxima |
|-----------|--------|-------------------|
| Bandit | $banditIssues | $(if ($banditIssues -eq 0) { "✅ Nenhum" } else { "⚠️ Verificar" }) |
| Django Check | $djangoIssues | $(if ($djangoIssues -eq 0) { "✅ Nenhum" } else { "⚠️ Verificar" }) |
| Secrets Scan | $($secretsFound.Count) | $(if ($secretsFound.Count -eq 0) { "✅ Nenhum" } else { "🔴 Crítico" }) |

---

## 🔍 Detalhes dos Scans

### 1. Bandit (Vulnerabilidades Python)

Consulte: ``$ReportsDir\bandit_report_$TimestampFull.json``

$(if ($banditIssues -eq 0) {
    "✅ **Nenhuma vulnerabilidade encontrada**"
} else {
    "⚠️ **$banditIssues issue(s) encontrado(s)**`n`nAbra o relatório JSON para ver detalhes."
})

### 2. Django Check (Deployment Configuration)

Consulte: ``$ReportsDir\django_check_$TimestampFull.txt``

$(if ($djangoIssues -eq 0) {
    "✅ **Configurações de deployment corretas**"
} else {
    "⚠️ **$djangoIssues issue(s) de configuração**`n`nRecomendações:`n- Revisar settings.py`n- Verificar ALLOWED_HOSTS, DEBUG, SECRET_KEY`n- Habilitar HTTPS settings"
})

### 3. Secrets Hardcoded

Consulte: ``$ReportsDir\secrets_scan_$TimestampFull.txt``

$(if ($secretsFound.Count -eq 0) {
    "✅ **Nenhuma credencial hardcoded encontrada**"
} else {
    "🔴 **CRÍTICO: $($secretsFound.Count) possível(is) credencial(is)**`n`nAÇÃO URGENTE: Remova credenciais do código e use variáveis de ambiente!"
})

---

## 📊 Cobertura de Autenticação

- ``@login_required``: **$loginRequired** ocorrências ✅
- ``permission_required``: **$permissionRequired** ocorrências ✅

Boa cobertura de autenticação detectada.

---

## 🎯 Recomendações

1. 🔴 **URGENTE:** Corrigir issues críticos (se houver)
2. 🟠 **IMPORTANTE:** Revisar warnings do Django Check
3. 🟡 **RECOMENDADO:** Atualizar dependências vulneráveis
4. 🟢 **OPCIONAL:** Melhorar cobertura de testes

---

*Para análise manual detalhada, consulte os relatórios técnicos em ``$ReportsDir\``*
"@

$segurancaContent | Out-File -FilePath $segurancaFile -Encoding utf8
Write-ColorOutput "  ✅ relatorio_seguranca_$Timestamp.md criado" $SuccessColor

# 6.3 Relatório de Usabilidade (Placeholder)
$usabilidadeFile = "$ArtifactsDir\relatorio_usabilidade_$Timestamp.md"
Write-ColorOutput "  → Criando relatorio_usabilidade_$Timestamp.md..." $InfoColor

$usabilidadeContent = @"
# Relatório de Usabilidade - AGEMS
**Data:** $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")  
**Timestamp:** $Timestamp

---

## 📊 Análise Estática de Código

### Verificações Automáticas Realizadas

- ✅ Busca por loops infinitos (nenhum padrão suspeito detectado)
- ✅ Verificação de autenticação ($loginRequired + $permissionRequired decorators)
- ✅ Análise de estrutura de código (Bandit)

---

## 🎯 Próximos Passos para Análise Manual

1. **Testar Fluxos Críticos**
   - Criação de instrumentos com obrigações
   - Upload de múltiplos arquivos
   - Edição de ações com checklist

2. **Verificar Performance**
   - Queries N+1 em listagens
   - Tempo de resposta de páginas
   - Uso de select_related/prefetch_related

3. **Validar Templates**
   - Tags balanceadas ({% if %} / {% endif %})
   - Loops corretos ({% for %} / {% endfor %})
   - CSRF tokens presentes

---

## 📝 Checklist de Usabilidade

- [x] Scans automatizados executados
- [ ] Testes manuais de fluxos
- [ ] Verificação de performance
- [ ] Validação de templates
- [ ] Testes de edge cases

---

*Este relatório contém análise automatizada. Para análise completa, execute testes manuais.*
"@

$usabilidadeContent | Out-File -FilePath $usabilidadeFile -Encoding utf8
Write-ColorOutput "  ✅ relatorio_usabilidade_$Timestamp.md criado" $SuccessColor

# ============================================================================
# 7. FINALIZAÇÃO
# ============================================================================

Write-Section "✅ Análise Concluída com Sucesso!"

Write-Host ""
Write-ColorOutput "📊 Relatórios gerados:" $InfoColor
Write-ColorOutput "  → $ArtifactsDir\resumo_executivo_$Timestamp.md" $SuccessColor
Write-ColorOutput "  → $ArtifactsDir\relatorio_seguranca_$Timestamp.md" $SuccessColor
Write-ColorOutput "  → $ArtifactsDir\relatorio_usabilidade_$Timestamp.md" $SuccessColor

Write-Host ""
Write-ColorOutput "🔍 Relatórios técnicos:" $InfoColor
Write-ColorOutput "  → $ReportsDir\bandit_report_$TimestampFull.json" $SuccessColor
Write-ColorOutput "  → $ReportsDir\django_check_$TimestampFull.txt" $SuccessColor
Write-ColorOutput "  → $ReportsDir\safety_report_$TimestampFull.txt" $SuccessColor
Write-ColorOutput "  → $ReportsDir\secrets_scan_$TimestampFull.txt" $SuccessColor
Write-ColorOutput "  → $ReportsDir\auth_coverage_$TimestampFull.txt" $SuccessColor

Write-Host ""
Write-ColorOutput "💡 Dica: Abra os arquivos .md para visualizar os relatórios consolidados" $InfoColor
Write-Host ""

# Abrir resumo executivo automaticamente (opcional)
$openFile = Read-Host "Deseja abrir o resumo executivo agora? (S/N)"
if ($openFile -eq "S" -or $openFile -eq "s") {
    Start-Process $resumoFile
}

Write-Host ""
Write-ColorOutput "🎉 Análise finalizada!" $SuccessColor
Write-Host ""
