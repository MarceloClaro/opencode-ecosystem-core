# SPEC-935-R1109 — Commit e push automáticos do Core

Data: 2026-11-12. Estado: implementado e testado localmente; push real
dependente de PAT fornecido pelo operador.

## Demanda

Toda alteração e produção feita pelo OpenCode Ecosystem Core deve ser
commitada e enviada ao repositório sem depender de uma chamada manual. O
checkout já continha o commit R1088–R1108, mas o push falhava por ausência de
credencial e não havia mecanismo de checkpoint automático.

## Escopo

1. `scripts/autocommit_push.sh`: cria checkpoint quando há mudanças, respeita
   `.gitignore`, recusa arquivo acima de 50 MB, usa `git add --sparse -A` e
   tenta push para o upstream.
2. `scripts/install_autocommit_hooks.sh`: instala `post-commit` que executa
   somente o push, sem criar commits recursivos.
3. `scripts/install_autocommit_timer.sh`: instala timer systemd `--user` de
   2 minutos para transformar mudanças não commitadas em checkpoints.
4. Credencial: o script lê `~/.config/opencode/github-pat` (ou
   `GITHUB_TOKEN` no ambiente) via `GIT_ASKPASS` temporário; o valor nunca é
   passado em argv nem gravado no log.
5. Log fora do repositório em `~/.local/state/opencode/autocommit-push.log`.
6. Testes herméticos com remote bare local; nenhuma rede.

## Fora do escopo

- Criar, rotacionar ou obter o PAT pelo Core. O segredo é do operador.
- Executar a suíte de testes antes de cada checkpoint automático.
- Commitar arquivos ignorados, binários grandes ou artefatos externos.
- Garantir que todo checkpoint seja uma entrega científica validada: o
  checkpoint automático é transporte, não gate de qualidade.

## Critérios de aceitação

- CA01: com mudanças e remote local, o script cria um commit e envia ao
  upstream.
- CA02: sem mudanças, nenhum commit é criado.
- CA03: arquivo acima de 50 MB bloqueia o commit e registra o motivo.
- CA04: o instalador cria `post-commit` executável e idempotente.
- CA05: o hook chama `--push-only` e não executa `git add`/`git commit`.
- CA06: o token não aparece em argv, no log ou no conteúdo versionado.
- CA07: o timer systemd é instalável e usa o script do repositório.
- CA08: os quatro testes R1109 passam sem rede.

## Evidência

- `pytest tests/test_r1109_autocommit_push.py -q` → **4 passed**.
- `bash -n scripts/autocommit_push.sh scripts/install_autocommit_hooks.sh
  scripts/install_autocommit_timer.sh` → OK.
- `doctor` → 16 pass, 6 warn, 0 fail.
- Push real: validado em 2026-11-12; commits `6bb51e9` e `26c450e` estão em
  `origin/main`. O token fica em `~/.config/opencode/github-pat` (600).

## Limites

O checkpoint automático não substitui SDD/TDD, revisão humana ou validação
externa. Ele apenas reduz o risco de trabalho local não versionado. Um PAT
vazado deve ser revogado e substituído; o arquivo tem permissão `600`.
