# ============================================================
# AGEMS - Sistema de Gestão Regulatória
# Script para Reiniciar o Sistema
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
Write-Host "  AGEMS - Reiniciando Sistema" -ForegroundColor $ColorTitle
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host ""

Write-Host "Reiniciando containers..." -ForegroundColor $ColorWarning
docker-compose restart

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Sistema reiniciado com sucesso!" -ForegroundColor $ColorSuccess
    Write-Host ""
    Write-Host "Aguardando sistema ficar pronto..." -ForegroundColor $ColorWarning
    Start-Sleep -Seconds 5
    
    Write-Host ""
    Write-Host "Acesse o sistema em:" -ForegroundColor $ColorTitle
    Write-Host "  http://localhost:8000" -ForegroundColor $ColorInfo
    Write-Host ""
    
    # Abrir navegador
    Start-Process "http://localhost:8000"
} else {
    Write-Host ""
    Write-Host "✗ Erro ao reiniciar o sistema" -ForegroundColor $ColorWarning
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

