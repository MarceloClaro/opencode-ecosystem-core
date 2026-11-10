---
name: mitigacao-e-correcao-quantica
description: Integra ZNE, PEC, DD, QEC, SPAM, crosstalk, drift e incerteza ao Core com planejamento, simulação e auditoria; não executa hardware, não declara threshold, fidelidade ou vantagem sem evidência.
metadata:
  version: "1"
  origem: "R1114 — mitigação e correção de erro quântico"
---

# Mitigação e correção de erro quântico

## Quando usar

Use para **planejar, simular e auditar** ZNE, PEC, DD, QEC, SPAM, crosstalk,
drift e incerteza. Para executar em hardware, o primário precisa de gates,
`confirm=True` e `allow_hardware=True`; esta skill não executa hardware.

## Contrato

1. **Declare a técnica e o modelo.** ZNE assume relação monotônica; PEC exige
   quasi-probabilidades; DD circuit-level não é pulse-level.
2. **Separe mitigação de correção.** ZNE/PEC/DD mitigam; QEC codifica. Nenhum
   deles garante fault tolerance.
3. **Registre overhead.** PEC cresce com `γ²`; DD adiciona portas; QEC adiciona
   qubits e síndromes.
4. **Não declare threshold.** O código de repetição 3 qubits não é superfície
   nem prova de threshold.
5. **Não declare fidelidade.** Métricas de TVD, erro lógico e SPAM não são
   fidelidade de estado.
6. **Incerteza é dispersão.** Três repetições não são prova estatística
   universal.

## Técnicas

| Técnica | Implementação | Limite |
|---|---|---|
| ZNE | folding global + extrapolação linear/quadrática/exponencial | assume monotonicidade; não é QEC |
| PEC | inversão de canal Pauli 1q/2q no planejador | 2q não executado; probabilidades não são taxas Lindblad; overhead γ² |
| DD | XY4/CPMG/echo circuit-level | não é schedule pulse-level |
| QEC | repetição 3 qubits para bit-flip | não protege fase; não é superfície |
| SPAM | \|0> e \|1> com rx(pi) | preparação e leitura parcialmente confundidas |
| Crosstalk | erro isolado vs simultâneo | descritivo; não identifica mecanismo |
| Drift | tendência e CUSUM | não corrige calibração |
| Incerteza | Wilson/bootstrap | dispersão, não significância universal |

## Comandos

```bash
# ZNE
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py zne \
  --profile perfil.json --circuit E05 --scales 1 3 5 --shots 2048 --out resultados/zne

# DD
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py dd \
  --circuit E05 --qubits 0 1 --sequence xy4 --out resultados/dd

# PEC 1q
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py pec \
  --profile perfil.json --circuit E05 --out resultados/pec

# QEC repetição
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py qec \
  --p 0.01 --shots 20000 --out resultados/qec

# SPAM
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py spam \
  --counts0 counts0.json --counts1 counts1.json --out resultados/spam

# crosstalk, drift, incerteza
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py crosstalk \
  --isolated 0.01 --simultaneous 0.02 --out resultados/crosstalk
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py drift \
  --values 0.010 0.011 0.013 0.016 0.020 --out resultados/drift
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py uncertainty \
  --values 0.020 0.025 0.022 0.024 --out resultados/uncertainty

# lições do loop
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py lessons \
  --loop-state loop_state.json --out resultados/lessons
```

## Agentes

| Necessidade | Agente |
|---|---|
| ZNE, PEC, DD | `quantum-error-mitigation` |
| QEC e síndromes | `quantum-error-correction` |
| SPAM, crosstalk, drift, incerteza | `quantum-noise-characterization` |
| Auditoria de claim | `quantum-benchmark-audit` |

## Calibração Rabi

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rabi_calibration.py \
  --qubit 1 --shots 4096 --confirm --allow-hardware --use-cached-account
