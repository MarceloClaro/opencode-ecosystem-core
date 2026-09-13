# SPEC-935-R494 — Structural Noise Scanner (SNS)

Status: **implementado** (R494)
Data: 2026-09-13
Requer: — (stdlib); proposta do usuário "Structural Noise Scanner (SNS)".

## 1. Contexto (proposta do usuário)

Em fenômenos complexos, nem tudo que aparece é estruturalmente relevante:
exemplos redundantes, metáforas, variações superficiais, diferenças
terminológicas, ruído contextual, representações múltiplas da mesma função.
O problema não é remover informação — é **remover ruído sem eliminar função
relevante**.

    C = E + S + R          (corpus = exemplos + estruturas + ruído)
    C' = S + E*            (modelo reduzido: estruturas + exemplos mínimos)
    Reconstrução(C') ≈ Estrutura(C)

## 2. Objetivos

- **OF1** — `ElementClassifier`: classifica cada elemento (exemplo, estrutura,
  ruído, redundância, vetor explicativo) por heurística lexical determinística.
- **OF2** — `FunctionPreservationEngine`: função = vocabulário funcional
  (palavras de conteúdo; stopwords removidas); verifica se a função permanece
  representada após remoção.
- **OF3** — `StructuralCompression`: agrupa manifestações com mesmo vocabulário
  funcional em cluster → estrutura comum (termos intersectados).
- **OF4** — `ReconstructionTest`: score de reconstrução = fração das funções
  originais ainda presentes no modelo reduzido.
- **OF5** — `RelevanceProtectionLayer`: regras de remoção do usuário (função
  representada em outro / retirada não altera reconstrução / repetição sem
  função nova).
- **OF6** — Métricas: SPS ≥ 0.90 (segura), 0.70–0.90 (moderada, exige revisão),
  < 0.70 (destrutiva); NRR; FLI.

## 3. Modelo formal

```
token_funcional(s) = palavras(s) − stopwords (minúsculas, sem pontuação)
função(e)          = foque nos tokens de conteúdo com len ≥ 3

similaridade(a,b)  = |A ∩ B| / |A ∪ B|  (Jaccard sobre tokens funcionais)

classificação(e):
    se similaridade(e, existentes) > 0.75           → redundância
    senão se marcador de exemplo (ex:, como, por exemplo, nome próprio) → exemplo
    senão se parágrafo/âncora ou tem 'é/significa/consiste'             → vetor explicativo
    senão → estrutura (ou ruído se sem tokens funcionais)

compressão: clusters conectados com Jaccard ≥ 0.60 → estrutura comum =
            interseção dos tokens (fallback: união ponderada)

SPS = |funções preservadas| / |funções totais|
NRR = |elementos classificados ruído| / |elementos totais|
FLI = |funções perdidas| / |funções totais|
Nível: SPS ≥ 0.90 seguro | 0.70 ≤ SPS < 0.90 moderado | SPS < 0.70 destrutivo
```

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Classificador identifica redundância (duplicata com alta similaridade) |
| CA2 | Classificador identifica exemplo (marcador `ex:`/`por exemplo`/nome próprio) |
| CA3 | Função preservada: remoção de elemento cuja função existe em outro não perde função |
| CA4 | Função perdida: elemento único removido → FLI > 0 |
| CA5 | Compressão agrupa manifestações equivalentes em estrutura comum |
| CA6 | SPS ≥ 0.90 para corpus com redundâncias removíveis |
| CA7 | NRR = ruído removido / total |
| CA8 | FLI = funções perdidas / funções totais |
| CA9 | Reconstruction test: score = funções presentes / totais |
| CA10 | RelevanceProtection protege elemento único (função não representada em outro) |
| CA11 | Anti-overclaim: sem `superhuman`, `verificad[oa]s?`, `qualis a1`, `superação`; docs do algoritmo |
| CA12 | Determinismo; corpus vazio → relatório vazio sem erro |

## 5. Entregáveis

- `scanners/noise_scanner.py` — `ElementClassifier`, `FunctionPreservation`,
  `StructuralCompression`, `ReconstructionTest`, `RelevanceProtection`,
  `NoiseScanReport`, `StructuralNoiseScanner`
- `tests/test_r494_noise_scanner.py`
- ciclo R494 + commit

## 6. Prontidão

- `pytest tests/test_r494_noise_scanner.py` verde; regressões R483-R493
  verdes