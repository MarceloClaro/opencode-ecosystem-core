# SPEC-935-R1151 — CI local, worktree limpo e validação externa

**Status:** implementação local; sem hardware
**Data:** 2026-11-11
**Depende de:** R1148, R1149, R1150

## 1. Objetivo

Mitigar três gaps operacionais:

1. CI de workflow pendente por escopo `workflow`;
2. worktree com 184 deleções históricas e 23 itens não rastreados;
3. ausência de pacote/verificação externa.

## 2. Requisitos

- **R1.** Criar `scripts/local_ci.sh` com testes R1148/R1150, regressão
  metacognitiva, `opencode_cli --check`, auditoria de catálogo e
  `git diff --check`; `--lean` compila os três arquivos Lean.
- **R2.** Remover do HEAD os artefatos históricos já deletados (`.backups/`,
  `pilots/`) e guardar os não rastreados em stash, sem perda.
- **R3.** Ignorar clones/artefatos locais (`mindquantum-master/`,
  `educacao_quantica/`, `videos/`, `reports/r1096-98/`).
- **R4.** Criar `validation/external_r1151/` com claims, comandos de
  reprodução, pedido de revisão e manifesto de hashes.
- **R5.** `verify_claims.py` confere certificados, hashes, relatório de
  catálogo e testes; separa `supported`, `insufficient` e `overclaim`.
- **R6.** Registrar explicitamente que a verificação não é peer review,
  validação clínica ou de hardware.

## 3. Critérios de aceitação

- `bash scripts/local_ci.sh` passa com 59 testes R1148/R1150 + 16
  metacognitivos, config e auditoria;
- `bash scripts/local_ci.sh --lean` compila `ComplexProofs`,
  `CorrelationCounterproof` e `MathlibCounterproof`;
- `git status` limpo após o commit (stash preserva os não rastreados);
- `verify_claims.py` retorna `reproducible=true`, `overclaims=[]`;
- `classification_pilot` e `clinical_claims` permanecem `insufficient`;
- nenhum hardware, participante ou peer review é declarado.

## 4. Limites

O patch de workflow continua pendente: o token OAuth não tem escopo `workflow`.
O gate local não é check remoto. A validação externa é automatizada, não humana;
peer review, ética e hardware permanecem abertos. O stash preserva os arquivos
não rastreados, mas não os versiona.
