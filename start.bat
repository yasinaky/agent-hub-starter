
@echo off
title AgentHub Starter
setlocal ENABLEDELAYEDEXPANSION

echo [AgentHub] Docker kontrol ediliyor...
docker --version >NUL 2>&1
if errorlevel 1 (
  echo [HATA] Docker Desktop yüklü değil veya calismiyor.
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >NUL
  echo [AgentHub] .env dosyasi olusturuldu. Degerleri gerekirse guncelleyin.
)

echo [AgentHub] Servisler baslatiliyor...
docker compose up -d --build
if errorlevel 1 (
  echo [HATA] Docker compose calismadi.
  pause
  exit /b 1
)

echo.
echo [OK] Servisler ayakta:
echo  - vLLM (LLM API):   http://localhost:8000/v1
echo  - Orchestrator:     http://localhost:7000
echo  - Postgres:         localhost:5432
echo.
pause
