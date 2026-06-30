@echo off
REM ============================================================
REM  run.bat - Lance le bot MT5 AI Trading
REM  Double-clique sur ce fichier pour demarrer le bot.
REM  (Pense a ouvrir MetaTrader 5 sur ton compte DEMO avant.)
REM ============================================================
title MT5 AI Trading Bot (XAUUSD)
cd /d "%~dp0"

echo ============================================================
echo   MT5 AI Trading Bot (XAUUSD)
echo   Assure-toi que MetaTrader 5 est ouvert (compte DEMO).
echo ============================================================
echo.

REM --- Verifie que Python est installe ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas detecte.
    echo Lance d'abord install.bat puis reessaie.
    echo.
    pause
    exit /b 1
)

python main.py

echo.
echo ============================================================
echo   Le bot a termine son analyse.
echo ============================================================
pause
