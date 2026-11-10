# SPEC-935-R1133 — Contrato de runtime e ativação das stop rules

**Status:** implementação local, sem efeitos externos
**Data:** 2026-11-10
**Depende de:** R1132 (camada de cognição), R212 (TaskRuntime), R110 (doctor)
**Origem:** limitação 5 do estudo “A casa que ajuda a pensar” e literatura de
runtime guardrails para agentes.

## 1. Objetivo

Ativar as stop rules no loop do orquestrador por meio de um contrato de runtime
que classifica ações por reversibilidade/risco e decide `allow`, `ask`, `defer`
ou `block` antes da ação, com auditoria e caminhos humanos.

## 2. Requisitos

- **R1.** `ActionClass`: `read_only`, `reversible`, `irreversible`, `high_risk`.
  Classe desconhecida falha fechada como `high_risk`.
- **R2.** `RuntimeState`: sessão, falhas consecutivas, specs abertas, manutenção,
  produtividade, trocas de contexto, hora local, parada solicitada, aprovação
  humana e contadores de decisões.
- **R3.** `RuntimeContract.evaluate`:
  - `stop` → `block` para ações não `read_only`; `defer` para `read_only`;
  - `ask` → `ask` para ações não `read_only`; `allow` para `read_only`;
  - `defer` → `defer` para ações não `read_only`; `allow` para `read_only`;
  - `irreversible` exige aprovação humana explícita;
  - `high_risk` exige aprovação humana e, se configurado, validação externa;
  - caso contrário, `allow`.
- **R4.** `authorize()` registra a decisão, atualiza contadores e mantém
  auditoria limitada a `max_audit_events`.
- **R5.** `require()` levanta `ContractViolation` quando a decisão não é
  `allow`.
- **R6.** O orquestrador expõe `authorize_action`, `require_action`,
  `update_runtime_context` e `runtime_contract_status`.
- **R7.** `dispatch_ready` consulta o contrato antes de conceder leases. Se a
  decisão não for `allow`, bloqueia as tarefas prontas, registra a explicação e
  publica `runtime_contract.blocked`.
- **R8.** `report_completion` registra o outcome e publica
  `runtime_contract.stop` quando o limiar de falhas é atingido.
- **R9.** A CLI `core_cognition.cli runtime --request --state` avalia um
  `ActionRequest` contra um `RuntimeState`.
- **R10.** Nenhum módulo faz rede, hardware, subprocesso ou efeito externo.

## 3. Não objetivos

- Garantir segurança completa de agentes.
- Substituir revisão humana, ética ou jurídica.
- Executar ações irreversíveis sem aprovação.
- Prever fidelidade, eficácia ou vantagem quântica.
- Interceptar efeitos de ferramentas que não chamam o contrato.

## 4. Critérios de aceitação

- **CA01.** `read_only` em estado `stop` retorna `defer`.
- **CA02.** `reversible` em estado `stop` retorna `block`.
- **CA03.** `irreversible` sem aprovação humana retorna `ask`.
- **CA04.** `irreversible` com aprovação humana retorna `allow`.
- **CA05.** `high_risk` sem aprovação humana retorna `ask`.
- **CA06.** `high_risk` com validação externa obrigatória e ausente retorna
  `ask`.
- **CA07.** Classe desconhecida retorna `ask` como `high_risk`.
- **CA08.** Horário de silêncio retorna `defer` para ação não `read_only`.
- **CA09.** `require()` levanta `ContractViolation` em decisão não `allow`.
- **CA10.** `dispatch_ready` não concede leases quando o contrato bloqueia.
- **CA11.** `report_completion` incrementa falhas e publica o evento de parada
  quando o limiar é atingido.
- **CA12.** `tests/test_r1133_runtime_contract.py` passa sem rede ou hardware.

## 5. Técnicas adaptadas

| Técnica | Fonte | Onde entra |
|---|---|---|
| Verificação de conformidade em runtime | Runtime Compliance Verification for AI Agents (2026), DOI 10.1007/978-3-032-41160-0_16 | `runtime_contract.py` |
| Política como código/guardrail | Policy-as-Prompt (2025), DOI 10.48550/arxiv.2509.23994 | `RuntimeContract` |
| Autoridade por classe de ação | Action-Class Authority (2026), DOI 10.2139/ssrn.7095138 | `ActionClass` |
| Tradução em camadas de normas | Layered Translation Method (2026), DOI 10.48550/arxiv.2604.05229 | política + auditoria |
| Limites do que pode ser imposto | What Can Be Enforced? (2026), DOI 10.48550/arxiv.2607.22868 | seção de limites |
| Segurança como contrato de runtime | Agent Safety Should Be a Runtime Contract (2026), DOI 10.48550/arxiv.2608.11274 | `authorize`/`require` |
| Síntese online de enforcement | Online Synthesis for Runtime Enforcement of Safety in Multiagent Systems (2021), DOI 10.1109/tcns.2021.3061900 | circuit breaker e bloqueio |

## 6. Evidência local

- `core_cognition/runtime_contract.py`
- `marceloclaro/orchestrator.py` (`authorize_action`, `dispatch_ready`,
  `report_completion`)
- `tests/test_r1133_runtime_contract.py`
- `core_cognition/cli.py` (comando `runtime`)
- `docs/CORE_COGNITION.md`

## 7. Limites

O contrato é um gate de política, não uma prova de segurança. Ele só aplica o
que consegue observar: ferramentas que não chamam `authorize_action` não são
interceptadas. A aprovação humana é declarativa; o contrato não verifica
identidade, consentimento ou competência de quem aprova. Ações irreversíveis
exigem integração explícita do tool/agent com o contrato.
