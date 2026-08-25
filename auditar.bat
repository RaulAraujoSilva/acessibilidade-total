@echo off
setlocal
chcp 65001 >nul
set "RAIZ=%~dp0"
set "PY=%RAIZ%.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo.
  echo   O ambiente nao esta instalado.
  echo   Rode primeiro:  instalar.ps1
  echo.
  pause
  exit /b 1
)

if "%~1"=="" (
  echo.
  echo   Como usar:
  echo     auditar.bat caminho\do\arquivo.pptx
  echo.
  echo   Ou simplesmente ARRASTE o arquivo .pptx para cima deste auditar.bat
  echo.
  pause
  exit /b 1
)

set "ALVO=%~1"
set "SAIDA=%~dpn1-auditoria.md"
set "LEITURA=%~dpn1-leitura-simulada.md"

echo.
echo   Auditando: %~nx1
echo.
"%PY%" "%RAIZ%scripts\audit_pptx.py" "%ALVO%" --md "%SAIDA%" --quiet
"%PY%" "%RAIZ%scripts\simular_leitura.py" "%ALVO%" --md "%LEITURA%" >nul

echo.
echo   Relatorio:        %SAIDA%
echo   Leitura simulada: %LEITURA%
echo.
start "" "%SAIDA%"
endlocal
