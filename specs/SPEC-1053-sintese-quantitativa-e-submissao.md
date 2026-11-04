---
spec_id: SPEC-1053
title: Síntese quantitativa human-gated e pacote de submissão
version: 1.0.0
status: green
test_file: tests/test_r1053_quantitative.py, tests/test_r1053_submission.py
---

# SPEC-1053 — síntese quantitativa e submissão, sem automação de julgamento

## Problema

O R1051–R1052 entregou recuperação, texto integral, triagem humana, integridade
e manuscrito para validação. Faltavam duas camadas:

1. **síntese quantitativa** com efeitos declarados, heterogeneidade, risco de
   viés e GRADE;
2. **pacote de submissão** com LaTeX/DOCX, template ABNT genérico, checklist e
   declarações.

A camada quantitativa não pode extrair efeitos de PDFs nem decidir risco de
viés/GRADE. Ela deve exigir protocolo humano e dados declarados.

## R1053-A — síntese quantitativa

### Entrada

JSON com:

```json
{
  "project_id": "RP-...",
  "protocol": {
    "reviewer": "nome",
    "declared_at": "ISO",
    "effect_measure": "SMD",
    "model": "random",
    "confidence_level": 0.95,
    "min_studies": 3,
    "max_i2_for_pooling": 75,
    "human_confirmation": true
  },
  "studies": [
    {
      "study_id": "S1",
      "effect_size": 0.4,
      "standard_error": 0.1,
      "risk_of_bias": {
        "overall": "low",
        "domains": {"randomization": "low"}
      }
    }
  ],
  "grade": {
    "human_confirmation": true,
    "reviewer": "nome",
    "declared_at": "ISO",
    "starting_level": "high",
    "domains": {
      "risk_of_bias": {"judgment": "serious", "reason": "..."},
      "inconsistency": {"judgment": "serious", "reason": "..."},
      "indirectness": {"judgment": "not_serious", "reason": "..."},
      "imprecision": {"judgment": "not_serious", "reason": "..."},
      "publication_bias": {"judgment": "not_serious", "reason": "..."}
    }
  }
}
```

### Cálculos

- Efeitos fixos por variância inversa.
- Efeitos aleatórios DerSimonian-Laird.
- Q, df, I², tau², H².
- Intervalo de confiança do efeito combinado.
- Intervalo de predição com t de Student (tabela 1–30; aproximação normal acima).
- Resumo de risco de viés por estudo/domínio.
- GRADE por rebaixamento declarado, sem nota automática.

### Critérios de aceitação

1. Protocolo sem `human_confirmation=true` é recusado.
2. Menos estudos que `min_studies` é recusado.
3. `effect_size` não finito ou `standard_error <= 0` é recusado.
4. Estudo sem `risk_of_bias` é recusado.
5. `study_id` duplicado é recusado.
6. GRADE exige humano e razão para julgamento sério/muito sério.
7. O resultado registra `truth_claim=false`, `external_validation=false` e
   `human_review_required=true`.
8. Nenhum efeito é extraído de PDF ou resumo.
9. O artefato é gravado em `04_analysis/quantitative-synthesis.json`.
10. O manuscrito ganha seção de síntese quantitativa e a auditoria verifica
    protocolo, pooled finito, I² em [0,100] e GRADE humano.

## R1053-B — pacote de submissão

### Saída

```text
10_submission/
  manuscript.md
  manuscript.tex
  manuscript.docx        # se pandoc
  manuscript.pdf         # se latexmk/pdflatex
  references.bib
  abnt-template.tex
  journal-checklist.json
  declarations.json
  declarations.md
  cover-letter.md
  figures/
  tables/
  submission-manifest.json
  README.md
```

### Critérios de aceitação

1. Markdown é sempre copiado.
2. LaTeX/DOCX são gerados quando `pandoc` existe; caso contrário, status
   `unavailable`.
3. PDF é gerado quando `latexmk`/`pdflatex` existe; caso contrário, status
   `unavailable`.
4. `references.bib` é gerado a partir de `references.json`.
5. Template ABNT é genérico e explicitamente não certificado.
6. Checklist e declarações ficam `pending_human`.
7. Carta de submissão é template, sem fato inventado.
8. Figuras/tabelas são copiadas com hash e limite de 50 MB.
9. Manifesto lista arquivos, hashes e ferramentas.
10. Nada é submetido ou publicado.
11. `refresh --submission` inclui `10_submission` no manifesto principal e na
    auditoria.
12. CLI expõe `research submission` e flags `--journal`, `--figures-dir`,
    `--tables-dir`.

## RED/GREEN

RED: 12 testes novos falharam antes dos módulos `quantitative` e `submission`
e da integração.

GREEN: `tests/test_r1053_quantitative.py` e
`tests/test_r1053_submission.py` passam; a regressão R1051–R1053 fica em
**41 passed**; a regressão focada R1033–R1053 fica em **388 passed, 1 skipped**.

## Evidência de execução

- Testes R1053: **12 passed**.
- R1051+R1052+R1053: **41 passed**.
- Regressão focada R1033–R1053: **388 passed, 1 skipped**.
- `doctor`: **healthy 22/22**.
- Guard Remotion: **11 casos, ok**.
- `pandoc`, `latexmk` e `pdflatex` presentes; o teste de integração gerou
  `.tex`, `.docx` e `.pdf` (90 KB) a partir do template genérico.
- Nenhum dado real de meta-análise foi usado; o exemplo é sintético.
- Nenhuma submissão, publicação ou credencial.

## Limitações

- A meta-análise usa apenas efeitos/erros declarados; não faz extração
  automática, imputação ou ajuste de risco de viés.
- O intervalo de predição usa t tabelado até df=30; acima disso, aproximação
  normal declarada.
- GRADE é rebaixamento por julgamento humano, não uma avaliação completa de
  certeza.
- O template ABNT é genérico e não certifica conformidade.
- A conversão DOCX/PDF depende de ferramentas locais.
- O checklist e as declarações exigem preenchimento humano.
- Nada foi submetido ou publicado.
