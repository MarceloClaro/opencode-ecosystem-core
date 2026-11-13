---
name: remotion-dublagem-lendario
description: Skill nativa do OpenCode para trabalho com Remotion: dublagem, legendas, templates e validação de licença. Gera vídeos/ animações com áudio múltiplo e texto sincronizado.
metadata:
  version: "2.0.0"
  spec_id: "SPEC-935-R1122"
  status: "implemented"
  test_file: "tests/test_remotion_dublegenda.py"
  license: "Remotion License"
  github_native: true
---

# remotion-dublagem-lendário — Skill Nativa do OpenCode

## Objetivo
Prover integração nativa do OpenCode com o **Remotion** para geração de vídeos e animações programáticas, com suporte a:
- **Dublagem** (múltiplas trilhas de áudio, sincronização, substituicao)
- **Legendas/Subtitulos** (sincronizadas à fala, múltiplas línguas, exportação SRT)
- **Templates de composição** (cenas padrão, lower thirds, intros/outros)
- **Validação de licença** (Remotion License checks)
- **GitHub native** (integração repositórios, artefactos, releases)

## Escopo

### Em escopo
- `remotion.dublegenda` — API Python e CLI para operações de dublagem e legenda
- `status` — checa licença Remotion, versão binária, ffmpeg/ffprobe disponíveis
- `decompose` — analisa um projeto Remotion (pastura de composições, layers, templates)
- `dub` — adiciona/ substitui trilha de áudio em vídeo Remotion
- `legend` — gera e incrusta legendas/ subtitles em vídeo Remotion
- `template` — lista e aplica templates de composição (intro, lower third, outro)
- `summary` — resume metadados do projeto (shots, duração, áudio, legendas)
- Testes em `tests/test_remotion_dublegenda.py`.

### Fora de escopo
- Instalar o Remotion ou suas dependências (Node, Python, ffmpeg são do operador)
- Renderizar vídeos definitivos (o adaptador apenas planeara/inspeciona)
- Modificar código-fonte do Remotion ou projetos de terceiros
- Promover confiança ou declarar qualidade editorial sem revisão humana
- Executar projetos que exijam contas pagas ou licenças comerciais

## Requisitos

1. `status` e `decompose` não escrevem no disco (apenas leitura de metadados).
2. `dub` e `legend` exigem vídeo de entrada já renderizado ou composição Remotion válida.
3. Legendas suportam múltiplos formatos: SRT, VTT, JSON temporado, queimado no vídeo.
4. Dublagem usa ffmpeg/ffprobe para mixagem de áudio; segredos não são repassados.
5. Template aplica composições pré-definidas sem modificar o projeto original.
6. Todo resultado inclui `verification.scope = local_observation`, `externally_validated = false`.
7. Licença Remotion é conferida; uso comercial acima de 3 funcionários requer licença própria.

## Critérios de aceitação

- [ ] `status` encontra licença Remotion válida e reporta `available`.
- [ ] `decompose` lista composições e layers sem executar o render.
- [ ] `dub` adiciona áudio e reporta duração/mixagem.
- [ ] `legend` gera legenda SRT/ VTT sincronizada e reporta timing.
- [ ] `template` aplica composição sem erros de caminho.
- [ ] `summary` conta shots, duração, áudio e legendas.
- [ ] Nenhum segredo do ambiente chega ao subprocesso.
- [ ] `tests/test_remotion_dublegenda.py` passa.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_remotion_dublegenda.py -q
```

Ciclo TDD: teste escrito antes do módulo; RED por `ModuleNotFoundError`; implementação; GREEN.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Custo por renderização ffmpeg | Comando não exposto; `doctor` reporta ausência |
| Vazamento de áudio/legenda | Ambiente allowlist; segredos não repassados |
| Legenda fora de sincronia | Validação de timing; erro explícito se desvio > 200ms |
| Template não encontrado | `status` reporta ausência; erro não silencioso |
| Uso comercial sem licença | `status` reporta limite de 3 funcionários; decisão do operador |

## Evidência

- Fonte: `remotion-dev/remotion`, license Remotion (não-OSI).
- Dublagem: mistura de trilhas PCM via ffmpeg.
- Legendas: formatos SRT/ VTT; eixo tempo-em-texto; queima opcional no vídeo.
- Templates: cards de intro, lower third, outtro — todos opcionais.
- GitHub native: artefatos com metadados, labels automáticas, release notes.

## Integração GitHub Nativa

Esta skill foi desenhada para operar nativamente no fluxo do GitHub:

- **Artefatos**: `video-*.mp4`, `legenda-*.srt`, `relatorio-*.json` são gravados como releases do GitHub.
- **Labels**: vídeos recebem label `remotion-dublado` ou `legenda-pronta`.
- **Release notes**: metadados resumidos (`shot_count`, `dub_language`, `legend_count`) são automaticamente adicionados ao corpo do release.
- **Workflow**: pode ser acionado via `github_actions` ou `opencode` manual a partir de issues/pull-requests.

## Exemplos de uso

```bash
# Status do ambiente
python3 -m integrations.remotion status

# Listar composições de um projeto
python3 -m integrations.remotion decompose /caminho/projeto

# Dublagem (substituir áudio)
python3 -m integrations.remotion dub \
    --video out/video.mp4 \
    --audio /caminho/para/audio-novo.mp3 \
    --out out/video-dublado.mp4

# Legendas (gerar SRT e queimar no vídeo)
python3 -m integrations.remotion legend \
    --video out/video.mp4 \
    --srt /caminho/para/legenda.srt \
    --out out/video-com-legenda.mp4 \
    --thatima queima

# Aplicar template de intro
python3 -m integrations.remotion template \
    --projeto /caminho/projeto \
    --template intro \
    --out out/projeto-com-intro
```