# SPEC-935-R1068 — Avaliação e instalação externa de skills

**Status:** executado conforme autorização do operador; nenhuma publicação ou
validação externa.
**Objetivo:** avaliar skills de terceiros em diretório isolado e instalar
externamente apenas o que foi autorizado, preservando licença, consentimento e
limites de execução.

## 1. Escopo autorizado

- Instalar **Archify** externamente e rodar `doctor`.
- Avaliar **hbg-life-simulation** em diretório isolado.
- Avaliar **image-story-video-wizard** em diretório isolado.
- Avaliar **distilly** com gate de consentimento/privacidade.
- Avaliar **opus-video-skills** e **reel-video** sem executar os pipelines.
- Manter como referência apenas as fontes sem licença.

## 2. Critérios de aceitação

1. Licença verificada e preservada no diretório externo.
2. Nenhuma cópia de conteúdo sem licença para o repositório do Core.
3. Nenhuma credencial, OAuth, cookie ou token lido ou impresso.
4. Nenhum instalador de terceiro executado sem necessidade e sem confirmação.
5. Checagens seguras: `doctor`, testes unitários, `node --check`, CLI de estado.
6. Relatório com caminho, commit, evidência, bloqueios e decisão.

## 3. Resultados

| Item | Licença | Evidência | Decisão |
|---|---|---|---|
| Archify 3.2.0 | Apache-2.0 | `doctor` 27/27; smoke test de arquitetura com hash `ffabd084...` | Instalado externamente em `~/.agents/skills/archify`; pronto. |
| hbg-life-simulation | MIT | 10 scripts `.mjs` com sintaxe válida; `HBG_STYLE.json` landscape 1920×1080; `ready` retornou `not-configured` | Não executável no Core hoje: faltam `/imagegen`, `/hyperframes`, `/media-use`, `/code-video-visual-qa`, Chrome e proxy local. |
| image-story-video-wizard | MIT | 9 testes passaram; `PROJECT_STATE.json` init/validate/summary OK | Candidato a instalação externa; não instalado nesta rodada. |
| distilly | MIT | 40 testes rápidos passaram; coletores usam Playwright/requests/credenciais | Não integrar como está; exige consentimento e privacidade. |
| opus-video-skills | MIT | Duas skills (`painted-animation`, `kinetic-reel`); requer Chrome/ffmpeg | Externo; Chrome ausente. |
| reel-video | MIT | CLI TypeScript + review board; requer Grok/Codex | Externo; `grok` e `codex` ausentes. |

## 4. Limites

- A instalação do Archify é externa ao repositório; não há cópia no Core.
- Nenhum pipeline de vídeo foi renderizado nesta rodada.
- Nenhum perfil de pessoa foi criado pelo Distilly.
- Nenhuma conta, OAuth ou proxy local foi configurado.
- Estrelas e trending não foram usados como prova de qualidade.
- Nenhuma validação externa ou publicação.
