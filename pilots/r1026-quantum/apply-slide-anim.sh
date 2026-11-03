#!/usr/bin/env bash
# R1027 — aplica a sequência animada de slides PT-BR ao master de lip sync.
set -euo pipefail
cd "$(dirname "$0")"

BASE="${BASE:-/home/marceloclaro/.cache/opencode-pilot}"
WORK="${WORK:-$BASE/lipsync-cpu}"
SRC="$WORK/composed-1080.mp4"
SLIDES="$PWD/slide-sequence.mp4"
AUDIO="$PWD/dub-pt-BR-clone.wav"
MASK="$PWD/slide-patch-mask.png"
OUT16="$PWD/pilot-16x9-lipsync-anim.mp4"
OUT9="$PWD/pilot-9x16-lipsync-anim.mp4"
DURATION=20

for f in "$SRC" "$SLIDES" "$AUDIO" "$MASK"; do
  [ -s "$f" ] || { echo "ERRO: ausente: $f" >&2; exit 2; }
done

# 1. slide animado 934->935 px, com máscara suave, sobre o master 1080p.
ffmpeg -y -v error -i "$SRC" -i "$SLIDES" -loop 1 -i "$MASK" -filter_complex "\
[1:v]scale=935:864,format=rgba[slide];\
[2:v]format=gray[mask];\
[slide][mask]alphamerge[slidem];\
[0:v][slidem]overlay=210:76:format=auto[v]" \
  -map "[v]" -an -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p -r 30 "$WORK/composed-slide-anim-1080.mp4"

FONT=$(fc-match -f '%{file}' "DejaVu Sans")
FONT_BOLD=$(fc-match -f '%{file}' "DejaVu Sans:bold")

# 2. 16:9 com legenda, selo e áudio.
ffmpeg -y -v error -i "$WORK/composed-slide-anim-1080.mp4" -i "$AUDIO" -filter_complex \
"[0:v]fps=30,setsar=1,drawbox=x=60:y=40:w=80:h=4:color=0x8b5cf6@1:t=fill,\
drawtext=fontfile='$FONT_BOLD':text='QISKIT':fontcolor=white@0.78:fontsize=22:x=w-tw-60:y=38:box=1:boxcolor=black@0.35:boxborderw=10,\
subtitles=filename='$PWD/captions-16x9.ass':fontsdir=/usr/share/fonts/truetype/dejavu[v];\
[1:a]atrim=0:$DURATION,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=19.7:d=0.3[a]" \
-map "[v]" -map "[a]" -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
-pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT16"

# 3. 9:16 a partir do master com slide animado.
ffmpeg -y -v error -i "$WORK/composed-slide-anim-1080.mp4" -i "$AUDIO" -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.45:saturation=0.8,drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill[bg];\
[0:v]scale=1080:608[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2-40[base];\
[base]drawbox=x=0:y=616:w=1080:h=608:color=white@0.15:t=2,\
drawbox=x=70:y=120:w=90:h=6:color=0x8b5cf6@1:t=fill,\
drawtext=fontfile='$FONT_BOLD':text='QISKIT':fontcolor=white@0.8:fontsize=26:x=70:y=140,\
drawtext=fontfile='$FONT_BOLD':text='Circuitos quânticos':fontcolor=white:fontsize=54:x=70:y=185,\
drawtext=fontfile='$FONT_BOLD':text='em larga escala':fontcolor=white:fontsize=54:x=70:y=250,\
drawtext=fontfile='$FONT':text='100+ qubits • dublado':fontcolor=white@0.8:fontsize=28:x=70:y=320,\
subtitles=filename='$PWD/captions-9x16.ass':fontsdir=/usr/share/fonts/truetype/dejavu,\
drawtext=fontfile='$FONT':text='Qiskit • voz sintética':fontcolor=white@0.6:fontsize=22:x=(w-tw)/2:y=1800[v];\
[1:a]atrim=0:$DURATION,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=19.7:d=0.3[a]" \
-map "[v]" -map "[a]" -t "$DURATION" -c:v libx264 -preset medium -crf 18 \
-pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT9"

for f in "$OUT16" "$OUT9"; do
  echo "=== $f ==="
  ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate \
    -of json "$f"
done
