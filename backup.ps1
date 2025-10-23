# ============================================================
# AGEMS - Sistema de Gestão Regulatória
# Script para Backup do Banco de Dados
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

Clear-Host
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host "  AGEMS - Backup do Banco de Dados" -ForegroundColor $ColorTitle
Write-Host "============================================================" -ForegroundColor $ColorTitle
Write-Host ""

# Criar diretório de backups se não existir
$backupDir = "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "✓ Diretório de backups criado" -ForegroundColor $ColorSuccess
}

# Gerar nome do arquivo com data e hora
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$backupDir\agems_backup_$timestamp.sqlite3"

# Verificar se o banco de dados existe
if (Test-Path "db.sqlite3") {
    Write-Host "Criando backup do banco de dados..." -ForegroundColor $ColorWarning
    
    try {
        Copy-Item "db.sqlite3" $backupFile -Force
        
        $fileSize = (Get-Item $backupFile).Length / 1KB
        $fileSizeFormatted = "{0:N2}" -f $fileSize
        
        Write-Host ""
        Write-Host "✓ Backup criado com sucesso!" -ForegroundColor $ColorSuccess
        Write-Host ""
        Write-Host "Arquivo: $backupFile" -ForegroundColor $ColorInfo
        Write-Host "Tamanho: $fileSizeFormatted KB" -ForegroundColor $ColorInfo
        Write-Host ""
        
        # Listar backups existentes
        Write-Host "Backups existentes:" -ForegroundColor $ColorTitle
        Get-ChildItem -Path $backupDir -Filter "*.sqlite3" | ForEach-Object {
            $size = "{0:N2}" -f ($_.Length / 1KB)
            Write-Host "  $($_.Name) - $size KB - $($_.LastWriteTime)" -ForegroundColor $ColorInfo
        }
        
    } catch {
        Write-Host ""
        Write-Host "✗ Erro ao criar backup: $_" -ForegroundColor $ColorError
    }
} else {
    Write-Host "✗ Banco de dados não encontrado!" -ForegroundColor $ColorError
    Write-Host "  Certifique-se de que o sistema foi iniciado pelo menos uma vez." -ForegroundColor $ColorWarning
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

