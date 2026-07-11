# R141 — Engine `ocr-vision` para documentos antigos (SPEC-1001)

## Objetivo

Adicionar ao pdf2latex um engine opcional de alta recuperação de texto para
documentos antigos/escaneados — OpenCV → remoção de assinatura → PaddleOCR →
correção contextual por Vision LLM — encaixado no adapter pattern do
SPEC-1000, com **fidelidade** como princípio inegociável.

## Contexto

O usuário propôs o pipeline (que costuma superar Tesseract/ABBYY isolados em
documentos antigos) e perguntou se ajudaria o ecossistema. Ajuda, e encaixa
como um novo `BaseEngine` sem redesenho. O risco real é o passo de correção
por LLM **alucinar** — "consertar" inventando texto. A entrega trata isso
como o núcleo, não um detalhe.

## Mudanças Entregues

1. **`specs/SPEC-1001-*.md`**: especifica o engine e, sobretudo, a política
   de correção fiel (sugere + marca, nunca reescreve cego).
2. **`tests/test_r141_ocr_vision_engine.py`** (novo, 12 testes, TDD
   vermelho→verde): registro/disponibilidade; **política de correção pura**
   (vazio/idêntico → mantém OCR; divergência baixa → aceita; divergência
   alta → NUNCA aplica, marca para revisão); orquestração `process_page`;
   `convert` agregando páginas/flags; `RuntimeError` quando indisponível;
   `best()` não escolhe o engine indisponível.
3. **`pdf2latex/engines/ocr_vision.py`** (novo):
   - `apply_correction_policy(...)` — função pura (só `difflib`), coração da
     fidelidade;
   - `OcrVisionEngine(BaseEngine)` com **injeção de dependência**
     (preprocessor/signature_remover/ocr/corrector/page_loader) → testável
     sem opencv/paddleocr/visão; deps reais carregadas sob demanda;
   - auto-registro guardado em `engines/__init__.py`.

## Verificação

- TDD: 12 testes escritos antes → vermelho (11 falhas) → verde após impl.
- `python3 -m pytest tests/ -q` completo.
- `python3 -m pdf2latex --list-engines` mostra `ocr-vision` (indisponível
  sem deps — degradação graciosa, como o docling).

## Lições

1. **A fidelidade tem de ser código, não intenção.** O ganho de recuperação
   de texto vem junto do risco de alucinação; a política `sugere → compara
   divergência → só aplica typo-level, senão marca` transforma o princípio
   anti-overclaim em comportamento verificável (7 dos 12 testes miram nisso).
2. **Injeção de dependência = testar o contrato sem a inferência.** Fakes de
   preprocessor/ocr/corrector cobrem toda a orquestração sem exigir opencv/
   paddleocr/modelo de visão — mesmo princípio dos testes de superfície do
   R139, sem flakiness.
3. **Opt-in por custo.** Vision LLM por página pesa na token economy; o
   engine fica fora da auto-seleção padrão (opt-in via `--engine ocr-vision`).

## Score

**8.4/10**

- Entrega um engine real, encaixado na arquitetura, com a fidelidade travada
  por testes — o ponto que mais importa para este ecossistema.
- Não implementa os backends reais (OpenCV/PaddleOCR/pdf2image/visão) nem o
  modelo de remoção de assinatura — só o contrato e a política. Recuperação
  E2E em corpus real e benchmark vs Tesseract ficam como trabalho futuro.
