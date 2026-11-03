#!/usr/bin/env bash
# R1029/R1031 — concatena abertura + miolo novo + encerramento pelo filtro concat.
set -euo pipefail
cd "$(dirname "$0")"

REMOTION="/tmp/opencode/remotion-pilot/out"
INTRO16="$REMOTION/didactic-intro-16.mp4"
INTRO9="$REMOTION/didactic-intro-9.mp4"
OUTRO16="$REMOTION/didactic-outro-16.mp4"
OUTRO9="$REMOTION/didactic-outro-9.mp4"
MID16="$PWD/didactic-middle-16.mp4"
MID9="$PWD/didactic-middle-9.mp4"
OUT16="$PWD/pilot-16x9-didatico-voz.mp4"
OUT9="$PWD/pilot-9x16-didatico-voz.mp4"

for f in "$INTRO16" "$INTRO9" "$OUTRO16" "$OUTRO9" "$MID16" "$MID9"; do
  [ -s "$f" ] || { echo "ERRO: ausente: $f" >&2; exit 2; }
done

concat_variant() {
  local intro="$1" base="$2" outro="$3" output="$4"
  local iv bv ov
  iv=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$intro")
  bv=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$base")
  ov=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$outro")
  ffmpeg -y -v error -i "$intro" -i "$base" -i "$outro" -filter_complex "\
[0:v]setsar=1[v0];[1:v]setsar=1[v1];[2:v]setsar=1[v2];\
[0:a]apad=whole_dur=$iv,atrim=0:$iv[a0];\
[1:a]apad=whole_dur=$bv,atrim=0:$bv[a1];\
[2:a]apad=whole_dur=$ov,atrim=0:$ov[a2];\
[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a];\
[v]fps=30,setsar=1[vout];\
[a]loudnorm=I=-16:TP=-1.5:LRA=11[aout]" \
    -map "[vout]" -map "[aout]" -c:v libx264 -preset medium -crf 18 \
    -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart "$output"
  ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate -of json "$output"
}

concat_variant "$INTRO16" "$MID16" "$OUTRO16" "$OUT16"
concat_variant "$INTRO9" "$MID9" "$OUTRO9" "$OUT9"
