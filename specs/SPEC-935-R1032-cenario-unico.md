---
spec_id: SPEC-935-R1032
title: Cenário único — miolo novo sem concatenar o vídeo antigo
component: pilots/r1026-quantum
status: implemented
test_file: tests/test_r1032_single_scenario.py
---

# SPEC-935-R1032 — Cenário único

## Objetivo

Eliminar a mistura do cenário novo (cartões escuros com a apresentadora) com o
miolo antigo (slide branco + vídeo antigo). O master deve ser contínuo do início
ao fim, com um miolo novo em tema escuro e a apresentadora no mesmo tratamento
dos cartões.

## Entregáveis

- `remotion-template/src/DarkSlideSequence.tsx` — slide de 20 s em tema escuro.
- `remotion-template/src/DidacticMiddle.tsx` — miolo 16:9 e 9:16 com slide
  escuro + cartão da apresentadora.
- `slide-sequence-dark.mp4` (20 s, 934×864).
- `presenter-middle-card.mp4` (20 s, 560×700).
- `didactic-middle-16.mp4` / `didactic-middle-9.mp4` (20 s).
- `concat-didatico.sh` usando apenas o miolo novo.
- `render-presenter-card-whole.sh` — Wav2Lip em passada contínua.
- `tests/test_r1032_single_scenario.py`.

## Critérios

1. `concat-didatico.sh` referencia `didactic-middle-16/9.mp4` e não referencia
   `pilot-*-didatico-base.mp4`.
2. O miolo novo tem 20 s, áudio AAC e as dimensões 1920×1080 / 1080×1920.
3. O slide escuro tem 20 s, 934×864 e não tem áudio; o cartão da apresentadora
   tem 20 s, 560×700 e não tem áudio.
4. A composição do miolo usa `slide-sequence-dark.mp4`,
   `presenter-middle-card.mp4` e `middle-clone.wav`.
5. O master final tem 44,1 s, H.264/AAC, 1320 frames, e os hashes batem com
   `hashes-r1031.txt`.
6. O lip sync é feito em passada contínua; a versão em blocos fica como fallback.

## Evidência

- Masters:
  - 16:9 `50caf1e8001a8ca0b4be16ed6e5b70dc24eb759cdd98cdb43ccc07c7361f4682`.
  - 9:16 `9b3969dde280f9e795a9dab4dab2dee074c2d0754147443708d1145e7bae3739`.
- Miolo novo: `d17c2a7b3e478ab2fd35a0dd7d090b80643f12980db3d4707bc7cea4d4793b0f`
  (16:9) e `9e0723864de963a068992ceaf51484c36e22c844acd96ad66998fea969b2d8a1`
  (9:16).
- Frames `r1032-16x9-20/30.png` e `r1032-9x16-20/30.png` mostram o miolo
  escuro; não há corte para o slide branco.
- Cartão do miolo em passada contínua: `e27067a6c0b8b5800b67c131c82138d64ce8e98ae7273ef8f5c20c07df180ac9`.
- RED inicial: falhas de concatenação/documentação; GREEN local: `5 passed`.

## Limites

- O cartão do miolo reutiliza o lip sync já existente do áudio de 20 s; não
  houve nova escuta humana.
- O slide escuro é uma re-renderização do conteúdo didático, não uma auditoria
  editorial nova.
- A passada contínua removeu os congelamentos de 5 s/10 s observados nos
  blocos, mas pode haver pausas naturais da fala.
- Nada foi publicado.