```

16 jobs (8 ângulos × 2 eixos) ajustam `p1(θ) = r0 + A·sin²((θ+ε)/2)` sob
um modelo restrito, sem separação autoconsistente de SPAM. Em q1: ε(rx) = −0,0006 ± 0,0091 rad;
ε(ry) = +0,0012 ± 0,0129 rad; nenhum desvio acima de 2σ; r1 0,0695–0,0786.
Não corrigir o ângulo do π; priorizar leitura.

## Validação RC em hardware

Duas pernas, 2 conjuntos × 4 circuitos, 9.600 shots, 16 jobs:

- baseline: TVD 0,0962;
- twirlado: TVD 0,0978;
- Δ = +0,0018 [−0,0071, +0,0108];
- decisão: **sem efeito detectável**.

Não foi detectada melhora neste ensaio; isso não prova ausência de efeito nem
identifica sua causa. +0,0018 é a média bootstrap do relatório legado;
a diferença direta das médias observadas é +0,00160156. O IC legado não
preserva os pares temporais; não é evidência de equivalência. A sobrevivência
dos twirls após compilação do servidor não foi auditada.

## Repetição de leitura

Três runs de mitigação do **subespaço 00/11**, não matriz 4×4: baseline 0,0247 (faixa 0,0228–0,0263); otimizado
0,0170 (faixa 0,0079–0,0277); sinal instável. O layout otimizado usa qubits
106/107 e o baseline usa 0/1, então a diferença mistura layout com qualidade
de qubit. Qubits diferentes são parte do efeito de mapeamento, não veto
universal à comparação. A rodada usou 4.096 shots, não o n da R1120, e não
cumpriu a sequência de gates prevista. Não repetir antes de corrigir o desenho.
Mitigação de leitura **não** reduz o r1 bruto, que aqui também inclui preparação.

## CB e GST

- **Cycle benchmarking (R1125):** gerador, paridade, ajuste e IC condicional
  testados em simulador. Repetição par de CZ tem **posto 9**, não 15: não
  identificar taxas individuais por `−log(f)/2` ou pseudoinversa.
- **R1126:** o posto 9 é do desenho **somente-CZ**; a matriz completa tem posto
  15. Aumentar com outros Cliffords pode chegar a 15 apenas sob gerador
  compartilhado/conjugado; com um gerador por ciclo, `9k < 15k`. Submodelo
  local tem posto 6; dois qubits, 9; ambos exigem taxas externas nulas. Nada
  foi executado em hardware; ver `docs/RELATORIO_CB_R1126.md`.
- **R1128:** Chen et al. 2023, DOI `10.1038/s41467-022-35759-4`: para um
  Clifford de 2 qubits, o espaço aprendível tem **13** funções e restam **2**
  não aprendíveis (ciclos vs cortes). O posto 9 é só o subespaço de órbitas;
  faltam 4 funções, recuperáveis com **Cliffords de 1 qubit intercalados**.
  As 2 de corte exigem hipótese adicional (preparação perfeita, GST ou
  restrição física). Nada medido; ver
  `docs/LITERATURA_APRENDIZABILIDADE_R1128.md`.
- **R1129:** desenho com 7 ciclos individuais + 6 produtos de pares recupera
  as **13 funções** em simulação exata (matriz 13×15, posto 13). As 2 de corte
  continuam fora. Correções de 1 qubit ideais e ruído antes do CZ; hardware
  não executado. Ver `docs/RELATORIO_CB_R1129.md`.
- **R1130:** twirl de Pauli por CZ com frames registrados; depolarização 1q
  após correções. Taxa 0,005 → erro máximo ~1,29×10⁻²; 0,010 → ~2,57×10⁻².
  O ajuste ainda retorna 13/13, mas isso não é precisão. Pré-registro local:
  325 jobs, 1.331.200 shots, `hardware_submission_allowed=False`.
- **R1131:** contraprova Lean 4 core dos invariantes finitos (13×15 com
  inversa à direita, 13/2, ortogonalidade). Identidades matriciais usam
  `native_decide`; não prova canal quântico, twirl ou hardware.
- **R1132:** LRE (Russo & Mari 2024) para ZNE layerwise; exata no modelo
  multilinear, mas exige mais configurações e não valida o Baihua.
- **R1133:** desenho pareado randomizado para layouts; `n` normal, r1 como
  covariável e bloqueio de pares diferentes sem randomização.
- **R1134:** as 13 funções são invariantes ao corte; as 15 fidelidades mudam.
  Rota para PEC 2q/2 cortes: GSPN/MLCB com gauge autoconsistente, não
  identificação direta das 2 funções.
- **R1135:** gates revisados e fail-closed: PEC 2q exige GSPN validado,
  held-out ≤0,01 e overhead ≤10; ZNE exige LRE ≥9 configurações, resíduo
  ≤0,005 e held-out estável; layout exige n, randomização, r1≤0,05, drift e
  efeito≥0,01; cortes são gauge, não identificação direta.
- **R1137:** o sampler GJQ envia QASM original e o serviço compila sem devolver
  layout. `compilation_audit.py` pré-transpila com `initial_layout` explícito e
  verifica layout/qubits ativos/QASM; `compile=False` no serviço não foi
  testado. REA: status/catálogo/sessão; análise nativa do `.so` sem Evidence útil.
- **R1138:** `gate_router.py --gate ...` roteia gate bloqueado para rota e
  evidência necessária; default fail-closed.
- **Mathlib:** `MathlibCounterproof.lean` compilou com `lake env lean`,
  retorno 0; `rank_D` usa `Matrix.rank` e as identidades usam `native_decide`
  (338 axiomas nativos em `D_mul_R`). A contraprova leve é Lean 4 core.
  Nenhuma das duas prova canal, twirl ou hardware.
- O piloto corrigido usa m=0,2,4,8,16, manifesto e hashes QASM. É proposta
  offline, não pré-registro histórico já executado. 150 jobs não resolvem a
  falta de identificação; nenhuma taxa foi medida em hardware.
- O simulador injeta canal Pauli após CZ com portas locais ideais. Sanduíches
  compensados não implementam toda a média de sinais SPAM-robusta de Erhard.
- Inversão disponível apenas para espectro completo rotulado e posto 15;
  `gamma_Q` do gerador não pode entrar como probabilidade em `pauli_channel_inverse`.
- **GST:** bloqueada; pyGSTi ausente e protocolo não validado.
- Handoff: `docs/HANDOFF_CB_GST.md`.

## Pré-registro e literatura

- `harnesses/quantum-error-mitigation/preregister_layout.py` pré-registra n e
  gates; decisão atual: não comparar layouts (n=38.411 por circuito/layout).
- `harnesses/quantum-error-mitigation/cycle_benchmarking_plan.py` planeja 150
  jobs históricos; sua suficiência para as 15 taxas foi refutada na R1125.
- `docs/LITERATURA_MITIGACAO_QUANTICA_R1121.md` mapeia gap → técnica →
  referência verificada por DOI/arXiv.

## Passe de Pauli-frame (RC)

O passe implementa o twirl `P' · G · P = G` para portas Clifford 1q/2q:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py rc \
  --qubit 1 --seed 1234 --out resultados/rc
