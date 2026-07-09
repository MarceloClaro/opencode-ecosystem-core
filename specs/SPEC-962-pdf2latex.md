# SPEC-962: PDF-to-LaTeX — Conversão Inteligente de PDF para Projeto LaTeX

**STATUS**: IMPLEMENTADO
**DATA**: 2026-07-09
**AUTOR**: marceloclaro
**VERSÃO**: 1.0

## 1. Objetivo

Capacitar o ecossistema OpenCode a **converter documentos PDF em projetos LaTeX completos**, preservando ao máximo a estrutura original (capítulos, seções, figuras, tabelas, equações, referências) e aplicando templates LaTeX do catálogo do ecossistema.

## 2. Critérios de Aceitação

- [ ] Extrair texto completo do PDF com formatação básica preservada
- [ ] Detectar e extrair figuras/imagens do PDF
- [ ] Detectar estrutura hierárquica (capítulos, seções, subseções)
- [ ] Detectar e converter tabelas para tabular/table
- [ ] Detectar e converter equações matemáticas para math mode
- [ ] Detectar referências bibliográficas e gerar .bib
- [ ] Gerar projeto LaTeX completo: main.tex + capítulos + figuras + .bib
- [ ] Aplicar template LaTeX escolhido do catálogo `templates/`
- [ ] Compilar projeto gerado com pdflatex/latexmk
- [ ] Criar agente especializado `pdf2latex-agent`

## 3. Pipeline de Conversão

```
PDF ENTRADA
    │
    ├── 1. Extração de Texto ────► pdftotext / pdfminer / PyMuPDF
    │         │
    │         ├── 1a. Detecção de Estrutura (capítulos, seções)
    │         ├── 1b. Detecção de Equações ($$, \( \), align, etc.)
    │         └── 1c. Detecção de Referências (citações, \bibitem)
    │
    ├── 2. Extração de Imagens ──► pdfimages / PyMuPDF (pixmap)
    │         │
    │         └── 2a. Salvamento como PNG/JPEG + legendas
    │
    ├── 3. Detecção de Tabelas ──► camelot / pdfplumber
    │         │
    │         └── 3a. Conversão para tabular + longtable
    │
    ├── 4. Geração do Projeto ──► LaTeX generator
    │         │
    │         ├── 4a. main.tex (preamble + \include)
    │         ├── 4b. Capitulos separados (capitulo-01.tex, ...)
    │         ├── 4c. Figuras extraídas (figures/fig-001.png, ...)
    │         ├── 4d. Arquivo .bib com referências
    │         └── 4e. Makefile para compilação
    │
    └── 5. Aplicação de Template ──► template_integrator.py
              │
              └── 5a. Copiar template escolhido
              └── 5b. Adaptar preamble ao template
              └── 5c. Compilar projeto final
```

## 4. Arquitetura do Módulo

```
pdf2latex/
├── __init__.py              # Orquestrador principal
├── cli.py                   # Interface de linha de comando
├── extractor.py             # Extração de texto com estrutura
├── image_extractor.py       # Extração de figuras/imagens
├── table_detector.py        # Detecção e conversão de tabelas
├── equation_detector.py     # Detecção de equações matemáticas
├── reference_parser.py      # Extração de referências → .bib
├── latex_generator.py       # Geração do projeto LaTeX completo
├── template_integrator.py   # Aplicação de template ao projeto
└── utils.py                 # Utilitários diversos
```

## 5. Modos de Operação

### 5.1 Automático (padrão)
Pipeline completo: extrai tudo e gera projeto LaTeX com template default.

### 5.2 Modos Seletivos
- `--text-only`: Apenas extração de texto com estrutura
- `--with-figures`: Inclui extração de figuras
- `--with-tables`: Inclui detecção de tabelas
- `--with-equations`: Inclui detecção de equações
- `--with-references`: Inclui extração de referências

### 5.3 Por Template
- `--template <nome>`: Aplica template do catálogo (ex: abntex2, acm, ieee, nature)

### 5.4 OCR
- `--ocr`: Ativa OCR para PDFs escaneados (usa Tesseract)
- `--ocr-lang`: Idioma do OCR (por, eng, fra, etc.)

## 6. Integração com o Ecossistema

### Uso via CLI
```bash
python3 -m pdf2latex documento.pdf --template abntex2 --output ./meu-projeto
```

### Uso via agente
```
📄 "Converta este PDF para LaTeX usando template ABNT"
    → pdf2latex-agent: pipeline completo + template abntex2
```

### Uso via API Python
```python
from pdf2latex import PDF2LaTeX

converter = PDF2LaTeX("documento.pdf")
converter.extract_all()
converter.generate_project(output_dir="./projeto", template="abntex2")
converter.compile()
```

## 7. Templates Suportados

Todos os templates do catálogo `templates/` são suportados:
- `abntex2` — ABNT brasileiro (8 modelos)
- `abnt2025` — ABNT 2025
- `acm` — ACM
- `ieee` — IEEE
- `elsevier` — Elsevier
- `nature` — Nature
- `springer` — Springer
- `unb-monografia` — UnB
- `icmc` — ICMC-USP
- `victoria-regia` — Livro Victoria Regia
- E todos os demais...

## 8. Limitações Conhecidas

- PDFs escaneados sem OCR têm qualidade limitada
- Layouts complexos (multi-coluna) podem ter perda de ordenação
- Equações complexas podem exigir revisão manual
- Fontes embutidas não-padrão podem gerar caracteres ausentes

## 9. Referências

- `SPEC-962` → esta especificação
- `templates/README.md` → catálogo de templates
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)
- [camelot-py](https://github.com/camelot-dev/camelot)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
