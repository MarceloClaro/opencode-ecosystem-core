# R138 — Versionamento da SPEC-108 (OpenCode Go + Zen + roteamento de modelos)

## Objetivo

Fechar e versionar a frente SPEC-108 (providers OpenCode Go/Zen, roteador
de modelos, comandos e capacidades cloud/go-zen no OpenCode CLI), que
estava completa e testada na árvore de trabalho mas ainda não commitada.

## Contexto

A SPEC-108 já existia com `status: verified` e uma suíte CA-driven
(`tests/test_opencode_go_zen.py`, 39 testes) verde, mas os fontes nunca
haviam sido commitados. Este ciclo os versiona sobre a base reconciliada
pelo R137 (gerador `opencode.json` reproduzível por slug).

## Mudanças Entregues

1. **`integrations/opencode_go.py`** (novo): `OpenCodeGoProvider` — catálogo
   de modelos Go (kimi-k2.7-code, deepseek-v4-pro, glm-5.2, qwen3.7-max…).
2. **`integrations/opencode_zen.py`** (novo): `OpenCodeZenProvider` —
   modelos curados do Zen.
3. **`integrations/model_router.py`** (novo): `ModelRouter` — roteamento por
   tipo de tarefa (coding/reasoning/academic…) com alternativas.
4. **`integrations/opencode_cli.py`**: bloco `provider` (opencode-go/zen com
   apiKey via env), `model` padrão e comandos `models`/`route`/`sdd`/`tdd`.
   (A correção de slug e a classe `OpenCodeCLIIntegration` já entraram no
   R137; aqui só se adicionam os providers/comandos.)
5. **`opencode.json`**: regenerado com o bloco de providers + os 2 agentes
   go/zen (173 agentes, reproduzível pelo gerador).
6. **`agents/catalog/opencode-go-agent.md` / `opencode-zen-agent.md`** (novos).
7. **`specs/SPEC-108-*.md`** + **`tests/test_opencode_go_zen.py`** (39 testes).

## Verificação

- `python3 -m pytest tests/test_opencode_go_zen.py -q` → 39 passed.
- `python3 -m pytest tests/ -q` completo (zero regressões).
- `python3 -m integrations.opencode_cli` reproduz o `opencode.json`
  commitado (garantia do R137 mantida com providers).

## Lições

1. **Ordem de dependência importa em infra compartilhada.** O `opencode.json`
   e o gerador são compartilhados entre a frente cloud (R137) e a SPEC-108.
   Reconciliar o gerador primeiro (R137, chaveamento por slug) deixou o
   delta da SPEC-108 limpo: apenas providers/comandos, sem re-chaveamento.
2. **Dívida de numeração assumida:** o frontmatter da SPEC-108 declara
   `cycle: R108`, que colide com o R108 do ledger (fusão do pipeline
   científico). Não reescrevi retroativamente; registro o ato de
   versionamento como R138 e deixo a colisão documentada — mesmo padrão da
   colisão `SPEC-935-R130.md` da frente cloud.

## Score

**8.3/10**

- Versiona uma frente já testada de forma limpa, aproveitando a
  reconciliação do R137 para um diff mínimo.
- Não valida os providers contra os endpoints reais (apiKey via env; sem
  chamada de rede nos testes) — a verificação é estrutural/CA, não E2E.
- Herda a dívida de numeração (`cycle: R108` no frontmatter).
