@echo off
title Loki Viewer - Docker
echo.
echo  =========================================
echo    Loki Viewer (Docker)
echo  =========================================
echo.

:: Check if Docker is available
docker info >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Docker is not running or not installed.
    echo  Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo  Building and starting Loki Viewer container...
docker compose up -d --build
if errorlevel 1 (
    echo  [ERROR] Failed to start container. Check the output above.
    pause
    exit /b 1
)

echo.
echo  Waiting for Loki Viewer to be ready...
timeout /t 3 /nobreak >nul

echo  Opening browser at: http://localhost:8501
start http://localhost:8501

echo.
echo  Loki Viewer is running in the background.
echo  To stop it, run:  docker compose down
echo.
pause
