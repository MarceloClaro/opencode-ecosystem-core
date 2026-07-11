# SPEC-1001: Engine `ocr-vision` — OCR de documentos antigos com correção contextual fiel

**Status:** Especificado (TDD)
**Versão:** 1.0.0
**Depende de:** SPEC-1000 (arquitetura multi-engine do pdf2latex)
**Ciclo:** R141
**Arquivo de testes:** `tests/test_r141_ocr_vision_engine.py`

## 1. Objetivo

Adicionar ao pdf2latex um **engine opcional** de alta recuperação de texto
para documentos **antigos/escaneados/de baixa qualidade**, onde o engine
`builtin` (pdfminer + Tesseract) rende pouco. O pipeline é:

```
Imagem → OpenCV (deskew + denoise + binarização)
       → remoção de assinatura
       → PaddleOCR (texto + confiança por região)
       → Vision LLM (correção contextual — SUGERE, não reescreve cego)
       → Texto final + regiões marcadas para revisão
```

Ele encaixa no adapter pattern do SPEC-1000 como um novo `BaseEngine`
(`name = "ocr-vision"`), sem alterar a arquitetura existente.

## 2. Princípio inegociável: fidelidade > fluência

O passo "Vision LLM corrige usando contexto" **pode alucinar** — "consertar"
inventando texto plausível que não existia no documento. Para material
histórico/jurídico isso é inaceitável. Portanto a **política de correção**
é o núcleo desta spec, e não um detalhe:

- A correção do LLM é **sugestão**, comparada ao texto do OCR por
  divergência (`1 - ratio` de `difflib.SequenceMatcher`).
- **Divergência baixa** (nível-caractere, típico de typo de OCR) → aceita a
  sugestão.
- **Divergência alta** (reescrita) → **NUNCA aplica**; mantém o texto do OCR
  e **marca a região para revisão humana** (`structure["ocr_review_flags"]`).
- Sugestão vazia ou idêntica → mantém o OCR.

Isso é coerente com a política anti-overclaim do ecossistema
(`CORRIGENDUM.md`, `metacognitive_evaluator`): o sistema não afirma texto que
não pode sustentar.

## 3. Design

- **`pdf2latex/engines/ocr_vision.py`**:
  - `apply_correction_policy(ocr_text, suggestion, *, ocr_confidence, max_divergence=0.35) -> CorrectionOutcome`
    — função **pura** (só stdlib `difflib`), o coração testável da fidelidade.
  - `class OcrVisionEngine(BaseEngine)` com **injeção de dependência**
    (`preprocessor`, `signature_remover`, `ocr`, `corrector`, `page_loader`),
    para que o engine seja testável sem `opencv`/`paddleocr`/modelo de visão.
  - `is_available()`: `True` se os componentes forem injetados **ou** se
    `cv2` + `paddleocr` importarem; `False` caso contrário (degradação
    graciosa — em ambiente sem deps o registro segue funcionando).
  - `process_page(image, *, context, page)`: orquestra o pipeline de UMA
    página e devolve `{text, confidence, replaced, flagged, flag}`.
  - `convert(pdf_path, **kwargs) -> ConversionResult`: carrega páginas,
    roda `process_page`, agrega texto e confiança (média), coleta as flags
    em `structure["ocr_review_flags"]`. Levanta `RuntimeError` claro quando
    indisponível.
- **Auto-registro** em `engines/__init__.py` (import guardado, como o
  docling_engine).

## 4. Custo e opt-in

Vision LLM por página tem custo de token/latência (relevante para a
*token economy* do ecossistema). Por isso o `ocr-vision` **não** entra na
ordem de auto-seleção padrão (`["docling","mineru","builtin"]`); é opt-in via
`--engine ocr-vision`. As dependências (`opencv-python`, `paddleocr`,
`pdf2image`, modelo de visão via OpenAI/Ollama do R128) são opcionais.

## 5. Critérios de Aceitação

- **CA-1:** `ocr-vision` aparece em `list_engines()` com `requires_gpu=False`.
- **CA-2:** `is_available()` retorna `bool`; `False` quando faltam deps e não
  há componentes injetados; `True` quando injetados.
- **CA-3 (fidelidade):** `apply_correction_policy`:
  - sugestão vazia/idêntica → mantém OCR, `replaced=False`, `flagged=False`;
  - divergência ≤ `max_divergence` → `replaced=True`, `text == suggestion`;
  - divergência > `max_divergence` → `replaced=False`, `flagged=True`,
    `text == ocr_text` (jamais aplica a reescrita).
- **CA-4:** `process_page` roda preprocessor → signature_remover → ocr →
  corrector (injetados) e aplica a política; reescrita divergente vira flag.
- **CA-5:** `convert` com componentes injetados agrega páginas, calcula
  confiança média, coleta `ocr_review_flags` e marca `engine_used="ocr-vision"`.
- **CA-6:** `convert` levanta `RuntimeError` quando indisponível.
- **CA-7:** o engine indisponível **não** é escolhido por `best()` (fallback
  para `builtin`).

## 6. Estratégia de Verificação

- TDD: `tests/test_r141_ocr_vision_engine.py` escrito antes; vermelho → verde.
- Testes cobrem a política de correção (pura) e a orquestração via injeção
  de fakes — **sem** exigir `opencv`/`paddleocr`/modelo de visão.
- `python3 -m pytest tests/ -q` completo (zero regressões).

## 7. Fora de escopo (trabalho futuro)

- Implementação real dos backends OpenCV/PaddleOCR/pdf2image e do modelo de
  visão (os componentes reais são carregados sob demanda; aqui garante-se o
  contrato e a política, não a inferência E2E).
- Modelo de remoção de assinatura treinado (interface pronta; peso não incluso).
- Benchmark de recuperação vs Tesseract/ABBYY em corpus real.
