# Commit e push automáticos — R1109

O Core mantém três camadas de automação, todas locais e auditáveis:

> **Status 2026-11-12:** push real validado; `origin/main` em `26c450e`.

| Camada | Arquivo | Efeito |
|---|---|---|
| Checkpoint | `scripts/autocommit_push.sh` | `git add --sparse -A`, commit e push quando há mudanças |
| Hook | `scripts/install_autocommit_hooks.sh` | todo commit local tenta push imediato |
| Timer | `scripts/install_autocommit_timer.sh` | checkpoint a cada 2 minutos via systemd `--user` |

## Instalação

```bash
chmod 700 scripts/autocommit_push.sh scripts/install_autocommit_*.sh
./scripts/install_autocommit_hooks.sh
./scripts/install_autocommit_timer.sh
```

## Credencial

O PAT não é criado nem lido do chat pelo Core. Preencha uma vez:

```bash
install -m 600 /dev/null ~/.config/opencode/github-pat
read -rsp "PAT GitHub (Contents: read/write): " PAT
printf '%s' "$PAT" > ~/.config/opencode/github-pat
unset PAT
```

Alternativa por ambiente:

```bash
export GITHUB_TOKEN='...'
```

O script usa `GIT_ASKPASS` temporário; o token não entra em `argv` nem no log.

## Operação

```bash
./scripts/autocommit_push.sh              # commit + push agora
./scripts/autocommit_push.sh --push-only  # somente push (hook)
tail -f ~/.local/state/opencode/autocommit-push.log
systemctl --user list-timers opencode-autocommit.timer
```

## Limites

- O checkpoint automático é transporte, não gate SDD/TDD.
- Arquivos acima de 50 MB são recusados.
- `.gitignore` é respeitado; o script nunca usa `git add -f`.
- Sem PAT (ou `GITHUB_TOKEN`), o commit é mantido local e o log registra
  `push pendente`. O timer repete a tentativa.
- Remote local ou `file://` dispensa token e é usado nos testes herméticos.
