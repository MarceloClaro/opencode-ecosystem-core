# R129 — Fluxo de trabalho resiliente/resumível (checkpoints)

## Objetivo

Mitigar a fricção de "o trabalho morre quando a sessão acaba" (limites de
sessão/tokens do plano, não corrigíveis por código) com um mecanismo
explícito de retomada: um `PROGRESS.md` vivo na raiz + uma seção no
`CLAUDE.md` documentando a disciplina de checkpoint.

## Motivação

Após rodar `/insights`, o usuário pediu para "corrigir" o bloqueio de
sessão e os erros de "500 output tokens" no Claude CLI e no ecossistema.

Diagnóstico honesto (feito antes de qualquer mudança):
- `~/.claude/settings.json` está limpo — **não há** má-configuração de
  tokens (`CLAUDE_CODE_MAX_OUTPUT_TOKENS` inexistente; modelo
  `claude-fable-5[1m]`). Os "500 tokens"/"limite de sessão" vêm de 2
  sessões antigas não relacionadas; são limites de conta/plano da
  Anthropic — **não** elimináveis por código.
- O problema real e atacável é a **perda de trabalho ao fim da sessão**.
  A resposta é resiliência: checkpoints + estado resumível.

## Mudanças Entregues

1. **`PROGRESS.md` (novo, raiz)**: checkpoint vivo — "Estado atual"
   (branch, suíte, ciclos R123–R128 concluídos, config de ambiente local
   não versionada), "Próximos passos" (independentes/resumíveis) e "Como
   retomar" (doctor → suíte → primeiro pendente sob SDD/TDD). Inclui a
   lista de frentes paralelas a não misturar (SPEC-108/SPEC-1000) e o
   lembrete de que `.env` nunca é versionado.
2. **`CLAUDE.md`**: nova seção "Retomada de trabalho (checkpoints)" —
   ler `PROGRESS.md` primeiro, quebrar em passos commitáveis, atualizar e
   commitar a cada passo, rodar trabalho longo em background.
3. **`tests/test_r129_resumable_workflow.py` (novo)**: 3 testes de
   conteúdo (PROGRESS.md com as seções esperadas; CLAUDE.md documenta a
   retomada).

## Verificação

- TDD de documentação: testes escritos antes → verde (3 passed).
- `python3 -m pytest tests/ -q` completo.

## Lições

1. Honestidade de escopo: o pedido era "corrigir o limite", mas o limite
   é de plano/conta — não há código a mudar em `settings.json` (que está
   correto). Em vez de simular uma correção impossível, ataquei a
   consequência real (perda de trabalho) com resiliência. Diagnosticar
   antes de "consertar" evitou uma mudança teatral.
2. O ecossistema já praticava resiliência implicitamente (ciclos R*,
   commits escopados, background + wakeups); o R129 apenas a tornou
   explícita e sempre disponível num artefato único (`PROGRESS.md`) — o
   mesmo padrão "existe mas não estava exposto" dos R125/R127/R128.

## Score

**8.2/10**

- Entrega um artefato de retomada real e verificado, com diagnóstico
  honesto do que não é corrigível por código (limites de plano).
- É sobretudo processo/documentação; a manutenção do `PROGRESS.md` é
  manual (gerador automático a partir de git/cycles fica como candidato
  futuro, junto da dívida das contagens vivas).
- Não toca `settings.json` do Claude Code (nada a corrigir lá) nem as
  frentes paralelas.
