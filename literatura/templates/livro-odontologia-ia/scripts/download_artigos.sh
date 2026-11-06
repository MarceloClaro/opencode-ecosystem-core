#!/bin/bash
# =============================================================================
# download_artigos.sh — Baixa PDFs de artigos científicos com DOI
# Uso: ./scripts/download_artigos.sh
#       ou ./scripts/download_artigos.sh 10.xxxx/xxxxx (para um artigo)
# =============================================================================

DIR_SAIDA="artigos"
mkdir -p "$DIR_SAIDA"

# Lista de DOIs dos artigos citados no livro (baixar via Unpaywall/DOI.org)
declare -a DOIS=(
    # História da IA em Odontologia
    "10.1016/j.jds.2020.06.019"
    "10.1016/S0300-5712(97)00027-4"
    "10.1016/j.jdent.2021.103610"
    "10.1177/0022034520915714"
    # CNNs e Deep Learning
    "10.1016/j.jdent.2024.105398"
    "10.1007/s10278-024-01025-w"
    "10.3390/diagnostics14232719"
    "10.3390/app13137947"
    # CariesNet
    "10.1007/s00521-021-06438-0"
    "10.3390/diagnostics13020202"
    # Segmentação
    "10.48550/arXiv.2310.17176"
    "10.48550/arXiv.2406.03747"
    # Classificação de lesões
    "10.1016/j.jds.2024.10.019"
    "10.1038/s41598-023-38343-y"
    "10.1016/j.jdent.2023.104657"
    # Radiologia
    "10.5051/jpis.2302880144"
    "10.1007/s10278-024-01317-1"
    # Periodontia
    "10.3389/fdmed.2024.1479380"
    "10.1186/s12903-024-03896-5"
    # Gêmeos Digitais
    "10.1109/ACCESS.2023.33256039"
    "10.3389/fdmed.2026.1737162"
    "10.3390/bioengineering11010084"
    # Lesões periapicais
    "10.1038/s41598-024-75748-9"
    "10.1186/s12903-025-06104-0"
    # LLM e Modelos Fundacionais
    "10.3390/diagnostics14171948"
    "10.48550/arXiv.2601.07499"
    "10.48550/arXiv.2311.06551"
    # Datasets
    "10.1016/j.oraloncology.2024.106946"
    "10.17632/mhjyrn35p4.2"
    "10.48550/arXiv.2203.15856"
)

baixar_doi() {
    local doi="$1"
    local nome_arquivo="${doi//\//_}.pdf"
    local caminho="$DIR_SAIDA/$nome_arquivo"

    if [ -f "$caminho" ]; then
        echo "✅ Já existe: $nome_arquivo"
        return 0
    fi

    echo "📥 Baixando DOI: $doi ..."

    # Tenta baixar via Unpaywall (maior taxa de sucesso para acesso aberto)
    HTTP_CODE=$(curl -sL -o "$caminho" -w "%{http_code}" --connect-timeout 10 --max-time 30 \
        -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AcademicBot/1.0" \
        "https://doi.org/$doi" 2>/dev/null)

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "301" ]; then
        # Verifica se é realmente um PDF
        if file "$caminho" | grep -qi "pdf"; then
            echo "   ✅ Baixado com sucesso ($HTTP_CODE)"
            return 0
        fi
    fi

    # Tenta via PubMed Central (PMC)
    PMID=$(curl -s "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=$doi&format=json" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['records'][0].get('pmid',''))" 2>/dev/null)
    
    if [ -n "$PMID" ]; then
        curl -sL -o "$caminho" --connect-timeout 10 --max-time 30 \
            -H "User-Agent: AcademicBot/1.0" \
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMID${PMID}/pdf/" 2>/dev/null
        if file "$caminho" | grep -qi "pdf"; then
            echo "   ✅ Baixado via PMC (PMID: $PMID)"
            return 0
        fi
    fi

    # Tenta via arXiv (se for arXiv ID)
    if [[ "$doi" == *"arXiv"* ]]; then
        ARXIV_ID=$(echo "$doi" | grep -oP '\d{4}\.\d{4,5}')
        if [ -n "$ARXIV_ID" ]; then
            curl -sL -o "$caminho" --connect-timeout 10 --max-time 30 \
                "https://arxiv.org/pdf/$ARXIV_ID.pdf" 2>/dev/null
            if file "$caminho" | grep -qi "pdf"; then
                echo "   ✅ Baixado via arXiv ($ARXIV_ID)"
                return 0
            fi
        fi
    fi

    # Remove arquivo inválido
    rm -f "$caminho"
    echo "   ❌ Não foi possível baixar (código: $HTTP_CODE)"
    return 1
}

# =============================================================================
# MAIN
# =============================================================================

if [ $# -eq 1 ]; then
    # Baixar um DOI específico
    baixar_doi "$1"
else
    # Baixar todos
    TOTAL=${#DOIS[@]}
    SUCESSO=0
    FALHA=0

    echo "============================================"
    echo "  📚 Download de PDFs — Livro OdontoIA"
    echo "  Total: $TOTAL artigos para baixar"
    echo "  Destino: $DIR_SAIDA/"
    echo "============================================"
    echo ""

    for doi in "${DOIS[@]}"; do
        if baixar_doi "$doi"; then
            ((SUCESSO++))
        else
            ((FALHA++))
        fi
        sleep 1  # Respeitar rate limits
    done

    echo ""
    echo "============================================"
    echo "  📊 RESULTADO:"
    echo "  ✅ Sucesso: $SUCESSO"
    echo "  ❌ Falha:   $FALHA"
    echo "  📁 Total:   $TOTAL"
    echo "============================================"
    echo ""
    echo "💡 Artigos não baixados podem estar atrás de paywall."
    echo "   Use https://sci-hub.se/ para acessá-los via DOI."
fi
