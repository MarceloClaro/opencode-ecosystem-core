"""CPU video control plane R1034; no implicit download, synthesis or upload.

Only ``transcribe`` imports faster-whisper. Caption exports require an
alignment tied to the exact final audio, not timestamps copied from a source.
This module does not claim automatic speaker identification or lip sync.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import textwrap
import time


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"invalid {name}: finite number required")
    return float(value)


def validate_turns(turns, speakers, duration):
    duration = _number(duration, "duration")
    if duration <= 0 or not isinstance(turns, list) or not turns:
        raise ValueError("nonempty turns and positive duration required")
    if not isinstance(speakers, dict) or not speakers:
        raise ValueError("speaker registry required")
    clean = []
    for turn in turns:
        if not isinstance(turn, dict):
            raise ValueError("turn must be an object")
        speaker = turn.get("speaker")
        if not isinstance(speaker, str) or speaker not in speakers:
            raise ValueError("unknown speaker")
        if not isinstance(speakers[speaker], dict):
            raise ValueError("speaker record must be an object")
        if speakers[speaker].get("consent_declared") is not True:
            raise ValueError(f"speaker {speaker}: consent not declared")
        start = _number(turn.get("start"), "start")
        end = _number(turn.get("end"), "end")
        if start < 0 or end <= start or end > duration + 0.001:
            raise ValueError("turn outside duration or reversed")
        clean.append({**turn, "start":start, "end":end})
    clean.sort(key=lambda item: (item["start"], item["end"]))
    ends = {}
    for turn in clean:
        if turn["start"] < ends.get(turn["speaker"], 0) - 0.001:
            raise ValueError("same speaker overlap requires manual review")
        ends[turn["speaker"]] = turn["end"]
    return clean


def validate_alignment(alignment, audio, speakers):
    if not isinstance(alignment, dict):
        raise ValueError("alignment must be an object")
    if alignment.get("language") != "pt-BR":
        raise ValueError("alignment must be approved pt-BR text")
    if alignment.get("audio_sha256") != sha256_file(audio):
        raise ValueError("final audio hash mismatch; realign after editing")
    words = validate_turns(alignment.get("words"), speakers, alignment.get("duration"))
    if abs(audio_duration(audio) - alignment["duration"]) > 0.1:
        raise ValueError("final audio duration mismatch")
    for word in words:
        if not isinstance(word.get("text"), str) or not word["text"].strip():
            raise ValueError("empty aligned word")
        if any(ord(c) < 32 and c not in "\n\t" for c in word["text"]):
            raise ValueError("control character in aligned word")
    return words


def _wrapped(words, width):
    text = " ".join(" ".join(word["text"].split()) for word in words)
    if any(len(token) > width for token in text.split()):
        raise ValueError("word longer than caption width; manual review required")
    return textwrap.wrap(text, width, break_long_words=False, break_on_hyphens=False)


def make_cues(words, max_chars=42, max_lines=2, max_duration=6.0, max_gap=0.65):
    if type(max_chars) is not int or max_chars < 8 or type(max_lines) is not int or max_lines < 1:
        raise ValueError("invalid caption layout")
    if _number(max_duration, "max_duration") <= 0 or _number(max_gap, "max_gap") < 0:
        raise ValueError("invalid caption timing limit")
    grouped = defaultdict(list)
    for word in words:
        grouped[word["speaker"]].append(dict(word))
    cues = []

    def emit(chunk, speaker):
        if not chunk:
            return
        start = min(w["start"] for w in chunk)
        end = max(w["end"] for w in chunk)
        text = "\n".join(_wrapped(chunk, max_chars))
        cps = len(text.replace("\n", " ")) / max(0.001, end - start)
        cues.append({"speaker": speaker, "start": start, "end": end, "text": text,
                     "words": chunk[:], "cps": round(cps, 2),
                     "review_required": cps > 17 or end - start > max_duration})

    for speaker, stream in grouped.items():
        stream.sort(key=lambda word: (word["start"], word["end"]))
        chunk = []
        for word in stream:
            if word["end"] <= word["start"] or word["start"] < 0:
                raise ValueError("invalid word timing")
            if chunk and word["start"] < chunk[-1]["end"] - 0.001:
                raise ValueError("same speaker word overlap requires manual review")
            proposed = chunk + [word]
            if chunk and (len(_wrapped(proposed, max_chars)) > max_lines
                          or word["end"] - chunk[0]["start"] > max_duration
                          or word["start"] - chunk[-1]["end"] > max_gap):
                emit(chunk, speaker)
                chunk = []
            chunk.append(word)
        emit(chunk, speaker)
    return sorted(cues, key=lambda cue: (cue["start"], cue["speaker"]))


def _timecode(value, ass=False, vtt=False):
    units = 100 if ass else 1000
    ticks = int(math.floor(_number(value, "timestamp") * units + 0.5))
    seconds, fraction = divmod(ticks, units)
    minutes, second = divmod(seconds, 60)
    hour, minute = divmod(minutes, 60)
    if ass:
        return f"{hour}:{minute:02}:{second:02}.{fraction:02}"
    return f"{hour:02}:{minute:02}:{second:02}{'.' if vtt else ','}{fraction:03}"


def _ass_literal(text):
    # Fullwidth literal delimiters avoid ASS override/escape injection.
    return text.replace("\\", "＼").replace("{", "｛").replace("}", "｝").replace("\n", "\\N")


def render_subtitles(cues):
    srt, vtt = [], ["WEBVTT\n"]
    ass = ["[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n",
           "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n",
           "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,80,80,60,1\n",
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"]
    speaker_ids = {s: i for i, s in enumerate(sorted({c["speaker"] for c in cues}))}
    # Give overlapping cues distinct lanes; reuse lane 0 outside overlaps.
    lane_ends = []
    for index, cue in enumerate(sorted(cues, key=lambda item: (item["start"], item["speaker"])), 1):
        begin = _number(cue["start"], "cue start")
        finish = _number(cue["end"], "cue end")
        if finish <= begin or begin < 0:
            raise ValueError("invalid cue timing")
        if _timecode(begin, ass=True) == _timecode(finish, ass=True):
            raise ValueError("cue collapses at ASS timestamp resolution; review required")
        if not isinstance(cue.get("text"), str):
            raise ValueError("cue text must be a string")
        lines = [line.strip() for line in cue["text"].splitlines() if line.strip()]
        literal = "\n".join(lines)
        if not literal or any(ord(c) < 32 and c != "\n" for c in literal):
            raise ValueError("empty cue or control character")
        safe_text = html.escape(literal, quote=False)
        start, end = _timecode(cue["start"]), _timecode(cue["end"])
        srt.append(f"{index}\n{start} --> {end}\n{safe_text}\n")
        label = f"speaker_{speaker_ids[cue['speaker']]+1}"
        vtt.append(f"{index}\n{_timecode(cue['start'], vtt=True)} --> {_timecode(cue['end'], vtt=True)}\n<v {label}>{safe_text}</v>\n")
        lane = next((i for i, finish in enumerate(lane_ends) if finish <= cue["start"]), len(lane_ends))
        if lane == len(lane_ends):
            lane_ends.append(cue["end"])
        else:
            lane_ends[lane] = cue["end"]
        margin = 60 + 115 * lane
        ass.append(f"Dialogue: {lane},{_timecode(cue['start'],ass=True)},{_timecode(cue['end'],ass=True)},Default,{label},0,0,{margin},,{_ass_literal(literal)}\n")
    return {"srt": "\n".join(srt), "vtt": "\n".join(vtt), "ass": "".join(ass)}


def _file_manifest(paths):
    return [{"path": str(Path(path).resolve()), "sha256": sha256_file(path),
             "bytes": Path(path).stat().st_size} for path in paths]


def stage_receipt(inputs, outputs, parameters, tool_version):
    if not inputs or not outputs or not tool_version:
        raise ValueError("inputs, outputs and tool version are mandatory")
    # Round-trip creates a detached snapshot and rejects NaN/non-JSON parameters.
    parameters = json.loads(json.dumps(parameters, sort_keys=True, allow_nan=False))
    return {"schema_version": 1, "status": "completed", "inputs": _file_manifest(inputs),
            "outputs": _file_manifest(outputs), "parameters": parameters, "tool_version": tool_version}


def can_resume(receipt, inputs, outputs, parameters, tool_version):
    try:
        return receipt == stage_receipt(inputs, outputs, parameters, tool_version)
    except (OSError, ValueError, TypeError):
        return False


def scene_timeline(durations, transition_frames):
    if not durations or type(transition_frames) is not int or transition_frames < 0:
        raise ValueError("invalid transition")
    if any(type(n) is not int or n < 1 or transition_frames >= n for n in durations):
        raise ValueError("transition must be shorter than every scene")
    if any(2 * transition_frames > n for n in durations[1:-1]):
        raise ValueError("middle scene cannot have simultaneous enter and exit transitions")
    scenes, start = [], 0
    for length in durations:
        scenes.append({"start":start, "end":start+length, "duration":length})
        start += length - transition_frames
    return {"scenes":scenes, "transition_frames":transition_frames,
            "total_frames":scenes[-1]["end"]}


def smooth_progress(frame, duration_frames):
    if type(duration_frames) is not int or duration_frames < 2:
        raise ValueError("at least two frames required")
    value = min(1.0, max(0.0, _number(frame, "frame") / (duration_frames - 1)))
    return value * value * (3.0 - 2.0 * value)


def _write_new(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def audio_duration(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                             "-show_entries", "stream=codec_type:format=duration", "-of", "json", str(path)],
                            capture_output=True, text=True, check=True, timeout=30)
    probe = json.loads(result.stdout)
    if not probe.get("streams"):
        raise ValueError("no audio stream")
    return float(probe["format"]["duration"])


def transcribe_cpu(audio, model_dir, output, language=None, *, cpu_threads=2, beam_size=3):
    if type(cpu_threads) is not int or not 1 <= cpu_threads <= 8:
        raise ValueError("cpu_threads must be an integer in [1, 8]")
    if type(beam_size) is not int or not 1 <= beam_size <= 5:
        raise ValueError("beam_size must be an integer in [1, 5]")
    path = Path(model_dir)
    if not path.is_dir() or not (path / "model.bin").is_file():
        raise ValueError("explicit cached CTranslate2 model directory required; no automatic download")
    if not (path / "config.json").is_file() or not (path / "tokenizer.json").is_file():
        raise ValueError("local model config.json and tokenizer.json are required")
    if Path(output).exists():
        raise FileExistsError(output)
    from faster_whisper import WhisperModel
    duration = audio_duration(audio)
    started = time.monotonic()
    model = WhisperModel(str(path), device="cpu", compute_type="int8", cpu_threads=cpu_threads,
                         num_workers=1, local_files_only=True)
    segments, info = model.transcribe(str(audio), language=language, word_timestamps=True,
                                     vad_filter=True, beam_size=beam_size, condition_on_previous_text=True)
    result = []
    for segment in segments:
        result.append({"start":segment.start,"end":segment.end,"text":segment.text,
                       "words":[{"start":w.start,"end":w.end,"text":w.word,"probability":w.probability} for w in (segment.words or [])]})
    data = {"audio_sha256":sha256_file(audio),"duration":duration,"language":info.language,
            "language_probability":info.language_probability,"segments":result,
            "wall_seconds":time.monotonic()-started,"device":"cpu","compute_type":"int8",
            "speaker_identification":"not_performed","translation":"not_performed"}
    _write_new(output,json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action",required=True)
    cmd = subs.add_parser("timeline")
    cmd.add_argument("--durations",type=int,nargs="+",required=True)
    cmd.add_argument("--transition",type=int,default=12)
    cmd = subs.add_parser("captions")
    cmd.add_argument("--alignment",required=True)
    cmd.add_argument("--audio",required=True)
    cmd.add_argument("--speakers",required=True)
    cmd.add_argument("--out",required=True)
    cmd = subs.add_parser("transcribe")
    cmd.add_argument("--audio",required=True)
    cmd.add_argument("--model-dir",required=True)
    cmd.add_argument("--out",required=True)
    cmd.add_argument("--language")
    cmd.add_argument("--cpu-threads",type=int,default=2)
    cmd.add_argument("--beam-size",type=int,default=3)
    args = parser.parse_args(argv)
    if args.action == "timeline":
        print(json.dumps(scene_timeline(args.durations,args.transition)))
    elif args.action == "transcribe":
        result=transcribe_cpu(args.audio,args.model_dir,args.out,args.language,
                              cpu_threads=args.cpu_threads,beam_size=args.beam_size)
        print(json.dumps({"segments":len(result["segments"]),"wall_seconds":result["wall_seconds"],"language":result["language"]}))
    else:
        alignment=json.loads(Path(args.alignment).read_text())
        speakers=json.loads(Path(args.speakers).read_text())
        words=validate_alignment(alignment,args.audio,speakers)
        cues=make_cues(words)
        folder=Path(args.out)
        names=[folder/f"captions.pt-BR.{ext}" for ext in ("srt","vtt","ass")]+[folder/"cues.json"]
        if any(p.exists() for p in names):
            raise FileExistsError("use a new output directory; existing exports preserved")
        for extension,content in render_subtitles(cues).items():
            _write_new(folder/f"captions.pt-BR.{extension}",content)
        _write_new(folder/"cues.json",json.dumps(cues,ensure_ascii=False,indent=2)+"\n")
        print(json.dumps({"cues":len(cues),"review_required":sum(c["review_required"] for c in cues)}))


if __name__ == "__main__":
    main()
