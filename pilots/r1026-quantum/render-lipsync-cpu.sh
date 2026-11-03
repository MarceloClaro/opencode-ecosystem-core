#!/usr/bin/env bash
# R1027 — lip sync CPU-safe, em blocos retomáveis, sem nvidia-smi.
#
# Uso: ./render-lipsync-cpu.sh [audio] [saida-16x9] [saida-9x16]
# Padrões: dub-pt-BR-clone.wav, pilot-16x9-lipsync.mp4, pilot-9x16-lipsync.mp4
#
# Estratégia:
#  - Wav2Lip em 640x360 (detecção facial viável em CPU; ~3,6 GB);
#  - blocos de 5 s, retomáveis por chunks/done-N;
#  - 2 threads, nice/ionice, watchdog de 4,5 GB;
#  - a boca sincronizada é sobreposta ao vídeo original 1080p apenas na
#    região do rosto, com máscara elíptica suavizada; o resto mantém 1080p.
set -euo pipefail
cd "$(dirname "$0")"

PILOT="$(pwd)"
BASE="${BASE:-/home/marceloclaro/.cache/opencode-pilot}"
WAV2LIP="$BASE/Wav2Lip"
PY="$BASE/venvs/wav2lip/bin/python"
WORK="${WORK:-$BASE/lipsync-cpu}"
AUDIO="${1:-$PILOT/dub-pt-BR-clone.wav}"
OUT16="${2:-$PILOT/pilot-16x9-lipsync.mp4}"
OUT9="${3:-$PILOT/pilot-9x16-lipsync.mp4}"
SRC="$PILOT/source.mp4"

SCALE="640:360"
CHUNK=5
DURATION=20
THREADS=2
BATCH=4
MAX_RSS_MB=4500
TIMEOUT=1200

mkdir -p "$WORK/chunks" "$PILOT/temp"
exec 9>"$WORK/lock"
if ! flock -n 9; then
  echo "ERRO: outra execução de lip sync está ativa." >&2
  exit 3
fi

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS"
export OPENBLAS_NUM_THREADS="$THREADS" NUMBA_NUM_THREADS="$THREADS"
export WAV2LIP_THREADS="$THREADS"

log() { echo "[$(date -Is)] $*" | tee -a "$WORK/run.log"; }

log "início: scale=$SCALE chunk=${CHUNK}s threads=$THREADS batch=$BATCH max_rss=${MAX_RSS_MB}MB"

# 1. fonte 640x360, 30 fps, 20 s, sem áudio.
if [ ! -s "$WORK/source-360.mp4" ]; then
  ffmpeg -y -v error -i "$SRC" -t "$DURATION" \
    -vf "scale=$SCALE:flags=lanczos" -r 30 \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -an "$WORK/source-360.mp4"
fi

# 2. blocos de 5 s.
for i in 0 1 2 3; do
  start=$((i * CHUNK))
  input="$WORK/chunks/in-$i.mp4"
  audio="$WORK/chunks/audio-$i.wav"
  output="$WORK/chunks/out-$i.mp4"
  done_marker="$WORK/chunks/done-$i"

  if [ -f "$done_marker" ]; then
    log "bloco $i já concluído; retomando"
    continue
  fi

  ffmpeg -y -v error -ss "$start" -t "$CHUNK" -i "$WORK/source-360.mp4" \
    -an -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 "$input"
  ffmpeg -y -v error -ss "$start" -t "$CHUNK" -i "$AUDIO" \
    -ar 48000 -ac 2 "$audio"

  log "bloco $i: iniciando (start=${start}s)"
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
  if [ ! -s "$output" ]; then
    log "bloco $i sem saída"
    exit 7
  fi
  touch "$done_marker"
  log "bloco $i ok (${max_rss}KB pico, $(( $(date +%s) - started ))s)"
done

# 3. concatena os blocos.
: > "$WORK/chunks/concat.txt"
for i in 0 1 2 3; do
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
img.save("/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum/face-mask-1080.png")
PY
fi

# 5. compõe: boca sincronizada só no rosto; resto = original 1080p.
ffmpeg -y -v error -i "$SRC" -i "$WORK/lipsync-360.mp4" -loop 1 -i "$MASK" \
  -filter_complex "\
[0:v]trim=0:$DURATION,setpts=PTS-STARTPTS[base];\
[1:v]scale=1920:1080:flags=lanczos,setsar=1,format=rgba[sync];\
[2:v]format=gray[mask];\
[sync][mask]alphamerge[syncm];\
[base][syncm]overlay=0:0:format=auto[v]" \
  -map "[v]" -an -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -r 30 "$WORK/composed-1080.mp4"

FONT=$(fc-match -f '%{file}' "DejaVu Sans")
FONT_BOLD=$(fc-match -f '%{file}' "DejaVu Sans:bold")

# 6. master 16:9 com legenda e selo.
ffmpeg -y -v error -i "$WORK/composed-1080.mp4" -i "$AUDIO" -filter_complex \
"[0:v]fps=30,setsar=1,drawbox=x=60:y=40:w=80:h=4:color=0x8b5cf6@1:t=fill,\
drawtext=fontfile='$FONT_BOLD':text='QISKIT':fontcolor=white@0.78:fontsize=22:x=w-tw-60:y=38:box=1:boxcolor=black@0.35:boxborderw=10,\
subtitles=filename='$PILOT/captions-16x9.ass':fontsdir=/usr/share/fonts/truetype/dejavu[v];\
[1:a]atrim=0:$DURATION,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=19.7:d=0.3[a]" \
-map "[v]" -map "[a]" -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
-pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT16"

# 7. vertical a partir do composto sem legendas.
ffmpeg -y -v error -i "$WORK/composed-1080.mp4" -i "$AUDIO" -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.45:saturation=0.8,drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill[bg];\
[0:v]scale=1080:608[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2-40[base];\
[base]drawbox=x=0:y=616:w=1080:h=608:color=white@0.15:t=2,\
drawbox=x=70:y=120:w=90:h=6:color=0x8b5cf6@1:t=fill,\
drawtext=fontfile='$FONT_BOLD':text='QISKIT':fontcolor=white@0.8:fontsize=26:x=70:y=140,\
drawtext=fontfile='$FONT_BOLD':text='Circuitos quânticos':fontcolor=white:fontsize=54:x=70:y=185,\
drawtext=fontfile='$FONT_BOLD':text='em larga escala':fontcolor=white:fontsize=54:x=70:y=250,\
drawtext=fontfile='$FONT':text='100+ qubits • dublado':fontcolor=white@0.8:fontsize=28:x=70:y=320,\
subtitles=filename='$PILOT/captions-9x16.ass':fontsdir=/usr/share/fonts/truetype/dejavu,\
drawtext=fontfile='$FONT':text='Qiskit • voz sintética':fontcolor=white@0.6:fontsize=22:x=(w-tw)/2:y=1800[v];\
[1:a]atrim=0:$DURATION,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=19.7:d=0.3[a]" \
-map "[v]" -map "[a]" -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
-pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT9"

log "concluído: $OUT16 e $OUT9"
for f in "$OUT16" "$OUT9"; do
  ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate \
    -of json "$f"
done
