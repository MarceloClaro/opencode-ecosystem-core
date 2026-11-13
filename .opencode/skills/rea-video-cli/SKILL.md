---
name: rea-video-cli
description: Adaptador somente leitura do rea-video para o Core OpenCode (SPEC-935-R1116)
metadata:
  version: "1.0.0"
  spec_id: "SPEC-935-R1116"
  status: "implemented"
  test_file: "tests/test_rea_video_cli.py"
---

# rea-video-cli — Adaptador somente leitura do rea-video

## Objetivo
Expor o `rea-video` ao Core como ferramenta externa de análise de vídeo, sem
instalar nada, sem chamar provedores pagos e sem executar `remake-run`.

O adaptador lê um vídeo local, escreve apenas em um diretório de saída
explicitamente autorizado e devolve artefatos com hash.

## Escopo
### Em escopo
- `integrations.rea_video_cli` com API Python e CLI.
- `status`: localiza o binário (`REA_VIDEO_BIN` ou PATH) e lê `--help`.
- `doctor`: confere binário, `ffmpeg`, `ffprobe` e escrita no diretório de saída.
- `decompose`: executa `rea-video decompose <video> -o <out>` com `--yes`;
  `--dry-run` mostra o argv sem executar.
- `summary`: lê `breakdown.json` e devolve contagens de shots, tipos e baixa
  confiança, sem executar nada.
- Inventário de artefatos com SHA-256 (`VIDEO.md`, `breakdown.json`,
  `report.html`, `report.md`, `storyboard.jpg`, `audio.png`) e contagem de
  `shots/` e `stems/`.

### Fora de escopo
- Instalar `rea-video`, `ffmpeg`, modelos de VLM/OCR/ASR ou dependências.
- Executar `remake-run`, `remake-plan`, `capsule-draft`, `assemble` ou qualquer
  comando que chame provedor pago.
- Modificar o vídeo de entrada.
- Promover confiança ou declarar qualidade/autoria do vídeo.

## Integração com Core
Este skill integra o adaptador `integrations.rea_video_cli` como componente
nativo do Core, seguindo o protocolo SDD/TDD e o gate de segurança do orquestrador.

Os principais comportamentos são:
- `status` e `summary` não escrevem no disco.
- `decompose` sem `--yes` é bloqueado.
- `decompose --dry-run` não cria o diretório de saída nem executa o binário.
- Saída só é permitida dentro de raízes autorizadas (`out/` do cwd e
  `/tmp/opencode` por padrão).
- Subprocesso usa lista de argumentos, `shell=False`, timeout e ambiente
  allowlist; segredos não são repassados.
- `remake-run` é bloqueado com erro explícito.
- Todo resultado inclui `verification.scope = local_observation`,
  `externally_validated = false` e `confidence_promoted = false`.

## Testes
- `tests/test_rea_video_cli.py`: 15 testes passando (RED→GREEN).
- Todos os testes seguem o ciclo TDD: teste escrito antes do módulo;
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
