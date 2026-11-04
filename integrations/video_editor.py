"""R1042: núcleo universal de projeto, plano e render de vídeo local.

Planos não executam FFmpeg. O render é separado, usa arquivo temporário,
confere frames e só promove com recibo. Dublagem é um plugin: sem adaptador,
o núcleo bloqueia em vez de inventar voz.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile

VERSION = 'R1042-1'
HEX = re.compile(r'[0-9a-f]{64}')
KINDS = {'video', 'audio', 'subtitle'}
PLAN_KEYS = {'operation', 'inputs', 'output', 'args', 'expected_frames',
             'frame_tolerance', 'warnings', 'limitations'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def parse_rational(value):
    if not isinstance(value, str) or '/' not in value:
        raise ValueError('fps rational required')
    a, b = value.split('/', 1)
    try:
        num, den = int(a), int(b)
    except ValueError as exc:
        raise ValueError('fps rational must be integer/integer') from exc
    if num <= 0 or den <= 0:
        raise ValueError('fps rational must be positive')
    g = math.gcd(num, den)
    return num // g, den // g


def fps_value(rational):
    return rational[0] / rational[1]


def source_fps(project, source):
    """Taxa da fonte; ausência só é aceita como a taxa da timeline."""
    value = source.get('fps')
    if value is None:
        return tuple(project['fps'])
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError('source fps rational required')
    num, den = value
    if type(num) is not int or type(den) is not int:
        raise ValueError('source fps must be integer rational')
    return parse_rational(f'{num}/{den}')


def timeline_frames(project, source, first, last):
    """Converte frames da fonte em frames da timeline, arredondando para cima.

    O arredondamento para cima evita encurtar o último frame quando a taxa da
    fonte difere da timeline (ex.: 30 fps em 30000/1001). A conformidade é
    registrada pelo planejador; não é uma conversão silenciosa de VFR.
    """
    src_num, src_den = source_fps(project, source)
    out_num, out_den = project['fps']
    value = (last - first) * src_den * out_num
    divisor = src_num * out_den
    return -(-value // divisor)



def _even(value, label):
    if type(value) is not int or value <= 0 or value % 2:
        raise ValueError(f'{label} must be a positive even integer')
    return value


def _confined(root, relative):
    root = Path(root).absolute()
    p = Path(relative)
    if p.is_absolute() or not p.parts or any(part in ('.', '..') for part in p.parts):
        raise ValueError('relative path required; escape blocked')
    target = root / p
    for node in (target, *target.parents):
        if node.is_symlink():
            raise ValueError('symlink blocked')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('path escape blocked')
    return target


def project_from_probe(source, probe, project_id='project', *, allow_silent=False):
    video = probe.get('video')
    audio = probe.get('audio')
    if not isinstance(video, dict):
        raise ValueError('video stream required')
    if not isinstance(audio, dict) and not allow_silent:
        raise ValueError('audio stream required')
    has_audio = isinstance(audio, dict)
    audio = audio if has_audio else {'sample_rate': 48000, 'channels': 2}
    fps = parse_rational(video.get('fps'))
    width, height = int(video['width']), int(video['height'])
    rotation = int(video.get('rotation', 0) or 0) % 360
    if rotation in (90, 270):
        width, height = height, width
    frames = video.get('frames')
    if type(frames) is not int or frames <= 0:
        raise ValueError('video frames required')
    record = {'path': probe.get('path', source), 'sha256': probe.get('sha256'),
              'frames': frames, 'duration_seconds': probe.get('duration_seconds'),
              'fps': list(fps), 'width': width, 'height': height,
              'variable_frame_rate': bool(video.get('variable_frame_rate', False)),
              'has_audio': has_audio}
    return {
        'schema_version': 1, 'version': VERSION, 'project_id': project_id,
        'root': '.', 'fps': list(fps), 'width': width, 'height': height,
        'sample_rate': int(audio['sample_rate']), 'channels': int(audio['channels']),
        'sources': {source: record}, 'video': copy.deepcopy(video),
        'audio': copy.deepcopy(audio),
        'tracks': [{'id': 'v1', 'kind': 'video', 'clips': []},
                   {'id': 'a1', 'kind': 'audio', 'clips': []}],
    }


def validate_project(project, *, strict=False):
    if not isinstance(project, dict) or project.get('schema_version') != 1:
        raise ValueError('project schema required')
    project = copy.deepcopy(project)
    if project.get('version') != VERSION:
        raise ValueError('project version mismatch')
    fps = project.get('fps')
    if not isinstance(fps, (list, tuple)) or len(fps) != 2:
        raise ValueError('project fps required')
    parse_rational(f'{fps[0]}/{fps[1]}')
    for name in ('width', 'height'):
        _even(project.get(name), name)
    if type(project.get('sample_rate')) is not int or project['sample_rate'] <= 0:
        raise ValueError('sample_rate required')
    sources = project.get('sources')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('sources required')
    for key, record in sources.items():
        if not isinstance(key, str) or not isinstance(record, dict):
            raise ValueError('source record required')
        if type(record.get('frames')) is not int or record['frames'] <= 0:
            raise ValueError('source frames required')
        if strict and (not isinstance(record.get('sha256'), str)
                       or not HEX.fullmatch(record['sha256'])):
            raise ValueError(f'source hash required: {key}')
    tracks = project.get('tracks')
    if not isinstance(tracks, list) or not tracks:
        raise ValueError('tracks required')
    ids, track_ids, clips = set(), set(), {}
    for track in tracks:
        if not isinstance(track, dict) or track.get('kind') not in KINDS:
            raise ValueError('invalid track kind')
        tid = track.get('id')
        if not isinstance(tid, str) or not tid or tid in track_ids:
            raise ValueError('duplicate/invalid track ID')
        track_ids.add(tid)
        rows = track.get('clips')
        if not isinstance(rows, list):
            raise ValueError('clips list required')
        for c in rows:
            if not isinstance(c, dict):
                raise ValueError('clip object required')
            cid = c.get('id')
            if not isinstance(cid, str) or not cid or cid in ids:
                raise ValueError(f'duplicate clip ID: {cid}')
            ids.add(cid)
            if c.get('track') != tid:
                raise ValueError(f'{cid}: clip track mismatch')
            src = sources.get(c.get('source'))
            if src is None:
                raise ValueError(f'{cid}: source unknown')
            inn, out = c.get('in_frame'), c.get('out_frame')
            if type(inn) is not int or type(out) is not int or inn < 0 or out <= inn:
                raise ValueError(f'{cid}: invalid source range')
            if out > src['frames']:
                raise ValueError(f'{cid}: clip outside source frames')
            if type(c.get('start_frame')) is not int or c['start_frame'] < 0:
                raise ValueError(f'{cid}: invalid timeline start')
            speed = c.get('speed', 1.0)
            if (isinstance(speed, bool) or not isinstance(speed, (int, float))
                    or not math.isfinite(speed) or speed <= 0):
                raise ValueError(f'{cid}: invalid speed')
            volume = c.get('volume', 1.0)
            if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not 0 <= volume <= 2:
                raise ValueError(f'{cid}: invalid volume')
            c['_duration'] = math.ceil(timeline_frames(project, src, inn, out) / speed)
            clips.setdefault(tid, []).append(c)
    for tid, rows in clips.items():
        ordered = sorted(rows, key=lambda c: c['start_frame'])
        for left, right in zip(ordered, ordered[1:]):
            if left['start_frame'] + left['_duration'] > right['start_frame']:
                raise ValueError(f'overlap on track {tid}: {left["id"]}/{right["id"]}')
    result = copy.deepcopy(project)
    for track in result['tracks']:
        for c in track['clips']:
            c.pop('_duration', None)
    return result


def _clip(project, clip_id):
    if not isinstance(clip_id, str):
        raise ValueError('clip_id required')
    for track in project['tracks']:
        for c in track['clips']:
            if c['id'] == clip_id:
                return track, c
    raise ValueError(f'clip not found: {clip_id}')


def _source(project, clip):
    return project['sources'][clip['source']]['path']


def _base_frames(project):
    for track in project['tracks']:
        if track['kind'] == 'video' and track['clips']:
            return project['sources'][track['clips'][0]['source']]['frames']
    return next(iter(project['sources'].values()))['frames']


def _base_source(project):
    for track in project['tracks']:
        if track['kind'] == 'video' and track['clips']:
            return _source(project, track['clips'][0])
    return next(iter(project['sources'].values()))['path']


def _output(params):
    value = params.get('output')
    if not isinstance(value, str) or not value or '\x00' in value:
        raise ValueError('output path required')
    return value


def _validate_base(project, params):
    if not isinstance(params, dict):
        raise ValueError('params object required')
    return params


def _trim(project, params):
    params = _validate_base(project, params)
    out = _output(params)
    track, c = _clip(project, params.get('clip_id'))
    if track['kind'] != 'video':
        raise ValueError('trim requires a video clip')
    if c.get('speed', 1.0) != 1.0:
        raise ValueError('speed != 1 requires the speed operation; trim blocks')
    fps = fps_value(tuple(project['fps']))
    frames = c['out_frame'] - c['in_frame']
    args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _source(project, c),
            '-ss', f'{c["in_frame"] / fps:.6f}', '-t', f'{frames / fps:.6f}',
            '-map', '0:v:0', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'medium',
            '-crf', '18', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
            '-y', '{output}']
    return {'operation': 'trim', 'inputs': [{'path': _source(project, c),
            'sha256': project['sources'][c['source']].get('sha256')}],
            'output': out, 'args': args, 'expected_frames': frames,
            'frame_tolerance': 0, 'warnings': ['re-encode for frame-accurate trim'],
            'limitations': ['audio/video duration may differ by container rounding']}


def _concat(project, params):
    params = _validate_base(project, params)
    out = _output(params)
    ids = params.get('clip_ids')
    if not isinstance(ids, list) or len(ids) < 2:
        raise ValueError('at least two clip_ids required')
    chosen = []
    for cid in ids:
        track, c = _clip(project, cid)
        if track['kind'] != 'video' or c.get('speed', 1.0) != 1.0:
            raise ValueError(f'{cid}: concat requires video clips at speed 1')
        chosen.append((track, c))
    sources, index = [], {}
    for _, c in chosen:
        if c['source'] not in index:
            index[c['source']] = len(sources)
            sources.append(c)
    fps = fps_value(tuple(project['fps']))
    filters, pairs = [], []
    for i, (_, c) in enumerate(chosen):
        j = index[c['source']]
        filters.append(f'[{j}:v]trim=start_frame={c["in_frame"]}:end_frame={c["out_frame"]},'
                       f'setpts=PTS-STARTPTS[v{i}]')
        filters.append(f'[{j}:a]atrim=start={c["in_frame"] / fps:.6f}:'
                       f'end={c["out_frame"] / fps:.6f},asetpts=PTS-STARTPTS[a{i}]')
        pairs.append(f'[v{i}][a{i}]')
    filters.append(''.join(pairs) + f'concat=n={len(chosen)}:v=1:a=1[v][a]')
    args = ['ffmpeg', '-nostdin', '-v', 'error']
    for c in sources:
        args += ['-i', _source(project, c)]
    args += ['-filter_complex', ';'.join(filters), '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-c:a', 'aac',
             '-b:a', '192k', '-movflags', '+faststart', '-y', '{output}']
    return {'operation': 'concat', 'inputs': [{'path': _source(project, c),
            'sha256': project['sources'][c['source']].get('sha256')} for c in sources],
            'output': out, 'args': args,
            'expected_frames': sum(c['out_frame'] - c['in_frame'] for _, c in chosen),
            'frame_tolerance': 0, 'warnings': ['all clips must share codec/timebase'],
            'limitations': ['no transition; hard cuts only', 'audio required on every source']}


def _scale(project, params):
    params = _validate_base(project, params)
    w, h = _even(params.get('width'), 'width'), _even(params.get('height'), 'height')
    args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _base_source(project),
            '-vf', f'scale={w}:{h}:flags=lanczos,setsar=1', '-map', '0:v:0',
            '-map', '0:a?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k', '-y', '{output}']
    return {'operation': 'scale', 'inputs': [], 'output': _output(params), 'args': args,
            'expected_frames': _base_frames(project), 'frame_tolerance': 0,
            'warnings': ['changes frame geometry; verify safe areas'],
            'limitations': ['no automatic subject-aware crop']}


def _pad(project, params):
    params = _validate_base(project, params)
    w, h = _even(params.get('width'), 'width'), _even(params.get('height'), 'height')
    x, y = params.get('x'), params.get('y')
    if type(x) is not int or type(y) is not int or x < 0 or y < 0:
        raise ValueError('pad x/y must be nonnegative integers')
    if x + project['width'] > w or y + project['height'] > h:
        raise ValueError('pad must contain the source frame')
    color = params.get('color', 'black')
    if not isinstance(color, str) or not re.fullmatch(r'[A-Za-z0-9#]+', color):
        raise ValueError('invalid pad color')
    args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _base_source(project),
            '-vf', f'pad={w}:{h}:{x}:{y}:{color}', '-map', '0:v:0', '-map', '0:a?',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-c:a', 'aac',
            '-b:a', '192k', '-y', '{output}']
    return {'operation': 'pad', 'inputs': [], 'output': _output(params), 'args': args,
            'expected_frames': _base_frames(project), 'frame_tolerance': 0,
            'warnings': ['adds borders'], 'limitations': []}


def _crop(project, params):
    params = _validate_base(project, params)
    w, h = _even(params.get('width'), 'width'), _even(params.get('height'), 'height')
    x, y = params.get('x'), params.get('y')
    if type(x) is not int or type(y) is not int or x < 0 or y < 0:
        raise ValueError('crop x/y must be nonnegative integers')
    if x + w > project['width'] or y + h > project['height']:
        raise ValueError('crop outside source frame')
    args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _base_source(project),
            '-vf', f'crop={w}:{h}:{x}:{y}', '-map', '0:v:0', '-map', '0:a?',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-c:a', 'aac',
            '-b:a', '192k', '-y', '{output}']
    return {'operation': 'crop', 'inputs': [], 'output': _output(params), 'args': args,
            'expected_frames': _base_frames(project), 'frame_tolerance': 0,
            'warnings': ['changes framing; no automatic reframe'],
            'limitations': []}


def _extract_audio(project, params):
    params = _validate_base(project, params)
    args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _base_source(project),
            '-vn', '-ac', str(project['channels']), '-ar', str(project['sample_rate']),
            '-c:a', 'pcm_s16le', '-y', '{output}']
    return {'operation': 'extract_audio', 'media_type': 'audio', 'inputs': [],
            'output': _output(params), 'args': args, 'expected_frames': None,
            'frame_tolerance': 0, 'warnings': [], 'limitations': ['audio only']}


def _replace_audio(project, params):
    params = _validate_base(project, params)
    video, audio = params.get('video'), params.get('audio')
    if not isinstance(video, str) or not isinstance(audio, str) or not video or not audio:
        raise ValueError('video and audio inputs required')
    args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', video, '-i', audio,
            '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
            '-b:a', '192k', '-shortest', '-y', '{output}']
    return {'operation': 'replace_audio', 'inputs': [{'path': video}, {'path': audio}],
            'output': _output(params), 'args': args, 'expected_frames': None,
            'frame_tolerance': 0, 'warnings': ['audio must match video duration'],
            'limitations': ['no automatic alignment']}


def _mix_audio(project, params):
    params = _validate_base(project, params)
    rows = params.get('sources')
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError('at least two audio sources required')
    args = ['ffmpeg', '-nostdin', '-v', 'error']
    filters = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get('path'), str):
            raise ValueError('audio source path required')
        volume = row.get('volume', 1.0)
        if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not 0 <= volume <= 2:
            raise ValueError('invalid volume')
        args += ['-i', row['path']]
        filters.append(f'[{i}:a]volume={volume:.3f}[a{i}]')
    filters.append(''.join(f'[a{i}]' for i in range(len(rows)))
                   + f'amix=inputs={len(rows)}:duration=longest:normalize=0[a]')
    args += ['-filter_complex', ';'.join(filters), '-map', '[a]', '-c:a', 'aac',
             '-b:a', '192k', '-y', '{output}']
    return {'operation': 'mix_audio', 'inputs': rows, 'output': _output(params),
            'args': args, 'expected_frames': None, 'frame_tolerance': 0,
            'warnings': ['no automatic ducking'], 'limitations': ['sums tracks; clipping possible']}


def _subtitles(project, params):
    params = _validate_base(project, params)
    file = params.get('file')
    mode = params.get('mode')
    if mode not in ('burn', 'soft'):
        raise ValueError('mode must be burn or soft')
    if not isinstance(file, str) or not file:
        raise ValueError('subtitle file required')
    if "'" in file or ':' in file or '\n' in file or '\\' in file:
        raise ValueError('subtitle path quote/escape blocked')
    root = Path(project.get('root', '.'))
    target = _confined(root, file)
    if not target.is_file():
        raise ValueError('subtitle file missing')
    if mode == 'burn':
        args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _base_source(project),
                '-vf', f'subtitles={file}', '-map', '0:v:0', '-map', '0:a?',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-c:a', 'aac',
                '-b:a', '192k', '-y', '{output}']
        warnings = ['burned subtitles are irreversible']
        expected = _base_frames(project)
    else:
        args = ['ffmpeg', '-nostdin', '-v', 'error', '-i', _base_source(project),
                '-i', str(target), '-map', '0:v:0', '-map', '0:a?', '-map', '1:0',
                '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text', '-y', '{output}']
        warnings = ['soft subtitles require player support']
        expected = _base_frames(project)
    return {'operation': 'subtitles', 'inputs': [{'path': str(target),
            'sha256': file_hash(target)}], 'output': _output(params), 'args': args,
            'expected_frames': expected, 'frame_tolerance': 0,
            'warnings': warnings, 'limitations': ['timing not verified by this plan']}


def _remotion(project, params):
    params = _validate_base(project, params)
    from integrations import remotion_guard
    raw = params.get('project_path')
    if not isinstance(raw, str) or not raw:
        raise ValueError('remotion project_path required')
    project_path = Path(raw)
    if project_path.is_symlink() or not project_path.is_dir():
        raise ValueError('remotion project directory required')
    composition = params.get('composition_id')
    if not isinstance(composition, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', composition):
        raise ValueError('valid composition_id required')
    entry = params.get('entry_point', 'src/index.ts')
    if not isinstance(entry, str) or entry.startswith('/') or '..' in Path(entry).parts:
        raise ValueError('confined entry_point required')
    entry_path = project_path / entry
    if not entry_path.is_file() or entry_path.is_symlink():
        raise ValueError('remotion entry_point missing')
    props = params.get('props', {})
    if not isinstance(props, dict):
        raise ValueError('remotion props object required')
    try:
        encoded = canonical(props)
    except (TypeError, ValueError) as exc:
        raise ValueError('remotion props must be finite JSON') from exc
    license_ack = params.get('license_ack')
    render_approved = params.get('render_approved')
    if type(license_ack) is not bool or type(render_approved) is not bool:
        raise ValueError('license_ack and render_approved booleans required')
    try:
        scanned = remotion_guard.scan_project(str(project_path))
    except Exception as exc:
        raise ValueError(f'remotion project scan failed: {exc}') from exc
    found = {item['id']: item for item in scanned.get('compositions', [])}
    if composition not in found:
        raise ValueError(f'composition not found in local project: {composition}')
    expected = found[composition].get('duration_in_frames')
    if expected is None:
        expected = params.get('expected_frames')
    if expected is not None and (type(expected) is not int or expected <= 0):
        raise ValueError('expected_frames must be positive integer')
    args = ['npx', '--no-install', 'remotion', 'render', entry, composition,
            '{output}', '--props', encoded]
    package = project_path / 'package.json'
    if not package.is_file() or package.is_symlink():
        raise ValueError('remotion package.json required')
    return {'operation': 'remotion', 'backend': 'remotion',
            'inputs': [{'path': str(package), 'sha256': file_hash(package)},
                       {'path': str(entry_path), 'sha256': file_hash(entry_path)}],
            'output': _output(params), 'args': args,
            'expected_frames': expected, 'frame_tolerance': 0,
            'license_ack': license_ack, 'render_approved': render_approved,
            'remotion': {'project_path': str(project_path.resolve()),
                         'composition_id': composition, 'entry_point': entry,
                         'license': scanned.get('license'),
                         'compositions': sorted(found)},
            'warnings': ['Remotion License applies; visual quality not verified',
                         *scanned.get('warnings', [])],
            'limitations': ['scanner uses regex and does not compile TypeScript',
                            'props schema is not validated against the composition',
                            'render approval is a human decision, not quality approval']}


def _dub_missing(project, params):
    raise ValueError('dubbing adapter not registered; refusing to invent a voice')


def _advanced_planner(operation):
    def planner(project, params):
        from integrations import video_editor_advanced
        return getattr(video_editor_advanced, operation)(project, params)
    return planner


BUILTINS = {'trim': (_validate_base, _trim), 'concat': (_validate_base, _concat),
            'scale': (_validate_base, _scale), 'pad': (_validate_base, _pad),
            'crop': (_validate_base, _crop), 'extract_audio': (_validate_base, _extract_audio),
            'replace_audio': (_validate_base, _replace_audio),
            'mix_audio': (_validate_base, _mix_audio),
            'subtitles': (_validate_base, _subtitles),
            'remotion': (_validate_base, _remotion), 'dub': (_validate_base, _dub_missing)}
OPERATIONS = dict(BUILTINS)
for _operation in ('multitrack', 'transition', 'color_grade'):
    BUILTINS[_operation] = (_validate_base, _advanced_planner(_operation))
    OPERATIONS[_operation] = BUILTINS[_operation]


def register_operation(name, validate, planner):
    if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_]{1,40}', name):
        raise ValueError('invalid operation name')
    OPERATIONS[name] = (validate, planner)
    return name


def plan(project, operation, params):
    clean = validate_project(project)
    if operation not in OPERATIONS:
        raise ValueError(f'unknown operation: {operation}')
    validate, planner = OPERATIONS[operation]
    normalized = validate(clean, params)
    result = planner(clean, normalized)
    missing = PLAN_KEYS - set(result)
    if missing:
        raise ValueError(f'plan missing: {sorted(missing)}')
    if not isinstance(result['args'], list) or result['args'].count('{output}') != 1:
        raise ValueError('plan requires exactly one {output} placeholder')
    result.setdefault('backend', 'ffmpeg')
    result['plan_sha256'] = digest(result)
    return result


def probe_media(path, runner=None, *, allow_silent=False):
    runner = runner or subprocess.run
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError('regular media file required')
    proc = runner(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                   '-count_frames', '-of', 'json', str(p)],
                  capture_output=True, text=True, timeout=120)
    if getattr(proc, 'returncode', 0) != 0:
        raise ValueError('ffprobe failed')
    data = json.loads(proc.stdout or '{}')
    streams = data.get('streams') or []
    video = next((s for s in streams if s.get('codec_type') == 'video'
                  and not s.get('disposition', {}).get('attached_pic')), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    if video is None:
        raise ValueError('video stream required')
    if audio is None and not allow_silent:
        raise ValueError('audio stream required')
    rotation = 0
    for side in video.get('side_data_list', []) or []:
        if 'rotation' in side:
            rotation = int(side['rotation'])
    rotation = int(video.get('tags', {}).get('rotate', rotation)) % 360
    avg, r = video.get('avg_frame_rate') or '0/0', video.get('r_frame_rate') or '0/0'
    try:
        fps = parse_rational(avg)
    except ValueError:
        fps = parse_rational(r)
    vfr = avg not in ('0/0', r) and r not in ('0/0', avg)
    duration = float(data.get('format', {}).get('duration') or 0)
    nb = video.get('nb_frames')
    streams_duration = float(video.get('duration') or duration)
    frames = int(nb) if isinstance(nb, str) and nb.isdigit() else (
        int(video['nb_read_frames']) if str(video.get('nb_read_frames', '')).isdigit() else (
            int(round(streams_duration * fps_value(fps))) if streams_duration > 0 else 0))
    if frames <= 0:
        raise ValueError('video frame count could not be determined')
    width, height = int(video.get('width', 0)), int(video.get('height', 0))
    return {'path': str(p), 'sha256': file_hash(p), 'duration_seconds': duration,
            'format_name': data.get('format', {}).get('format_name'),
            'video': {'index': video.get('index'), 'codec': video.get('codec_name'),
                      'width': width, 'height': height, 'fps': f'{fps[0]}/{fps[1]}',
                       'r_fps': r, 'frames': frames, 'rotation': rotation,
                       'duration_seconds': float(video['duration']) if video.get('duration') else None,
                       'variable_frame_rate': vfr, 'pix_fmt': video.get('pix_fmt')},
            'audio': {'index': audio.get('index'), 'codec': audio.get('codec_name'),
                      'sample_rate': int(audio.get('sample_rate') or 0),
                       'channels': int(audio.get('channels') or 0),
                       'duration_seconds': float(audio['duration']) if audio.get('duration') else None}
                      if audio else None}


def _ffmpeg_preflight(plan):
    return None


def _remotion_preflight(plan):
    from integrations import remotion_guard
    if plan.get('license_ack') is not True:
        raise ValueError('Remotion license acknowledgement required')
    if plan.get('render_approved') is not True:
        raise ValueError('Remotion render approval required')
    policy = remotion_guard.command_policy(' '.join(plan['args']),
                                           render_approved=True, license_ack=True)
    if policy.get('decision') != 'allow':
        raise ValueError(f'Remotion policy blocked: {policy.get("reason")}')


BACKENDS = {'ffmpeg': _ffmpeg_preflight, 'remotion': _remotion_preflight}


def register_backend(name, preflight):
    if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_]{1,40}', name):
        raise ValueError('invalid backend name')
    if not callable(preflight):
        raise ValueError('backend preflight must be callable')
    BACKENDS[name] = preflight
    return name


def probe_audio(path, runner=None):
    runner = runner or subprocess.run
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError('regular audio file required')
    proc = runner(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                   '-of', 'json', str(p)], capture_output=True, text=True, timeout=120)
    if getattr(proc, 'returncode', 0) != 0:
        raise ValueError('ffprobe failed')
    data = json.loads(proc.stdout or '{}')
    audio = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
    if audio is None:
        raise ValueError('audio stream required')
    return {'path': str(p), 'sha256': file_hash(p),
            'duration_seconds': float(data.get('format', {}).get('duration') or 0),
            'audio': {'index': audio.get('index'), 'codec': audio.get('codec_name'),
                      'sample_rate': int(audio.get('sample_rate') or 0),
                      'channels': int(audio.get('channels') or 0)}}


def render(plan, runner=None, probe_fn=None, dry_run=False):
    runner = runner or subprocess.run
    probe_fn = probe_fn or probe_media
    backend = plan.get('backend', 'ffmpeg')
    preflight = BACKENDS.get(backend)
    if preflight is None:
        raise ValueError(f'unsupported render backend: {backend}')
    preflight(plan)
    advanced = plan.get('operation') in ('multitrack', 'transition', 'color_grade')
    if advanced:
        from integrations import video_editor_advanced
        video_editor_advanced.preflight(plan, inspect_media=not dry_run)
        probe_fn = lambda path: video_editor_advanced.verify_output(path, plan['advanced_contract'])
    if dry_run:
        return {'status': 'dry_run', 'backend': backend, 'args': plan['args'],
                'output': plan['output']}
    output = Path(plan['output'])
    receipt_path = Path(str(output) + '.receipt.json')
    if output.exists():
        if not receipt_path.is_file():
            raise FileExistsError(output)
        receipt = json.loads(receipt_path.read_text())
        if receipt.get('plan_sha256') != plan.get('plan_sha256'):
            raise ValueError('plan integrity mismatch')
        if receipt.get('output_sha256') != file_hash(output):
            raise ValueError('output integrity mismatch')
        return {'status': 'cached', 'output': str(output),
                 'sha256': receipt['output_sha256'], 'receipt': str(receipt_path)}
    if receipt_path.exists():
        raise FileExistsError('orphan receipt requires reconciliation: ' + str(receipt_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{output.name}.tmp-', suffix=output.suffix, dir=output.parent)
    os.close(fd)
    temp = Path(name)
    args = [str(temp) if a == '{output}' else a for a in plan['args']]
    try:
        proc = runner(args, capture_output=True, text=True, timeout=3600)
        if getattr(proc, 'returncode', 0) != 0:
            tail = (getattr(proc, 'stderr', '') or '')[-1200:]
            raise ValueError(f'ffmpeg failed: {tail}')
        if not temp.is_file():
            raise ValueError('render produced no output')
        if plan.get('media_type') == 'audio':
            info = probe_audio(temp)
        elif backend == 'remotion' and probe_fn is probe_media:
            # Composições visuais Remotion podem não ter áudio; o render é
            # validado por frames e streams de vídeo, sem inventar áudio.
            info = probe_media(temp, allow_silent=True)
        else:
            info = probe_fn(temp)
        expected = plan.get('expected_frames')
        if expected is not None:
            actual = (info.get('video') or {}).get('frames')
            if type(actual) is not int or abs(actual - expected) > plan.get('frame_tolerance', 0):
                raise ValueError(f'frame count mismatch: expected {expected}, got {actual}')
        sha = file_hash(temp)
        if advanced:
            video_editor_advanced.preflight(plan, inspect_media=False)
        if receipt_path.exists():
            raise FileExistsError(receipt_path)
        if output.exists():
            raise FileExistsError(output)
        # Same-directory hard link is atomic and fails if another writer won.
        # Do not fall back to replace(), which could destroy that writer's file.
        os.link(temp, output)
    finally:
        if temp.exists():
            temp.unlink()
    probe_summary = {'duration_seconds': info.get('duration_seconds'),
                     'video': info.get('video'), 'audio': info.get('audio')}
    receipt = {'schema_version': 1, 'status': 'rendered_pending_review',
               'backend': backend, 'media_type': plan.get('media_type', 'video'),
               'plan_sha256': plan['plan_sha256'], 'output': str(output),
               'output_sha256': sha, 'bytes': output.stat().st_size,
               'expected_frames': plan.get('expected_frames'),
               'frame_tolerance': plan.get('frame_tolerance', 0),
               'probe': probe_summary, 'audiovisual_approved': False,
                'limitations': ['technical render only; content, voice and lip sync '
                                'remain unapproved']}
    if advanced:
        receipt.update(info['technical_checks'])
    with receipt_path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return {'status': 'rendered', 'output': str(output), 'sha256': sha,
            'receipt': str(receipt_path)}


def dumps_project(project):
    return json.dumps(validate_project(project), ensure_ascii=False, indent=2) + '\n'


def load_project(text):
    try:
        data = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError('project JSON invalid') from exc
    return validate_project(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('probe')
    p.add_argument('source')
    p.add_argument('--out', required=True)
    p.add_argument('--allow-silent', action='store_true')
    p = sub.add_parser('plan')
    p.add_argument('project')
    p.add_argument('operation')
    p.add_argument('params')
    p.add_argument('--out', required=True)
    p = sub.add_parser('render')
    p.add_argument('plan')
    p.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    if args.command == 'probe':
        info = probe_media(args.source, allow_silent=args.allow_silent)
        Path(args.out).write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': 'probed', 'out': args.out,
                          'frames': info['video']['frames']}))
        return 0
    if args.command == 'plan':
        project = load_project(Path(args.project).read_text())
        params = json.loads(Path(args.params).read_text())
        result = plan(project, args.operation, params)
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'status': 'planned', 'out': args.out,
                          'plan_sha256': result['plan_sha256']}))
        return 0
    result = render(json.loads(Path(args.plan).read_text()), dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
