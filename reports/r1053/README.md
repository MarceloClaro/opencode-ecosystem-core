# R1053 — síntese quantitativa human-gated e pacote de submissão

Data: 2026-11-04. Frente autorizada em duas etapas: R1053-A (meta-análise,
heterogeneidade, risco de viés e GRADE) e R1053-B (pacote de submissão).

## R1053-A — síntese quantitativa

### O que foi entregue

| Item | Caminho |
|---|---|
| Meta-análise e GRADE | `scientific_lab/quantitative.py` |
| Schema de entrada | `reports/r1053/example-input.json` |
| Exemplo de saída | `reports/r1053/example-result.json` |
| Spec | `specs/SPEC-1053-sintese-quantitativa-e-submissao.md` |
| Testes | `tests/test_r1053_quantitative.py` |

### Comando

```bash
python -m marceloclaro.scientific_lab research refresh \
  --out projects/tema-r1053 \
  --quantitative-data dados-de-efeito.json
```

### O que o módulo calcula

- efeitos fixos por variância inversa;
- efeitos aleatórios DerSimonian-Laird;
- Q, df, I², tau², H²;
- intervalo de confiança do efeito combinado;
- intervalo de predição com t de Student;
- resumo de risco de viés por estudo/domínio;
- rebaixamento GRADE por julgamento humano.

### Exemplo sintético

Entrada: 3 estudos, efeitos 0,0 / 0,8 / 0,4, erro-padrão 0,1, modelo aleatório.

| Métrica | Resultado |
|---|---|
| k | 3 |
| Efeito combinado | **0,400** |
| IC 95% | **−0,053 a 0,853** |
| Q (df) | **32,0 (2)** |
| I² | **93,75%** |
| tau² | **0,150** |
| Intervalo de predição | **−5,329 a 6,129** |
| Risco de viés alto | **1 estudo** |
| GRADE | **low** |

O intervalo de predição é muito amplo porque há apenas 3 estudos e
heterogeneidade substancial. Isso é um resultado matemático, não uma recomendação
clínica. O exemplo é **sintético**; nenhum dado real de paciente foi usado.

### O que o módulo recusa

- protocolo sem `human_confirmation=true`;
- menos estudos que `min_studies`;
- efeito não finito ou erro-padrão ≤ 0;
- estudo sem risco de viés;
- `study_id` duplicado;
- GRADE sem humano ou sem razão para julgamento sério/muito sério.

### O que o módulo não faz

- não extrai efeitos de PDFs;
- não imputa dados faltantes;
- não decide risco de viés;
- não atribui nota GRADE automaticamente;
- não declara verdade, eficácia ou causalidade.

## R1053-B — pacote de submissão

### O que foi entregue

| Item | Caminho |
|---|---|
| Gerador de submissão | `scientific_lab/submission.py` |
| Testes | `tests/test_r1053_submission.py` |

### Comando

```bash
python -m marceloclaro.scientific_lab research submission \
  --out projects/tema-r1053 \
  --journal "Revista de Teste" \
  --figures-dir figures \
  --tables-dir tables
```

### Estrutura

```text
10_submission/
  manuscript.md
  manuscript.tex
  manuscript.docx
  manuscript.pdf
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

### O que é gerado de fato

- Markdown sempre;
- LaTeX e DOCX se `pandoc` existir;
- PDF se `latexmk`/`pdflatex` existir;
- `.bib` a partir de `references.json`;
- template ABNT genérico;
- checklist e declarações `pending_human`;
- carta de submissão como template;
- manifesto com hashes e status das ferramentas.

No ambiente desta execução, `pandoc`, `latexmk` e `pdflatex` estavam presentes.
O teste de integração gerou `manuscript.tex`, `manuscript.docx` e um
`manuscript.pdf` de 90 KB. Isso prova a conversão local, **não** conformidade
ABNT ou aceite editorial.

### O que não é gerado

- conformidade ABNT certificada;
- regras específicas do periódico;
- declaração ética inventada;
- conflito de interesse inventado;
- submissão ou publicação automática.

## Validação

| Verificação | Resultado |
|---|---|
| Testes R1053 | **13 passed** (inclui o teste de perfil real do R1054) |
| R1051 + R1052 + R1053 | **42 passed** |
| Regressão R1033–R1053 | **388 passed, 1 skipped** |
| Guard Remotion | **11 casos, ok** |
| `doctor` | **healthy 22/22** |
| Dados reais de meta-análise | **nenhum** |
| Submissão/publicação | **nenhuma** |

## Limites

- A meta-análise é apenas sobre os efeitos e erros declarados.
- O intervalo de predição usa t tabelado até df=30; acima, aproximação normal.
- GRADE é um rebaixamento por julgamento humano, não uma avaliação completa.
- O template ABNT é genérico.
- DOCX/PDF dependem de ferramentas locais.
- O checklist e as declarações precisam de preenchimento humano.
- Nada foi submetido ou publicado.
