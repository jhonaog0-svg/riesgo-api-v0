@echo off
setlocal
cd /d "%~dp0"
title Riesgo API - Servidor

echo ========================================
echo       RIESGO API - INICIO DEL SERVICIO
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

echo Comprobando dependencias...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo La API iniciara en http://localhost:8000
echo No cierres esta ventana mientras uses el servicio.
echo Para detenerla, presiona Ctrl+C.
echo.
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

pause
