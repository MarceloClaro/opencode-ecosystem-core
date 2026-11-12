---
spec_id: SPEC-935-R1116
component: integrations.rea_video_cli
title: Adaptador somente leitura para o rea-video
version: 1.0.0
status: implemented
test_file: tests/test_rea_video_cli.py
---

# SPEC-935-R1116 — Adaptador somente leitura do `rea-video`

## Objetivo

Expor o `rea-video` ao Core como ferramenta externa de análise de vídeo, sem
instalar nada, sem chamar provedores pagos e sem executar `remake-run`.
O adaptador lê um vídeo local, escreve apenas em um diretório de saída
explicitamente autorizado e devolve artefatos com hash.

## Motivação

O `rea-video` faz forensics de vídeo shot a shot (live/AI/3D/code), produz
`VIDEO.md` em camadas e um `breakdown.json` com evidência. Ele complementa
`cp-extratora-de-referencia` e `video-editor-universal`, mas seu CLI tem
comandos pagos (`remake-run`) e baixa modelos opcionais. O Core precisa de uma
fronteira explícita: análise sim, geração paga não.

## Escopo

### Em escopo
- `integrations/rea_video_cli.py` com API Python e CLI.
- `status`: localiza o binário (`REA_VIDEO_BIN` ou PATH) e lê `--help`.
- `doctor`: confere binário, `ffmpeg`, `ffprobe` e escrita no diretório de saída.
- `decompose`: executa `rea-video decompose <video> -o <out>` com `--yes`;
  `--dry-run` mostra o argv sem executar.
- `summary`: lê `breakdown.json` e devolve contagens de shots, tipos e baixa
  confiança, sem executar nada.
- Inventário de artefatos com SHA-256 (`VIDEO.md`, `breakdown.json`,
  `report.html`, `report.md`, `storyboard.jpg`, `audio.png`) e contagem de
  `shots/` e `stems/`.
- Testes em `tests/test_rea_video_cli.py`.

### Fora de escopo
- Instalar `rea-video`, `ffmpeg`, modelos de VLM/OCR/ASR ou dependências.
- Executar `remake-run`, `remake-plan`, `capsule-draft`, `assemble` ou qualquer
  comando que chame provedor pago.
- Modificar o vídeo de entrada.
- Promover confiança ou declarar qualidade/autoria do vídeo.

## Requisitos

1. `status` e `summary` não escrevem no disco.
2. `decompose` sem `--yes` é bloqueado.
3. `decompose --dry-run` não cria o diretório de saída nem executa o binário.
4. Saída só é permitida dentro de raízes autorizadas (`out/` do cwd e
   `/tmp/opencode` por padrão; raízes explícitas em testes).
5. Vídeo de entrada deve existir e ter extensão de vídeo reconhecida.
6. Diretório de saída não vazio exige `--overwrite`.
7. Subprocesso usa lista de argumentos, `shell=False`, timeout e ambiente
   allowlist; segredos não são repassados.
8. `remake-run` é bloqueado com erro explícito.
9. Todo resultado inclui `verification.scope = local_observation`,
   `externally_validated = false` e `confidence_promoted = false`.

## Critérios de aceitação

- [ ] `status` encontra um CLI falso via `REA_VIDEO_BIN` e reporta `available`.
- [ ] `decompose --dry-run` não executa e não cria saída.
- [ ] `decompose` sem `--yes` levanta `ReaVideoBlocked`.
- [ ] `decompose` com `--yes` cria artefatos e calcula SHA-256.
- [ ] Saída fora das raízes é rejeitada.
- [ ] Diretório não vazio é rejeitado sem `--overwrite`.
- [ ] `summary` conta shots, tipos e baixa confiança.
- [ ] `remake-run` é bloqueado.
- [ ] Nenhum segredo do ambiente chega ao subprocesso.
- [ ] `tests/test_rea_video_cli.py` passa.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_rea_video_cli.py -q
```

Ciclo TDD: teste escrito antes do módulo; RED por `ModuleNotFoundError`;
implementação; GREEN.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Custo por `remake-run` | Comando não exposto; erro explícito |
| Download de modelos | `decompose` só usa o que já está instalado; `doctor` reporta ausência |
| Vazamento de chave | Ambiente allowlist; `--env-file` não é repassado por padrão |
| Escrita fora do destino | Resolução canônica + raízes autorizadas |
| Saída parcial | Inventário pós-execução + exit code + timeout |
| Confundir análise com validação | Bloco `verification` em todo resultado |

## Evidência

- Fonte: `rea-video`, commit `3974260fb52476b453b5992f667e7dc1dd83c6eb`,
  Apache-2.0.
- CLI: `rea-video decompose <video> -o <out> [--vlm] [--lang zh|en]`.
- Nenhum código do alvo foi executado durante a análise.
