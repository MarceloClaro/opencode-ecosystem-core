# Gates revisados — PEC 2q, ZNE, layouts e cortes

**Status:** política offline fail-closed; nenhum gate executado em hardware.

## 1. Por que revisar

Os gates anteriores eram heurísticos:

- PEC 2q exigia 15 taxas, mas 2 são gauge;
- ZNE exigia monotonicidade global, que não é necessária para LRE;
- layouts comparavam pares físicos diferentes sem randomização;
- as 2 funções de corte eram tratadas como medida direta, não como gauge.

## 2. Critérios revisados

| Gate | Evidência necessária | O que não é exigido |
|---|---|---|
| PEC 2q | GSPN validado, erro held-out ≤0,01, overhead ≤10 | identificar as 2 funções de corte |
| ZNE | LRE ≥9 configurações, resíduo ≤0,005, held-out estável | monotonicidade global |
| Layout | n≥n_required, randomização, r1≤0,05, drift resolvido, efeito≥0,01 | apagar r1 por mitigação |
| 2 cortes | GSPN autoconsistente + MLCB; `identified=False` | identificação direta |

## 3. Fail-closed

`gate_policy.evaluate({})` bloqueia os quatro gates. A aprovação exige
evidência declarada; o default é negar. Testes em
`tests/test_r1135_gate_policy.py`.

Exemplos que passam (apenas em teste sintético):

- PEC: `gspn_model_validated=True`, `heldout_error=0.005`,
  `sampling_overhead=5`;
- ZNE: `lre_configurations=27`, `residual=0.002`, `heldout_stable=True`;
- Layout: `n_pairs=32`, `randomized=True`, `r1=0.04`,
  `drift_resolved=True`, `effect=0.02`;
- Cortes: `gspn_self_consistent=True`, `mlcb_applied=True`.

Falhas: r1=0,08 bloqueia layout; PEC sem GSPN bloqueia; cortes sem GSPN/MLCB
bloqueiam; ZNE com 3 configurações bloqueia.

## 4. Relação com as rotas

- **GSPN/MLCB:** Chen et al. 2026, DOI `10.1103/1pnv-t9px`; Calzona et al.
  2026, DOI `10.1103/4hbl-hpl3`.
- **Gauge:** Chen et al. 2026, DOI `10.1103/69wc-gzl6`.
- **LRE:** Russo & Mari 2024, DOI `10.1103/PhysRevA.110.062420`.

## 5. Limites

Aprovar um gate é necessário, não suficiente. Nenhum dado de hardware foi
coletado; PEC 2q, ZNE e layouts continuam bloqueados na prática. A tarefa
`760869c6…` segue `RUNNING` e arquivada, sem reenvio/cancelamento.

## 6. Mathlib

O job dedicado `MathlibCounterproof.lean` compilou com `lake env lean`,
retorno 0. `rank_D` usa `Matrix.rank_le_height` e `Matrix.rank_mul_le_left`;
as identidades finitas usam `native_decide` (338 axiomas nativos em
`D_mul_R`). Log: `lean/quantum-cb/mathlib_compile.log`. A prova Lean 4 core
continua sendo a contraprova leve. Nenhuma das duas prova o canal, o twirl ou
o hardware.

## 7. Reprodução

```bash
.venv-quantum/bin/python -m pytest tests/test_r1135_gate_policy.py -q
.venv-quantum/bin/python harnesses/quantum-error-mitigation/solution_audit.py \
  --out /tmp/opencode/solutions.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/gate_router.py \
  --gate pec_2q
```

## 8. Compilação e roteamento

- `compilation_audit.py` verifica `initial_layout`, qubits ativos e QASM com
  backend genérico; `compile=False` no serviço não foi testado.
- `gate_router.py` devolve rota/evidência para cada gate bloqueado.
- REA foi usado para status/catálogo/sessão; a análise nativa do `.so` não
  entregou Evidence útil. Ver `docs/REA_COMPILACAO_R1137.md`.
