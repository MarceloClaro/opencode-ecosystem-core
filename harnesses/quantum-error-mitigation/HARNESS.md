# HARNESS — Mitigação e correção de erro quântico (R1114)

**Objetivo:** planejar, simular e auditar ZNE, PEC, DD, QEC, SPAM, crosstalk,
drift e incerteza.

**Runner/wrapper offline:** não executam hardware nem instalam dependências.
Os scripts `hardware_*` são separados e exigem gates do primário. Nenhuma
destas ferramentas garante threshold, fidelidade ou vantagem.

## Comandos

| Comando | O que faz |
|---|---|
| `zne` | folding e extrapolação ZNE em simulação |
| `dd` | plano DD circuit-level com verificação de identidade |
| `pec` | planejador PEC 1q/2q com hipótese depolarizante e overhead |
| `qec` | repetição de 3 qubits com síndrome e decodificador |
| `spam` | ajuste \|0>/\\|1> |
| `crosstalk` | métrica isolado vs simultâneo |
| `drift` | tendência linear e CUSUM |
| `uncertainty` | Wilson/bootstrap |
| `lessons` | extrai lições do `loop_state.json` |
| `audit` | auditoria lexical de overclaim |

## Exemplos

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py zne \
  --profile perfil.json --circuit E05 --scales 1 3 5 --shots 2048 --out resultados/zne

.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py qec \
  --p 0.01 --shots 20000 --out resultados/qec

.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py lessons \
  --loop-state loop_state.json --out resultados/lessons
```

## Agentes

| Agente | Comandos |
|---|---|
| `quantum-error-mitigation` | `zne*`, `dd*`, `pec*`, `audit*`, `lessons*` |
| `quantum-error-correction` | `qec*`, `audit*`, `lessons*` |
| `quantum-noise-characterization` | `spam*`, `crosstalk*`, `drift*`, `uncertainty*`, `audit*`, `lessons*` |

O wrapper é `agent_qem.py`. Nenhum agente executa hardware.

## Gates

- [ ] ZNE declara folding e método de extrapolação;
- [ ] PEC 2q permanece não executado com taxas caracterizadas;
- [ ] DD é circuit-level;
- [ ] QEC é repetição bit-flip, não superfície;
- [ ] SPAM declara `rx(pi)` e preparação do |1>;
- [ ] crosstalk/drift são descritivos;
- [ ] bootstrap/Wilson não são significância universal;
- [ ] nenhuma chave em arquivo.

## Validação RC em hardware

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rc_validation.py \
  --set 1 --shots 9600 --confirm --allow-hardware --use-cached-account
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rc_validation.py --analyze
```

16 jobs (2 conjuntos × 4 baseline + 4 twirls). Resultado: baseline 0,0962;
twirlado 0,0978; Δ +0,0018 [−0,0071, +0,0108]; **sem efeito detectável**.
O Δ acima é a média bootstrap histórica; a diferença observada é +0,00160156.
O bootstrap legado ignora pareamento temporal. Não inferir equivalência nem
atribuir causalmente o resultado ao custo de portas extras.

## Repetição de leitura

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/readout_repeat_analysis.py
```

Três runs de mitigação do **subespaço 00/11**, não 4×4. Sinal instável;
baseline usa 0/1 e otimizado usa 106/107. Isso mede um possível efeito total
do mapeamento, sem isolar a transpilação. Os runs de 4.096 shots não cumpriram
o pré-registro de layouts nem reavaliaram isoladamente o gate r1. Mitigação
de leitura não reduz o r1 bruto (preparação também está incluída).

## CB e GST

R1125 implementa CB inspirado em CZ **offline**, com paridade em vez de P00,
ajuste direto e bootstrap condicional. O desenho **somente-CZ** tem posto 9;
a matriz completa tem posto 15 (R1126). Aumentar com outros Cliffords só
recupera 15 sob gerador compartilhado/conjugado; com geradores separados,
`9k < 15k`. Proibir pseudoinversa como identificação. A R1128 (Chen et al.
2023) mostra que o espaço aprendível do CZ tem **13** funções e **2** não
aprendíveis; o posto 9 é só o subespaço de órbitas. Faltam 4, recuperáveis
com **Cliffords de 1 qubit intercalados**; as 2 de corte exigem hipótese
adicional. Nenhum job CB/GST foi submetido. pyGSTi/protocolo experimental
permanecem pendentes. Ver `docs/HANDOFF_CB_GST.md`,
`docs/RELATORIO_CB_R1126.md` e `docs/LITERATURA_APRENDIZABILIDADE_R1128.md`.

### Laboratório reproduzível R1125 (sem hardware)

Escolha um diretório novo; os arquivos de evidência não são sobrescritos.

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py plan --out /tmp/opencode/cb-novo/manifest.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py simulate --manifest /tmp/opencode/cb-novo/manifest.json --out /tmp/opencode/cb-novo/synthetic_counts.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py analyze --manifest /tmp/opencode/cb-novo/manifest.json --data /tmp/opencode/cb-novo/synthetic_counts.json --bootstrap 500 --out /tmp/opencode/cb-novo/analysis.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py rank --out /tmp/opencode/cb-novo/rank.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py learnability --out /tmp/opencode/cb-novo/learnability.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py interleaved --out /tmp/opencode/cb-novo/interleaved.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py interleaved-noise --out /tmp/opencode/cb-novo/noise.json
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py preregister --out /tmp/opencode/cb-novo/prereg.json
```

Simulação injeta 15 taxas conhecidas; o ajuste retorna decaimentos de órbitas,
**não** taxas individuais. Os ICs não cobrem drift/seeds e não têm cobertura
validada. Há testes negativos de paridade, posto, CP/Lindblad, hashes e JSON.

