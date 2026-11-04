# Pesquisador científico — R1054: automação assistida e validação real

O R1054 implementa a sequência autorizada:

1. extração automática de efeitos de texto integral;
2. risco de viés e GRADE automáticos como sugestão auditável;
3. perfil real do periódico PLOS ONE;
4. submissão automática fail-closed;
5. gate de validação externa, aceite editorial e publicação;
6. validação numérica com uma meta-análise publicada (BCG).

A regra central: **automação com rastro, não autoridade automática**.

## Extração automática de efeitos

```bash
python -m marceloclaro.scientific_lab research extract-effects \
  --out projects/tema-r1054 \
  --fulltext-dir /caminho/dos/pdfs \
  --reviewer "Nome do revisor" \
  --confirm
```

Gera:

```text
04_analysis/auto-effect-candidates.json
04_analysis/auto-quantitative-draft.json
```

O rascunho tem status `automated_draft`, método `REML`, efeitos em escala log
para OR/RR/HR e risco de viés `not_assessed`. Só entra na meta-análise com
`human_confirmation=true`.

Limites:

- regex não lê tabelas, figuras ou PDF sem camada textual;
- medidas mistas exigem decisão humana;
- todo recorte precisa de conferência.

## Risco de viés e GRADE automáticos

```bash
python -m marceloclaro.scientific_lab research auto-rob-grade \
  --out projects/tema-r1054 \
  --data dados-de-efeito.json \
  --fulltext-dir /caminho/dos/pdfs \
  --reviewer "Nome do revisor" \
  --confirm
```

Gera:

```text
04_analysis/auto-rob-grade.json
04_analysis/quantitative-auto.json
```

As sugestões têm `automated=true` e `authoritative=false`. Não são RoB 2,
ROBINS-I ou GRADE de painel.

## Perfil real: PLOS ONE

```bash
python -m marceloclaro.scientific_lab research submission \
  --out projects/tema-r1054 \
  --journal-profile plos-one
```

O perfil transcreve regras públicas verificadas em 2026-11-04:

- inglês;
- resumo ≤ 300 palavras, sem citações;
- título ≤ 250 caracteres;
- Vancouver/ICMJE;
- seções obrigatórias;
- figuras separadas;
- declarações de financiamento, conflitos, dados, autoria, ORCID e ética.

Gera `journal-compliance.json` e um checklist específico. O manuscrito em
português é corretamente marcado como `blocked`; um manuscrito em inglês com as
seções e citações numéricas fica `pending_human` por causa das declarações.

## Submissão automática fail-closed

```bash
python -m marceloclaro.scientific_lab research submit \
  --out projects/tema-r1054 \
  --profile plos-one \
  --confirm
```

Sem backend injetado, retorna `no_submission_backend_configured`. O Core não
possui portal ou credenciais embutidos. Nenhuma submissão real é feita.

## Validação externa, aceite e publicação

```bash
python -m marceloclaro.scientific_lab research publication-gate \
  --out projects/tema-r1054 \
  --attach-external validacao-externa.json \
  --attach-acceptance aceite.json \
  --attach-authorization autorizacao.json
```

O gate confere:

- validação externa independente com hash do manuscrito;
- carta de aceite com hash;
- autorização do autor vinculada ao manuscrito.

Só então retorna `cleared_for_publication`. `publication_performed=false`
sempre. O gate não emite aceite nem publica.

## Validação real BCG

```bash
python -m marceloclaro.scientific_lab research benchmark-meta \
  --data reports/r1054/bcg.csv \
  --reference reports/r1054/reference.json \
  --out projects/tema-r1054
```

Resultado:

| Métrica | Core REML | Referência pública |
|---|---|---|
| k | 13 | 13 |
| OR | 0,474649896 | 0,474649913 |
| tau² | 0,337772471 | 0,337772045 |
| Q | 163,164915 | 163,164915 |
| I² padrão | 92,6455% | 92,6455% |
| I² publicado | 92,6455% | 92,0727% |

A diferença do I² publicado (0,5728 p.p.) está registrada. A referência é uma
reanálise pública REML, não o texto original de 1994.

## Limites

- Extração, RoB e GRADE são assistivos, não autoritativos.
- PLOS ONE é um perfil parcial e datado.
- Submissão real exige backend e credenciais.
- Validação externa e aceite exigem artefatos institucionais reais.
- Nada foi submetido, aceito ou publicado.

## Evidência

- [README R1054](../reports/r1054/README.md)
- [Benchmark BCG](../reports/r1054/real-meta-benchmark.json)
- [Dataset e fonte](../reports/r1054/SOURCE.md)
- [Spec R1054](../specs/SPEC-1054-automacao-assistida-validacao-real.md)