```

Gera QASM twirlado, relatório e verificação unitária. No circuito de tomografia
de q1, `n_twirls=1` e equivalência up to fase confirmada. **Houve ensaio em
hardware na R1123**, sem ganho detectado; igualdade ideal não prova mitigação.
Portas não-Clifford são recusadas em modo estrito.

## Scorecard híbrido

O comando `resilience` combina readout 4x4, tomografia q0/q1, ZNE, PEC e
incerteza para recomendar o próximo passo e listar técnicas bloqueadas:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py resilience \
  --readout comparacao.json --zne zne.json \
  --tomography-q0 comparison.json --tomography-q1 comparison.json \
  --comparison comparison_q0_q1.json \
  --rabi rabi_q1.json \
  --pec pec.json --surface --pulse-dd
```

No run simétrico (2 conjuntos por qubit): ZNE bloqueado por não monotonicidade;
Δ r1 q1−q0 = +0,0072, mas ICs se sobrepõem e o Δ é menor que o spread entre
conjuntos, então a diferença não é conclusiva. `prep |0>/|1>` e `r0/r1` são a
mesma contagem Z. Os indicadores `|+>` e `|+i>` ainda dependem de SPAM e das
rotações de análise; não são preparação independente de leitura. Superfície e
DD pulse-level bloqueados; PEC 2q com 15 taxas não
caracterizadas.

## Resultado R1115

No Baihua, ZNE continuou não monotônica mesmo com 4 escalas; não use a
extrapolação como ganho. O SPAM por pulsos π repetidos falhou, mas a
tomografia multi-base (4 estados x 3 bases) separou preparação e leitura sob
hipóteses declaradas. PEC 2q, superfície e DD pulse-level não foram executados.

## Correlação e arranjos (R1147)

Para erro de leitura correlacionado, use a skill
`correlacoes-arranjos-contraprovas`: `quantum_mitigation/correlation_layout.py`
mede `p_ij`/`phi`, otimiza layout com custo de porta + leitura + crosstalk +
correlação e produz contraprovas. A contraprova formal está em
`lean/quantum-cb/CorrelationCounterproof.lean` (10 teoremas kernel-checked).
Nunca decidir layout só por marginais.

## Limites

- Runner/wrapper são offline; scripts `hardware_*` só pelo primário com gates.
- ZNE não é QEC; há planejamento PEC 2q, mas não execução caracterizada.
- DD é circuit-level, não pulse-level.
- QEC de repetição não protege fase.
- SPAM |11> usa `rx(pi)` e inclui preparação do |1>.
- Crosstalk e drift são descritivos.
- Bootstrap/Wilson não provam significância universal.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