O comando `interleaved` implementa 7 ciclos individuais + 6 produtos de pares
e recupera **13/13** funções em simulação exata, com matriz 13×15 de posto 13.
As 2 funções de corte não são medidas; as correções de 1 qubit são ideais e o
ruído é aplicado antes do CZ. Nenhum hardware foi executado.

`interleaved-noise` adiciona twirl/frame e depolarização 1q após as correções.
A taxa 0,005 produz erro máximo ~1,29×10⁻²; 13/13 ajustes não significa
13/13 precisão. `preregister` grava 325 jobs planejados, 1.331.200 shots e
`hardware_submission_allowed=False`.

Contraprova Lean: `cd lean/quantum-cb && lean QuantumCB.lean`. Ela prova os
invariantes finitos 13/2; não prova o canal, o twirl ou o hardware.

Rotas de desbloqueio offline:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/solution_audit.py \
  --out /tmp/opencode/solutions.json
```

O relatório inclui LRE para ZNE layerwise, desenho pareado randomizado para
layouts, auditoria de gauge/PEC e a política fail-closed de gates. Nenhuma
rota é execução de hardware; PEC 2q continua condicionado a GSPN/MLCB e dados.
Ver `docs/SOLUCOES_BLOQUEIOS_R1132.md` e `docs/GATES_REVISADOS_R1135.md`.

Quando um gate bloquear, consulte a rota e a evidência necessária:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/gate_router.py \
  --gate pec_2q
```

### Compilação/layout (R1137)

O sampler GJQ envia o QASM original e o serviço compila sem devolver layout.
`quantum_mitigation/compilation_audit.py` pré-transpila com `initial_layout`
explícito e verifica `final_index_layout`, qubits ativos e QASM. Teste local:
identidade preserva 106/107; troca 106/107 tem `identity_preserved=False`.
REA foi usado para status/catálogo/sessão; a análise nativa do `.so` não
entregou Evidence utilizável. Ver `docs/REA_COMPILACAO_R1137.md`.
Nenhum QASM foi submetido com `compile=False`.

## Pré-registro e planos

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/preregister_layout.py
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cycle_benchmarking_plan.py
```

- Layout: decisão **não comparar agora**; n=38.411 por circuito/layout;
  12 jobs e 460.932 shots no orçamento.
- Cycle benchmarking: orçamento histórico 150 jobs; R1125 refuta sua
  suficiência para 15 taxas. Profundidades novas 0,2,4,8,16 não foram executadas.
- Literatura: `docs/LITERATURA_MITIGACAO_QUANTICA_R1121.md` (18 referências
  verificadas).

## Passe de Pauli-frame (RC)

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py rc \
  --qubit 1 --seed 1234 --out resultados/rc
```

Twirl de portas Clifford 1q/2q com verificação unitária. Saída:
`resultado.json`, `twirled.qasm` e `RELATORIO.md`. Não executa hardware.
No circuito de tomografia de q1: 1 twirl, equivalência up to fase `true`.
Portas não-Clifford são recusadas em modo estrito (`--allow-non-clifford`
permite e registra).

## Calibração Rabi da preparação

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rabi_calibration.py \
  --qubit 1 --shots 4096 --confirm --allow-hardware --use-cached-account
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rabi_calibration.py \
  --qubit 1 --analyze
```

16 jobs (8 ângulos × 2 eixos). Em q1: ε(rx) = −0,0006 ± 0,0091 rad;
ε(ry) = +0,0012 ± 0,0129 rad; eixo preferido `none`; r1 0,0695–0,0786.
Nenhum desvio acima de 2σ nesse modelo. Atribuir todo erro restante à leitura
não é identificação autoconsistente de SPAM; o ajuste não substitui GST.

## Scorecard híbrido

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py resilience \
  --readout comparacao.json --zne zne.json \
  --tomography-q0 comparison.json --tomography-q1 comparison.json \
  --comparison comparison_q0_q1.json \
  --rabi rabi_q1.json \
  --pec pec.json --surface --pulse-dd
```

Combina técnicas e aponta bloqueios/recomendações. Não executa hardware.

## Validação de hardware R1115

No Baihua (q0/q1, 4096 shots, 9 jobs):

- ZNE escalas 1/3/5: TVD 0,0706 / 0,1003 / 0,0671; não monotônica; extrapolações
  linear 0,0819 e quadrática 0,0320 divergem; sem ganho.
- SPAM por pulsos π repetidos: P1≈0,93 constante; ajuste não identificável.
- Tomografia multi-base (16 jobs, 4096 shots): fidelidades 0,9875 / 0,9292 /
  0,9824 / 0,9839; r0=0,0125 e r1=0,0708.
- ZNE 4 escalas: TVD 0,0645 / 0,0747 / 0,0735 / 0,0967; ainda não monotônica.
- Tomografia q1 (2 conjuntos): |1> 0,9163 [0,9100; 0,9221]; r1 0,0837
  [0,0779; 0,0900].
- Tomografia q0 (2 conjuntos): |1> 0,9235 [0,9178; 0,9290]; r1 0,0765
  [0,0710; 0,0822].
- Δ q1−q0: r1 +0,0072; ICs se sobrepõem e Δ < spread entre conjuntos; não
  conclusivo. `prep |0>/|1>` e `r0/r1` são a mesma contagem Z.
- PEC 2q, superfície e DD pulse-level não foram executados.

## Limites

- ZNE não é QEC; PEC 2q é planejamento, não execução caracterizada.
- DD não é schedule pulse-level.
- QEC de repetição não protege fase.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
- O loop registra lições; não promove confiança automaticamente.
