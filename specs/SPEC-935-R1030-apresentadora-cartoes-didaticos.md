---
spec_id: SPEC-935-R1030
title: Apresentadora nos cartões didáticos e linha do tempo vertical
component: pilots/r1026-quantum + .opencode/skills/video-didatico-tecnico
status: implemented
test_file: tests/test_r1030_presenter_cards.py
---

# SPEC-935-R1030 — Apresentadora nos cartões didáticos

## Objetivo

Levar a apresentadora para a abertura e o encerramento do vídeo didático,
mantendo a animação/roadmap visível, e unificar os cartões com o miolo. No
formato 9:16, substituir as linhas compactas por uma linha do tempo vertical
que ocupe a metade inferior e acompanhe a ordem da narração.

## Entregáveis

- `pilots/r1026-quantum/presenter-cutout.png` — recorte 560×800 com alfa.
- `pilots/r1026-quantum/make-presenter-cutout.py` — reprodução do recorte.
- `pilots/r1026-quantum/remotion-template/src/DidacticIntroOutro.tsx` — cartão
  de retrato, timeline vertical e linhas compactas.
- `pilot-16x9-didatico-voz.mp4` e `pilot-9x16-didatico-voz.mp4` — masters de
  44 s com os novos cartões.
- `tests/test_r1030_presenter_cards.py` — teste de regressão.
- Atualização de `README.md`, `DISCOVERIES.md` (#15 e #16) e `manifest.json`.

## Critérios

1. O cartão usa `presenter-cutout.png` com `objectFit: contain`, fundo escuro,
   glow roxo e zoom lento; não simula fala.
2. No 16:9, o retrato fica à direita e o roadmap à esquerda; no 9:16, o retrato
   fica no topo direito e a linha do tempo vertical abaixo.
3. O rótulo “APRESENTADORA / VOZ SINTÉTICA” permanece legível.
4. Os três passos da timeline acendem nos atrasos 45/135/345 (abertura) e
   0/75/150 (encerramento), com opacidade de repouso 0,26.
5. O recorte é reproduzível por script e o master mantém 44,0 s, H.264/AAC e
   loudness −16,29 LUFS.
6. O teste local passa; o pipeline de concatenação mantém `apad`, `atrim`,
   `setsar=1` e `concat=n=3:v=1:a=1`.

## Evidência

- RED inicial: 3 falhas (README, manifesto e skill) e 4 testes estruturais já
  verdes; os ativos e o código visual foram implementados antes da suíte.
- Frames: `final-16x9-8.png`, `final-9x16-8.png`, `final-16x9-40.png`,
  `final-9x16-40.png`; zoom do recorte em `cutout-head-zoom.png`.
- Hashes históricos do R1030 (substituídos pelo R1031, que adicionou vídeo falante):
  - 16:9 `915f4a18707fecb28cacea0f6e1502dcd2f329adcff2ffc0dc7e8cacd9d8acab`.
  - 9:16 `2cfbe9fefa5e3620a908a241174f19625364cdeb69c3326d27dc7f95fdd23669`.
  - Hashes atuais em `hashes-r1031.txt`.
- Recorte: `bc6e5c0ee2026a1321f82d3ef8c28c0289b28fad12e436f2028e1be2bf875197`.
- GREEN local: `8 passed` em `tests/test_r1030_presenter_cards.py`.

## Limites

- A matte é um recorte por limiar de luminosidade + morfologia, não um modelo de
  segmentação; pode haver franjas no cabelo/ombros.
- Não houve reprodução contínua com áudio, escuta humana ou revisão em tela
  grande; `visual_quality_verified` permanece **falso**.
- O consentimento de voz é declarado, não verificado; XTTS/CPML e Wav2Lip são
  não comerciais.
- A timeline é temporal; não prova sincronia labial nem compreensão do
  espectador.
- Nada foi publicado.
