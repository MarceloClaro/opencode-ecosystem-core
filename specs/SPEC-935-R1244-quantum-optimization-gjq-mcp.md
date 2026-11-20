---
spec_id: SPEC-935-R1244
title: Harness e MCP de otimização QUBO/QAOA com GJQ/Tiangong
component: integrations.quantum_optimization
status: proposed
test_file: tests/test_r1244_quantum_optimization.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    problem:
      - tests/test_r1244_quantum_optimization.py::test_qubo_validation_energy_and_canonical_hash
      - tests/test_r1244_quantum_optimization.py::test_exact_classical_baseline_and_limits
      - tests/test_r1244_quantum_optimization.py::test_qubo_to_ising_and_qaoa_ir
    optimizer:
      - tests/test_r1244_quantum_optimization.py::test_bounded_optimizer_respects_evaluation_budget
      - tests/test_r1244_quantum_optimization.py::test_counts_to_energy_uses_qiskit_bit_order
    remote_gate:
      - tests/test_r1244_quantum_optimization.py::test_remote_runner_requires_per_call_consent_before_secret_or_sdk
      - tests/test_r1244_quantum_optimization.py::test_remote_runner_requires_rotated_environment_credential
      - tests/test_r1244_quantum_optimization.py::test_hardware_classifier_rejects_simulators_and_unknown_types
      - tests/test_r1244_quantum_optimization.py::test_remote_runner_uses_fake_provider_without_network
    mcp:
      - tests/test_r1244_quantum_optimization.py::test_mcp_catalog_and_tools
      - tests/test_r1244_quantum_optimization.py::test_mcp_stdio_transport_read_only_operations
    agents:
      - tests/test_r1244_quantum_optimization.py::test_managed_quantum_research_profiles_are_valid
---

# R1244 — Aplicabilidade e otimização quântica com GJQ

## Demanda e fronteiras

Implementar, no Core local, um harness original para problemas QUBO/Ising e
QAOA, um servidor MCP stdio e dois perfis subordinados de pesquisa:
aplicabilidade de métodos quânticos e formulação/benchmark de otimização.
O caminho de execução suportado é Qiskit + `gjq-client` da Tiangong. PennyLane
é uma integração opcional de circuitos variacionais documentada pelo GJQ; não é
dependência do harness inicial. Cirq é pesquisado, mas não conectado ao GJQ,
pois os documentos consultados não mostram esse adaptador e o Google Quantum
Engine informa que a API não está aberta ao público. Hugging Face Transformers
é classificado como ML/NLP clássico, não como runtime quântico. XQuad é
referência/intercâmbio, não dependência: o repositório declara AGPL-3.0-or-later,
API pré-1.0 e backends não listados para GJQ.

Não instalar dependências de terceiros, não incorporar código dos links,
não ler/guardar a credencial fornecida em conversa, não autenticar durante a
implementação e não submeter jobs reais como parte deste ciclo. A credencial
exposta deve ser revogada/rotacionada antes de qualquer uso. O artefato apenas
aceita `GJQ_API_KEY` do ambiente em uma chamada remota explicitamente confirmada.

## Contratos

- QUBO schema v1: objeto com `schema_version=1`, `name`, `num_variables`
  (1–20), `constant`, vetor `linear` de comprimento exato e lista
  `quadratic=[[i,j,coefficient], ...]`. Coeficientes devem ser finitos;
  índices inteiros, distintos e dentro do domínio; pares são canonicalizados
  para `i<j` e duplicatas rejeitadas. Bool não é número válido.
- Avaliação: minimizar
  `constant + Σ linear[i] x[i] + Σ quadratic[i,j] x[i]x[j]`, com bits
  `x[i] ∈ {0,1}`. Baseline exato clássico permitido até 16 variáveis,
  resultado determinístico e desempate lexicográfico.
- Conversão Ising: `x[i]=(1-Z[i])/2`; preservar deslocamento constante,
  campos e acoplamentos, sem alterar o argmin. QAOA IR declara estado inicial
  Hadamard, operadores RZ/RZZ do separador de fase, RX do mixer e medição.
- Otimização clássica de ângulos é busca coordenada determinística, com limite
  rígido de avaliações, sem alegação de ótimo global. Cada avaliação remota
  corresponde a no máximo um job e usa Sampler finito em circuito Qiskit
  transpilado para o backend selecionado.
- MCP: `quantum_catalog`, `qubo_inspect`, `qaoa_prepare` (locais e sem rede) e
  `qaoa_optimize_gjq` (efeito externo, marcado como tal). A operação remota
  exige `confirm_remote=true`, backend exato, `GJQ_API_KEY` no ambiente,
  `max_evaluations` explícito (1–8), shots (1–2048) e `max_total_shots`
  suficiente e limitado a 16.384. Limites medem jobs/shots, não preço em
  dinheiro; o provedor pode cobrar segundo regras não conhecidas pelo Core.
  `list_backends()` só é chamado após o gate remoto; simuladores e tipos de
  backend desconhecidos são recusados como hardware.
