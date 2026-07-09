# =============================================================================
# Makefile — Livro "Gêmeos Digitais na Odontologia" Volume 2
# Uso: make light   → compila tema claro
#      make dark    → compila tema escuro
#      make all     → compila ambos os temas
#      make test    → executa testes Python TDD
#      make plots   → gera gráficos científicos
#      make clean   → limpa arquivos auxiliares
#      make validate→ validação completa (testes + plots)
# =============================================================================

LATEX = pdflatex -interaction=nonstopmode
BIBTEX = bibtex
PYTHON = python

# === Compilação Tema Light ===
.PHONY: light
light:
	$(LATEX) light.tex
	$(BIBTEX) light
	$(LATEX) light.tex
	$(LATEX) light.tex
	@echo "✓ light.pdf gerado com sucesso"

# === Compilação Tema Dark ===
.PHONY: dark
dark:
	$(LATEX) dark.tex
	$(BIBTEX) dark
	$(LATEX) dark.tex
	$(LATEX) dark.tex
	@echo "✓ dark.pdf gerado com sucesso"

# === Compilação Completa ===
.PHONY: all
all: plots light dark

# === Testes Python (TDD) ===
.PHONY: test
test:
	$(PYTHON) -m pytest test_sus_twin_framework.py -v --tb=short
	@echo "✓ Testes TDD executados"

# === Geração de Gráficos ===
.PHONY: plots
plots:
	$(PYTHON) generate_plots.py
	@echo "✓ Gráficos gerados"

# === Validação Completa ===
.PHONY: validate
validate: plots test
	@echo "✓ Validação completa aprovada"

# === Limpeza ===
.PHONY: clean
clean:
	-rm -f *.aux *.bbl *.blg *.idx *.ilg *.ind *.lof *.log *.lot *.toc *.out *.lol *.run.xml
	-rm -f sections/*.aux sections/part*/*.aux sections/appendices/*.aux
	-rm -f __pycache__/*.pyc
	@echo "✓ Arquivos auxiliares removidos"

# === Limpeza Total ===
.PHONY: distclean
distclean: clean
	-rm -f light.pdf dark.pdf
	@echo "✓ PDFs removidos"
