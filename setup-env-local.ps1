# Script PowerShell para configurar variáveis de ambiente localmente (SQLite)
# Use: .\setup-env-local.ps1

Write-Host "🔧 Configurando variáveis de ambiente para testes locais..." -ForegroundColor Green
Write-Host ""

# ===== CONFIGURAÇÃO DO BANCO DE DADOS (SQLite) =====
Write-Host "📦 Configuração do SQLite" -ForegroundColor Cyan
$dbPath = "$PWD\cronograma.db"
[Environment]::SetEnvironmentVariable("DATABASE_URL", "sqlite:///$dbPath", "Process")
Write-Host "✓ DATABASE_URL: sqlite:///$dbPath" -ForegroundColor Green

# ===== CONFIGURAÇÃO DO BANCO DE DADOS (Variáveis individuais para compatibilidade) =====
[Environment]::SetEnvironmentVariable("POSTGRES_DB", "cronograma_dev", "Process")
[Environment]::SetEnvironmentVariable("POSTGRES_USER", "dev_user", "Process")
[Environment]::SetEnvironmentVariable("POSTGRES_PASSWORD", "dev_password_local", "Process")
[Environment]::SetEnvironmentVariable("POSTGRES_PORT", "5432", "Process")
Write-Host "✓ POSTGRES_DB: cronograma_dev" -ForegroundColor Green
Write-Host "✓ POSTGRES_USER: dev_user" -ForegroundColor Green
Write-Host "✓ POSTGRES_PASSWORD: dev_password_local" -ForegroundColor Green
Write-Host "✓ POSTGRES_PORT: 5432" -ForegroundColor Green
Write-Host ""

# ===== CONFIGURAÇÃO DO USUÁRIO ADMIN =====
Write-Host "👤 Configuração do usuário admin" -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("ADMIN_NOME", "Desenvolvedor", "Process")
[Environment]::SetEnvironmentVariable("ADMIN_EMAIL", "admin@ufc.br", "Process")
[Environment]::SetEnvironmentVariable("ADMIN_SENHA", "senha123", "Process")
[Environment]::SetEnvironmentVariable("ADMIN_PAPEL", "admin", "Process")
Write-Host "✓ ADMIN_NOME: Desenvolvedor" -ForegroundColor Green
Write-Host "✓ ADMIN_EMAIL: admin@ufc.br" -ForegroundColor Green
Write-Host "✓ ADMIN_SENHA: senha123" -ForegroundColor Green
Write-Host "✓ ADMIN_PAPEL: admin" -ForegroundColor Green
Write-Host ""

# ===== CONFIGURAÇÃO DE SEGURANÇA =====
Write-Host "🔐 Configuração de segurança" -ForegroundColor Cyan
$secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
[Environment]::SetEnvironmentVariable("SECRET_KEY", $secretKey, "Process")
Write-Host "✓ SECRET_KEY gerada aleatoriamente (chave de 32 caracteres)" -ForegroundColor Green
Write-Host ""

# ===== CONFIGURAÇÃO DE CAMINHO =====
Write-Host "🌐 Configuração de caminho" -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("ROOT_PATH", "", "Process")
Write-Host "✓ ROOT_PATH: (vazio - aplicação na raiz)" -ForegroundColor Green
Write-Host ""

# ===== RESUMO FINAL =====
Write-Host "✅ Variáveis de ambiente configuradas com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Resumo da configuração:" -ForegroundColor Yellow
Write-Host "  • Banco de dados: SQLite ($dbPath)" -ForegroundColor White
Write-Host "  • Usuário admin: Desenvolvedor (admin@ufc.br)" -ForegroundColor White
Write-Host "  • Senha admin: senha123" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Esta configuração é apenas para testes locais!" -ForegroundColor Yellow
Write-Host "   Não use em produção!" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Próximas etapas:" -ForegroundColor Cyan
Write-Host "  1. Certifique-se de que o ambiente virtual está ativado" -ForegroundColor White
Write-Host "  2. Execute: python main.py" -ForegroundColor White
Write-Host "  3. Acesse: http://localhost:5000" -ForegroundColor White
Write-Host ""
