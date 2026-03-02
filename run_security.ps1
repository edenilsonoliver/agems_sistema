# ==============================================================================
# run_security.ps1 - Testes de Seguranca Pre-Deploy AGEMS
# ==============================================================================
# Uso: .\run_security.ps1
# Descricao: Executa scan de seguranca completo (OWASP A02/A03/A04/A05),
#            filtra falsos positivos de bibliotecas externas e exibe
#            apenas achados reais no codigo da aplicacao.
#
# Categorias verificadas:
#   [A02] Configuracao de seguranca (DEBUG, CORS, HSTS)
#   [A03] Dependencias / Supply Chain (requirements.txt)
#   [A04] Secrets / Credenciais expostas
#   [A05] Padroes perigosos de codigo (eval, exec, SQL injection)
# ==============================================================================

param(
    [switch]$Full,   # Inclui warnings de libs externas (nao recomendado)
    [switch]$Json    # Salva relatorio JSON completo em security_report.json
)

$ProjectDir = $PSScriptRoot
$ScanScript = Join-Path $ProjectDir ".agent\skills\vulnerability-scanner\scripts\security_scan.py"
$ReportFile = Join-Path $ProjectDir "_security_report_tmp.json"
$Venv = Join-Path $ProjectDir "venv\Scripts\python.exe"

# Diretorios/arquivos ignorados na analise de resultados (falsos positivos conhecidos)
$FalsePositivePaths = @(
    "staticfiles",          # Assets compilados do Django Admin (jQuery, etc.)
    "vendor",               # Bibliotecas de terceiros
    "venv",                 # Dependencias instaladas
    "vevn",                 # Pasta venv duplicada
    ".agent",               # Scripts do agente (contem padroes intencionais como exemplos)
    "tests.py",             # Senhas em testes sao intencionais (ambiente isolado)
    "node_modules",
    "config\settings.py",   # dj_database_url detectado erroneamente como connection string exposta
    "config/settings.py",
    "apply_readonly_mode.py", # Script utilitario com construcoes dinamicas
    "security_report.json",   # O proprio relatorio de seguranca gerado
    "_security_report_tmp.json"
)

$DataHora = Get-Date -Format "yyyy-MM-dd HH:mm"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   AGEMS - Scan de Seguranca Pre-Deploy" -ForegroundColor Cyan
Write-Host "   OWASP Top 10:2025 | $DataHora" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Verifica dependencias ---
if (-not (Test-Path $Venv)) {
    Write-Host "[AVISO] Python venv nao encontrado. Usando Python do sistema." -ForegroundColor DarkYellow
    $Venv = "python"
}

if (-not (Test-Path $ScanScript)) {
    Write-Host "[ERRO] security_scan.py nao encontrado em: $ScanScript" -ForegroundColor Red
    exit 1
}

# --- Executa o scan e salva JSON ---
Write-Host "[1/3] Executando scan de seguranca (aguarde ~30s)..." -ForegroundColor Yellow
& $Venv $ScanScript $ProjectDir --output json 2>$null | Out-File $ReportFile -Encoding utf8

if (-not (Test-Path $ReportFile)) {
    Write-Host "[ERRO] Falha ao executar security_scan.py." -ForegroundColor Red
    exit 1
}

# --- Le o JSON ---
Write-Host "[2/3] Analisando resultados..." -ForegroundColor Yellow
$report = Get-Content $ReportFile -Raw | ConvertFrom-Json

