# Piloto R1058 — Plano de ação Airam Veras

Vídeo didático do plano de ação pedagógica SPAECE de novembro de 2026 da
Escola de Cidadania Airam Veras (Crateús/CE), 5º ano A e B, Língua Portuguesa
e Matemática. Original, com logo da escola, mapa animado e narração sintética
PT-BR sem clonagem.

## Entregável

Vídeo institucional de 7min38s, com 19 cenas, 11 habilidades exemplificadas e rotina semanal fixa.

- `out/airam-plano-acao.mp4` — 1440×810, 30 fps, 13.749 frames, 458,30 s.
- `audio/narration.wav` — narração 48 kHz mono.
- `assets/` — logo, mapas e metadados de marcadores.
- `SCRIPT.md` — roteiro, tempos, exemplos e porquês.
- `REFERENCES.md` — fontes, créditos, mapa, licenças e limites.
- `../../reports/r1058/README.md` — QC, hashes e checklist.

## Estrutura

```
pilots/r1058-airam-veras/
  generate_audio.py       # Edge TTS por batida + timeline + SRT
  assets/                 # logo, mapas, map-meta.json
  audio/                  # narration.wav, timeline.json, subtitles.srt
  out/                    # vídeo, plano, recibo e QC
```

## Reproduzir

```bash
# 1. Narração (cache de WAVs por batida; requer edge-tts)
/home/marceloclaro/.cache/opencode-pilot/venvs/edge-tts/bin/python \
  pilots/r1058-airam-veras/generate_audio.py

# 2. Timeline do Remotion (script de build incluído no piloto/reports)
# 3. Stills de controle
cd editor-workspace/remotion-smoke
node node_modules/@remotion/cli/remotion-cli.js still \
  src/r1058-airam/EntryAiram.tsx AiramVerasVideo /tmp/still.png --frame=480

# 4. Render + mux + QC: ver reports/r1058/README.md
```

## Dependências

- Edge TTS no venv do operador.
- Remotion 4.0.540 em `editor-workspace/remotion-smoke`.
- FFmpeg, Python 3, Pillow, matplotlib.
- Tiles OSM e malhas IBGE já convertidos em assets; o vídeo não usa rede.

## Limites

- Linha de base de 11/08/2026; não é resultado de novembro.
- Metas propostas; não são garantia.
- H01–H20 são marcadores CAEd; não são descritores oficiais.
- Sem nomes, notas individuais ou ranking de estudantes.
- Nada foi publicado automaticamente.
