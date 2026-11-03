"""R1046: planejadores FFmpeg locais; não são um NLE completo ou selo de qualidade."""
from __future__ import annotations

from fractions import Fraction
import math
from pathlib import Path
import subprocess

from integrations import video_editor as ve

OPERATIONS = frozenset({'multitrack', 'transition', 'color_grade'})
EFFECTS = frozenset({'fade', 'dissolve', 'wipeleft', 'wiperight', 'wipeup',
                     'wipedown', 'slideleft', 'slideright', 'slideup', 'slidedown'})
PRESETS = frozenset({'ultrafast', 'superfast', 'veryfast', 'faster', 'fast',
                     'medium', 'slow', 'slower', 'veryslow'})
COLOR_RANGES = {'brightness': (-1, 1, 0), 'contrast': (0, 4, 1),
                'saturation': (0, 3, 1), 'gamma': (.1, 10, 1),
                **{k: (-1, 1, 0) for k in ('rs', 'gs', 'bs', 'rm', 'gm', 'bm', 'rh', 'gh', 'bh')}}


def quality_scope(passed):
    return {'technical_checks_passed': passed is True, 'audiovisual_approved': False,
            'translation_accuracy_verified': False, 'scientific_validity_verified': False,
            'evaluation_scope': 'geometry, decoded frames, fps, duration and audio format only',
            'requires_review': ['perceptual audiovisual review', 'bilingual source review',
                                'primary evidence and scientific methodology review']}


def _unknown(obj, allowed, label):
    if not isinstance(obj, dict) or set(obj) - set(allowed):
        raise ValueError(f'{label}: object with supported fields required')


