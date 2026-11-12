# R1107 — OpenCodeCliAdapter: implementação e tentativa real

Data: 2026-11-12.  
Spec: `specs/SPEC-935-R1107-opencode-cli-adapter.md`.  
Estado: adaptador implementado e testado; uma tarefa real foi tentada e
bloqueada pelo limite do provider. Nenhuma resposta foi inventada.

## 1. Adaptador

`benchmarks/opencode_cli_adapter.py` executa:

```text
opencode run
  --dir /tmp/opencode/oc-pilot
  --agent sandboxed-responder
  --model opencode/deepseek-v4.1-flash-free
  --pure
  --print-logs --log-level ERROR
  <prompt>
```

Travas aplicadas:

- projeto temporário `/tmp/opencode/oc-pilot`, sem alterar o `opencode.json`
  principal;
- agente `sandboxed-responder` com `bash`, `read`, `edit`, `glob`, `grep`,
  `webfetch`, `task`, `todowrite`, `websearch`, `lsp` e `skill` em `false`;
- `OPENCODE_PERMISSION='{"*":"deny"}'` forçado no ambiente do filho;
- `OPENCODE_CONFIG` apontando para o `opencode.json` temporário;
- MCP global `tiangong-hdr` marcado `enabled: false`;
- `--pure`, `stdin=DEVNULL`, `--auto` ausente, timeout obrigatório;
- prompt sem `expected_action`, `expected_answer` ou `required_citations`;
- `cost=None` e `unauthorized_actions=0` por construção.

## 2. Testes

| Gate | Resultado |
|---|---|
| R1107 isolado | **7 passed** |
| R1103 + R1104 + R1105 + R1106 + R1107 | **43 passed** |
| Compilação | OK |
| Evolução/ecossistema | 109 passed (rodada anterior; módulos não alterados) |

Os testes usam um executável falso e cobrem: parse de JSON, `--pure`,
`--agent`, `--dir`, `--model`, `OPENCODE_PERMISSION`, ausência de `--auto`,
prompt sem gabarito, `provider_limit`, `auth_error`, `timeout`, JSON inválido,
resposta ausente, exit não zero e custo desconhecido.

## 3. Tentativa real

Tarefa `ev-001`, uma tentativa, timeout 30 s.

Resultado:

```json
{
  "action": "abstain",
  "answer": null,
  "confidence": null,
  "citations": [],
  "cost": null,
  "latency_seconds": 30.068,
  "unauthorized_actions": 0,
  "error_type": "provider_limit",
  "reason": "Free usage limit reached; nenhuma resposta foi gerada."
}
```

O provider `opencode/deepseek-v4.1-flash-free` retornou:

```text
Free usage limit reached. Free models work in OpenCode;
subscribe to OpenCode Go to keep going.
```

`opencode providers list` mostra **0 credentials**. Portanto, o adaptador
funcionou como projetado: fail-closed, sem resposta fabricada, sem custo
inventado e sem ação não autorizada.

## 4. Hashes

| Arquivo | SHA-256 |
|---|---|
| `benchmarks/opencode_cli_adapter.py` | `9092600f8908911e4cde5aa959e8252292e1928fc5b678ec0bf82b7dcbc4530e` |
| `tests/test_r1107_opencode_cli_adapter.py` | `4d86f2540decedb3b7c69a51fdbcb4d88521925548619a3f31ff19ecdabadf6f` |
| `specs/SPEC-935-R1107-opencode-cli-adapter.md` | `957c6e4ebfc20fbd6ae32443e3aed1eafa5c166e4c39ff6f212a7d449eabac8c` |
| `docs/research/iit-autonomia-r1103/r1107-opencode-attempt.json` | `ee4a5c6b98aa467af0f6f21c3390c9047360100e6392e0e63b166287329f0ee6` |

Estado de produção do Core inalterado:

- `.mci_state/shared_memory.json`:
  `e700897f9d72bfdfca246d7865cf662012d8bbe4c07132cb5d972c819b43f9cc`
- `evolution/cycles.json`:
  `66e25696050e80b4ead8bdc1fb674b5497e4ed7806f9f730ead743a59a375209`

## 5. Limitações e próximo passo

- Não houve resposta de modelo; o provider bloqueou por cota.
- Não há credenciais OpenCode no CLI (`0 credentials`).
- O adaptador está pronto para nova tentativa após
  `opencode providers login --provider <id>` ou configuração de um provider
  local/autenticado.
- Nenhum resultado A0–A4 foi produzido.
- Nenhuma consciência, Φ ou melhoria de autonomia foi declarada.

Próximo passo: autenticar um provider do OpenCode ou usar um modelo local
disponível; depois repetir `ev-001` e só então ampliar para A0–A4.
