# SPEC-935-R471 — Compatibilidade de Invocação do Reversa no OpenCode Ecosystem Core

## Objetivo

Eliminar o bloqueio de pipelines Reversa quando uma skill de fase estiver marcada como `user-invoked`, especialmente com `disable-model-invocation: true` no `SKILL.md` e/ou `policy.allow_implicit_invocation: false` em `agents/openai.yaml`.

O orquestrador deve preservar a experiência de continuidade (`CONTINUAR`) sem obrigar o usuário a digitar manualmente `/reversa-clarify`, `/reversa-plan` ou qualquer outra skill de fase. Quando a invocação implícita estiver proibida, o handoff correto é **ler o `SKILL.md` do próximo agente e executar suas instruções no contexto atual**, não chamar o Skill tool/subagente pelo nome.

## Contexto do defeito

A política moderna do Reversa separa pontos de entrada `model-invoked` de agentes de fase `user-invoked`. Isso reduz contexto permanente, mas cria uma incompatibilidade quando um orquestrador antigo continua tentando ativar um agente de fase pelo nome após o usuário responder `CONTINUAR`.

Sintoma típico:

```text
Error: Skill reversa-clarify cannot be used with Skill tool due to disable-model-invocation.
Ask the user to run /reversa-clarify themselves.
```

Esse comportamento viola a intenção do pipeline, porque `CONTINUAR` já é consentimento explícito para avançar.

## Invariantes

1. Nunca remover `disable-model-invocation: true` apenas para contornar o erro.
2. Nunca alterar `allow_implicit_invocation: false` para `true` apenas para permitir encadeamento automático.
3. O orquestrador deve detectar ambas as marcas, Claude/Agent Skills e OpenAI/Codex.
4. Skill marcada como `user-invoked` deve usar `read-and-execute`.
5. Skill sem bloqueio pode usar ativação nativa; leitura do `SKILL.md` permanece fallback válido.
6. `CONTINUAR` deve ser tratado como consentimento para o handoff já proposto, não como uma nova tentativa de auto-invocação implícita.
7. O dispatcher não executa código, shell, rede ou modelo; apenas resolve caminhos e classifica metadados.
8. Nomes de skill devem ser validados para impedir traversal de diretório.
9. A resolução deve suportar raízes usuais de harness: `.agents/skills`, `.claude/skills`, `.kiro/skills`, `.opencode/skills`, `agents` e `skills`.
10. O OpenCode Ecosystem Core deve documentar a mesma regra em `AGENTS.md` e no agente `agents/catalog/reversa.md`.

## Contrato do dispatcher

Módulo: `reversa_universal/skill_dispatch.py`.

Entrada:

```python
ReversaSkillDispatcher(project_root=".").plan("reversa-clarify")
```

Saída mínima:

```python
{
    "skill_name": "reversa-clarify",
    "found": True,
    "skill_path": ".../reversa-clarify/SKILL.md",
    "user_invoked": True,
    "execution_mode": "read-and-execute",
    "reason": "disable-model-invocation=true; allow_implicit_invocation=false",
    "instruction": "..."
}
```

## Critérios de aceitação

- CA1: Detecta `disable-model-invocation: true` no frontmatter e retorna `read-and-execute`.
- CA2: Detecta `allow_implicit_invocation: false` em `agents/openai.yaml` mesmo sem a flag no `SKILL.md`.
- CA3: Skill sem restrição retorna `native-or-read`.
- CA4: Skill ausente retorna fallback seguro, sem exceção de I/O.
- CA5: Nome contendo `/`, `..` ou caracteres fora da allowlist é rejeitado com `ValueError`.
- CA6: `REVERSA_SKILLS_ROOT` é aceito como raiz explícita, sem substituir as raízes locais padrão.
- CA7: `ReversaBridge` expõe o plano de handoff para consumidores Python.
- CA8: `AGENTS.md` proíbe orquestradores de transformar `CONTINUAR` em chamada implícita de skill user-invoked.
- CA9: `agents/catalog/reversa.md` usa a política de dispatch antes de acionar subagentes.
- CA10: A suíte existente permanece compatível em Python 3.10–3.14.

## Plano TDD

RED: criar testes para CA1–CA6 e CA7 antes do retrofit textual dos orquestradores.

GREEN: implementar o dispatcher com stdlib, integrá-lo ao `ReversaBridge` e atualizar instruções do OpenCode.

VERIFY: executar `pytest tests/test_r471_reversa_skill_dispatch.py -q` e, no CI, a suíte completa `pytest tests/ -q --tb=short --timeout=120`.

## Limites

Esta camada não substitui o mecanismo nativo de skills do OpenCode, Claude Code, Codex, Cursor, Gemini ou Kiro. Ela resolve a incompatibilidade de roteamento ao fornecer uma decisão explícita e auditável sobre **como** o próximo skill deve ser alcançado.