def _number(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: finite number required')
    if not low <= value <= high:
        raise ValueError(f'{label}: range {low}..{high}')
    return value


def _fps(p):
    n, d = p['fps']
    if type(n) is not int or type(d) is not int or n <= 0 or d <= 0:
        raise ValueError('integer rational fps required')
    return Fraction(n, d)


def _sec(frames, p):
    return f'{float(Fraction(frames) / _fps(p)):.12f}'.rstrip('0').rstrip('.') or '0'


def _samples(frames, p):
    return round(Fraction(frames * p['sample_rate']) / _fps(p))


def _local(root, raw, *, exists=False):
    if not isinstance(raw, str) or not raw or '\x00' in raw or '\n' in raw:
        raise ValueError('local path required')
    root = Path(root).absolute()
    path = Path(raw)
    if path.is_absolute():
        try:
            path = path.relative_to(root)
        except ValueError as exc:
            raise ValueError('path escape blocked') from exc
    target = ve._confined(root, str(path))
    if exists and not target.is_file():
        raise ValueError('regular local source required')
    return target


def _context(p, params, allowed):
    _unknown(params, {'output', 'preset', *allowed}, 'params')
    preset = params.get('preset', 'medium')
    if not isinstance(preset, str) or preset not in PRESETS:
        raise ValueError('unsupported x264 preset')
    _fps(p)
    if p.get('channels') not in (1, 2) or type(p.get('channels')) is not int:
        raise ValueError('mono/stereo channels required')
    if not 8000 <= p['sample_rate'] <= 192000:
        raise ValueError('sample rate out of supported range')
    output = _local(p.get('root', '.'), params.get('output'))
    if output.suffix.lower() != '.mp4':
        raise ValueError('advanced output must be MP4')
    return output


def _clip(p, cid, *, video=True):
    track, clip = ve._clip(p, cid)
    if video and track['kind'] != 'video':
        raise ValueError('video clip required')
    _unknown(clip, {'id', 'track', 'source', 'in_frame', 'out_frame', 'start_frame',
                    'speed', 'volume', 'transform', 'color'}, 'clip')
    if clip.get('speed', 1) != 1:
        raise ValueError('advanced operations require speed=1')
    return clip


def _source_samples(frames, source_rate, sample_rate):
    return round(Fraction(frames * sample_rate) * source_rate.denominator
                 / source_rate.numerator)


def _sources(p, clips):
    """Valida fontes e registra conformidade de fps sem esconder a conversão."""
    inputs, indices, warnings = [], {}, []
    for c in clips:
        key = c['source']
        if key in indices:
            continue
        src = p['sources'][key]
        path = _local(p.get('root', '.'), src.get('path'), exists=True)
        if path.suffix.lower() not in {'.mp4', '.mov', '.mkv', '.webm', '.avi'}:
            raise ValueError('supported local video container required')
        # Older fixtures omitted the field; only an explicit VFR flag blocks.
        if src.get('variable_frame_rate') is True:
            raise ValueError('explicit CFR source required; VFR unsupported')
        rate_pair = ve.source_fps(p, src)
        rate = Fraction(*rate_pair)
        conformed = rate != _fps(p)
        if conformed:
            warnings.append(f'source {key} conformed from {rate_pair[0]}/{rate_pair[1]} '
                            f'to {p["fps"][0]}/{p["fps"][1]}; timeline duration rounds up')
        if type(src.get('has_audio')) is not bool:
            raise ValueError('explicit has_audio source metadata required; re-probe source')
        sha = src.get('sha256')
        if not isinstance(sha, str) or not ve.HEX.fullmatch(sha) or ve.file_hash(path) != sha:
            raise ValueError('source hash integrity mismatch')
        indices[key] = len(inputs)
        inputs.append({'path': str(path), 'sha256': sha, 'has_audio': src['has_audio'],
                       'source_fps': list(rate_pair),
                       'fps': list(p['fps']), 'frames': src['frames'],
                       'conformed_to_timeline': conformed})
    return inputs, indices, warnings



def _color(settings):
    _unknown(settings, {*COLOR_RANGES, 'preserve_lightness'}, 'color')
    for key, value in settings.items():
        if key == 'preserve_lightness':
            if type(value) is not bool:
                raise ValueError('color preserve_lightness must be boolean')
        else:
            low, high, _ = COLOR_RANGES[key]
            _number(value, low, high, key)
    eq = [f'{k}={settings.get(k, COLOR_RANGES[k][2]):.8g}'
          for k in ('brightness', 'contrast', 'saturation', 'gamma')]
    balance = [f'{k}={settings.get(k, 0):.8g}' for k in COLOR_RANGES
               if k not in ('brightness', 'contrast', 'saturation', 'gamma')]
    balance.append('pl=' + ('1' if settings.get('preserve_lightness', False) else '0'))
    return 'eq=' + ':'.join(eq) + ',colorbalance=' + ':'.join(balance)


def _transform(p, c):
    t = c.get('transform', {})
    _unknown(t, {'x', 'y', 'width', 'height', 'opacity', 'corner_radius'}, 'transform')
    w = ve._even(t.get('width', p['width']), 'width')
    h = ve._even(t.get('height', p['height']), 'height')
    x, y = t.get('x', 0), t.get('y', 0)
    if type(x) is not int or type(y) is not int or x < 0 or y < 0:
        raise ValueError('integer nonnegative transform position required')
    if x + w > p['width'] or y + h > p['height']:
        raise ValueError('transform outside output frame')
    opacity = _number(t.get('opacity', 1), 0, 1, 'opacity')
    radius = t.get('corner_radius', 0)
    if type(radius) is not int or radius < 0 or radius > min(w, h) // 2:
        raise ValueError('corner_radius must be a nonnegative integer no larger than half the box')
    return x, y, w, h, opacity, radius


def _video(p, c, index, label, *, place=False, color=None):
    if not place and c.get('transform'):
        raise ValueError('transform is only supported by multitrack')
    x, y, w, h, opacity, radius = (_transform(p, c) if place
                                   else (0, 0, p['width'], p['height'], 1, 0))
    rate = _fps(p)
    src = p['sources'][c['source']]
    length = ve.timeline_frames(p, src, c['in_frame'], c['out_frame'])
    chain = (f'[{index}:v:0]trim=start_frame={c["in_frame"]}:end_frame={c["out_frame"]},'
             f'setpts=PTS-STARTPTS,fps={rate.numerator}/{rate.denominator},'
             f'settb={rate.denominator}/{rate.numerator},'
             f'scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2,'
             f'pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p')
    grade = color if color is not None else c.get('color', {})
    if grade:
        chain += ',' + _color(grade)
    if place:
        if radius:
            # Máscara alfa de retângulo arredondado; preserva a opacidade.
            # As vírgulas internas precisam de escape no filtergraph.
            chain += (f",format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                      f"a='if(lte(hypot(max(0\\,abs(X-W/2)-(W/2-{radius}))\\,"
                      f"max(0\\,abs(Y-H/2)-(H/2-{radius})))\\,{radius})\\,"
                      f"alpha(X,Y)*{opacity:.8g}\\,0)'")
        elif opacity < 1:
            chain += f',format=rgba,colorchannelmixer=aa={opacity:.8g}'
    # A conformidade entre taxas pode gerar um frame a menos; clone no máximo
    # um segundo e corte exatamente no comprimento calculado da timeline.
    chain += (f',tpad=stop_mode=clone:stop_duration=1,trim=end_frame={length},'
              f'setpts=N')
    if place:
        chain += f'+{c["start_frame"]}'
    return chain + f'[{label}]', x, y



def _audio(p, c, index, label):
    src = p['sources'][c['source']]
    source_rate = Fraction(*ve.source_fps(p, src))
    length = ve.timeline_frames(p, src, c['in_frame'], c['out_frame'])
    samples = _samples(length, p)
    layout = 'stereo' if p['channels'] == 2 else 'mono'
    if src['has_audio']:
        chain = (f'[{index}:a:0]aresample={p["sample_rate"]},'
                 f'aformat=sample_fmts=fltp:channel_layouts={layout},'
                 f'atrim=start_sample={_source_samples(c["in_frame"], source_rate, p["sample_rate"])}:'
                 f'end_sample={_source_samples(c["out_frame"], source_rate, p["sample_rate"])},'
                 f'asetpts=PTS-STARTPTS,apad')
    else:
        chain = f'anullsrc=r={p["sample_rate"]}:cl={layout}'
    return chain + f',atrim=end_sample={samples},volume={c.get("volume", 1):.8g}[{label}]'



def _finish(p, op, output, inputs, graph, frames, warnings=None, *, preset='medium'):
    if preset not in PRESETS:
        raise ValueError('unsupported x264 preset')
    if str(output) in {row['path'] for row in inputs}:
        raise ValueError('output cannot replace a source')
    args = ['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-filter_complex_threads', '1']
    for row in inputs:
        args += ['-protocol_whitelist', 'file,pipe', '-i', row['path']]
    rate = _fps(p)
    args += ['-filter_complex', ';'.join(graph), '-map', '[vout]', '-map', '[aout]',
             '-c:v', 'libx264', '-threads', '2', '-preset', preset, '-crf', '18',
             '-pix_fmt', 'yuv420p', '-r', f'{rate.numerator}/{rate.denominator}',
             '-fps_mode', 'cfr', '-frames:v', str(frames), '-t', _sec(frames, p),
             '-c:a', 'aac', '-b:a', '192k', '-ar', str(p['sample_rate']),
             '-ac', str(p['channels']), '-movflags', '+faststart', '-y', '{output}']
    return {'operation': op, 'backend': 'ffmpeg', 'inputs': inputs, 'output': str(output),
            'args': args, 'expected_frames': frames, 'frame_tolerance': 0,
            'warnings': warnings or [],
            'encoding': {'video': 'libx264', 'preset': preset, 'crf': 18,
                         'audio': 'aac', 'audio_bitrate': '192k'},
            'limitations': ['CPU SDR 8-bit output; no HDR/ACES/LUT or automatic color matching',
                            'CFR and speed=1 only; no keyframes or arbitrary effects',
                            'technical output is not perceptual, linguistic or scientific approval'],
            'advanced_contract': {'version': 1, 'root': str(Path(p['root']).absolute()),
                                  'width': p['width'], 'height': p['height'],
                                  'fps': list(p['fps']), 'sample_rate': p['sample_rate'],
                                  'channels': p['channels'], 'frames': frames}}


def multitrack(p, params):
    output = _context(p, params, set())
    preset = params.get('preset', 'medium')
    videos, audios = [], []
    for t in p['tracks']:
        _unknown(t, {'id', 'kind', 'clips'}, 'track')
        if t['kind'] == 'subtitle' and t['clips']:
            raise ValueError('subtitle tracks require separate subtitles operation')
        for c in t['clips']:
            _clip(p, c['id'], video=False)
            if t['kind'] == 'video':
                videos.append(c)
            elif t['kind'] == 'audio':
                if c.get('transform') or c.get('color'):
                    raise ValueError('audio clip cannot have visual effects')
                audios.append(c)
    if not videos:
        raise ValueError('at least one video clip required')
    inputs, index, conform_warnings = _sources(p, videos + audios)
    lengths = {c['id']: ve.timeline_frames(p, p['sources'][c['source']],
                                           c['in_frame'], c['out_frame'])
               for c in videos + audios}
    frames = max(c['start_frame'] + lengths[c['id']] for c in videos + audios)
    rate = _fps(p)
    graph = [f'color=c=black:s={p["width"]}x{p["height"]}:r={rate}:d={_sec(frames,p)},'
             f'trim=end_frame={frames},settb={rate.denominator}/{rate.numerator},setpts=N[base0]']
    for i, c in enumerate(videos):
        chain, x, y = _video(p, c, index[c['source']], f'layer{i}', place=True)
        graph.append(chain)
        end = c['start_frame'] + lengths[c['id']]
        graph.append(f'[base{i}][layer{i}]overlay=x={x}:y={y}:eof_action=pass:repeatlast=0:'
                     f'format=auto:enable=\'gte(n,{c["start_frame"]})*lt(n,{end})\'[base{i+1}]')
    graph.append(f'[base{len(videos)}]trim=end_frame={frames},format=yuv420p[vout]')
    layout = 'stereo' if p['channels'] == 2 else 'mono'
    graph.append(f'anullsrc=r={p["sample_rate"]}:cl={layout},atrim=end_sample={_samples(frames,p)}[silence]')
    for i, c in enumerate(audios):
        if not p['sources'][c['source']]['has_audio']:
            raise ValueError('audio track references a silent source')
        graph.append(_audio(p, c, index[c['source']], f'raw{i}'))
        graph.append(f'[raw{i}]adelay={_samples(c["start_frame"],p)}S:all=1[a{i}]')
    graph.append('[silence]' + ''.join(f'[a{i}]' for i in range(len(audios))) +
                 f'amix=inputs={len(audios)+1}:duration=first:dropout_transition=0:normalize=0,'
                 f'alimiter=limit=0.95:level=0:latency=1,atrim=end_sample={_samples(frames,p)}[aout]')
    return _finish(p, 'multitrack', output, inputs, graph, frames,
                   ['last video track is on top; audio comes ONLY from explicit audio tracks',
                    'black/silence fill gaps; fixed limiter is not perceptual loudness mastering',
                    *conform_warnings], preset=preset)


def transition(p, params):
    output = _context(p, params, {'clip_ids', 'duration_frames', 'effect'})
    preset = params.get('preset', 'medium')
    ids = params.get('clip_ids')
    if not isinstance(ids, list) or len(ids) != 2 or ids[0] == ids[1]:
        raise ValueError('exactly two distinct clip_ids required')
    clips = [_clip(p, cid) for cid in ids]
    lengths = [ve.timeline_frames(p, p['sources'][c['source']],
                                  c['in_frame'], c['out_frame']) for c in clips]
    n = params.get('duration_frames')
    if type(n) is not int or n <= 0 or n >= min(lengths) or Fraction(n) / _fps(p) > 60:
        raise ValueError('duration_frames must be positive and shorter than both clips (max 60 s)')
    effect = params.get('effect', 'fade')
    if not isinstance(effect, str) or effect not in EFFECTS:
        raise ValueError('unsupported transition effect')
    inputs, indices, conform_warnings = _sources(p, clips)
    graph = []
    for i, c in enumerate(clips):
        graph.append(_video(p, c, indices[c['source']], f'v{i}')[0])
        graph.append(_audio(p, c, indices[c['source']], f'a{i}'))
    graph.append(f'[v0][v1]xfade=transition={effect}:duration={_sec(n,p)}:'
                 f'offset={_sec(lengths[0]-n,p)},format=yuv420p[vout]')
    graph.append(f'[a0][a1]acrossfade=ns={_samples(n,p)}:c1=tri:c2=tri[aout]')
    return _finish(p, 'transition', output, inputs, graph, sum(lengths)-n,
                   ['clip_ids define sequence; timeline start_frame ignored explicitly',
                    'transition overlaps footage and audio; silence substituted for missing audio',
                    *conform_warnings], preset=preset)


def color_grade(p, params):
    output = _context(p, params, {'clip_id', 'color'})
    preset = params.get('preset', 'medium')
    color = params.get('color')
    _color(color)
    c = _clip(p, params.get('clip_id'))
    inputs, indices, conform_warnings = _sources(p, [c])
    graph = [_video(p, c, indices[c['source']], 'vout', color=color)[0],
             _audio(p, c, indices[c['source']], 'aout')]
    length = ve.timeline_frames(p, p['sources'][c['source']],
                                c['in_frame'], c['out_frame'])
    return _finish(p, 'color_grade', output, inputs, graph, length,
                   ['parametric SDR correction, not calibrated color grading or white balance',
                    *conform_warnings], preset=preset)


def preflight(plan, *, inspect_media=False):
    expected = plan.get('plan_sha256')
    if ve.digest({k: v for k, v in plan.items() if k != 'plan_sha256'}) != expected:
        raise ValueError('plan hash integrity mismatch')
    contract = plan.get('advanced_contract')
    if not isinstance(contract, dict) or contract.get('version') != 1:
        raise ValueError('advanced contract required')
    root = contract['root']
    _local(root, plan['output'])
    for row in plan['inputs']:
        path = _local(root, row['path'], exists=True)
        if ve.file_hash(path) != row['sha256']:
            raise ValueError('source hash integrity mismatch')
        if inspect_media:
            def restricted_probe(argv, **kwargs):
                return subprocess.run([argv[0], '-protocol_whitelist', 'file,pipe',
                                       '-format_whitelist', 'mov,matroska,webm,avi',
                                       *argv[1:]], **kwargs)
            info = ve.probe_media(path, runner=restricted_probe, allow_silent=True)
            v = info['video']
            if (v['variable_frame_rate']
                    or Fraction(v['fps']) != Fraction(*row['source_fps'])
                    or v['frames'] != row['frames']
                    or bool(info['audio']) != row['has_audio']):
                raise ValueError('actual source metadata does not match plan; re-probe')


def verify_output(path, contract):
    info = ve.probe_media(path)
    p = subprocess.run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                        '-format_whitelist', 'mov,matroska,webm,avi',
                        '-select_streams', 'v:0', '-count_frames',
                        '-show_entries', 'stream=nb_read_frames', '-of', 'default=nw=1:nk=1', str(path)],
                       capture_output=True, text=True, timeout=3600)
    if p.returncode or not p.stdout.strip().isdigit():
        raise ValueError('decoded frame count unavailable')
    frames = int(p.stdout.strip())
    v, a = info['video'], info['audio']
    duration = float(Fraction(contract['frames']) / _fps(contract))
    tolerance = max(float(1 / _fps(contract)), 2048 / contract['sample_rate'])
    video_duration = v.get('duration_seconds')
    if (not isinstance(video_duration, (int, float)) or not math.isfinite(video_duration)
            or abs(video_duration - duration) > tolerance):
        raise ValueError('video stream duration contract mismatch')
    audio_duration = a.get('duration_seconds')
    if (not isinstance(audio_duration, (int, float)) or not math.isfinite(audio_duration)
            or abs(audio_duration - duration) > tolerance):
        raise ValueError('audio stream duration contract mismatch')
    if (frames != contract['frames'] or v['width'] != contract['width']
            or v['height'] != contract['height'] or Fraction(v['fps']) != _fps(contract)
            or a['sample_rate'] != contract['sample_rate'] or a['channels'] != contract['channels']
            or abs(info['duration_seconds'] - duration) > tolerance):
        raise ValueError('advanced output contract mismatch')
    info['video']['frames'] = frames
    info['technical_checks'] = {**quality_scope(True), 'decoded_frames': frames,
                                'duration_tolerance_seconds': tolerance}
    return info
