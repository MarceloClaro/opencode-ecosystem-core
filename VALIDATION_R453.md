# Recibo local de validação — R453

## Escopo

Este recibo registra a execução local associada à
`SPEC-935-R453-precommit-security-closure.md`. Ele não é certificação externa,
auditoria independente, garantia de segurança absoluta nem execução E2E elevada
em Windows ou macOS.

## Evidência runtime SDD

Em 2026-08-24, `TDDRunner.run_spec_test()` executou a suíte vinculada a
`tests` e `SpecVerifier` avaliou uma entrega não nula com a evidência emitida
pelo runtime:

- spec: `SPEC-935-R453`;
- critérios: **9/9** aprovados;
- retorno pytest: `0`;
- resumo: **3.529 passed**, **70 skipped**, **1 warning** e **4 subtests
  passed** em **900,63 s**;
- resultado do gate: `verified: true`, `status: green`.

Em `SPEC-935-R454`, a sustentação granular dessa spec foi revalidada em modo
`criterion-runtime-v1`, com **20/20 nodeids** aprovados para os **9/9**
critérios declarados. O recibo dessa migração está em `VALIDATION_R454.md`.

Também foram executados localmente: o arquivo focal R453, a seleção CI de Ruff
`E4,E7,E9,F`, `pip check`, `git diff --cached --check`, sintaxe Bash dos quatro
scripts e parsing PowerShell sem perfil.

## Correção observada durante o gate

A primeira tentativa do executor SDD atingiu o timeout padrão anterior de 900
segundos, apesar da suíte não ter reportado falha. Os valores padrão de
`run_pytest()` e do relatório de qualidade da CI foram elevados para 1.200
segundos, cobertos por regressão R453, e o gate foi repetido integralmente até
terminar com evidência verde. Essa mudança
não transforma duração de teste em qualidade adicional; ela apenas evita uma
negação falsa da evidência runtime observada.

## Controles exercitados

- scanner de padrões de segredo de alta confiança nos blobs do índice Git;
- rejeição de URL com credenciais, consulta ou fragmento e de checkouts sujos;
- validação de metadados de artefatos antes de operações privilegiadas;
- `PATH` de sistema para cada instalação de CLI e interrupção no primeiro erro;
- atestação SHA-256 do staging WSL e verificação de bytes antes de WSL/DISM;
- Bash WSL não interativo em ambiente mínimo, sem perfis;
- Ollama iniciado somente a partir de binário baixado e verificado, sem
  `sudo` ou unidade `systemd` preexistente.

## Limites e riscos residuais

- operações shell por pathname continuam sujeitas a janela TOCTOU local;
- o hash NPM cobre o tarball principal, não cada dependência transitiva de cache;
  portanto, não constitui integridade transitiva;
- não foi executado fluxo E2E Windows/WSL elevado nem em hardware macOS;
- os manifests Python têm pins diretos, mas ainda não constituem lockfile
  transitivo universal com hashes; esse endurecimento é trabalho separado de
  proveniência de dependências.

Revise o diff, o manifesto de versão e o ambiente real antes de executar
instaladores ou usar os resultados como base operacional.
