#!/usr/bin/env python3
"""Clean the Demucs music stem: tame strident highs, denoise, limit."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'pilot-P0006/stems/music.wav'
OUT = ROOT / 'pilot-P0006/stems/music-clean.wav'
FILTER = (
    'highpass=f=35,'
    'equalizer=f=2500:t=q:w=1.2:g=-2,'
    'equalizer=f=6500:t=q:w=1.2:g=-3.5,'
    'equalizer=f=10000:t=h:w=2000:g=-2,'
    'lowpass=f=15000,'
    'afftdn=nr=10:nf=-38,'
    'acompressor=threshold=0.125:ratio=2:attack=20:release=250,'
    'alimiter=limit=0.9'
)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def stats(path):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-v', 'info', '-i', str(path),
                             '-af', 'astats=metadata=1:reset=0', '-f', 'null', '-'],
                            capture_output=True, text=True, timeout=300)
    rms = re.findall(r'RMS level dB:\s*(-?[0-9.]+)', result.stderr)
    peak = re.findall(r'Peak level dB:\s*(-?[0-9.]+)', result.stderr)
    return {'rms_dbfs': float(rms[-1]) if rms else None,
            'peak_dbfs': float(peak[-1]) if peak else None}


if OUT.exists():
    raise SystemExit(f'refusing overwrite: {OUT}')
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(SOURCE), '-af', FILTER,
                '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', '-y', str(OUT)],
               check=True, timeout=1800)
manifest = {
    'schema_version': 1,
    'part_id': '02XpQTA-_XE-P0006',
    'source': str(SOURCE.relative_to(ROOT)),
    'output': str(OUT.relative_to(ROOT)),
    'filter': FILTER,
    'sample_rate': 48000,
    'channels': 2,
    'before': stats(SOURCE),
    'after': stats(OUT),
    'sha256': sha256(OUT),
    'status': 'music_cleaned_pending_listening_review',
    'limitations': ['EQ/denoise reduce harshness but cannot restore separation damage',
                    'no listening or audiovisual approval',
                    'music is a Demucs estimate, not the original multitrack'],
}
(ROOT / 'pilot-P0006/stems/music-clean.json').write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(manifest['after'], ensure_ascii=False))
