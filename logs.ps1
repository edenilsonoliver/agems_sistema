# ============================================================
# AGEMS - Sistema de Gestão Regulatória
# Script para Visualizar Logs
# ============================================================

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Cores
$ColorTitle = "Cyan"
$ColorInfo = "White"

Clear-Host
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host "  AGEMS - Logs do Sistema" -ForegroundColor $ColorTitle
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host ""
Write-Host "Pressione Ctrl+C para sair" -ForegroundColor $ColorInfo
Write-Host ""

docker-compose logs -f --tail=100

