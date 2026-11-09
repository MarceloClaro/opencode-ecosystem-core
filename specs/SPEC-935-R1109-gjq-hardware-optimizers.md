# SPEC-935-R1109 — Otimizadores para hardware GJQ

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1099 (runtime GJQ), R1104 (catálogo de backends), R1108 (eficiência de código quântico)

## 1. Contexto

O runtime GJQ já submete circuitos, mas a otimização usada no caminho atual é o
preset do Qiskit com `optimization_level` configurável. Isso não escolhe
explicitamente a região do chip com menor erro, não compara candidatos de
layout/roteamento e não separa a transpilação local da submissão.

Para hardware real, a diferença importa: o Baihua tem 156 qubits, e um circuito
pequeno pode ser mapeado em uma região ruim. O objetivo desta spec é criar um
otimizador que use o `Target` real do backend GJQ, escolha o layout por erro de
porta/leitura, compare candidatos e submeta o circuito já otimizado com
`transpile=False`, evitando dupla transpilação.

## 2. Requisitos

- **R1.** Criar `gjq_hardware_opt/` com perfil de hardware, layout noise-aware,
  estimador de sucesso, otimizador, exportação e execução.
- **R2.** Construir `HardwareProfile` a partir do `Target` real de um backend
  GJQ (`backend.target`), preservando largura, acoplamentos, portas base,
  erros de 1q/2q, erro de leitura e durações.
- **R3.** Aceitar perfil offline a partir dos payloads JSON de
  `gjq_backend_config` e `gjq_backend_properties`, sem rede.
- **R4.** Calcular um layout inicial noise-aware a partir do grafo de interação
  do circuito e dos erros do perfil, escolhendo uma região física conectada.
- **R5.** Gerar candidatos: baseline trivial, layout noise-aware, Sabre e Dense,
  com níveis de otimização e seeds declarados.
- **R6.** Selecionar por estratégia: `balanced`, `min_error`, `min_depth`,
  `min_two_qubit` e `noise_aware`.
- **R7.** Compactar o circuito transpilado para os índices físicos usados,
  preservando a numeração física do backend.
- **R8.** Estimar `success_proxy` como produto de `(1 - erro)` por porta e
  leitura; declarar que é proxy, não fidelidade de estado.
- **R9.** Exportar QASM 2.0 (submissão GJQ), QASM 3.0 (auditoria), JSON e
  Markdown, com SHA-256.
- **R10.** Conectar ao runtime GJQ somente quando `GJQ_API_KEY` estiver no
  ambiente; nunca aceitar chave por argumento, arquivo versionado ou prompt.
- **R11.** Submeter com `confirm=True`, `allow_hardware=True` para hardware e
  `transpile=False`; registrar `task_id`, backend, shots, timestamps, hashes e
  auditoria de counts.
- **R12.** Bloquear submissão sem chave, sem confirmação, sem `allow_hardware`
  para hardware, com shots fora do limite ou circuito sem medição.
- **R13.** Criar harness `harnesses/gjq-hardware-optimizers/` com os comandos
  `profile`, `optimize`, `benchmark`, `run`, `status`, `result` e `audit`.
- **R14.** Criar skill e agente `managed-v1` para operar o fluxo no Core.
- **R15.** Criar testes que não acessem rede e não submetam jobs.
- **R16.** Não adicionar dependência nova; usar `gjq-client==0.2.1`,
  Qiskit 2.3.0 e o `.venv-quantum`.

## 3. Perfil de hardware

O perfil contém:

| Campo | Conteúdo |
|---|---|
| `name` | nome do backend |
| `num_qubits` | largura do target |
| `coupling_map` | arestas direcionadas do target |
| `basis_gates` | portas base, sem `measure` |
| `oneq_gates` / `twoq_gates` | separação por aridade |
| `oneq_error` | erro por porta e qubit |
| `twoq_error` | erro por porta e aresta |
| `readout_error` | erro de leitura por qubit |
| `oneq_duration` / `twoq_duration` | duração por porta e qubit/aresta |
| `readout_duration` | duração da medição |
| `target_fingerprint` | SHA-256 do conteúdo canônico |
| `profile_kind` | `gjq_live_target`, `gjq_saved_payload` ou `synthetic_test` |
| `calibration_source` | origem declarada da calibração |

Erros ausentes usam `default_error` e geram aviso; não são inventados como
calibração.

