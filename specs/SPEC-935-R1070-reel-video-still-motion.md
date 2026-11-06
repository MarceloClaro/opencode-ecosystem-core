# SPEC-935-R1070 — Fallback `still-motion` no reel-video

**Status:** implementado no clone externo MIT, com typecheck e testes verdes.
**Objetivo:** permitir vídeo de 6/10 s sem Grok, usando motion determinístico
por ffmpeg sobre os stills aprovados.

## 1. Origem

- Repositório: `AsadMoulviDev/reel-video`, MIT.
- Clone estável: `~/.local/share/opencode-core/reel-video`.
- Commit base: `39a5ea97e81994bbaa0a546fc85fd7668f012890`.
- O clone em `~/.cache/opencode-pilot/external-evals/reel-video` é um symlink
  para o caminho estável.

## 2. Mudanças

| Arquivo | Mudança |
|---|---|
| `src/types.ts` | `VideoProvider = "grok" \| "still-motion"`; `VideoShot.provider?`. |
| `src/project.ts` | `AddVideoOptions.provider`; `AddSceneOptions.videoProvider`; persistência do provider. |
| `src/runner.ts` | Seleciona `renderStillMotion` ou `animateImage`; mantém Grok opcional. |
| `src/still-motion.ts` | Render ffmpeg: 1 still com zoompan; 2–3 stills com crossfade. |
| `src/cli.ts` | `--video-provider grok\|still-motion` e `CANVAS_VIDEO_PROVIDER`. |
| `test/still-motion.test.ts` | Testes de provider padrão, still-motion e plumbing de `addScene`. |

## 3. Comportamento

- `canvas scene add ... --video-provider still-motion`
- `canvas add video ... --provider still-motion`
- `CANVAS_VIDEO_PROVIDER=still-motion` como padrão do processo.
- 1 still: zoompan lento, 6/10 s.
- 2–3 stills: crossfade na ordem first → middle → last.
- Saída: H.264, `yuv420p`, 30 fps, sem áudio, `+faststart`.
- Dimensões: 9:16 1080×1920; 1:1 1080×1080; 16:9 1920×1080;
  4:3 1440×1080; 3:4 1080×1440.

## 4. Aceitação

1. `npm run typecheck` passa.
2. `npm test` passa com 22 testes.
3. 3 stills → MP4 6,000 s, 1920×1080, H.264.
4. 1 still → MP4 6,000 s, 1080×1920, H.264.
5. `runProject` adota `assets/vid-1.mp4`, status `ready`, `costUsd=0`.
6. Grok permanece opcional; nenhum login/API é necessário para still-motion.

**Evidência:** os quatro renders e o runner foram executados; ver
`reports/r1070/README.md` para hashes e comandos.

## 5. Limites

- Não é vídeo generativo; é motion graphics determinístico.
- Não cria stills; o pipeline ainda precisa de Codex, Grok ou `imagegen`.
- Não adiciona áudio, legendas, TTS ou sincronização.
- A ordem dos refs é first → middle → last; refs além de três são ignoradas.
- Nenhuma validação externa ou publicação.
