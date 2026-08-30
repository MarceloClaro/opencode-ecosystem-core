# Makefile — compila o manual técnico RAG/Recamán (R456)
#
# O manual é modular: main.tex (documento-mestre) inclui cada seção via \input.
#
# Uso:
#   make        -> compila main.pdf via latexmk (recomendado)
#   make test   -> roda a validação documental (pdftotext/pdfinfo contagem)
#   make clean  -> remove artefatos de compilação

ABNTEX_DIR := ../../publishing/templates/abntex2
SRC        := main

export TEXINPUTS := .:$(ABNTEX_DIR)/:$(TEXINPUTS)
export BSTINPUTS := .:$(ABNTEX_DIR)/:$(BSTINPUTS)
export BIBINPUTS := .:$(ABNTEX_DIR)/:$(BIBINPUTS)

.PHONY: all test clean

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(SRC).tex
	@test -f $(SRC).pdf && echo "[make] OK -> $(SRC).pdf" || (echo "ERRO: PDF nao gerado" && exit 1)

test:
	@test -f $(SRC).pdf || (echo "ERRO: compile antes (make)" && exit 1)
	@pages=$$(pdfinfo $(SRC).pdf | awk '/^Pages/{print $$2}'); \
	chars=$$(pdftotext $(SRC).pdf - | wc -c); \
	echo "[test] paginas=$$pages chars=$$chars"; \
	test "$$pages" -ge "15" || (echo "ERRO: poucas paginas" && exit 1); \
	test "$$chars" -gt "20000" || (echo "ERRO: texto insuficiente" && exit 1); \
	echo "[test] OK: PDF legivel e nao trivial."

clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot *.brf *.synctex.gz \
	      *.fls *.fdb_latexmk *.run.xml *.bcf *.nav *.snm *.vrb *.idx *.ilg *.ind \
	      main.pdf manual_rag_recaman.pdf
	echo "[make] limpo."