## 4. Layout noise-aware

1. Extrair do circuito os pesos de 1q, medição e arestas de 2q.
2. Calcular o custo de cada qubit físico:
   `erro_1q + erro_leitura` ponderado pelo uso.
3. Calcular o custo de cada aresta física pelo erro de 2q.
4. Calcular caminhos mínimos entre qubits físicos usando o erro como peso.
5. Atribuir qubits lógicos por grau de interação, escolhendo o qubit físico de
   menor custo.
6. Refinar com trocas locais (2-opt) e conectar a região escolhida por
   caminhos mínimos.
7. Devolver um layout `lógico -> físico` e a região física conectada.

O layout é determinístico para a mesma seed e o mesmo perfil.

## 5. Candidatos e seleção

| Candidato | Layout | Roteamento |
|---|---|---|
| `trivial` | trivial | basic |
| `noise_aware` | noise-aware | sabre |
| `sabre` | sabre | sabre |
| `dense` | dense | sabre |

Níveis de otimização: `1, 2, 3` no modo completo; `1, 3` no modo rápido.
Seeds: `42` no modo rápido; `42, 43` no modo completo.

A seleção usa uma chave lexicográfica:

- `balanced`: erro estimado, profundidade, 2q, tamanho;
- `min_error`: erro estimado, 2q, profundidade, tamanho;
- `min_depth`: profundidade, erro estimado, 2q, tamanho;
- `min_two_qubit`: 2q, erro estimado, profundidade, tamanho;
- `noise_aware`: restrita aos candidatos noise-aware.

O baseline nunca é escolhido; ele serve apenas de comparação.

## 6. Submissão GJQ

O circuito escolhido é compactado para os índices físicos usados e exportado em
QASM 2.0. A submissão usa `Sampler(backend=backend).run(circuit, shots=shots)`
com o circuito já transpilado. O gate exige:

- `GJQ_API_KEY` no ambiente;
- `confirm=True`;
- `allow_hardware=True` para Baihua, Guoji01/04/07/08 e Yudu;
- `1 <= shots <= 100000`;
- pelo menos uma medição;
- limite de submissões por processo.

O resultado registra `task_id` e não reenvia o mesmo circuito.

## 7. Critérios de aceitação

- perfil extraído de um `Target` de teste com erros e acoplamentos;
- roundtrip JSON do perfil;
- layout noise-aware com custo menor ou igual ao trivial em um caso de teste;
- circuito escolhido usa apenas portas base e arestas do perfil;
- compactação preserva índices físicos;
- `success_proxy` em `[0, 1]`;
- QASM 2.0, QASM 3.0, JSON e Markdown gerados com hash;
- gate de submissão bloqueia sem chave, sem confirmação e sem
  `allow_hardware`;
- testes R1109 passam sem rede;
- `opencode.json` contém o agente;
- nenhum segredo em arquivo;
- nenhuma alegação de fidelidade medida, vantagem quântica ou execução física
  quando não houve job.

## 8. Não objetivos

- Executar hardware sem chave e autorização explícita.
- Medir fidelidade de estado, T1/T2 ou calibração em tempo real.
- Provar vantagem quântica, emaranhamento ou interpretação de Bohm.
- Substituir o `gjq-runtime` ou o `gjq-experiments`.
- Fazer mitigação de erro (ZNE/PEC/DD) nesta versão.
- Prometer custo, fila ou disponibilidade do Baihua.

## 9. Riscos

- **Perfil obsoleto:** a calibração muda; o perfil registra a data e o
  fingerprint, e a execução deve reler as propriedades.
- **Dupla transpilação:** se `transpile=True` for usado no `Sampler`, o layout
  escolhido é desfeito. O gate exige `transpile=False`.
- **Comparação injusta:** baseline e candidatos usam o mesmo target, a mesma
  seed e as mesmas portas base.
- **Overclaim:** `success_proxy` não é fidelidade; uma execução não é prova
  estatística.
- **Custo:** o harness não estima preço nem fila; o operador confirma o backend
  e os shots.

## 10. Testes

`tests/test_r1109_gjq_hardware_optimizers.py` verifica:

- perfil, target, layout, estimador, otimizador e exportação;
- gates de submissão;
- CLI offline com perfil de teste;
- bloqueio sem chave;
- ausência de segredos e de frases de overclaim;
- registro no `opencode.json`.
