# R1068 — Execução da avaliação externa de skills

**Status:** Archify instalado externamente e verificado; demais candidatos
avaliados em diretório isolado. Nenhum pipeline de vídeo foi renderizado.
Nenhuma publicação ou validação externa.

## 1. Archify — instalado e verificado

- Instalação oficial: `npx -y skills@latest add https://archify.si --skill archify --agent opencode --global --copy --yes`.
- Destino: `~/.agents/skills/archify` (203 arquivos, cópia, não symlink).
- Versão: 3.2.0; licença Apache-2.0; `LICENSE`, `NOTICE` e
  `THIRD_PARTY_NOTICES.md` preservados.
- `doctor`: **27 checagens, todas `[ok]`** — Node 22.23.1, template, renderers,
  validadores, preview, visual-check, finalize, caminhos e safe area.
- Smoke test: exemplo de arquitetura renderizado em
  `/tmp/opencode/archify-smoke/web-app-smoke.html` (827 KB), `check` sem
  `issues`; SHA-256 `ffabd084c754ee97ed9e9355ba19fab449533432537d6b8cdb5c6d276293741a`.
- Nenhum arquivo do Archify foi copiado para o repositório do Core.

## 2. hbg-life-simulation — avaliado, bloqueado por dependências

- Clone isolado: `~/.cache/opencode-pilot/external-evals/hbg-life-simulation`.
- Commit: `288f780c2f5ccce975e11dd3c5ff6d6eda15afa6`; MIT; 564 KB.
- Verificações seguras:
  - 10 scripts `.mjs` passaram em `node --check`;
  - `scripts/init_project_style.mjs` criou `HBG_STYLE.json` landscape
    1920×1080/30 fps, legendas 48 px e margem inferior 58 px;
  - `scripts/setup_local_cliproxyapi.sh ready` retornou `not-configured`
    (somente leitura; nada foi instalado ou iniciado).
- Dependências presentes: Node 22.23.1, ffmpeg 8.0.1, ffprobe, HyperFrames
  0.9.15 no cache do npx, `edge_tts` no venv
  `~/.cache/opencode-pilot/venvs/edge-tts`.
- Bloqueios:
  - exige as skills `/imagegen`, `/hyperframes`, `/media-use` e
    `/code-video-visual-qa`, ausentes no Core;
  - não há Chrome/Chromium no host;
  - o proxy local de imagem está `not-configured`; instalá-lo exige OAuth e
    consentimento por projeto;
  - o pipeline é chinês e usa GSAP via CDN no build da composição.
- Nenhum render foi executado. A skill não está pronta para uso no Core hoje.

## 3. image-story-video-wizard — avaliado, pronto para instalação externa

- Clone isolado:
  `~/.cache/opencode-pilot/external-evals/image-story-video-wizard`.
- Commit: `6c6979fd95698f1c784acf89fe5fcc78ca8a56de`; MIT; 348 KB.
- Testes: `python3 -m unittest discover -s tests -v` — **9 passed**.
- Smoke test do CLI de estado:
  - `init` criou `PROJECT_STATE.json`;
  - `validate` retornou `VALID`;
  - `summary` mostrou `Stage: START`, próximo `BRIEF`.
- Natureza: máquina de estados de 16 fases; não executa imagem, TTS ou render
  sozinha. Depende de Codex/WorkBuddy, Doubao Seed-TTS, geração de imagem e
  HyperFrames nas etapas externas.
- Decisão: candidato a instalação externa; não foi instalado nesta rodada.

## 4. distilly — avaliado, gate de consentimento

- Clone isolado: `~/.cache/opencode-pilot/external-evals/distilly`.
- Commit: `0afc45c29c360ba7bc8260f1bb0bf34e9155f4fa`; MIT; 3,6 MB.
- Testes rápidos: `test_owner_profile`, `test_owner_sources` e
  `test_skill_entrypoint_docs` — **40 passed**.
- Coletores usam `requests`, Playwright, Slack/Feishu/DingTalk e credenciais
  próprias. Nenhum coletor foi executado; nenhum perfil foi criado.
- Decisão: **não integrar como está**. Qualquer uso exige consentimento
  verificável, minimização de dados, direito de exclusão e proibição de
  simular pessoa real sem autorização.

## 5. opus-video-skills — avaliado, externo

- Clone isolado: `~/.cache/opencode-pilot/external-evals/opus-video-skills`.
- Commit: `59744a69c7b916cfbe4c4ec84006b0c2f5e2fde1`; MIT; 17 MB.
- Duas skills: `painted-animation` (p5.js + p5.brush) e `kinetic-reel`
  (Canvas/three.js/WebGL).
- Requer Node, Google Chrome e ffmpeg. Chrome está ausente no host.
- Nenhum projeto ou render foi executado. Instalação externa possível, mas
  depende de Chrome.

## 6. reel-video — avaliado, externo

- Clone isolado: `~/.cache/opencode-pilot/external-evals/reel-video`.
- Commit: `39a5ea97e81994bbaa0a546fc85fd7668f012890`; MIT; 18 MB.
- CLI TypeScript + review board; usa `grok` e `codex` com `workspace-write`,
  além de S3/fetch.
- `grok` e `codex` não estão instalados no host.
- Nenhum comando do CLI foi executado. Decisão: ferramenta externa; não entra
  no Core sem uma decisão arquitetural e sem conta autorizada.

## 7. Decisão consolidada

| Item | Decisão |
|---|---|
| Archify | **Instalado externamente e pronto**; usar via skill `archify`. |
| image-story-video-wizard | **Pronto para instalação externa**; não instalado. |
| hbg-life-simulation | **Bloqueado** por skills ausentes, Chrome e proxy de imagem. |
| distilly | **Não integrar**; exige gate de consentimento/privacidade. |
| opus-video-skills | **Externo**; depende de Chrome. |
| reel-video | **Externo**; depende de Grok/Codex. |
| OpenDesign / Paperclip | Mantidos como apps externos; não decididos nesta rodada. |
| Fontes sem licença | Referência apenas; nenhuma cópia. |

## 8. Limites

- Nenhum vídeo foi renderizado, publicado ou validado externamente.
- Nenhuma conta, OAuth, cookie, token ou credencial foi lida.
- Nenhum perfil de pessoa foi criado.
- As avaliações usaram apenas checagens seguras: `doctor`, testes unitários,
  `node --check`, CLI de estado e leitura de arquivos.
- O Archify é a única instalação externa efetiva desta rodada.

## 9. Próximo passo

1. Se autorizado, instalar `image-story-video-wizard` em
   `~/.agents/skills/image-story-video-wizard` e validar o carregamento.
2. Para `hbg-life-simulation`, decidir se as skills `/hyperframes`,
   `/media-use`, `/code-video-visual-qa` e `/imagegen` serão instaladas e se o
   proxy local será configurado com consentimento.
3. Para `opus-video-skills`, instalar Chrome ou usar um host que já o tenha.
4. Para `reel-video`, decidir se o fluxo com Grok/Codex será adotado.
