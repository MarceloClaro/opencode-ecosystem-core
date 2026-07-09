# =============================================================================
# Makefile para compilação do Livro OpenCode Ecosystem
# Uso: make          -> compila o PDF completo
#      make clean    -> remove arquivos temporários
#      make purge    -> remove tudo exceto .tex e Makefile
#      make view     -> compila e abre o PDF
#      make chapter  -> compila apenas um capítulo específico
# =============================================================================

LATEXMK = latexmk
LATEX = xelatex
BIBER = biber
MAIN = livro
VIEWER = evince
CHAPTER_DIR = capitulos

.PHONY: all clean purge view chapter pdf

all: pdf

pdf:
	@echo "=== Compilando o Livro OpenCode Ecosystem ==="
	$(LATEXMK) -$(LATEX) -$(BIBER) -f $(MAIN)
	@echo "=== PDF gerado: $(MAIN).pdf ==="

# Compilação simplificada (pdflatex + bibtex)
quick:
	pdflatex $(MAIN)
	bibtex $(MAIN)
	pdflatex $(MAIN)
	pdflatex $(MAIN)

# Compilação usando latexmk (automática)
continuous:
	$(LATEXMK) -pvc -$(LATEX) -$(BIBER) $(MAIN)

view: pdf
	$(VIEWER) $(MAIN).pdf &

clean:
	$(LATEXMK) -c $(MAIN)
	rm -f *.bbl *.blg *.run.xml *.bcf *.synctex.gz
	rm -f *_tmp.tex
	find $(CHAPTER_DIR) -name '*.aux' -delete
	find ilustracoes -name '*.aux' -delete
	find ilustracoes -name '*.log' -delete

purge: clean
	rm -f $(MAIN).pdf
	rm -f *.pdf
	rm -rf auto/

# Compilar um capítulo específico como documento independente
chapter:
	@if [ -z "$(c)" ]; then \
		echo "Uso: make chapter c=08-capitulo1-mat-est"; \
		exit 1; \
	fi; \
	echo "Compilando capítulo: $(c)"; \
	cp $(MAIN).tex _tmp_main.tex; \
	sed -i "s/\\include{capitulos\/[^}]*}/% &/" _tmp_main.tex; \
	sed -i "s/% \\\\include{capitulos\/$(c)}/\\include{capitulos\/$(c)}/" _tmp_main.tex; \
	sed -i 's/\\bibliography{.*}/% \\bibliography{&}/' _tmp_main.tex; \
	pdflatex _tmp_main && bibtex _tmp_main && pdflatex _tmp_main && pdflatex _tmp_main; \
	mv _tmp_main.pdf $(c).pdf; \
	rm -f _tmp_main.*; \
	echo "Capítulo $(c).pdf gerado."

# Verificar contagem de laudas (páginas)
pages:
	@echo "Contagem de páginas do PDF:"
	@pdfinfo $(MAIN).pdf 2>/dev/null | grep Pages || echo "PDF não encontrado. Compile primeiro."

# Estatísticas de palavras e caracteres
stats:
	@echo "=== Estatísticas do Livro ==="
	@wc -w capitulos/0*.tex capitulos/1*.tex 2>/dev/null | tail -1
	@echo "Arquivos .tex:"
	@find . -name '*.tex' -not -path './templates/*' | wc -l
	@echo "Linhas totais de LaTeX:"
	@cat capitulos/0*.tex capitulos/1*.tex 2>/dev/null | wc -l

# Backup do livro
backup:
	@mkdir -p backups
	@tar czf backups/livro-$$(date +%Y%m%d_%H%M%S).tar.gz \
		livro.tex Makefile \
		capitulos/ referencias/ ilustracoes/
	@echo "Backup criado em backups/"
