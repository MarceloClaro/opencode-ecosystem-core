#!/usr/bin/env bash
# Re-render do piloto padrão (R1026) a partir de source.mp4.
# Não baixa mídia, não instala nada e não usa Remotion.
set -euo pipefail
cd "$(dirname "$0")"

FONT=$(fc-match -f '%{file}' "DejaVu Sans")
FONT_BOLD=$(fc-match -f '%{file}' "DejaVu Sans:bold")

# 16:9 — 20 s, legenda pt-BR, selo discreto.
ffmpeg -y -v error -i source.mp4 -filter_complex \
"[0:v]scale=1920:1080,fps=30,setsar=1[base];\
[base]drawbox=x=60:y=40:w=80:h=4:color=0x8b5cf6@1:t=fill,\
drawtext=fontfile='$FONT_BOLD':text='QISKIT':fontcolor=white@0.78:fontsize=22:x=w-tw-60:y=38:box=1:boxcolor=black@0.35:boxborderw=10,\
subtitles=filename='captions-16x9.ass':fontsdir=/usr/share/fonts/truetype/dejavu[v];\
[0:a]atrim=start=0:duration=20,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=19.7:d=0.3[a]" \
-map "[v]" -map "[a]" -t 20 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
-c:a aac -b:a 192k -ar 48000 -movflags +faststart pilot-16x9-standard.mp4

# 9:16 — 20 s, fundo desfocado escurecido, primeiro plano claro.
ffmpeg -y -v error -i source.mp4 -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.45:saturation=0.8,drawbox=x=0:y=0:w=1080:h=1920:color=black@0.35:t=fill[bg];\
[0:v]scale=1080:608[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2-40[base];\
[base]drawbox=x=0:y=616:w=1080:h=608:color=white@0.15:t=2,\
drawbox=x=70:y=120:w=90:h=6:color=0x8b5cf6@1:t=fill,\
drawtext=fontfile='$FONT_BOLD':text='QISKIT':fontcolor=white@0.8:fontsize=26:x=70:y=140,\
drawtext=fontfile='$FONT_BOLD':text='Circuitos quânticos':fontcolor=white:fontsize=54:x=70:y=185,\
drawtext=fontfile='$FONT_BOLD':text='em larga escala':fontcolor=white:fontsize=54:x=70:y=250,\
drawtext=fontfile='$FONT':text='100+ qubits • legendado':fontcolor=white@0.8:fontsize=28:x=70:y=320,\
subtitles=filename='captions-9x16.ass':fontsdir=/usr/share/fonts/truetype/dejavu,\
drawtext=fontfile='$FONT':text='Qiskit • legendado':fontcolor=white@0.6:fontsize=22:x=(w-tw)/2:y=1800[v];\
[0:a]atrim=start=0:duration=20,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=19.7:d=0.3[a]" \
-map "[v]" -map "[a]" -t 20 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
-c:a aac -b:a 192k -ar 48000 -movflags +faststart pilot-9x16-standard.mp4

for f in pilot-16x9-standard.mp4 pilot-9x16-standard.mp4; do
  ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate \
    -of json "$f"
done
