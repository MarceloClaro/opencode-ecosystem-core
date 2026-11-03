#!/usr/bin/env bash
# Concatena intro + master + outro com áudio silencioso nas pontas.
# Uso: ./render-studio.sh [intro] [master] [outro] [saida]
set -euo pipefail
cd "$(dirname "$0")"

INTRO="${1:-out/intro.mp4}"
MAIN="${2:-pilot-16x9-lipsync.mp4}"
OUTRO="${3:-out/outro.mp4}"
OUT="${4:-pilot-16x9-studio.mp4}"

for f in "$INTRO" "$MAIN" "$OUTRO"; do
  [ -s "$f" ] || { echo "ERRO: arquivo ausente: $f" >&2; exit 2; }
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Intro/outro não têm áudio; adiciona silêncio para o concat com o master.
ffmpeg -y -v error -i "$INTRO" -f lavfi -i anullsrc=r=48000:cl=stereo \
  -shortest -c:v copy -c:a aac -b:a 192k -ar 48000 "$TMP/intro.mp4"
ffmpeg -y -v error -i "$OUTRO" -f lavfi -i anullsrc=r=48000:cl=stereo \
  -shortest -c:v copy -c:a aac -b:a 192k -ar 48000 "$TMP/outro.mp4"

printf "file '%s'\n" "$TMP/intro.mp4" "$MAIN" "$TMP/outro.mp4" > "$TMP/concat.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$TMP/concat.txt" \
  -c copy -fflags +genpts -movflags +faststart "$OUT"

ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate \
  -of json "$OUT"
