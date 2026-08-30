# Makefile — compila o manual técnico RAG/Recamán (R456)
#
# Uso:
#   make        -> compila manual_rag_recaman.pdf via latexmk (recomendado)
#   make test   -> roda a validação documental (pdftotext/pdfinfo contagem)
#   make clean  -> remove artefatos de compilação

ABNTEX_DIR := ../../publishing/templates/abntex2
SRC        := manual_rag_recaman

export TEXINPUTS := .:$(ABNTEX_DIR)/:$(TEXINPUTS)

.PHONY: all test clean

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(SRC).tex
	@test -f $(SRC).pdf && echo "[make] OK -> $(SRC).pdf" || (echo "ERRO: PDF nao gerado" && exit 1)

test:
	@test -f $(SRC).pdf || (echo "ERRO: compile antes (make)" && exit 1)
	@pages=$$(pdfinfo $(SRC).pdf | awk '/^Pages/{print $$2}'); \
	chars=$$(pdftotext $(SRC).pdf - | wc -c); \
	echo "[test] paginas=$$pages chars=$$chars"; \
	test "$$pages" -ge "5" || (echo "ERRO: poucas paginas" && exit 1); \
	test "$$chars" -gt "5000" || (echo "ERRO: texto insuficiente" && exit 1); \
	echo "[test] OK: PDF legivel e nao trivial."

clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot *.synctex.gz \
	      *.fls *.fdb_latexmk *.run.xml *.bcf *.nav *.snm *.vrb *.idx *.ilg *.ind
	echo "[make] limpo."
