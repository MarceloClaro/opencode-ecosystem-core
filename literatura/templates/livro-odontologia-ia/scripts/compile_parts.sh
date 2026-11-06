#!/bin/bash
# compile_parts.sh — Compila o livro em 5 partes e une os PDFs
# Resolve o problema de memória do TeX com documentos muito grandes
# Uso: bash compile_parts.sh

set -e
BOOK_DIR="/home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia"
cd "$BOOK_DIR"

echo "📚 Compilando livro OdontoIA em 5 partes..."
echo ""

# Gerar main_partial.tex com includeonly
gen_main() {
    local PART_NUM=$1
    local PART_NAME=$2
    shift 2
    local CHAPTERS=("$@")
    
    # Criar arquivo temporário com includeonly
    cat > main_partial.tex << 'TEXEOF'
\documentclass[12pt,a4paper,twoside,openright]{book}
\input{config/preambulo}
\begin{document}
\frontmatter
\input{capa/capa}
\input{prefacio/prefacio}
\input{prefacio/dedicatoria}
\input{prefacio/agradecimentos}
\input{prefacio/autor-odontoia}
\tableofcontents
\mainmatter
TEXEOF
    
    # Adicionar includeonly para os capítulos desta parte
    echo "\\includeonly{" >> main_partial.tex
    for ch in "${CHAPTERS[@]}"; do
        echo "  $ch," >> main_partial.tex
    done
    echo "}" >> main_partial.tex
    
    # Adicionar includes de todos os capítulos
    echo "\\include{capitulos/01-historia-ia-odontologia}" >> main_partial.tex
    echo "\\include{capitulos/02-evidencia-revisoes}" >> main_partial.tex
    echo "\\include{capitulos/03-python-colab}" >> main_partial.tex
    echo "\\include{capitulos/04-estatistica-essencial}" >> main_partial.tex
    echo "\\include{capitulos/05-ml-classico}" >> main_partial.tex
    echo "\\include{capitulos/06-redes-neurais}" >> main_partial.tex
    echo "\\include{capitulos/07-cnns-imagens}" >> main_partial.tex
    echo "\\include{capitulos/08-segmentacao-dental}" >> main_partial.tex
    echo "\\include{capitulos/09-radiologia-dl}" >> main_partial.tex
    echo "\\include{capitulos/10-lesoes-bucais-classificacao}" >> main_partial.tex
    echo "\\include{capitulos/11-cancer-oral-opmd}" >> main_partial.tex
    echo "\\include{capitulos/12-sdd-metodologia}" >> main_partial.tex
    echo "\\include{capitulos/13-tdd-python}" >> main_partial.tex
    echo "\\include{capitulos/14-projetos-guiados}" >> main_partial.tex
    echo "\\include{capitulos/15-interpretacao-modelos}" >> main_partial.tex
    echo "\\include{capitulos/16-auditoria-github}" >> main_partial.tex
    echo "\\include{capitulos/17-reprodutibilidade}" >> main_partial.tex
    echo "\\include{capitulos/18-periodontia-ia}" >> main_partial.tex
    echo "\\include{capitulos/19-implantodontia-ia}" >> main_partial.tex
    echo "\\include{capitulos/20-ortodontia-ia}" >> main_partial.tex
    echo "\\include{capitulos/21-gemeos-digitais}" >> main_partial.tex
    echo "\\include{capitulos/22-modelos-fundacionais}" >> main_partial.tex
    echo "\\include{capitulos/23-rag-odontologico}" >> main_partial.tex
    echo "\\include{capitulos/24-publicacao-cientifica}" >> main_partial.tex
    echo "\\include{capitulos/25-etica-lgpd-regulacao}" >> main_partial.tex
    echo "\\include{capitulos/26-educacao-odontologica-ia}" >> main_partial.tex
    echo "\\include{capitulos/27-futuro-odontologia}" >> main_partial.tex
    echo "\\include{capitulos/28-conclusao-final}" >> main_partial.tex
    
    cat >> main_partial.tex << 'TEXEOF'
\backmatter
\end{document}
TEXEOF
    
    echo "  📄 Compilando $PART_NAME..."
    xelatex -interaction=nonstopmode -jobname="parte${PART_NUM}" main_partial.tex > /dev/null 2>&1
    
    PAGES=$(pdfinfo "parte${PART_NUM}.pdf" 2>/dev/null | grep "Pages" | awk '{print $2}')
    echo "     ✅ $PART_NAME: ${PAGES:-?} páginas"
}

# PARTE I: Cap 1-5
gen_main 1 "Parte I - Fundamentos" \
    "capitulos/01-historia-ia-odontologia" \
    "capitulos/02-evidencia-revisoes" \
    "capitulos/03-python-colab" \
    "capitulos/04-estatistica-essencial" \
    "capitulos/05-ml-classico"

# PARTE II: Cap 6-11
gen_main 2 "Parte II - Teoria e Modelos" \
    "capitulos/06-redes-neurais" \
    "capitulos/07-cnns-imagens" \
    "capitulos/08-segmentacao-dental" \
    "capitulos/09-radiologia-dl" \
    "capitulos/10-lesoes-bucais-classificacao" \
    "capitulos/11-cancer-oral-opmd"

# PARTE III: Cap 12-17
gen_main 3 "Parte III - SDD/TDD" \
    "capitulos/12-sdd-metodologia" \
    "capitulos/13-tdd-python" \
    "capitulos/14-projetos-guiados" \
    "capitulos/15-interpretacao-modelos" \
    "capitulos/16-auditoria-github" \
    "capitulos/17-reprodutibilidade"

# PARTE IV: Cap 18-23
gen_main 4 "Parte IV - Aplicações Avançadas" \
    "capitulos/18-periodontia-ia" \
    "capitulos/19-implantodontia-ia" \
    "capitulos/20-ortodontia-ia" \
    "capitulos/21-gemeos-digitais" \
    "capitulos/22-modelos-fundacionais" \
    "capitulos/23-rag-odontologico"

# PARTE V: Cap 24-28
gen_main 5 "Parte V - Futuro e Regulação" \
    "capitulos/24-publicacao-cientifica" \
    "capitulos/25-etica-lgpd-regulacao" \
    "capitulos/26-educacao-odontologica-ia" \
    "capitulos/27-futuro-odontologia" \
    "capitulos/28-conclusao-final"

echo ""
echo "📊 Unindo PDFs..."
# Unir todos os PDFs
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=main_completo.pdf \
    parte1.pdf parte2.pdf parte3.pdf parte4.pdf parte5.pdf 2>/dev/null

TOTAL_PAGES=$(pdfinfo main_completo.pdf 2>/dev/null | grep "Pages" | awk '{print $2}')
echo ""
echo "============================================"
echo "  📚 LIVRO COMPLETO COMPILADO"
echo "  Total: ${TOTAL_PAGES:-?} páginas"
echo "  Arquivo: main_completo.pdf"
echo "============================================"
