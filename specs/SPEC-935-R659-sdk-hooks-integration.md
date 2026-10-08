---
spec_id: SPEC-935-R659
title: Execucao coerente de hooks e ferramentas no SDK local
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R659_R662_RELEASE_GATE.json
component: hooks/engine.py + hooks/policy.py + integrations/opencode_agent_sdk.py
test_file: tests/test_r659_sdk_hooks_contract.py
---

# R659 — Correção do caminho agente → hook → ferramenta → resultado

## Contratos

1. PreToolUse respeita matchers globais e callbacks legados; negação/erro bloqueia
   ferramenta. Adaptar assinatura antes da execução; TypeError do corpo não repete hook.
2. SessionStart, PostToolUse e SessionEnd executam no ciclo real, inclusive erro
   e término por orçamento. Falha de hook é explícita; pós-hook não desfaz efeito.
3. JSON inválido ou não objeto, argumentos fora do schema e ferramenta fora da
   allowlist não chegam ao handler. dispatch direto usa a mesma validação.
4. Schemas completos e forma legada por propriedades mantêm compatibilidade;
   conversa HTTP inclui assistant/tool_calls antes das respostas role=tool.
5. Orçamentos e CLI recusam entradas inválidas; erro de execução retorna saída
   não zero. Não confundir disponibilidade do provedor com inferência concluída.
6. Logs de hooks não expõem comandos contendo credenciais; hooks importados
   continuam declarativos. TDD precede mudanças; prova real não usa respostas simuladas.

## Critérios de aceitação executáveis

- `R659-HOOKS` — Matchers, assinaturas e lifecycle têm efeitos observáveis e únicos.
- `R659-TOOLS` — Argumentos inválidos não executam handlers; histórico é válido.
- `R659-ERRORS` — Erros e orçamento terminam explicitamente, preservando compatibilidade.
