---
name: producao-livro-quantico
description: Produz e verifica um livro didático de física quântica em escala, com SDD/TDD, prática manual, Python, hardware, Lean 4 e auditoria. Use ao gerar, reconstruir ou revisar obras longas em PDF navegável; não declare eficácia pedagógica, peer review ou 10/10 sem estudo e pareceres externos.
metadata:
  version: "1"
  origem: "R1099 — fábrica do livro Do Bit ao Todo"
---

# Produção de livro quântico

## Quando usar

Use quando a tarefa for criar, regenerar ou auditar uma obra longa de ensino de
informação quântica com laudas, fichas, experimentos, cálculo manual e prova
formal. Não use para um artigo curto ou para uma resposta isolada.

## Contrato

1. **Spec primeiro.** Toda mudança nasce de `specs/SPEC-935-R*.md` com critérios
   de aceitação.
2. **Manual antes do código.** A lauda deve prever, medir e limitar antes de
   rodar simulador.
3. **Testes antes do build.** `pytest` precisa passar antes de gerar o PDF.
4. **Build único.** O PDF é volume único, com links internos e marcadores.
5. **Auditoria.** Rodar contagem de rodapés, notas, links, repetição e Lean.

## Fluxo

```bash
# 1. estado
python3 -m marceloclaro.cli doctor

# 2. regenerar laudas e fichas
.venv-quantum/bin/python educacao_quantica_bohm/livro_pixel/gerar_secoes.py
.venv-quantum/bin/python educacao_quantica_bohm/scripts/gerar_fichas.py

# 3. auditar repetição
python3 scripts/auditar_repeticoes.py

# 4. testes
.venv-quantum/bin/python -m pytest educacao_quantica_bohm/tests/test_pixel_book.py -q

# 5. build
.venv-quantum/bin/python educacao_quantica_bohm/livro_pixel/build_pixel_fast.py

# 6. verificar links e Lean
.venv-quantum/bin/python - <<'PY'
from pypdf import PdfReader
r = PdfReader("educacao_quantica_bohm/livro_pixel/LIVRO_3000_LAUDAS.pdf")
print(len(r.pages), len(r.named_destinations))
PY
cd livro-core/lean && lake env lean QuantumTrails.lean
```

## Critérios de aceitação

- 3000 laudas e 100 fichas presentes.
- 3000 rodapés `LNNNN/3000` únicos.
- 400 notas de cálculo.
- Links internos resolvidos.
- Nenhuma chave literal.
- Lean compila sem `sorry`/`admit`.
- Relatório de repetição atualizado.

## Limites

Build verde não é aprovação científica. Eficácia, peer review e adoção
internacional exigem estudo com estudantes e pareceres externos. Declare
`protocol` ou `não medido` quando for o caso.
