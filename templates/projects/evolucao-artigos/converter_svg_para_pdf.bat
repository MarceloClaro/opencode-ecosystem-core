@echo off
REM ============================================================
REM  Converter SVGs dos fluxogramas para PDF
REM  Requer: Inkscape (https://inkscape.org) no PATH
REM  Uso:   converter_svg_para_pdf.bat
REM ============================================================

cd /d "%~dp0"

echo Convertendo fluxogramas SVG para PDF...
echo.

for %%f in (fluxograma_*.svg) do (
    echo   %%f -^> %%~nf.pdf
    inkscape --export-type=pdf "%%f" 2>nul
    if errorlevel 1 (
        echo   ERRO: Inkscape nao encontrado. Instale: https://inkscape.org
        echo   Alternativa: use rsvg-convert -f pdf -o "%%~nf.pdf" "%%f"
    )
)

echo.
echo Pronto! Recompile o artigo: pdflatex artigo_evolucao_standalone.tex
