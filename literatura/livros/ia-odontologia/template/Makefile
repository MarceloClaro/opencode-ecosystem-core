# Makefile para compilação do projeto LaTeX
# Gerado automaticamente
# Template aplicado: victoria-regia via pdf2latex — OpenCode Ecosystem Core

TEX = main.tex
AUX = main.aux
PDF = main.pdf

all: pdf

pdf:
	latexmk -pdf -interaction=nonstopmode $(TEX)

quick:
	pdflatex -interaction=nonstopmode $(TEX)

clean:
	latexmk -c
	rm -f *.bbl *.blg *.run.xml *.synctex.gz

purge: clean
	rm -f $(PDF)

view: pdf
	open $(PDF) 2>/dev/null || xdg-open $(PDF) 2>/dev/null || echo "Abra: $(PDF)"

# Compilação manual passo a passo
manual:
	pdflatex -interaction=nonstopmode $(TEX)
	bibtex $(AUX) 2>/dev/null || true
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)

.PHONY: all pdf quick clean purge view manual
