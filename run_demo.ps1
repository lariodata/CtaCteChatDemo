# Script para arrancar el demo completo (Backend + Frontend Streamlit)
# Uso: .\run_demo.ps1

Write-Host "🚀 Chat Cuenta Corriente - Demo Etapa 7" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Activar venv
Write-Host "📦 Activando venv..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Verificar que Ollama está corriendo
Write-Host "🤖 Verificando Ollama..." -ForegroundColor Yellow
$ollama_check = curl -s -m 2 http://localhost:11434/api/tags 2>&1 | findstr /C:"qwen"
if ($ollama_check) {
    Write-Host "✅ Ollama está activo (qwen2.5:7b-instruct)" -ForegroundColor Green
} else {
    Write-Host "⚠️  No detectó Ollama. Asegúrate que está corriendo:" -ForegroundColor Yellow
    Write-Host "   ollama serve" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📝 Para usar la demo:" -ForegroundColor Cyan
Write-Host "  1. Backend (FastAPI):     python main_api.py" -ForegroundColor Gray
Write-Host "  2. Frontend (Streamlit):  streamlit run web/app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  - API:        http://localhost:8001" -ForegroundColor Gray
Write-Host "  - Streamlit:  http://localhost:8501" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 Listo. Abre dos terminales y ejecuta los comandos de arriba." -ForegroundColor Green
