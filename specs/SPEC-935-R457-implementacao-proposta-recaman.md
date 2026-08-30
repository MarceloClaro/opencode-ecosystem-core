---
spec_id: SPEC-935-R457
title: Implementação da proposta pós-Recamán — diversificador estruturado determinístico
component: rag/recaman.py, rag/enhanced_search_rag.py
status: green
round_id: R457
test_file: tests/test_r457_recaman_diversifier.py
---

# SPEC-935-R457 — Implementação da proposta pós-Recamán

## Objetivo

Implementar, em código, a **arquitetura-alvo proposta** documentada no manual
(docs/r456_manual_tecnico_rag, SPEC-935-R456): um conjunto de 4 artefatos que
diversificam de forma **determinística** e **estruturada** o ranking pós-ranqueado
da arquitetura RAG, fechando a lacuna de métrica de diversidade do painel
`EnhancedRAG.metrics()`.

A implementação é **aditiva, de baixo acoplamento e não-invasiva**: cria um novo
módulo `rag/recaman.py` e acrescenta um campo novo (`diversity`) ao dicionário de
métricas, **sem alterar o contrato** dos campos existentes nem o comportamento dos
ranqueadores atuais.

## Definição matemática da proposta (do manual, Seções 5–6)

**Sequência de Recamán** (OEIS A005132):
`a₀ = 0`, `aₙ = aₙ₋₁ − n` se `aₙ₋₁ − n > 0` e não visitado, senão `aₙ = aₙ₋₁ + n`.

**Offset do índice** para um ranking de `N` candidatos: `offset = aₙ mod N`
(Tabela 1 do manual: N=8 → índices `1,2,4,7,3,0`).

**Métrica de diversidade** (Eq. 6.1 do manual):
`Div(S) = 1/(|S|(|S|−1)) · Σ_{i≠j, r_i,r_j∈S} (1 − Sim(r_i, r_j))`,
onde `Sim ∈ [0,1]` é uma medida de similaridade sobre **âncoras canônicas**
(identidade de fonte/âmago), garantindo "diversidade efetiva" e não "variedade de
redação".

**Custo**: geração da sequência em `O(M)`; seleção pós-ranqueamento em `O(N)`.

## Critérios de Aceitação Executáveis

- `module_exists` — existe `rag/recaman.py` importável.
- `recaman_sequence_oracle` — `recaman_sequence(n)` retorna `[0,1,3,6,2,7,13,...]`
  para os primeiros termos (oráculo OEIS A005132), com `a₅ = 7`.
- `recaman_terminates` — a geração da sequência termina para todos os `N` e `k`
  razoáveis (sem loop infinito; via implementação iterativa com conjunto visitado).
- `diversifier_indices` — para `N=8`, os offsets/índices selecionados seguem
  `1,2,4,7,3,0` (Tabela 1 do manual), determinísticos.
- `diversifier_deterministic` — a diversificação é reproduzível: mesma entrada,
  mesma saída, sem seed.
- `diversifier_preserves_rank` — a relevância primária do topo não é descartada:
  um elemento de rank `0` (top-1 relevante) é sempre incluído na saída.
- `diversifier_within_budget` — retorna exatamente `k` itens (ou menos se `N<k`),
  sem duplicatas.
- `anchor_resolver_dedup` — `AnchorResolver` deduplica por identidade de âncora
  canônica (mesma fonte/âmago agrupa em um só âncora).
- `metric_diversity_range` — `diversity(S)` retorna valor em `[0,1]`.
- `metric_diversity_same` — itens idênticos (Sim=1) → `Div ≈ 0`.
- `metric_diversity_distinct` — itens disjuntos (Sim=0) → `Div = 1`.
- `packer_canonical` — `CanonicalContextPacker` posiciona âncoras canônicas de
  forma determinística (núcleo/relevantes no início e fim, mitigando
  "lost in the middle").
- `integration_enhanced_metrics` — `EnhancedRAG.metrics()` passa a incluir o campo
  `diversity` além dos 4 existentes, sem remover/renomear nenhum.
- `metrics_backward_compatible` — a chamada de `metrics()` com lista vazia continua
  retornando os 4 campos originais + `diversity: 0.0` (sem quebra).
- `aditivo_nao_invasivo` — `rag/evolved.py` e `rag/enhanced_search_rag.py` não têm
  seu comportamento de ranqueamento alterado (nenhuma remoção de API pública).

## Estratégia TDD

1. Escrever testes (RED) em `tests/test_r457_recaman_diversifier.py` cobrindo os
   critérios executáveis acima.
2. Implementar `rag/recaman.py` (GREEN): `recaman_sequence`, `ArtifactType`,
   `AnchorResolver`, `RecamanDiversifier`, `CanonicalContextPacker`, `diversity`.
3. Integrar (GREEN) o campo `diversity` em `EnhancedRAG.metrics()` de forma
   aditiva no `rag/enhanced_search_rag.py`.
4. Reexecutar R455/R456 e o `doctor`; registrar recibo local e ciclo evolutivo
   R457.

## Não objetivos

- Não alterar o ranqueamento primário (BM25/denso) nem o roteamento adaptativo.
- Não introduzir dependências externas novas (módulo 100% stdlib).
- Não promover o diversificador ao pipeline padrão sem avaliação empírica —
  expõe-se a API, mas o fluxo principal permanece configurável/desligado.
- Não alegar ganhos de qualidade medidos (isso exige experimento de coorte
  futuro); esta spec apenas implementa a capacidade e a métrica.
