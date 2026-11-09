# SPEC-935-R1108 — Eficiência de código quântico

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1099 (livro quântico), R1107 (estudo acadêmico)

## 1. Contexto

O projeto já tem circuitos, experimentos e um programa de estudo. Falta uma
camada que responda, com métricas e gates, a uma pergunta prática: **o código
quântico ficou mais eficiente sem mudar o que ele calcula?**

Eficiência, aqui, não é “speedup quântico”. É um conjunto de métricas de
circuito e de transpilação: número de qubits, portas de um e dois qubits,
profundidade, tamanho, tempo de transpilação e distância entre distribuições
ideais.

## 2. Requisitos

- **R1.** Criar a skill `eficiencia-codigo-quantico` com contrato, métricas,
  workflow, otimizações e limites.
- **R2.** Criar dois agentes `managed-v1`:
  `quantum-code-efficiency` (engenharia) e `quantum-benchmark-audit`
  (auditoria).
- **R3.** Criar o harness `harnesses/quantum-code-efficiency/` com baseline
  `optimization_level=0` e otimizado `optimization_level=3`.
- **R4.** O harness deve medir, no mínimo: qubits, portas 1q, portas 2q,
  profundidade, tamanho, tempo de transpilação e TVD entre distribuições
  ideais.
- **R5.** Gates: `TVD ≤ 1e-9`; `2q_otimizado ≤ 2q_baseline`;
  `depth_otimizado ≤ depth_baseline`; `hardware=False`; `network=False`.
- **R6.** O harness deve usar benchmarks determinísticos: Bell, GHZ-4, QFT-4,
  VQE-2, circuito em camadas, circuito redundante e CNOT não adjacente com
  coupling map.
- **R7.** Gerar `resultados.json` e `RELATORIO.md` com protocolo, seed,
  versão, tabela e limites.
- **R8.** Criar testes que validem arquivos, frontmatter, skill, harness,
  gates, ausência de segredos e ausência de overclaim.
- **R9.** Criar documento `docs/EFICIENCIA_CODIGO_QUANTICO_R1108.md` com
  métricas, técnicas, protocolo e leitura dos resultados.
- **R10.** Não adicionar dependência nova; usar Qiskit/Aer do
  `.venv-quantum`.
- **R11.** Importar os circuitos de E01–E18 do livro e tratá-los como
  benchmarks nomeados (25 circuitos em 18 experimentos).
- **R12.** Varrer os níveis de otimização 0, 1, 2 e 3 e registrar, por
  circuito, 2q, profundidade, tamanho, TVD, redução e status.
- **R13.** Executar uma varredura de ruído depolarizante de porta em
  `p = 0; 0,001; 0,005; 0,01`, com 2048 tiros, comparando baseline e melhor
  nível; a varredura é descritiva e não é gate de aprovação.
- **R14.** Gerar `resultados_experimentos.json` e
  `RELATORIO_EXPERIMENTOS.md`, com resumo, tabela por circuito, tabela de
  ruído e limites.

## 3. Benchmarks

| Benchmark | O que exercita | Coupling map |
|---|---|---|
| `bell` | emaranhamento mínimo | não |
| `ghz4` | fan-out de CNOT | não |
| `qft4` | decomposição de QFT | não |
| `vqe2` | ansatz variacional curto | não |
| `layered4` | camadas de rotação e CNOT | não |
| `redundant` | cancelamento de portas | não |
| `nonadjacent` | roteamento | linear 0–1–2–3 |

## 4. Gates

- **G1.** Correção: TVD ≤ `1e-9` entre baseline e otimizado.
- **G2.** Não aumentar portas de dois qubits.
- **G3.** Não aumentar profundidade.
- **G4.** Não executar hardware.
- **G5.** Não acessar rede.
- **G6.** Registrar seed e versão.

## 5. Critérios de aceitação

- 7 benchmarks sintéticos executam e todos passam nos gates;
- 25 circuitos de E01–E18 executam, com 25/25 pass;
- a varredura de níveis e a varredura de ruído geram JSON e Markdown;
- JSON e Markdown são gerados;
- testes R1108 passam;
- `opencode.json` contém os dois agentes;
- nenhum segredo em arquivo;
- nenhuma alegação de vantagem quântica ou speedup real.

## 6. Não objetivos

- Executar em hardware quântico.
- Medir fidelidade de estado ou calibração.
- Comparar circuitos de tarefas diferentes.
- Declarar “mil vezes mais rápido” sem benchmark de tarefa completa.
- Substituir revisão humana ou peer review.

## 7. Riscos

- **Comparação inválida:** baseline e otimizado precisam do mesmo circuito,
  seed, portas base e coupling map.
- **Métrica enganosa:** redução de portas pode aumentar profundidade; o gate
  G3 evita trade-off não declarado.
- **Versão volátil:** Qiskit muda passes; o JSON registra a versão.
- **Overclaim:** redução de 2q não é vantagem quântica.

## 8. Testes

`tests/test_r1108_quantum_code_efficiency.py` verifica:

- spec, skill, agentes, docs e harness existem;
- frontmatter `managed-v1` dos dois agentes;
- skill contém métricas, gates, protocolo e limites;
- harness executa em modo rápido e retorna 7 benchmarks com `pass`;
- JSON não contém `hardware=True` nem `network=True`;
- ausência de segredos e de frases de overclaim.
