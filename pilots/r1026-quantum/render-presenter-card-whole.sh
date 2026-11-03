#!/usr/bin/env bash
# R1031 — lip sync contínuo da apresentadora para os cartões.
#
# Uso: ./render-presenter-card-whole.sh <audio.wav> <duracao> <rotulo> [saida]
# Ex.: ./render-presenter-card-whole.sh intro-narracao.wav 14.187 intro
#
# Uma única passada do Wav2Lip (sem blocos de 5 s) evita os congelamentos nas
# emendas. O compose-presenter-card.py faz o recorte e a matte por frame.
set -euo pipefail
cd "$(dirname "$0")"

PILOT="$(pwd)"
BASE="${BASE:-/home/marceloclaro/.cache/opencode-pilot}"
WAV2LIP="$BASE/Wav2Lip"
PY="$BASE/venvs/wav2lip/bin/python"
AUDIO="${1:?audio ausente}"
DURATION="${2:?duração ausente}"
LABEL="${3:?rótulo ausente}"
OUT="${4:-$PILOT/presenter-$LABEL-1080.mp4}"
WORK="${WORK:-$BASE/lipsync-cards/$LABEL-whole}"
SRC="$PILOT/source.mp4"

MAX_RSS_MB=4500

[ -s "$AUDIO" ] || { echo "ERRO: áudio ausente: $AUDIO" >&2; exit 2; }
[ -s "$SRC" ] || { echo "ERRO: fonte ausente: $SRC" >&2; exit 2; }
[ -s "$WAV2LIP/inference.py" ] || { echo "ERRO: Wav2Lip ausente" >&2; exit 2; }
[ -x "$PY" ] || { echo "ERRO: venv do Wav2Lip ausente" >&2; exit 2; }

mkdir -p "$WORK" "$PILOT/temp"
exec 9>"$WORK/lock"
if ! flock -n 9; then
  echo "ERRO: outra execução de lip sync está ativa para $LABEL." >&2
  exit 3
fi

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMBA_NUM_THREADS=2

log() { echo "[$(date -Is)] $*" | tee -a "$WORK/run.log"; }

# 1. fonte 640x360, duração alvo, sem áudio.
if [ ! -s "$WORK/source-360-whole.mp4" ]; then
  ffmpeg -y -v error -i "$SRC" -t "$DURATION" \
    -vf "scale=640:360:flags=lanczos" -r 30 \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -an "$WORK/source-360-whole.mp4"
fi

# 2. Wav2Lip em uma passada contínua, com watchdog de memória.
log "início: label=$LABEL duration=$DURATION whole"
nice -n 19 ionice -c3 "$PY" "$WAV2LIP/inference.py" \
  --checkpoint_path "$WAV2LIP/checkpoints/wav2lip_gan.pth" \
  --face "$WORK/source-360-whole.mp4" \
  --audio "$AUDIO" \
  --outfile "$WORK/lipsync-360-whole.mp4" \
  --pads 0 10 0 0 --resize_factor 1 --wav2lip_batch_size 4 \
  >> "$WORK/run.log" 2>&1 &
pid=$!
started=$(date +%s)
while kill -0 "$pid" 2>/dev/null; do
  rss=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
  rss=${rss:-0}
  if [ "$rss" -gt $((MAX_RSS_MB * 1024)) ]; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    log "ABORTADO: RSS ${rss}KB acima de ${MAX_RSS_MB}MB"
    exit 4
  fi
  sleep 5
done
if ! wait "$pid"; then
  log "Wav2Lip FALHOU; veja $WORK/run.log"
  tail -20 "$WORK/run.log" >&2 || true
  exit 5
fi
[ -s "$WORK/lipsync-360-whole.mp4" ] || { log "sem saída do Wav2Lip"; exit 6; }
log "Wav2Lip ok em $(( $(date +%s) - started ))s"

# 3. máscara elíptica suave na região do rosto (1080p).
MASK="$PILOT/face-mask-1080.png"
if [ ! -s "$MASK" ]; then
  python3 - <<'PY'
from PIL import Image, ImageDraw, ImageFilter
img = Image.new("L", (1920, 1080), 0)
draw = ImageDraw.Draw(img)
draw.ellipse((1150, 120, 1750, 780), fill=255)
img = img.filter(ImageFilter.GaussianBlur(35))
img.save("face-mask-1080.png")
PY
fi

# 4. compõe a boca sincronizada sobre o original 1080p, só no rosto.
# O tpad cobre os poucos frames que o Wav2Lip não gera no fim.
ffmpeg -y -v error -i "$SRC" -i "$WORK/lipsync-360-whole.mp4" -loop 1 -i "$MASK" \
  -filter_complex "\
[0:v]trim=0:$DURATION,setpts=PTS-STARTPTS[base];\
[1:v]tpad=stop_mode=clone:stop_duration=0.5,scale=1920:1080:flags=lanczos,setsar=1,format=rgba[sync];\
[2:v]format=gray[mask];\
[sync][mask]alphamerge[syncm];\
[base][syncm]overlay=0:0:format=auto[v]" \
  -map "[v]" -an -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -r 30 "$OUT"

log "concluído: $OUT"
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate \
  -of json "$OUT"
