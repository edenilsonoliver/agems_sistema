# ==============================================================================
# run_tests.ps1 — Executa os testes funcionais pré-produção do AGEMS
# ==============================================================================
# Uso: .\run_tests.ps1
# Descrição: Ativa o virtualenv, executa django check e roda toda a suite
#            de testes funcionais (acoes, instrumentos, entidades, usuarios, core).
# ==============================================================================

param(
    [string]$App = "",
    [switch]$Quick
)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🧪 AGEMS — Testes Funcionais Pre-Producao" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Caminho do projeto ---
$ProjectDir = $PSScriptRoot

# --- Ativa o virtualenv ---
$VenvScript = Join-Path $ProjectDir "venv\Scripts\Activate.ps1"
if (Test-Path $VenvScript) {
    Write-Host "[1/3] Ativando virtualenv..." -ForegroundColor Yellow
    & $VenvScript
} else {
    Write-Host "[AVISO] virtualenv nao encontrado em .\venv. Usando Python do sistema." -ForegroundColor DarkYellow
}

# --- Navegação para a pasta do projeto ---
Set-Location $ProjectDir

# --- Etapa 1: Verificação de integridade do Django ---
Write-Host ""
Write-Host "[2/3] Executando django check (verificacao de integridade)..." -ForegroundColor Yellow
python manage.py check
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: django check retornou falhas. Corrija antes de prosseguir." -ForegroundColor Red
    exit 1
}
Write-Host "[ OK ] django check passou sem errors." -ForegroundColor Green

# --- Etapa 2: Executa a suite de testes ---
Write-Host ""
Write-Host "[3/3] Executando suite de testes funcionais..." -ForegroundColor Yellow
Write-Host ""

if ($App -ne "") {
    # Executa apenas um app especifico
    Write-Host "Modo: App especifico → $App" -ForegroundColor Cyan
    $TestArgs = @($App, "--verbosity=2")
} elseif ($Quick) {
    # Modo rapido: apenas testes de modelo (sem views HTTP)
    Write-Host "Modo: Quick (modelos apenas)" -ForegroundColor Cyan
    $TestArgs = @("acoes.tests", "instrumentos.tests", "entidades.tests", "usuarios.tests", "--verbosity=1")
} else {
    # Suite completa
    Write-Host "Modo: Suite completa" -ForegroundColor Cyan
    $TestArgs = @("acoes", "instrumentos", "entidades", "usuarios", "core", "--verbosity=2", "--keepdb")
}

python manage.py test @TestArgs

$ExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($ExitCode -eq 0) {
    Write-Host "   RESULTADO: TODOS OS TESTES PASSARAM " -ForegroundColor Green
    Write-Host "   Sistema aprovado para deploy em producao!" -ForegroundColor Green
} else {
    Write-Host "   RESULTADO: FALHAS DETECTADAS " -ForegroundColor Red
    Write-Host "   Corrija os erros antes de subir em producao!" -ForegroundColor Red
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

exit $ExitCode
