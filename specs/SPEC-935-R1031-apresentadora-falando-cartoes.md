---
spec_id: SPEC-935-R1031
title: Apresentadora falando nos cartões com lip sync
component: pilots/r1026-quantum
status: implemented
test_file: tests/test_r1031_talking_presenter_cards.py
---

# SPEC-935-R1031 — Apresentadora falando nos cartões

## Objetivo

Substituir o retrato estático da abertura/encerramento por vídeo da
apresentadora com **boca sincronizada** às narrações clonadas, mantendo o
roadmap animado visível e a unidade visual com o miolo.

## Entregáveis

- `render-presenter-card-lipsync.sh` — Wav2Lip CPU em blocos, watchdog,
  retomada e composição 1080p.
- `compose-presenter-card.py` — recorte 560×700, matte suave por frame,
  composição no gradiente do cartão e fade inferior.
- `presenter-intro-1080.mp4` / `presenter-outro-1080.mp4`.
- `presenter-intro-card.mp4` / `presenter-outro-card.mp4` (560×700, 30 fps).
- `card-bg-560x700.png`.
- `remotion-template/src/DidacticIntroOutro.tsx` com `<Video muted>` e
  `<Audio>` separado.
- `tests/test_r1031_talking_presenter_cards.py`.

## Critérios

1. O vídeo do cartão tem a boca sincronizada à narração e é mudo; o áudio
   permanece em `<Audio>`.
2. O recorte é em cabeça e ombros (560×700), sem as mãos/frestas que geravam
   manchas brancas.
3. A matte é suave (`V*(1-S)`), com fade inferior de 20 px; sem caixa branca.
4. O cartão mantém o roadmap animado e a timeline vertical no 9:16.
5. Os masters continuam com 44,0 s, H.264/AAC, 1920×1080 e 1080×1920.
6. O teste local passa; o pipeline é retomável e documentado.

## Evidência

- `presenter-intro-1080.mp4` (14,2 s) e `presenter-outro-1080.mp4` (9,8 s).
- `presenter-intro-card.mp4` (426 frames) e `presenter-outro-card.mp4`
  (294 frames), 560×700.
- Frames: `intro-card4-7.png`, `lipsync-intro16-7.png`,
  `lipsync-intro9-7.png`; o teste verifica metadados e a presença de `<Video>`.
- O Wav2Lip roda em CPU, 640×360, blocos de 5 s, watchdog de 4,5 GB.
- RED inicial: 4 falhas (ativos do encerramento, TSX, hashes e documentação);
  GREEN local: `6 passed`.
> O R1032 regenerou os cartões e o miolo; os hashes atuais estão em
> `hashes-r1031.txt`. Os valores abaixo são históricos do R1031.

- Masters históricos de 44,0 s e loudness −16,29 LUFS:
  - 16:9 `e9c17d5f91f9d6ffeb9de8c45b3350f70da40cfd85403022642e84d76c248afc`.
  - 9:16 `d3e3d0d843241a1b39a6de97d071acb874cc7387465cfdfd0524e2fc88b3f462`.
- Cartões históricos: intro `8ab10089dc5ecf6a26d18a8792fb3f8d00c0a6a37889b6b0d99c71fedc688e6e`;
  outro `962989f2674a656faeb7adc140714424007164358fb3eae467f1731d449b9a0a`.
- A passada contínua (`render-presenter-card-whole.sh`) substituiu os blocos
  de 5 s; ver R1032.

## Limites

- A qualidade do lip sync em CPU não foi avaliada por escuta humana nem por
  reprodução contínua; frames com boca aberta não provam sincronia.
- A matte é heurística; franjas de cabelo/ombros e gestos rápidos podem exigir
  revisão. O enquadramento fechado reduz as manchas da base.
- O consentimento de voz é declarado, não verificado; XTTS/CPML e Wav2Lip são
  não comerciais; Remotion usa a Remotion License.
- Nada foi publicado.
