# Camada de cognição do Core (R1132)

A camada `core_cognition/` transforma achados do estudo sobre próteses
cognitivas autorais em instrumentos operacionais. Ela **não** mede eficácia
cognitiva, não valida clinicamente o sistema e não substitui revisão humana.
Os instrumentos são heurísticas estruturais, auditáveis e fail-closed quando
aplicável.

## Módulos

| Módulo | Função | Limite |
|---|---|---|
| `cognitive_function_map.py` | Mapa explícito de funções cognitivas externalizadas | Contrato de leitura; não prova eficácia |
| `epistemic_risk.py` | Overclaim, falsa objetividade, viés de automação, deskilling, sobrecarga | Heurísticas; não mede o usuário |
| `stop_rules.py` | Continuar, perguntar, adiar ou parar; caminhos humanos | Não substitui julgamento clínico |
| `claims_ledger.py` | Claims com status, falsificador, evidência e validação externa | Organiza evidência; não a produz |
| `contestability.py` | Exportação, segunda pessoa, documentação, apelação e saída | Proxies estruturais; não prova usabilidade |
| `n_of_1.py` | Validação de protocolo N-of-1 e resumo descritivo | Não executa o estudo nem infere causalidade |
| `runtime_contract.py` | Contrato de runtime: allow/ask/defer/block por classe de ação | Só aplica o que consegue observar |
| `doctor_checks.py` | Três checks para o `doctor` | Estruturais; não substituem a suíte |
| `cli.py` | Interface de linha de comando | Sem rede, hardware ou LLM |

## CLI

```bash
python3 -m core_cognition.cli map
python3 -m core_cognition.cli audit
python3 -m core_cognition.cli risk
python3 -m core_cognition.cli stop --state state.json
python3 -m core_cognition.cli ledger --path claims.jsonl
python3 -m core_cognition.cli ledger --template claims.jsonl
python3 -m core_cognition.cli contest
python3 -m core_cognition.cli n-of-1 --template protocol.json
python3 -m core_cognition.cli n-of-1 --validate protocol.json
```

### Exemplo de estado para `stop`

```json
{
  "session_minutes": 130,
  "consecutive_failures": 1,
  "maintenance_minutes": 80,
  "productive_minutes": 60,
  "open_specs": 12,
  "context_switches": 8,
  "local_hour": 23,
  "user_requested_stop": false
}
```

A decisão inclui `action`, `rule`, `reason` e um `humane_default` com
explicação, alternativa, contato humano e saída.

## Contrato de runtime (R1133)

O contrato classifica ações em `read_only`, `reversible`, `irreversible` e
`high_risk`. Antes de uma ação, `RuntimeContract.evaluate` aplica as stop rules
e as exigências de aprovação humana. Decisões possíveis: `allow`, `ask`,
`defer`, `block`.

- `read_only`: permitido em `ask`/`defer`; adiado em `stop`.
- `reversible`: bloqueado em `stop`; pergunta em `ask`.
- `irreversible`: exige `human_approved=True`.
- `high_risk`: exige aprovação humana e, se configurado, validação externa.
- Classe desconhecida: tratada como `high_risk` (fail-closed).

### No orquestrador

```python
from marceloclaro.orchestrator import MarceloClaroOrchestrator

orch = MarceloClaroOrchestrator()
orch.update_runtime_context(session_minutes=130, local_hour=12)
decision = orch.authorize_action("publicar", "irreversible", human_approved=False)
# decision.decision == "ask"
```

`dispatch_ready` consulta o contrato antes de conceder leases. Se a decisão
não for `allow`, as tarefas prontas são bloqueadas e a explicação fica em
`explain_assignment`. `report_completion` registra o outcome e publica
`runtime_contract.stop` quando o limiar de falhas é atingido.

### CLI

```bash
python3 -m core_cognition.cli runtime --request request.json --state state.json
```

`request.json` deve conter `action_id`, `actor_id`, `tool`, `action_class` e,
opcionalmente, `human_approved`, `external_validation` e `metadata`.
`state.json` aceita os campos de `RuntimeState`.

## Mapa de funções cognitivas

O mapa fica em `core_cognition/data/cognitive_function_map.json`. Cada entrada
tem seis campos obrigatórios:

```json
{
  "function": "memory",
  "module": "mci/metabus.py",
  "mechanism": "descrição do mecanismo",
  "failure_addressed": "falha que a função endereça",
  "evidence": "arquivos ou artefatos que sustentam a leitura",
  "limit": "limite explícito"
}
```

O `doctor` verifica cobertura das funções obrigatórias, existência dos módulos
e presença de limite. O mapa não é uma prova de que o módulo funciona; é um
contrato de leitura e um gatilho de auditoria.

## Claims ledger

Cada linha do ledger é um JSON com:

- `claim_id`, `text`, `status`, `falsifier`;
- `evidence` (lista de objetos);
- `source_sha256` (opcional, 64 hex);
- `external_validation` (obrigatório para `externally_validated`);
- `history`.

Status válidos: `observation`, `inference`, `hypothesis`, `tested`,
`externally_validated`, `refuted`. A promoção a `externally_validated` exige
`independent: true`, `verifier` e `artifact_sha256` de 64 hex.

## Protocolo N-of-1

O validador exige:

- desenho ABAB;
- pelo menos cinco desfechos distintos;
- randomização, cegamento e pré-registro;
- ética com consentimento, supervisão clínica e proteção de dados;
- regras de parada;
- duração mínima de 8 semanas e washout explícito.

O resumo é descritivo (`mean_A`, `mean_B`, `delta_B_minus_A`) e não deve ser
lido como efeito causal.

## Contestabilidade

O relatório cobre cinco portas: exportação, segunda pessoa, documentação,
apelação e saída. O `require()` recusa releases com score abaixo de 0.8. São
proxies estruturais; a avaliação de usabilidade e justiça exige revisão humana.

## Limites e anti-overclaim

- A camada não demonstra que o Core melhora cognição, previne Alzheimer ou
  trata demência.
- O mapa cognitivo é interpretativo; não é biomarcador.
- Trust score, stake e token economy não são medidas de verdade.
- O protocolo N-of-1 é um validador de desenho, não um estudo executado.
- O claims ledger organiza evidência; não a produz.

## Testes

```bash
.venv/bin/python -m pytest tests/test_r1132_core_cognition.py -q
```

A suíte cobre mapa, risco epistêmico, regras de parada, ledger, contestabilidade,
N-of-1 e os três checks do doctor.
