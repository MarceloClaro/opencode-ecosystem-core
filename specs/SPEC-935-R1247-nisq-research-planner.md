---
spec_id: SPEC-935-R1247
title: Planejador auditável de pesquisa NISQ e lacunas quânticas
component: integrations.quantum_research
status: proposed
test_file: tests/test_r1247_quantum_research.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    AC1:
      - tests/test_r1247_quantum_research.py::test_catalog_covers_nisq_methods_and_preserves_tiangong_labels
      - tests/test_r1247_quantum_research.py::test_user_supplied_tiangong_resources_are_unverified_and_non_executable
    AC2:
      - tests/test_r1247_quantum_research.py::test_invalid_payloads_fail_closed
      - tests/test_r1247_quantum_research.py::test_cli_rejects_duplicate_json_keys
    AC3:
      - tests/test_r1247_quantum_research.py::test_plan_is_gap_aware_deterministic_and_never_claims_execution
      - tests/test_r1247_quantum_research.py::test_plan_reports_common_and_method_specific_gaps_without_recommendation
      - tests/test_r1247_quantum_research.py::test_explicitly_declaring_no_constraints_is_not_a_gap
    AC4:
      - tests/test_r1247_quantum_research.py::test_catalog_covers_nisq_methods_and_preserves_tiangong_labels
    AC5:
      - tests/test_r1247_quantum_research.py::test_catalog_covers_nisq_methods_and_preserves_tiangong_labels
    AC6:
      - tests/test_r1247_quantum_research.py::test_catalog_cli_and_plan_cli_are_local_json_only
      - tests/test_r1247_quantum_research.py::test_cli_rejects_duplicate_json_keys
    AC7:
      - tests/test_r1247_quantum_research.py::test_skill_and_managed_profiles_route_without_editing_cards
    AC8:
      - tests/test_r1247_quantum_research.py::test_plan_is_gap_aware_deterministic_and_never_claims_execution
    AC9:
      - tests/test_r1247_quantum_research.py::test_user_supplied_tiangong_resources_are_unverified_and_non_executable
---

# SPEC-935-R1247 — Planejador de pesquisa NISQ e auditoria das aplicações Tiangong

## Demanda e autoridade

Estender o Pesquisador Universal com planejamento de pesquisa NISQ/quântica,
análise explícita de lacunas, métodos híbridos clássicos-quânticos, simulação,
cozimento quântico, autômatos celulares quânticos e mitigação de erro. Auditar os
rótulos `VRP`, `WSA`, `HDR`, `QSS`, `OPC`, `PTO`, `CA`, `RSA`, `ECC` e `SDES`
sem expandir siglas cuja semântica não foi confirmada. MarceloClaro continua como
orquestrador primário.

## Escopo desta entrega

1. Criar um planejador local, determinístico e sem dependências externas que
   exponha catálogo de métodos, pré-requisitos, lacunas e próximos passos de
   pesquisa; seu produto é um plano, nunca uma solução ou resultado quântico.
2. Incorporar o inventário de evidências/limites disponível para os dez rótulos
   Tiangong e registrar uma matriz de auditoria e roadmap.
3. Estender a skill do Pesquisador Universal com protocolo, invocação e
   roteamento para os perfis quânticos já existentes.
4. Reutilizar os harnesses locais existentes somente nos limites documentados;
   solver novo por domínio exige contrato primário confirmado e spec própria.

## Fora de escopo e segurança

- Não instalar dependências, consultar rede, ler credenciais, autenticar,
  submeter jobs, executar QPU, habilitar MCP remoto ou executar bundles da Tiangong.
- Não declarar vantagem quântica, superioridade, custo, otimalidade ou mitigação
  de ruído eficaz sem benchmark e evidência próprios.
- Não inferir a semântica de `WSA`, `QSS`, `OPC`, `PTO`, `CA`, `RSA`, `ECC` ou
  `SDES` a partir apenas do rótulo, de strings de bundle ou de endpoints.
- Não reimplementar como se fosse equivalente qualquer aplicação proprietária.

## Contrato de software

- Módulo: `integrations/quantum_research.py`.
- API pública: `research_catalog()`, `tiangong_application_catalog()` e
  `build_research_plan(payload)`; CLI local `python -m integrations.quantum_research`
  com `catalog` ou `plan` (JSON fornecido por stdin).
