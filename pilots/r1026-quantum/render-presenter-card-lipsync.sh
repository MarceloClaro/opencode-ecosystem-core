#!/usr/bin/env bash
# R1031 — lip sync da apresentadora para os cartões de abertura/encerramento.
#
# Uso: ./render-presenter-card-lipsync.sh <audio.wav> <duracao> <rotulo> [saida]
# Ex.: ./render-presenter-card-lipsync.sh intro-narracao.wav 14.187 intro
#
# Estratégia: mesma do R1027 (Wav2Lip em 640x360, blocos de 5 s, watchdog,
# retomada), mas com duração variável e saída 1080p composta. O recorte e a
# matte por frame ficam em compose-presenter-card.py.
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
WORK="${WORK:-$BASE/lipsync-cards/$LABEL}"
SRC="$PILOT/source.mp4"

SCALE="640:360"
CHUNK=5
THREADS=2
BATCH=4
MAX_RSS_MB=4500
TIMEOUT=1200

[ -s "$AUDIO" ] || { echo "ERRO: áudio ausente: $AUDIO" >&2; exit 2; }
[ -s "$SRC" ] || { echo "ERRO: fonte ausente: $SRC" >&2; exit 2; }
[ -s "$WAV2LIP/inference.py" ] || { echo "ERRO: Wav2Lip ausente" >&2; exit 2; }
[ -x "$PY" ] || { echo "ERRO: venv do Wav2Lip ausente" >&2; exit 2; }

mkdir -p "$WORK/chunks" "$PILOT/temp"
exec 9>"$WORK/lock"
if ! flock -n 9; then
  echo "ERRO: outra execução de lip sync está ativa para $LABEL." >&2
  exit 3
fi

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS"
export OPENBLAS_NUM_THREADS="$THREADS" NUMBA_NUM_THREADS="$THREADS"
export WAV2LIP_THREADS="$THREADS"

log() { echo "[$(date -Is)] $*" | tee -a "$WORK/run.log"; }

log "início: label=$LABEL duration=$DURATION scale=$SCALE threads=$THREADS"

# 1. fonte 640x360, duração alvo, sem áudio.
if [ ! -s "$WORK/source-360.mp4" ]; then
  ffmpeg -y -v error -i "$SRC" -t "$DURATION" \
    -vf "scale=$SCALE:flags=lanczos" -r 30 \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -an "$WORK/source-360.mp4"
fi

# 2. número de blocos = ceil(duração / 5)
N_CHUNKS=$(python3 -c "import math; print(math.ceil(float('$DURATION') / 5.0))")
log "blocos: $N_CHUNKS"

for ((i = 0; i < N_CHUNKS; i++)); do
  start=$((i * CHUNK))
  chunk_dur=$(python3 -c "print(min(5.0, float('$DURATION') - $start))")
  input="$WORK/chunks/in-$i.mp4"
  audio="$WORK/chunks/audio-$i.wav"
  output="$WORK/chunks/out-$i.mp4"
  done_marker="$WORK/chunks/done-$i"

  if [ -f "$done_marker" ] && [ -s "$output" ]; then
    log "bloco $i já concluído; retomando"
    continue
  fi

  ffmpeg -y -v error -ss "$start" -t "$chunk_dur" -i "$WORK/source-360.mp4" \
    -an -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 "$input"
  ffmpeg -y -v error -ss "$start" -t "$chunk_dur" -i "$AUDIO" \
    -ar 48000 -ac 2 "$audio"

  log "bloco $i: start=${start}s dur=${chunk_dur}s"
  nice -n 19 ionice -c3 "$PY" "$WAV2LIP/inference.py" \
    --checkpoint_path "$WAV2LIP/checkpoints/wav2lip_gan.pth" \
    --face "$input" --audio "$audio" --outfile "$output" \
    --pads 0 10 0 0 --resize_factor 1 --wav2lip_batch_size "$BATCH" \
    > "$WORK/chunks/log-$i.txt" 2>&1 &
  pid=$!
  started=$(date +%s)
  max_rss=0
  while kill -0 "$pid" 2>/dev/null; do
    rss=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
    rss=${rss:-0}
    [ "$rss" -gt "$max_rss" ] && max_rss=$rss
    if [ "$rss" -gt $((MAX_RSS_MB * 1024)) ]; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      log "bloco $i ABORTADO: RSS ${rss}KB acima de ${MAX_RSS_MB}MB"
      exit 4
    fi
    if [ $(( $(date +%s) - started )) -gt "$TIMEOUT" ]; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      log "bloco $i ABORTADO: timeout de ${TIMEOUT}s"
      exit 5
    fi
    sleep 5
  done
  if ! wait "$pid"; then
    log "bloco $i FALHOU; veja chunks/log-$i.txt"
    tail -20 "$WORK/chunks/log-$i.txt" >&2 || true
    exit 6
  fi
  [ -s "$output" ] || { log "bloco $i sem saída"; exit 7; }
  touch "$done_marker"
  log "bloco $i ok (${max_rss}KB pico, $(( $(date +%s) - started ))s)"
done

# 3. concatena os blocos.
: > "$WORK/chunks/concat.txt"
for ((i = 0; i < N_CHUNKS; i++)); do
  echo "file '$WORK/chunks/out-$i.mp4'" >> "$WORK/chunks/concat.txt"
done
ffmpeg -y -v error -f concat -safe 0 -i "$WORK/chunks/concat.txt" \
  -c copy -fflags +genpts "$WORK/lipsync-360.mp4"

# 4. máscara elíptica suave na região do rosto (1080p).
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

# 5. compõe a boca sincronizada sobre o original 1080p, só no rosto.
# O tpad cobre pequenas diferenças de frames no fim do último bloco.
ffmpeg -y -v error -i "$SRC" -i "$WORK/lipsync-360.mp4" -loop 1 -i "$MASK" \
  -filter_complex "\
[0:v]trim=0:$DURATION,setpts=PTS-STARTPTS[base];\
[1:v]tpad=stop_mode=clone:stop_duration=1,scale=1920:1080:flags=lanczos,setsar=1,format=rgba[sync];\
[2:v]format=gray[mask];\
[sync][mask]alphamerge[syncm];\
[base][syncm]overlay=0:0:format=auto[v]" \
  -map "[v]" -an -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -r 30 "$OUT"

log "concluído: $OUT"
ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate \
  -of json "$OUT"
