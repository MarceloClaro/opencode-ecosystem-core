@echo off
echo =======================================
echo COMPILACAO LaTeX - Artigo Disruptivo
echo =======================================
echo.

REM Verifica se MiKTeX esta instalado
where pdflatex >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] pdflatex encontrado. Compilando...
    goto :compile
)

echo [INFO] MiKTeX nao encontrado. Verificando TeX Live...
where xelatex >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] xelatex encontrado. Compilando...
    goto :compile_xetex
)

echo [INFO] Nenhuma distribuicao LaTeX encontrada.
echo [INFO] Baixando e instalando MiKTeX...
echo.

REM Download MiKTeX (small installer)
powershell -Command "& { Invoke-WebRequest -Uri 'https://miktex.org/download/win' -OutFile '%TEMP%\miktex-setup.exe' }"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao baixar MiKTeX. Verifique sua conexao.
    echo [DICA] Instale manualmente: https://miktex.org/download
    pause
    exit /b 1
)

echo [INFO] Instalando MiKTeX (modo silencioso, isto pode levar alguns minutos)...
"%TEMP%\miktex-setup.exe" --unattended --shared
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na instalacao do MiKTeX.
    pause
    exit /b 1
)

REM Refresh PATH
set PATH=%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64

:compile
echo.
echo [INFO] Compilando artigo_ifrs_banca.tex (Qualis A1 - Banca)...
echo.

cd /d "%~dp0"

REM --- artigo_ifrs_banca: 3 passagens ---
pdflatex -interaction=nonstopmode artigo_ifrs_banca.tex
pdflatex -interaction=nonstopmode artigo_ifrs_banca.tex
pdflatex -interaction=nonstopmode artigo_ifrs_banca.tex

echo.
echo =======================================
echo [OK] artigo_ifrs_banca.pdf gerado!
echo =======================================

echo.
echo [INFO] Compilando artigo_disruptivo.tex...
echo.

REM --- artigo_disruptivo: 3 passagens ---
pdflatex -interaction=nonstopmode artigo_disruptivo.tex
pdflatex -interaction=nonstopmode artigo_disruptivo.tex
pdflatex -interaction=nonstopmode artigo_disruptivo.tex

echo.
echo =======================================
echo [OK] artigo_disruptivo.pdf gerado!
echo =======================================
pause
goto :end

:compile_xetex
cd /d "%~dp0latex"
xelatex -interaction=nonstopmode artigo_disruptivo.tex
xelatex -interaction=nonstopmode artigo_disruptivo.tex
xelatex -interaction=nonstopmode artigo_disruptivo.tex
echo [OK] Compilacao XeLaTeX concluida!
pause
goto :end

:end
