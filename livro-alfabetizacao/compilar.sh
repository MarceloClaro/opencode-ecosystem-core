#!/bin/bash
# ============================================================
# Script de Compilação do Livro Didático "Alfabetizar Bem"
# Método Híbrido Fonico-Kumon com Técnica da Boquinha
# ============================================================

set -e

echo "=========================================="
echo "  ALFABETIZAR BEM — Compilação LaTeX"
echo "  Método Híbrido Fonico-Kumon"
echo "=========================================="
echo ""

# Verificar se pdflatex está instalado
if ! command -v pdflatex &> /dev/null; then
    echo "ERRO: pdflatex não encontrado."
    echo "Instale com: sudo apt-get install texlive-full"
    exit 1
fi

# Diretório base
BASE_DIR="/home/marceloclaro/opencode-ecosystem-core/livro-alfabetizacao"

# Compilar cada volume
for VOLUME in Volume1 Volume2 Volume3 Volume4 Volume5; do
    echo "------------------------------------------"
    echo "Compilando $VOLUME..."
    echo "------------------------------------------"
    
    DIR="$BASE_DIR/$VOLUME"
    
    if [ ! -f "$DIR/main.tex" ]; then
        echo "AVISO: $DIR/main.tex não encontrado. Pulando..."
        continue
    fi
    
    cd "$DIR"
    
    # Primeira passagem
    echo "  Passagem 1/2..."
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
    
    # Segunda passagem (para referências e sumário)
    echo "  Passagem 2/2..."
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
    
    # Verificar se o PDF foi gerado
    if [ -f "main.pdf" ]; then
        echo "  ✓ PDF gerado: $DIR/main.pdf"
        # Renomear para nome mais descritivo
        cp main.pdf "$BASE_DIR/Alfabetizar_Bem_${VOLUME}.pdf"
        echo "  ✓ Copiado para: Alfabetizar_Bem_${VOLUME}.pdf"
    else
        echo "  ✗ ERRO ao gerar PDF para $VOLUME"
    fi
    
    echo ""
done

echo "=========================================="
echo "  COMPILAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "PDFs gerados em: $BASE_DIR/"
echo ""
ls -la "$BASE_DIR"/*.pdf 2>/dev/null || echo "Nenhum PDF encontrado."
echo ""
echo "Para visualizar, abra os arquivos PDF no navegador ou leitor de PDF."
