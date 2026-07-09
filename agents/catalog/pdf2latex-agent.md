# pdf2latex-agent — Agente de Conversão PDF → LaTeX

**Parte do OpenCode Ecosystem Core**
**SPEC-962** — Implementado em 2026-07-09

## Descrição

Agente especializado na conversão de documentos PDF para projetos LaTeX completos. Utiliza o pipeline `pdf2latex` com extração de texto, estrutura, figuras, tabelas, equações e referências, aplicando templates do catálogo do ecossistema.

## Competências

### Pipeline Completo
1. **Extrair texto**: pdftotext + pdfminer + OCR (Tesseract) para PDFs escaneados
2. **Detectar estrutura**: capítulos, seções, subseções automaticamente
3. **Extrair figuras**: pdfimages + PyMuPDF (todas as imagens embutidas)
4. **Detectar tabelas**: camelot-py + pdfplumber → tabular LaTeX
5. **Detectar equações**: padrões LaTeX e heurísticas → math mode
6. **Extrair referências**: detecção de citações → arquivo .bib
7. **Gerar projeto**: main.tex + capítulos separados + figures/ + .bib + Makefile
8. **Aplicar template**: todos os templates do catálogo `templates/`

## Como usar

### Via CLI
```bash
# Conversão básica
python3 -m pdf2latex documento.pdf

# Com template ABNT
python3 -m pdf2latex documento.pdf --template abntex2 --output ./meu-projeto

# Para PDF escaneado (OCR)
python3 -m pdf2latex documento.pdf --ocr --ocr-lang por

# Compilar automaticamente após conversão
python3 -m pdf2latex documento.pdf --template ieee --compile

# Listar templates disponíveis
python3 -m pdf2latex --list-templates
```

### Via Python
```python
from pdf2latex import PDF2LaTeX

conv = PDF2LaTeX("artigo.pdf", template="acm")
conv.convert(output_dir="./artigo-latex")
conv.compile()
```

### Via Orquestrador (marceloclaro)
O agente `marceloclaro` pode delegar a conversão para este agente quando o usuário solicitar transformação de PDF para LaTeX.

## Templates suportados

| Nome | Descrição |
|------|-----------|
| `abntex2` | ABNT brasileiro (8 modelos) |
| `abnt2025` | ABNT 2025 |
| `acm` | Association for Computing Machinery |
| `ieee` | IEEE |
| `elsevier` | Elsevier |
| `nature` | Nature Portfolio |
| `springer` | Springer Nature |
| `tandf` | Taylor & Francis |
| `mdpi` | MDPI |
| `sbc` | SBC |
| `icmc` | ICMC-USP |
| `unb-monografia` | UnB |
| `usp` | USP |
| `ipleiria` | IPLeiria |
| `victoria-regia` | Victoria Regia (livro) |
| `book-simple` | Livro simples |
| `artigo-qualis-a1` | Qualis A1 |

## Flags de controle

| Flag | Efeito |
|------|--------|
| `--ocr` | Ativa OCR para PDFs escaneados |
| `--ocr-lang` | Idioma do OCR (padrão: por+eng) |
| `--no-tables` | Pular detecção de tabelas |
| `--no-equations` | Pular detecção de equações |
| `--no-references` | Pular extração de referências |
| `--no-images` | Pular extração de imagens |
| `--compile` | Compilar projeto após gerar |
| `--verbose` | Modo verboso (debug) |

## Fluxo de trabalho

1. Usuário fornece PDF e especifica template desejado
2. Agente executa pipeline de extração:
   - Extrai texto com estrutura hierárquica
   - Extrai imagens e figuras
   - Detecta tabelas e converte para tabular
   - Detecta equações matemáticas
   - Extrai referências bibliográficas
3. Gera projeto LaTeX completo (main.tex + capítulos + figures + .bib + Makefile)
4. Aplica template escolhido do catálogo
5. (Opcional) Compila projeto com latexmk
6. Retorna caminho do projeto gerado

## Referências

- SPEC-962 — Especificação formal PDF-to-LaTeX
- `templates/README.md` — Catálogo completo de templates
- Módulo: `pdf2latex/` no diretório raiz do ecossistema
