@echo off
REM ============================================================
REM Script para enviar o Volume 2 ao GitHub
REM Uso: Execute este script na pasta livro-volume2
REM Pré-requisitos: git instalado e autenticado no GitHub
REM ============================================================

echo Inicializando repositorio git...
if not exist .git (
    git init
    git remote add origin https://github.com/MarceloClaro/odonto-digital-twin.git
)

echo Adicionando arquivos ao stage...
git add README.md
git add validation_report.md
git add .sdd_v2_specs.md
git add PESQUISA_COMPLETA.md
git add .tdd_validate_v2.py
git add light.tex dark.tex preamble-common.tex referencias.bib
git add sections/00-capa.tex sections/00-capa-dark.tex sections/00-prefacio.tex
git add sections/01-folha-rosto.tex sections/02-ficha-catalografica.tex
git add sections/03-dedicatoria.tex sections/04-agradecimentos.tex
git add sections/05-epigrafe.tex sections/06-resumo.tex sections/07-abstract.tex

echo Adicionando capitulos Parte I...
git add sections/part1/*.tex

echo Adicionando capitulos Parte II...
git add sections/part2/*.tex

echo Adicionando capitulos Parte III...
git add sections/part3/*.tex

echo Adicionando capitulos Parte IV...
git add sections/part4/*.tex

echo Adicionando appendices...
git add appendices/*.tex

echo ============================================================
echo Commit e Push...
git commit -m "Volume 2 completo — Framework SUS-Twin, 17 caps V2, TDD 85/85

- 17 capitulos V2 standalone (Partes I-IV)
- 97 sub-arquivos V1 deletados
- ~290 footnotes, 46 codigos Python, 32 tabelas
- TDD expandido: 85 testes (S7 encoding, S8 citacoes, S9 labels)
- 8 novas citacoes bibtex
- 0 erros LaTeX, 0 overfull, 0 BibTeX warnings
- 184 paginas (light), 184 paginas (dark)"

git push -u origin main

echo ============================================================
echo Pronto! Verifique em https://github.com/MarceloClaro/odonto-digital-twin
pause
