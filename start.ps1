#!/usr/bin/env pwsh
# AgriPulse AI - Quick Start Script (PowerShell)
# Usage: .\start.ps1

Write-Host ""
Write-Host "🌱 AgriPulse AI - Starting..." -ForegroundColor Green
Write-Host "Smart Advice. Better Farming." -ForegroundColor DarkGreen
Write-Host ""

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host ""
Write-Host "🚀 Starting all services (postgres, ollama, backend, frontend)..." -ForegroundColor Cyan
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ docker compose failed. Check docker-compose.yml" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Pull Llama model
Write-Host ""
Write-Host "🤖 Pulling Llama model (llama3.2:3b) — this may take a few minutes on first run..." -ForegroundColor Cyan
docker exec agripulse-ollama ollama pull llama3.2:3b

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ AgriPulse AI is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "📡 Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Demo Flow:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:5173"
Write-Host "  2. Click 'Load Demo Farm (Ramesh)'"
Write-Host "  3. Go to AI Advisor"
Write-Host "  4. Ask: 'Should I irrigate my tomato crop today?'"
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""
