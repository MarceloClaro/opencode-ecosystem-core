# Literatura — otimização, mitigação, correlações e arranjos (R1147)

**Data:** 2026-11-10
**Pergunta:** que técnicas reais de otimização e mitigação podem gerar novas
correlações, novos arranjos e contraprovas auditáveis no Core?

## 1. Técnicas e fontes

| Técnica | Fonte | Gap que o Core ataca |
|---|---|---|
| Mitigação de erro de leitura correlacionado sem medidas randomizadas | *Mitigation of correlated readout errors without randomized measurements*, PRA (2025), DOI `10.1103/6p6s-t8b7` | marginais não determinam a junta; é preciso medir co-ocorrência |
| Mapeamento ciente de crosstalk (TRIM) | *TRIM: crossTalk-awaRe qubIt Mapping for multiprogrammed quantum systems*, QSW (2023), DOI `10.1109/qsw59989.2023.00025` | custo de layout precisa incluir penalidade de crosstalk, não só distância |
| Mapeamento noise-adaptive | *Noise-Adaptive Compiler Mappings for NISQ Computers*, ASPLOS (2019), DOI `10.1145/3297858.3304075` | erro de porta e leitura entram no custo; ótimo depende do regime |
| Expansão por simetria | *Quantum Error Mitigation using Symmetry Expansion*, Quantum (2021), DOI `10.22331/q-2021-09-21-548` | rota de mitigação para observáveis com simetria; não implementada nesta rodada |
| ZNE com análise polinomial e cotas | *Direct Analysis of Zero-Noise Extrapolation: Polynomial Methods, Error Bounds...*, Quantum (2025), DOI `10.22331/q-2025-11-14-1909` | ZNE já existe no Core; falta acoplar a correlação de leitura |
| PEC com escalonamento de ruído | *Extending quantum probabilistic error cancellation by noise scaling*, PRA (2021), DOI `10.1103/physreva.104.052607` | PEC existe; modelo de ruído correlacionado ainda não |
| RB com desfasamento temporal correlacionado | *Randomized benchmarking in the presence of time-correlated dephasing noise*, PRA (2021), DOI `10.1103/physreva.103.022607` | independência entre ciclos é hipótese, não fato |
| Crosstalk em arrays de spin | *Crosstalk analysis for single-qubit and two-qubit gates in spin qubit arrays*, PRB (2021), DOI `10.1103/physrevb.104.045420`; e PRB (2022), DOI `10.1103/physrevb.105.085414` | penalidade estática é proxy; acoplamento depende de portas simultâneas |
| GSPN / MLCB | já registrados em `quantum_mitigation/solution_audit.py`: `10.1103/1pnv-t9px`, `10.1103/4hbl-hpl3` | gauge e aprendizado autoconsistente; não medidos |

## 2. Técnicas extraídas

1. **Co-ocorrência > marginal**: medir `p_ij` e `phi`, não apenas `p_i`.
2. **Custo de layout multi-termo**: caminho de portas, leitura, crosstalk e
   correlação de leitura.
3. **Ótimo condicional**: o melhor arranjo depende do regime de ruído; não é
   universal.
4. **Cotas de união**: `P(∪A_i)` é limitado por marginais e co-ocorrências;
   usar isso como sanity check e contraprova do modelo independente.
5. **Contraprova obrigatória**: toda inovação de correlação/arranjo deve vir
   com um caso que a falsifique ou que mostre o limite do ganho.

## 3. Gaps declarados

| Gap | Estado no Core |
|---|---|
| dados reais de calibração | não usados; apenas counts sintéticos |
| correlação de ordem superior | não modelada; só pares `phi` |
| agendamento/timing de portas | não modelado; crosstalk é proxy estático |
| acoplamento ZNE/PEC × correlação | planejado, não implementado |
| validação em hardware | nenhuma; sem submissão |
| vantagem quântica | nenhuma alegação |

## 4. O que foi implementado

- `quantum_mitigation/correlation_layout.py`:
  - `calibration_correlations`: marginais, `p_ij`, `phi`, cotas e deltas;
  - `simulate_correlated_readout`: modelo latente para testes;
  - `make_device`, `shortest_paths`, `layout_cost`;
  - `greedy_layout`, `two_opt`, `exhaustive_layout`, `optimize_layout`;
  - `find_greedy_counterexample`, `find_regime_reversal`,
    `correlation_blind_counterexample`.
- `lean/quantum-cb/CorrelationCounterproof.lean`: 10 teoremas kernel-checked
  sobre marginais iguais e juntas diferentes.
- `quantum_mitigation/correlation_gate.py`: gate fail-closed que exige prova e
  contraprova e compila o arquivo.

## 5. Limites

Nenhum resultado desta rodada usa hardware, calibração real, crosstalk medido
ou ruído real. Os custos são proxies declarados. O pareamento
alegação↔contraprova é editorial. “Vantagem” não é testada.
