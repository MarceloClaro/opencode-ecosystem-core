"""R1037 fixtures are synthetic ASR records, not real transcriptions."""
import importlib.util
import json
import math
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'integrations/video_dialogue_timing.py'


def api():
    assert MODULE.is_file(), 'extrator de pausas ainda ausente'
    spec = importlib.util.spec_from_file_location('video_dialogue_timing', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def alignment(words, duration=10.0):
    return {'audio_sha256': '0' * 64, 'duration': duration, 'language': 'tr',
            'segments': [{'start': words[0]['start'] if words else 0,
                          'end': words[-1]['end'] if words else 0,
                          'text': 'fixture', 'words': words}]}


def test_gap_midpoint_and_frames():
    m = api()
    words = [{'start': 0, 'end': 1.0, 'text': 'a'}, {'start': 1.4, 'end': 2.0, 'text': 'b'},
             {'start': 3.0, 'end': 4.0, 'text': 'c'}]
    result = m.dialogue_pauses(alignment(words), fps='25/1', total_frames=250,
                               min_gap_seconds=0.25)
    assert result['pause_frames'] == [30, 63]
    assert result['gap_count'] == 2
    assert result['speech_intervals'][0] == [0.0, 1.0]


def test_short_gap_ignored():
    m = api()
    words = [{'start': 0, 'end': 1.0, 'text': 'a'}, {'start': 1.1, 'end': 2.0, 'text': 'b'}]
    result = m.dialogue_pauses(alignment(words), fps='25/1', total_frames=250,
                               min_gap_seconds=0.25)
    assert result['pause_frames'] == []


def test_overlap_merged():
    m = api()
    words = [{'start': 0, 'end': 1.0, 'text': 'a'}, {'start': 0.5, 'end': 1.5, 'text': 'b'},
             {'start': 2.0, 'end': 3.0, 'text': 'c'}]
    result = m.dialogue_pauses(alignment(words), fps='10/1', total_frames=100,
                               min_gap_seconds=0.25)
    assert result['pause_frames'] == [18]
    assert result['speech_intervals'] == [[0.0, 1.5], [2.0, 3.0]]


def test_segment_fallback_without_words():
    m = api()
    data = {'audio_sha256': '0' * 64, 'duration': 10.0, 'segments': [
        {'start': 0, 'end': 1, 'text': 'a'}, {'start': 2, 'end': 3, 'text': 'b'}]}
    result = m.dialogue_pauses(data, fps='10/1', total_frames=100, min_gap_seconds=0.25)
    assert result['pause_frames'] == [15]


@pytest.mark.parametrize('words', [
    [{'start': -1, 'end': 1, 'text': 'x'}],
    [{'start': 2, 'end': 1, 'text': 'x'}],
    [{'start': float('nan'), 'end': 1, 'text': 'x'}],
    [{'start': 0, 'end': 11, 'text': 'x'}],
    [{'start': 0, 'end': 1, 'text': ''}],
])
def test_bad_words_rejected(words):
    with pytest.raises(ValueError):
        api().dialogue_pauses(alignment(words), fps='25/1', total_frames=250)


def test_audio_hash_mismatch(tmp_path):
    m = api()
    audio = tmp_path / 'audio.wav'
    audio.write_bytes(b'fixture')
    data = alignment([{'start': 0, 'end': 1, 'text': 'a'}])
    data['audio_sha256'] = 'f' * 64
    with pytest.raises(ValueError, match='hash'):
        m.dialogue_pauses(data, fps='25/1', total_frames=250, audio=audio)


def test_empty_asr_is_valid_and_empty():
    m = api()
    result = m.dialogue_pauses({'audio_sha256': '0' * 64, 'duration': 10, 'segments': []},
                               fps='25/1', total_frames=250)
    assert result['pause_frames'] == [] and result['speech_intervals'] == []


def test_zero_duration_word_skipped_and_counted():
    m = api()
    words = [{'start': 0, 'end': 1, 'text': 'a'},
             {'start': 1.0, 'end': 1.0, 'text': 'degenerate'},
             {'start': 2, 'end': 3, 'text': 'b'}]
    result = m.dialogue_pauses(alignment(words), fps='10/1', total_frames=100,
                               min_gap_seconds=0.25)
    assert result['degenerate_words_skipped'] == 1
    assert result['pause_frames'] == [15]
    assert result['speech_intervals'] == [[0.0, 1.0], [2.0, 3.0]]


def test_fractional_fps_and_clamp():
    m = api()
    words = [{'start': 0, 'end': 1, 'text': 'a'}, {'start': 1.5, 'end': 9.99, 'text': 'b'}]
    result = m.dialogue_pauses(alignment(words), fps='30000/1001', total_frames=300,
                               min_gap_seconds=0.2, max_gap_seconds=5)
    assert result['pause_frames'] == sorted(set(result['pause_frames']))
    assert all(1 <= frame <= 299 for frame in result['pause_frames'])


def test_cli_no_overwrite(tmp_path):
    m = api()
    data = alignment([{'start': 0, 'end': 1, 'text': 'a'}, {'start': 2, 'end': 3, 'text': 'b'}])
    source = tmp_path / 'asr.json'
    source.write_text(json.dumps(data))
    out = tmp_path / 'pauses.json'
    args = ['--alignment', str(source), '--fps', '10/1', '--total-frames', '100',
            '--out', str(out)]
    m.main(args)
    assert json.loads(out.read_text())['pause_frames'] == [15]
    with pytest.raises(FileExistsError):
        m.main(args)


def test_total_frames_exceeds_video_duration_guard():
    m = api()
    with pytest.raises(ValueError, match='total_frames|duration'):
        m.dialogue_pauses(alignment([{'start': 0, 'end': 1, 'text': 'a'}]),
                          fps='25/1', total_frames=10)
