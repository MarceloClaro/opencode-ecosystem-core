#===============================================================================
# Makefile — OdontoIA: Livro ABNT
# Compilação: xelatex + biber (ABNT)
#===============================================================================

MAIN = main
LATEX = TEXMFCNF=/home/marceloclaro/texmf/web2c:$$TEXMFCNF xelatex
BIBER = biber
LATEXOPT = -interaction=nonstopmode

.PHONY: all pdf pdf-quick clean cleanall watch

all: pdf

pdf:
	@echo "=== Compilação ABNT (4 passagens) ==="
	$(LATEX) $(LATEXOPT) $(MAIN)
	$(BIBER) $(MAIN)
	$(LATEX) $(LATEXOPT) $(MAIN)
	$(LATEX) $(LATEXOPT) $(MAIN)
	@echo "=== PDF gerado: $(MAIN).pdf ==="
	@pdfinfo $(MAIN).pdf 2>/dev/null | grep -E "Pages|Title" || true

pdf-quick:
	$(LATEX) $(LATEXOPT) $(MAIN)

biber:
	$(BIBER) $(MAIN)

clean:
	rm -f *.aux *.log *.bcf *.idx *.ist *.toc *.lof *.lot *.out *.synctex.gz
	rm -f *.acn *.glsdefs *.run.xml *.bbl *.blg *.glo *.gls *.syg *.syi *.alg
	rm -f parte1-fundamentos/*.aux parte2-teoria-modelos/*.aux
	rm -f parte3-engenharia-sdd-tdd/*.aux parte4-aplicacoes-avancadas/*.aux
	rm -f parte5-futuro-etica/*.aux prefacio/*.aux apendices/*.aux config/*.aux
	@echo "=== Limpeza concluída ==="

cleanall: clean
	rm -f *.pdf
	@echo "=== Todos os PDFs removidos ==="

watch:
	while inotifywait -e modify -r . --exclude '.git|__pycache__'; do \
		make pdf; \
	done