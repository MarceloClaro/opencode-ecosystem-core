#!/usr/bin/env python3
"""Render a human-readable audit table for the planned/extracted parts."""
import argparse
import json
from pathlib import Path
from datetime import timedelta


def timecode(seconds):
    delta = timedelta(seconds=float(seconds))
    total = int(delta.total_seconds())
    millis = int(round((float(seconds) - total) * 1000))
    if millis == 1000:
        total += 1
        millis = 0
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f'{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--segments', required=True)
    parser.add_argument('--manifest')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    plan = json.loads(Path(args.segments).read_text())
    manifest = json.loads(Path(args.manifest).read_text()) if args.manifest else None
    by_id = {part['id']: part for part in manifest['parts']} if manifest else {}
    rows = []
    for segment in plan['segments']:
        part = by_id.get(segment['id'], {})
        artifact = part.get('artifact', {})
        rows.append('| {id} | {start} | {end} | {duration:.3f} | {frames} | {kind} | {file} | {hash} | {edit} | {qa} | {approval} |'.format(
            id=segment['id'],
            start=timecode(segment['start_seconds']),
            end=timecode(segment['end_seconds']),
            duration=segment['duration_seconds'],
            frames=segment['end_frame'] - segment['start_frame'],
            kind=segment['boundary_kind'],
            file=Path(artifact['path']).name if artifact.get('path') else '—',
            hash=(artifact.get('sha256') or '—')[:12],
            edit=part.get('states', {}).get('editing', 'pending'),
            qa=part.get('states', {}).get('technical_qa', 'pending'),
            approval=part.get('states', {}).get('approval', 'pending'),
        ))
    durations = [segment['duration_seconds'] for segment in plan['segments']]
    kinds = {}
    for segment in plan['segments']:
        kinds[segment['boundary_kind']] = kinds.get(segment['boundary_kind'], 0) + 1
    lines = [
        f'# Partes — {plan["video_id"]}',
        '',
        f'- Fonte: `{plan.get("source", {}).get("path", "—")}`',
        f'- SHA-256 da fonte: `{plan.get("source", {}).get("sha256", "—")}`',
        f'- Frames totais: {plan["total_frames"]}; fps: {plan["fps"]}; duração: {timecode(plan["duration_seconds"])}',
        f'- Partes: {len(plan["segments"])}; duração mínima: {min(durations):.3f} s; máxima: {max(durations):.3f} s',
        f'- Fronteiras: {", ".join(f"{k}={v}" for k, v in sorted(kinds.items()))}',
        f'- Extração: {"manifesto presente" if manifest else "ainda não executada"}',
        '- Montagem: **bloqueada** até edição, QA técnico, revisão audiovisual e aprovação de todas as partes.',
        '',
        '| ID | Início | Fim | Dur. s | Frames | Fronteira | Arquivo | SHA-256 | Edição | QA | Aprovação |',
        '|---|---|---|---:|---:|---|---|---|---|---|---|',
        *rows,
        '',
        'Os tempos são intervalos editoriais `[início,fim)`; o contexto de ±2 s existe apenas nos intermediários e não entra na montagem.',
        '',
    ]
    Path(args.out).write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'parts': len(plan['segments']), 'out': str(Path(args.out).resolve())}))


if __name__ == '__main__':
    main()