- Entrada JSON versionada, com chaves allowlisted, limites estritos e validação
  finita; campos ausentes produzem lacunas, não valores presumidos.
- Saída inclui hash canônico da solicitação, hipóteses/métodos candidatos,
  pré-requisitos declarados e faltantes, rota local conhecida, limitações,
  `network=false`, `execution_attempted=false`, `jobs_submitted=0` e
  `quantum_advantage="not_assessed"`.
- Completar os pré-requisitos declarados permite avançar para protocolo de
  pesquisa, não autoriza execução nem prova viabilidade do método.

## Critérios de aceitação executáveis

- `AC1` — catálogo determinístico cobre baselines clássicos, métodos híbridos,
  simulação clássica, annealing, autômatos celulares quânticos e mitigação de
  erros e registra recursos declarados pelo operador com proveniência explícita.
- `AC2` — validação da entrada rejeita versões, campos, tipos, métodos, chaves JSON
  duplicadas e valores
  numéricos inválidos; listas e recursos têm limites documentados.
- `AC3` — plano detecta lacunas comuns e por método, preserva referências de
  evidência e não converte entradas declaradas em fatos verificados.
- `AC4` — os dez rótulos são listados exatamente como fornecidos; sem evidência de
  fonte suficiente, semântica permanece `unverified` e solver fica bloqueado.
- `AC5` — somente rotas locais já existentes são citadas; VRP não é descrito como
  execução quântica e HDR não como reconhecimento treinado. Outros rótulos não
  recebem implementação presumida.
- `AC6` — CLI lê JSON de stdin, emite JSON determinístico e não usa rede, arquivos
  indicados pelo payload, shell, credenciais ou dependências quânticas.
- `AC7` — skill descreve o novo planejamento e roteamento; nenhum perfil gerenciado
  `allow_edit: false` é editado diretamente.
- `AC8` — testes RED→GREEN focais e regressão quantum/Tiangong passam; doctor é
  executado; limitações, recibos e reflexão não alegam revisão externa ausente.
- `AC9` — inventário de hardware/simuladores recebido do usuário é preservado
  como snapshot não verificado; não é tratado como estado live, elegibilidade,
  autorização de job ou prova de acesso ao provedor.

## Evidência e estado inicial

- Capturas REA R1089 locais abrangem páginas-raiz HDR, RSIR e VRP e bundles
  estáticos; não incluem as outras sete aplicações solicitadas além de HDR/VRP.
- Evidência REA anterior: `ev_d4fafa5023de258fbccba21eaec6f8845ddd4302d6467740bdc659f0018808ef`,
  raiz SHA-256 `bfddef3dce8945269bcadd62a18f83ddc11740260ac2f20420e8863f9ad79888`.
  O resumo disponível aponta inventário estático, 28 candidatos de rota e zero
  janelas de navegador; não prova comportamento runtime ou backend.
- Nova tentativa de análise REA do diretório completo foi concluída pelo REA,
  mas a resposta excedeu 10 MiB (`resource_constraint`); tentativas em diretórios
  menores também excederam o limite. Não repetir a análise idêntica.
- Fetch direto em 20/11/2026 bloqueado porque `robots.txt` respondeu HTTP 500;
  busca web respondeu HTTP 402. Uma chamada Antigravity devolveu task/prompt,
  não resultado observado de navegador.
- O usuário informou um inventário Tiangong em 20/11/2026 (backend, qubits,
  estado, calibração e métricas T1/T2). O dado será rotulado como `user_supplied`,
  sem consulta live ou confirmação independente; listar recursos não autoriza
  job, autenticação ou uso de credenciais.
- Árvore inicial tinha modificações concorrentes em `mci/metabus_store.py`,
  `evolution/cycles.json` e testes R1243/R886 em checkpoints distintos; preservar
  integralmente e validar o diff antes de concluir.

## Sequência após esta entrega

1. Atualizar evidência primária por REA/navegador autorizado, em lotes pequenos,
   sem reanalisar o mesmo diretório completo acima do limite MCP.
2. Fixar contrato, entradas/saídas, objetivo e baseline de cada domínio confirmado.
3. Para cada domínio, abrir spec e testes próprios antes de implementar solver;
   preferir algoritmo clássico local como baseline e manter execução remota
   desabilitada por padrão.