- Resultados não incluem chave, cabeçalho, cache de conta nem resposta SDK
  integral. O transporte stdio nunca recebe prints de SDK no stdout. Falha de
  dependência, autenticação, disponibilidade ou tipo de backend retorna estado
  explícito, sem simular execução.
- OpenCode recebe instrução de registro V2 com MCP desabilitado por padrão;
  a configuração compartilhada existente não é migrada neste escopo.
- Perfis novos são criados/validados pelo lifecycle do primário, `allow_edit`
  falso, sem webfetch/tarefa/shell arbitrário; cada um referencia esta spec e
  o teste focal. Criação/registro não significam execução de pesquisa.

## Critérios de aceitação

- AC1: validar QUBO finito e canônico, calcular energia e hash determinístico;
  rejeitar esquemas, booleanos, índices, duplicatas e limites inválidos.
- AC2: baseline clássico exato e conversão QUBO→Ising têm resultados
  reproduzíveis para fixtures conhecidas; o limite de dimensão é fail-closed.
- AC3: QAOA IR respeita convenções de fase documentadas e o otimizador não
  ultrapassa o orçamento de avaliações; não promete otimalidade.
- AC4: caminho GJQ usa Qiskit/Sampler/transpilação da documentação primária,
  dependências opcionais importadas sob demanda e backend remoto identificado
  por metadado do provedor. Testes usam provider falso, sem rede.
- AC5: nenhuma consulta/execução remota antes da confirmação explícita em cada
  chamada; credencial ausente ou backend não comprovadamente hardware bloqueia
  sem expor dados sensíveis. Nenhum job de hardware é enviado neste ciclo.
- AC6: MCP inclui quatro ferramentas e passa teste de transporte stdio para as
  operações locais; anúncio do MCP fica desabilitado por padrão na configuração
  de exemplo V2.
- AC7: dois perfis gerenciados distintos são válidos, subordinados a MarceloClaro,
  somente leitura e não alegam execução nem vantagem quântica.
- AC8: documentação cita fontes primárias, compatibilidade/limites/licenças,
  segredo rotacionado e instruções de ativação; nenhuma dependência foi
  instalada e nenhum código terceiro foi copiado.

## Arquivos no escopo

- `integrations/quantum_optimization.py`
- `integrations/quantum_optimization_mcp.py`
- `tests/test_r1244_quantum_optimization.py`
- `docs/quantum/QUANTUM_OPTIMIZATION_GJQ.md`
- `agents/catalog/quantum-applicability-researcher.md`
- `agents/catalog/quantum-optimization-researcher.md` (via lifecycle)
- `opencode.json` somente pela compilação dos perfis locais; sem ativar o MCP.

## Verificação exigida

RED no teste focal antes da implementação; GREEN e regressões focais após.
Executar SpecVerifier e BehavioralGate do Core, inspecionar diff e configuração
gerada, registrar revisão/limitações e ciclo de evolução. Testes locais não
comprovam compatibilidade do SDK externo, acesso à conta, execução em QPU,
vantagem quântica nem custo monetário.

## Fontes consultadas

- Tiangong/GJQ docs: https://tiangongqs.com/docs/en/index.html?theme=light
- GJQ framework e autenticação: https://tiangongqs.com/docs/en/framework/index.html
- GJQ backends, Qiskit circuit transpilation, Sampler/Estimator, PennyLane:
  `framework/{backends,circuits,jobs,pennylane,installation}.html`.
- GJQ SDK e changelog: https://github.com/guoji-quantum/gjq_client
- Qiskit: https://github.com/Qiskit/qiskit ; docs consultadas via Context7
  (`/qiskit/qiskit`).
- PennyLane: https://github.com/PennyLaneAI/pennylane ; docs consultadas via
  Context7 (`/pennylaneai/pennylane`).
- Cirq / Google Quantum Engine:
  https://github.com/quantumlib/Cirq e https://quantumai.google/cirq/google/engine.
- XQuad: https://github.com/QuipNetwork/xquad e
  https://github.com/QuipNetwork/xquad/blob/main/xqsa/README.md.
- Transformers: https://github.com/huggingface/transformers e
  https://huggingface.co/docs/transformers/index.

## Estado

Spec criada antes de implementação. `python3 -m marceloclaro.cli doctor` não
importa por `whoosh` ausente no Python global; `.venv/bin/python -m
marceloclaro.cli doctor` executa em modo estrutural e retorna `degraded`, com
16 checks pass, 6 warn, 0 fail. Nenhuma dependência quântica está instalada.
Busca web geral indisponível (HTTP 402); documentação oficial acessada por URL.
