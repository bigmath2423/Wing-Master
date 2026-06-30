@echo off
REM ============================================================
REM  install.bat - Installe les dependances du bot MT5 AI
REM  Double-clique sur ce fichier pour tout installer.
REM ============================================================
title Installation - MT5 AI Trading Bot
cd /d "%~dp0"

echo ============================================================
echo   Installation du MT5 AI Trading Bot (XAUUSD)
echo ============================================================
echo.

REM --- Verifie que Python est installe ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas detecte.
    echo.
    echo  1. Telecharge Python sur https://www.python.org/downloads/
    echo  2. Pendant l'installation, COCHE "Add Python to PATH"
    echo  3. Relance ce fichier install.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte :
python --version
echo.

REM --- Met pip a jour ---
echo Mise a jour de pip...
python -m pip install --upgrade pip

REM --- Installe les dependances ---
echo.
echo Installation des dependances (MetaTrader5, pandas, numpy)...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERREUR] L'installation des dependances a echoue.
    echo Verifie ta connexion internet et reessaie.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation terminee avec succes !
echo   Lance le bot avec run.bat (double-clic).
echo ============================================================
echo.
pause
