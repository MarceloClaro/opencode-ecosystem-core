# SPEC-935-R1216 — Wakaru standalone executável sob limites REA

## Status

`concluído` — criado antes da implementação, conforme SDD/TDD do Core; validado com smoke REA e GREEN de R1215+R1216 (`14 passed`).

## Contexto

A SPEC-935-R1215 instalou Wakaru `1.14.0` pelo npm em diretório isolado e validou o banner `wakaru 1.14.0`. O smoke test de `recover_javascript_sources` da REA 6.8.0 falhou antes da execução da recuperação:

```text
capability_unavailable / unsupported_provider
Wakaru --version failed; reported version: ; exit: null.
Fatal process out of memory: Failed to reserve virtual memory for CodeRange
```

A causa é o limite fixo de REA para recover (`--as=1073741824`, `--fsize=67108864`, `--cpu=120`, `--core=0`) aplicado ao wrapper que usa Node `v24.22.3`; o V8 reserva mais espaço virtual do que o teto permite. Não há patch autorizado da REA nem do bridge.

## Decisão

Usar o binário standalone oficial `wakaru-linux-x64.tar.gz` da release `v1.14.0`, que satisfaz o requisito REA (`^1.13.0`, verificado com `1.14.0`) e não depende do Node V8 local.

## Critérios de aceitação

1. O asset oficial deve ser obtido somente de `https://github.com/pionxzh/wakaru/releases/download/v1.14.0/wakaru-linux-x64.tar.gz`.
2. O SHA-256 do asset deve ser exatamente `db0e620034723195ab426e94d00d55dbd8fd0106a928ada2563f1103196d09fa`, conforme metadado da release GitHub.
3. O binário standalone deve ficar em `/home/marceloclaro/opencode-ecosystem-core/.opencode/rea/wakaru/standalone-v1.14.0/`.
4. O arquivo executável deve ser ELF e responder a `--version` com `wakaru 1.14.0`.
5. O comando precisa executar com sucesso sob o mesmo limite de REA:
   `/usr/bin/prlimit --as=1073741824:1073741824 --fsize=67108864:67108864 --cpu=120:120 --core=0:0 -- <comando> --version`.
6. O wrapper usado por `REA_WAKARU_COMMAND` deve passar a apontar para o binário standalone; o wrapper anterior baseado em Node deve ser preservado como `.bak` para rollback.
7. O manifesto `install-manifest.json` deve registrar `standalone` com asset, SHA, caminho e `execution_under_rea_prlimit_verified: true`, sem apagar os dados da instalação npm da R1215.
8. Um smoke test de `rea recover-javascript-sources` deve ser executado em arquivo JS pequeno, com diretório de saída isolado, e registrado como evidência.
9. Nenhuma alteração em `~/.codex/config.toml`, nenhuma persistência de `REA_WAKARU_COMMAND`/`NODE_OPTIONS`, nenhum patch em REA/bridge, nenhuma execução de alvo e nenhuma leitura de credenciais.
10. Os testes da R1215 e da R1216 devem passar.

## Fora de escopo

- Instalação global.
- Alteração de auth, permissões, MCPs ou configuração do ChatGPT/Codex.
- Execução de código extraído de `app.asar`.
- Alegação de que a recuperação de todos os módulos do Codex Desktop funcionará; apenas o smoke test limitado será verificado.

## Evidências exigidas

- Spec e testes com RED/GREEN.
- SHA-256 do asset e do executável.
- Hash da config do Codex antes/depois.
- Saída resumida do smoke test REA com `code`/`status` e contagem de arquivos recuperados.
- Atualização do manifesto.