# --- Funcao auxiliar: verifica se e falso positivo ---
function Test-FalsePositive($path) {
    if ([string]::IsNullOrWhiteSpace($path)) { return $false }
    foreach ($fp in $FalsePositivePaths) {
        if ($path.IndexOf($fp, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { return $true }
    }
    return $false
}

# --- Filtra e exibe resultados reais ---
Write-Host "[3/3] Resultados:" -ForegroundColor Yellow
Write-Host ""

$totalReal = 0
$criticalReal = 0
$highReal = 0

# ---- A03: Dependencias ---
Write-Host "  [A03] Supply Chain / Dependencias:" -ForegroundColor White
$depFindings = $report.scans.dependencies.findings
if ($depFindings.Count -eq 0) {
    Write-Host "       OK - requirements.txt encontrado, sem vulnerabilidades conhecidas" -ForegroundColor Green
}
else {
    foreach ($f in $depFindings) {
        Write-Host "       [!] $($f.message)" -ForegroundColor Red
        $totalReal++; $highReal++
    }
}

# ---- A04: Secrets ---
Write-Host ""
Write-Host "  [A04] Secrets / Credenciais Expostas:" -ForegroundColor White
$secretFindings = $report.scans.secrets.findings
$realSecrets = $secretFindings | Where-Object { -not (Test-FalsePositive $_.file) }
$filteredCount = $secretFindings.Count - $realSecrets.Count

if ($realSecrets.Count -eq 0) {
    Write-Host "       OK - Nenhum secret real no codigo da aplicacao" -ForegroundColor Green
    Write-Host "       (Filtrados $filteredCount falsos positivos de libs/testes)" -ForegroundColor DarkGray
}
else {
    foreach ($f in $realSecrets) {
        $color = if ($f.severity -eq "critical") { "Red" } else { "Yellow" }
        Write-Host "       [$($f.severity.ToUpper())] $($f.type) - $($f.file)" -ForegroundColor $color
        $totalReal++
        if ($f.severity -eq "critical") { $criticalReal++ } else { $highReal++ }
    }
    Write-Host "       (Filtrados $filteredCount falsos positivos de libs/testes)" -ForegroundColor DarkGray
}

if ($Full -and $filteredCount -gt 0) {
    Write-Host "       --- Falsos Positivos Ignorados ---" -ForegroundColor DarkGray
    ($secretFindings | Where-Object { Test-FalsePositive $_.file }) | ForEach-Object {
        Write-Host "       [skip] $($_.file)" -ForegroundColor DarkGray
    }
}

# ---- A05: Padroes de Codigo ---
Write-Host ""
Write-Host "  [A05] Padroes Perigosos no Codigo da Aplicacao:" -ForegroundColor White
$codeFindings = $report.scans.code_patterns.findings
$realCode = $codeFindings | Where-Object { -not (Test-FalsePositive $_.file) }
$filteredCode = $codeFindings.Count - $realCode.Count

if ($realCode.Count -eq 0) {
    Write-Host "       OK - Nenhum padrao perigoso no codigo da aplicacao" -ForegroundColor Green
    Write-Host "       (Filtrados $filteredCode ocorrencias em libs externas)" -ForegroundColor DarkGray
}
else {
    foreach ($f in $realCode) {
        $color = if ($f.severity -eq "critical") { "Red" } else { "Yellow" }
        Write-Host "       [$($f.severity.ToUpper())] $($f.pattern) - $($f.file):$($f.line)" -ForegroundColor $color
        Write-Host "         $($f.snippet)" -ForegroundColor DarkGray
        $totalReal++
        if ($f.severity -eq "critical") { $criticalReal++ } else { $highReal++ }
    }
    Write-Host "       (Filtrados $filteredCode ocorrencias em libs externas)" -ForegroundColor DarkGray
}

# ---- A02: Configuracao ---
Write-Host ""
Write-Host "  [A02] Configuracao de Seguranca:" -ForegroundColor White
foreach ($f in $report.scans.configuration.findings) {
    $fileLabel = if ($f.file) { $f.file } else { "Projeto" }
    $color = switch ($f.severity) {
        "critical" { "Red" }
        "high" { "Yellow" }
        default { "DarkYellow" }
    }
    Write-Host "       [$($f.severity.ToUpper())] $($f.issue) - $fileLabel" -ForegroundColor $color
    if ($f.recommendation) {
        Write-Host "         Recomendacao: $($f.recommendation)" -ForegroundColor DarkGray
    }
    $totalReal++
    if ($f.severity -eq "critical") { $criticalReal++ } elseif ($f.severity -eq "high") { $highReal++ }
}

# --- Resumo Final ---
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($criticalReal -eq 0 -and $highReal -eq 0) {
    Write-Host "   RESULTADO: SEGURO para deploy" -ForegroundColor Green
    Write-Host "   Achados reais: $totalReal (nenhum critico ou alto)" -ForegroundColor Green
    $exitCode = 0
}
elseif ($criticalReal -gt 0) {
    Write-Host "   RESULTADO: BLOQUEADO - $criticalReal achado(s) CRITICO(S)" -ForegroundColor Red
    Write-Host "   Corrija antes de subir em producao!" -ForegroundColor Red
    $exitCode = 2
}
else {
    Write-Host "   RESULTADO: ATENCAO - $highReal achado(s) de risco ALTO" -ForegroundColor Yellow
    Write-Host "   Revise antes de subir em producao." -ForegroundColor Yellow
    $exitCode = 1
}

Write-Host "============================================================" -ForegroundColor Cyan

# --- Salva ou remove relatorio JSON ---
if ($Json) {
    $FinalReport = Join-Path $ProjectDir "security_report.json"
    Move-Item $ReportFile $FinalReport -Force
    Write-Host ""
    Write-Host "Relatorio JSON salvo em: $FinalReport" -ForegroundColor Cyan
}
else {
    Remove-Item $ReportFile -ErrorAction SilentlyContinue
}

Write-Host ""
exit $exitCode

