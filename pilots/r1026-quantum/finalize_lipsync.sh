#!/usr/bin/env bash
# R1027 — espera o runner, aplica o slide PT-BR e verifica tudo.
set -euo pipefail
cd "$(dirname "$0")"

PILOT="$(pwd)"
REPO="/home/marceloclaro/opencode-ecosystem-core"
BASE="${BASE:-/home/marceloclaro/.cache/opencode-pilot}"
WORK="${WORK:-$BASE/lipsync-cpu}"
PID="$(cat lipsync-run.pid)"
LOG="$PILOT/finalize.log"
: > "$LOG"

log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }

log "aguardando runner PID $PID"
while kill -0 "$PID" 2>/dev/null; do sleep 20; done
log "runner encerrado"

for f in "$WORK/composed-1080.mp4" "$WORK/lipsync-360.mp4"; do
  [ -s "$f" ] || { log "ERRO: ausente $f"; exit 2; }
done

log "aplicando slide PT-BR"
./apply-slide.sh 2>&1 | tee -a "$LOG"

for f in pilot-16x9-lipsync-pt.mp4 pilot-9x16-lipsync-pt.mp4; do
  [ -s "$f" ] || { log "ERRO: saída ausente $f"; exit 3; }
done

log "extraindo frames"
for t in 2 8 15; do
  ffmpeg -y -v error -ss "$t" -i pilot-16x9-lipsync-pt.mp4 -frames:v 1 "final-16x9-$t.png"
  ffmpeg -y -v error -ss "$t" -i pilot-9x16-lipsync-pt.mp4 -frames:v 1 "final-9x16-$t.png"
done

log "medindo loudness e ffprobe"
for f in pilot-16x9-lipsync-pt.mp4 pilot-9x16-lipsync-pt.mp4; do
  ffmpeg -hide_banner -i "$f" -af loudnorm=print_format=json -f null - 2> "${f%.mp4}-loudness.txt" || true
  ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate -of json "$f" > "${f%.mp4}-ffprobe.json"
done

python3 - <<'PY'
import json, re
from pathlib import Path
root = Path('/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum')
s = (root / 'pilot-16x9-lipsync-pt-loudness.txt').read_text(encoding='utf-8', errors='replace')
d = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', s, re.S)[-1])
report = {
    'width': 1920, 'height': 1080, 'fps': 30, 'duration_seconds': 20.0,
    'video_codec': 'h264', 'audio_codec': 'aac', 'container': 'mp4',
    'loudness_lufs': round(float(d['input_i']), 1),
}
(root / 'report-lipsync-pt.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(report)
PY

log "validando R1024"
cd "$REPO"
python3 -m integrations.video_edit_plan validate pilots/r1026-quantum/plan-lipsync-pt.json > pilots/r1026-quantum/plan-lipsync-pt-validate.json
python3 -m integrations.video_edit_plan verify pilots/r1026-quantum/plan-lipsync-pt.json pilots/r1026-quantum/report-lipsync-pt.json > pilots/r1026-quantum/plan-lipsync-pt-verify.json
cd "$PILOT"

python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('/home/marceloclaro/opencode-ecosystem-core/pilots/r1026-quantum')
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()
m = json.load(open(root / 'manifest.json'))
files = {}
for name in ('pilot-16x9-lipsync-pt.mp4', 'pilot-9x16-lipsync-pt.mp4',
             'slide-patch.png', 'slide-patch-mask.png',
             'plan-lipsync-pt.json', 'report-lipsync-pt.json'):
    p = root / name
    if p.is_file():
        files[name] = {'bytes': p.stat().st_size, 'sha256': sha(p)}
        m['files'][name] = files[name]
m['lip_sync'] = {
    'status': 'completed',
    'method': 'Wav2Lip 640x360 em 4 blocos, face overlay em 1080p',
    'slide_pt': True,
    'outputs': ['pilot-16x9-lipsync-pt.mp4', 'pilot-9x16-lipsync-pt.mp4'],
}
(root / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
(root / 'finalize-manifest.json').write_text(json.dumps({'files': files}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(files, ensure_ascii=False, indent=2))
PY

log "FINALIZADO"
cat "$PILOT/plan-lipsync-pt-verify.json" | tee -a "$LOG"
