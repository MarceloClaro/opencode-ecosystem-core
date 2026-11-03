#!/usr/bin/env bash
# Lip sync com Wav2Lip em GPU (não execute em CPU; o teste de 5 s não terminou).
# Uso: ./render-lipsync-gpu.sh [audio] [saida]
set -euo pipefail
cd "$(dirname "$0")"

BASE="${BASE:-/home/marceloclaro/.cache/opencode-pilot}"
AUDIO="${1:-dub-pt-BR-clone.wav}"
OUT="${2:-pilot-16x9-lipsync.mp4}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "ERRO: Wav2Lip em CPU não é viável neste host (teste de 5 s > 1h11 sem saída)." >&2
  echo "Execute este script em uma máquina com GPU NVIDIA e CUDA." >&2
  exit 2
fi

if [ ! -f "$BASE/Wav2Lip/inference.py" ]; then
  echo "ERRO: Wav2Lip não encontrado em $BASE/Wav2Lip" >&2
  exit 2
fi
if [ ! -f "$BASE/Wav2Lip/checkpoints/wav2lip_gan.pth" ]; then
  echo "ERRO: checkpoint wav2lip_gan.pth ausente" >&2
  exit 2
fi

python "$BASE/Wav2Lip/inference.py" \
  --checkpoint_path "$BASE/Wav2Lip/checkpoints/wav2lip_gan.pth" \
  --face source.mp4 \
  --audio "$AUDIO" \
  --outfile "$OUT" \
  --pads 0 10 0 0 \
  --resize_factor 1 \
  --wav2lip_batch_size 16

ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate \
  -of json "$OUT"
