# Piloto R1055 — O que é um qubit?

Explicador animado original, em português brasileiro, com narração neural,
mapa de origem e câmera cinematográfica. Não é um corte do vídeo de
referência e não usa voz clonada.

## Entregáveis

- `out/r1055-qubit-16x9.mp4` — master 1920×1080, 30 fps, 109,73 s.
- `out/r1055-qubit-9x16.mp4` — vertical nativo 1080×1920, 30 fps.
- `REFERENCES.md` — DOIs verificados, créditos, licenças e cautelas.
- `SCRIPT.md` — roteiro, tempos, princípios neuropsicopedagógicos e câmera.
- `../../reports/r1055/README.md` — QC, ASR, prosódia, hashes e limites.
- `../../docs/CINEMATIC_REMOTION_R1055.md` — módulo de câmera e pesquisa.

## Estrutura

```
pilots/r1055-qubit/
  generate_audio_edge.py      # TTS por batida + timeline + SRT
  generate_audio.py           # XTTS anterior (proveniência; não usado)
  build_remotion_timeline.py  # timeline.ts para o Remotion
  render_world_map.py         # Natural Earth 4096×1354
  audio/                      # narração, cenas, SRT, timeline, ASR
  audio-xtts/                 # áudio XTTS anterior (proveniência)
  assets/                     # foto do autor e mapa
  out/                        # vídeos, planos, recibos, QC, contatos
```

## Dependências

- `edge-tts` no venv do operador:
  `/home/marceloclaro/.cache/opencode-pilot/venvs/edge-tts`.
- Remotion 4.0.540 em `editor-workspace/remotion-smoke`.
- FFmpeg, Python 3.14, Pillow, matplotlib, NumPy.
- ASR opcional: `faster-whisper-large-v3` no venv `r1034-cpu`.

## Como reproduzir

```bash
# 1. Narração (cache de WAVs por batida; não re-sintetiza se existir)
/home/marceloclaro/.cache/opencode-pilot/venvs/edge-tts/bin/python \
  pilots/r1055-qubit/generate_audio_edge.py

# 2. Timeline do Remotion
python3 pilots/r1055-qubit/build_remotion_timeline.py

# 3. Mapa
python3 pilots/r1055-qubit/render_world_map.py

# 4. Render 16:9 e 9:16 (usar video_editor; ver report)
# 5. Mux, loudnorm e QC
ffmpeg -i out/qubit-visual-camera-16b.mp4 -i audio/narration.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -shortest out/r1055-qubit-16x9.mp4
python3 scripts/video_qa.py --video out/r1055-qubit-16x9.mp4 \
  --out out/qa-camera-16.json --expect-frames 3292 --expect-fps 30/1 \
  --loudness-target -14 --loudness-tolerance 1.0 --max-true-peak -1.5
```

## Limites

- QC técnico não é aprovação estética ou científica.
- O mapa é ilustrativo; ver as cautelas em `REFERENCES.md`.
- A voz é sintética; revisão humana é necessária antes de publicar.
- Nada é publicado automaticamente.
