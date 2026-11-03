"""Evidência OCR local para revisão; não traduz, não mapeia vozes, não dubla."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from integrations import dubbing_batch as batch

VERSION = 'R1041-evidence-1'
WIDTH, HEIGHT = 2160, 400


def requests(part, fps=25):
    frames = part['end_frame'] - part['start_frame']
    by_frame = {}
    if part['units']:
        for u in part['units']:
            frame = min(frames - 1, max(0, int((u['start_part'] + u['end_part']) * fps / 2)))
            by_frame.setdefault(frame, []).append(u['id'])
    else:
        for frame in range(min(frames - 1, fps), frames, 10 * fps):
            by_frame[frame] = []
    return [{'frame': k, 'unit_ids': v} for k, v in sorted(by_frame.items())]


def extract_frames(video, frame_numbers):
    select = '+'.join(f'eq(n\\,{n})' for n in frame_numbers)
    command = ['ffmpeg', '-nostdin', '-v', 'error', '-threads', '2', '-i', str(video),
        '-an', '-filter_threads', '1', '-vf',
        f'select={select},crop=1080:200:100:520,scale={WIDTH}:{HEIGHT}',
        '-fps_mode', 'vfr', '-pix_fmt', 'gray', '-f', 'rawvideo', 'pipe:1']
    proc = subprocess.run(command, capture_output=True, timeout=600, check=True)
    size = WIDTH * HEIGHT
    if len(proc.stdout) != len(frame_numbers) * size:
        raise ValueError('extracted frame count mismatch')
    header = f'P5\n{WIDTH} {HEIGHT}\n255\n'.encode()
    # White subtitles -> black, other pixels -> white. Candidate evidence only.
    table = bytes(0 if i > 220 else 255 for i in range(256))
    return [header + proc.stdout[i:i+size].translate(table)
            for i in range(0, len(proc.stdout), size)]


def ocr_frame(pgm):
    result = subprocess.run(['tesseract', 'stdin', 'stdout', '-l', 'eng', '--psm', '6'],
        input=pgm, capture_output=True, timeout=60, check=True,
        env={**os.environ, 'OMP_THREAD_LIMIT': '1'})
    return result.stdout.decode('utf-8').strip()


def process_part(root, part, video, extractor=extract_frames, ocr=ocr_frame, toolchain=None):
    pid = part['part_id']
    if not batch.ID.fullmatch(pid):
        raise ValueError('invalid part ID')
    root = Path(root)
    video = Path(video)
    if video.is_symlink() or not video.is_file() or not video.resolve().is_relative_to(root.resolve()):
        raise ValueError('unconfined video')
    samples = requests(part)
    inputs = {'source_sha256': batch.file_hash(video), 'part_request': part,
              'tools': toolchain or {}, 'module_sha256': batch.file_hash(__file__)}
    key = batch.cache_key(inputs, {'crop': [100, 520, 1080, 200], 'threshold': 220,
                                 'scale': [WIDTH, HEIGHT], 'psm': 6}, VERSION)
    rel = f'.dubbing-evidence/{VERSION}/{pid}/{key}'
    out = batch.confined_path(root, rel)
    manifest = out / 'evidence.json'
    if out.exists():
        data = batch.read_json(manifest)
        if data.get('key') != key:
            raise ValueError('evidence key integrity mismatch')
        for row in data['frames']:
            image = batch.confined_path(root, f'{rel}/{row["image"]}')
            if batch.file_hash(image) != row['sha256']:
                raise ValueError('evidence image integrity mismatch')
        checksum = batch.confined_path(root, f'{rel}/evidence.sha256').read_text().strip()
        if batch.file_hash(manifest) != checksum:
            raise ValueError('evidence manifest integrity mismatch')
        return {'part_id': pid, 'frames': len(samples), 'cache_hit': True,
                'artifact': f'{rel}/evidence.json', 'dubbed': False}
    images = extractor(video, [r['frame'] for r in samples])
    if len(images) != len(samples):
        raise ValueError('extracted frame count mismatch')
    if batch.file_hash(video) != inputs['source_sha256']:
        raise ValueError('source changed during extraction')
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for request, image in zip(samples, images):
        name = f'frame-{request["frame"]:06d}.pgm'
        with (out / name).open('xb') as f:
            f.write(image)
        text = ocr(image)
        rows.append({**request, 'image': name, 'sha256': hashlib.sha256(image).hexdigest(),
                     'ocr_english_candidate': text, 'source_review': 'pending'})
    batch.write_new(manifest, {'key': key, 'inputs': inputs, 'part_id': pid, 'frames': rows,
        'status': 'evidence_collected_not_reviewed', 'audiovisual_approved': False,
        'limitations': ['one midpoint image per ASR unit may omit changing subtitles',
                       'English subtitles are secondary translation, OCR may be wrong',
                       'no-ASR sparse samples cannot establish absence of dialogue']})
    with (out / 'evidence.sha256').open('x') as f:
        f.write(batch.file_hash(manifest) + '\n')
    return {'part_id': pid, 'frames': len(samples), 'cache_hit': False,
            'artifact': f'{rel}/evidence.json', 'dubbed': False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--exclude-part', default='02XpQTA-_XE-P0006')
    args = p.parse_args(argv)
    root = Path(args.root)
    status = batch.status(root)
    manifest = batch.read_json(batch.confined_path(root, status['run_dir'] + '/manifest.json'))
    versions = {name: subprocess.run([name, flag], capture_output=True, text=True,
                 check=True, timeout=20).stdout.splitlines()[0]
                for name, flag in [('ffmpeg', '-version'), ('tesseract', '--version')]}
    outputs = []
    # Same job lock as prepare, so no competing writers through supported entrypoints.
    with batch.locked(root):
        for pid in manifest['part_ids']:
            if pid == args.exclude_part:
                continue
            part = batch.read_json(batch.confined_path(root, f'{status["run_dir"]}/parts/{pid}.json'))
            video = batch.confined_path(root, f'parts-final/parts/{pid}.mp4')
            result = process_part(root, part, video, toolchain=versions)
            outputs.append(result)
            print(json.dumps(result), flush=True)
    receipt_key = batch.digest(outputs)
    receipt_rel = f'.dubbing-evidence/receipt-{receipt_key}.json'
    receipt = batch.confined_path(root, receipt_rel)
    report = {'status': 'source_evidence_collected_not_dubbed', 'parts': outputs,
              'parts_processed': len(outputs), 'frames': sum(r['frames'] for r in outputs),
              'cache_hits': sum(r['cache_hit'] for r in outputs), 'new_dubbed_parts': 0}
    if not receipt.exists():
        batch.write_new(receipt, report)
    print(json.dumps({k: v for k, v in report.items() if k != 'parts'} | {'receipt': receipt_rel}), flush=True)


if __name__ == '__main__':
    main()
