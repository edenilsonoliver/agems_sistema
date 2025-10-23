# ============================================================
# AGEMS - Sistema de Gestão Regulatória
# Script para Parar o Sistema
# ============================================================

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Cores
$ColorTitle = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorInfo = "White"

Clear-Host
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host "  AGEMS - Parando Sistema" -ForegroundColor $ColorTitle
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host ""

Write-Host "Parando containers..." -ForegroundColor $ColorWarning
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Sistema parado com sucesso!" -ForegroundColor $ColorSuccess
    Write-Host ""
    Write-Host "Para iniciar novamente, execute:" -ForegroundColor $ColorInfo
    Write-Host "  .\iniciar.ps1" -ForegroundColor $ColorInfo
} else {
    Write-Host ""
    Write-Host "✗ Erro ao parar o sistema" -ForegroundColor $ColorWarning
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

