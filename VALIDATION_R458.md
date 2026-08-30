# VALIDATION_R458 — Experimento de coorte Recamán vs MMR vs atual

**Status:** GREEN (testes passam) · **Resultado de hipótese:** `refuta_H2` (honesto)
**Escopo:** corpus-piloto controlado e determinístico — NÃO generaliza para produção.

## O que foi validado

- 11 contratos executáveis (`tests/test_r458_cohort_experiment.py`) passam:
  módulo existe, corpus determinístico com ≥3 ângulos, estratégias definidas,
  Recamán preserva top-1, determinismo, métricas em [0,1], queda relativa de
  groundedness ≤ 5% (Recamán não degradou: 0.0% de queda), relatório estruturado
  com veredito e rótulo de escopo.

## Métricas observadas (médias, n_queries=4, k=4)

| Estratégia | Div(S) | groundedness | coverage |
|---|---|---|---|
| atual (top-k) | 0.500 | 0.4561 | 0.667 |
| MMR (λ=0.7)  | 0.750 | 0.4256 | 0.917 |
| Recamán       | 0.500 | 0.4561 | 0.667 |

- `gain_div_vs_atual(Recamán) = 0.0` (empate, não ganho estrito).
- `mmr_supera_recaman = true` (baseline clássico diverge mais neste desenho).
- `loss_rel_groundedness(Recamán) = 0.0` (sem degradação de relevância).

## Descoberta científica (limite do esquema posicional)

Recamán diversifica **posição** (offsets determinísticos), não **âncora/fonte**.
Em rankings "localmente monopolistas" (3 docs da mesma família no topo — típico
de retriever que colapsa numa família), os offsets recaem na mesma família e o
resultado coincide com o top-k. MMR, maximizando dissimilaridade de conteúdo,
espalha por família e supera neste desenho.

## Detalhe metodológico (correções de validade aplicadas)

O benchmark passou por correções de validade até o run final:
1. Query equilibrada em ângulos (evita domínio da 1ª família por ordem de tokens).
2. **Dedup por documento** antes de diversificar — o `ScientificRAG.retrieve`
   retorna múltiplos chunks por doc; sem dedup, o topo é monopolizado por chunks
   do mesmo doc, impedindo qualquer diversificação observável (gargalo real do
   retrieve, documentado).
3. **Pool amplo** (`poll_size=40`) antes do corte — captura mais de uma família.
4. **Veredito anti-empate espúrio**: H2 exige ganho ESTRITO de diversidade;
   empate (0.0) é tratado como não-demonstração.

## Limites (anti-overclaim)

- NÃO promove o diversificador ao pipeline padrão.
- NÃO declara "Recamán melhor que MMR". O oposto foi observado.
- NÃO equivale a certificação externa; é observação em corpus sintético/piloto.
```
