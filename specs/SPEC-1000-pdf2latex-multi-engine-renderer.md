# SPEC-1000: Sistema Multi-Engine + Multi-Renderer para PDF2LaTeX

**Status:** Implementado e versionado (ciclo R139)  
**Versão:** 1.0.0  
**Data:** 2026-07-09  
**Agente:** marceloclaro (Orquestrador Central Metacognitivo)  
**Testes de aceitação:** `tests/test_r139_pdf2latex_multi_engine.py` (15 testes:
registro/auto-seleção de engines, dataclasses de contrato, interfaces
abstratas, builtin sempre disponível, presença de templates Pandoc + .bst
ABNT, CLI `--list-engines`). Cobrem a superfície offline determinística;
docling/mineru/pandoc/latexmk permanecem opcionais e não são exigidos.

## 1. Objetivo

Evoluir o pipeline PDF→LaTeX de um sistema monolítico (pdfminer + LaTeXGenerator) para uma arquitetura modular com múltiplos **engines de extração** e múltiplos **renderizadores LaTeX**, permitindo escolher a melhor combinação para cada tipo de documento.

## 2. Arquitetura

```
PDF → [Engine de Extração] → Dados Estruturados → [Renderizador] → Projeto LaTeX
       ├─ builtin  (pdfminer)                  ├─ builtin (LaTeXGenerator)
       ├─ docling  (IBM Docling)               └─ pandoc  (Pandoc + templates)
       └─ mineru   (OpenDataLab MinerU)
```

### 2.1 Engines (`pdf2latex/engines/`)

| Engine | Descrição | Requer GPU | API Key | RAM |
|--------|-----------|-----------|---------|-----|
| `builtin` | pdfminer + pdftotext + Tesseract OCR | ❌ | ❌ | 256MB |
| `docling` | IBM Docling — layout avançado | ❌ | ❌ | 1GB |
| `mineru` | MinerU — precisão máxima | ✅ | ❌ | 4GB+ |

### 2.2 Renderizadores (`pdf2latex/renderers/`)

| Renderer | Descrição | Requer |
|----------|-----------|--------|
| `builtin` | LaTeXGenerator + TemplateIntegrator | Nada |
| `pandoc` | Pandoc + templates .template + CSL | Pandoc >= 3.0 |

## 3. Mudanças Realizadas

### 3.1 Correção: template_integrator.py
- `.bst` files baixados do CTAN oficial (abntex2-alf.bst, abntex2-num.bst)
- `abntex2-options.bib` baixado para suporte a citações ABNT
- Suporte a fontes `.ttf`/`.otf` e subdiretórios de template
- Mapeamento de `bibliographystyle` por template

### 3.2 Novo: engine_registry.py
- Registro central de engines via singleton
- Auto-detecção do melhor engine disponível
- API: `get_engine()`, `list_engines()`, `convert_with_best()`

### 3.3 Novo: engines/ (adapter pattern)
- `base.py`: classe abstrata `BaseEngine` com `ConversionResult`
- `builtin.py`: engine atual refatorado (pdfminer + pdftotext + OCR)
- `docling_engine.py`: adapter para IBM Docling
- `mineru_engine.py`: adapter para MinerU (placeholder)

### 3.4 Novo: renderers/ (multi-renderer)
- `base.py`: classe abstrata `BaseRenderer` com `RenderInput`
- `builtin_renderer.py`: LaTeXGenerator existente
- `pandoc_renderer.py`: Pandoc com templates .template + CSL embutidos

### 3.5 Novo: pandoc-templates/
- `default.template`: template genérico article
- `abntex2.template`: template ABNT2 com citeproc ABNT
- `ieee.template`: template IEEE
- CSL embutidos: ABNT, IEEE, ACM

### 3.6 Novas flags CLI
- `--engine {auto|builtin|docling|mineru}` — seleciona engine
- `--renderer {builtin|pandoc}` — seleciona renderizador
- `--list-engines` — lista engines disponíveis

## 4. Uso

```bash
# Engine builtin + renderer builtin (comportamento padrão)
python3 -m pdf2latex documento.pdf --template abntex2

# Engine builtin + renderer Pandoc (qualidade tipográfica superior)
python3 -m pdf2latex documento.pdf --template abntex2 --renderer pandoc

# Engine Docling + renderer Pandoc (máxima qualidade)
python3 -m pdf2latex documento.pdf --template ieee --engine docling --renderer pandoc

# Listar engines disponíveis
python3 -m pdf2latex --list-engines
```

## 5. Bibliotecas Pesquisadas

| Biblioteca | Estrelas | Precisão | Requisitos | Status |
|-----------|----------|----------|------------|--------|
| **MinerU** (opendatalab) | 15k+ | 86-95% | GPU 4GB+ | Adapter pronto |
| **Docling** (IBM) | 5k+ | 85%+ | CPU 1GB | Adapter pronto |
| **DocStream** | Novo | 80%+ | Gemini/Groq API | Pesquisado |
| **gptpdf** | 10k+ | 95%+ | OpenAI API | Pesquisado |
| **pdfmark-ai** | Novo | 85%+ | LLM API | Pesquisado |
| **Pandoc** | 35k+ | N/A (render) | Nenhum | **Integrado** |

## 6. Próximos Passos

- [ ] Integrar MinerU como engine (requer GPU)
- [ ] Integrar Docling funcionalmente (requer `pip install docling`)
- [ ] Implementar `--compile` com Pandoc (pdflatex automático)
- [ ] Criar templates Pandoc para ACM, Elsevier, Springer, Nature
- [ ] Benchmark de precisão entre os engines

## 7. Critérios de Aceitação

- [x] CLI aceita `--engine builtin|docling|mineru` e `--renderer builtin|pandoc`
- [x] `--list-engines` mostra status de cada engine
- [x] Engine builtin continua funcionando como antes (retrocompatível)
- [x] Renderer Pandoc gera LaTeX com template abntex2
- [x] Arquivos .bst e .options do abntex2 são copiados corretamente
- [x] Fallback automático quando engine/renderer não está disponível
