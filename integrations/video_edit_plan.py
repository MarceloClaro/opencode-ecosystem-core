"""R1024 — validação de plano de edição de vídeo e conferência de render.

O módulo é somente leitura: não abre mídia, não executa ffprobe, não acessa a
rede e não renderiza. Ele verifica a coerência do plano e compara um relatório
de metadados produzido pelo usuário com o que foi planejado.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_PLAN_BYTES = 2 * 1024 * 1024
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

TOP_KEYS = {
    "schema_version", "project", "sources", "video", "audio", "captions",
    "output", "notes",
}
PROJECT_KEYS = {"id", "title", "fps", "width", "height", "sample_rate"}
SOURCE_KEYS = {"id", "path", "sha256", "duration_frames", "width", "height", "rights"}
CLIP_KEYS = {
    "id", "source", "in_frame", "out_frame", "timeline_start", "lane", "crop", "scale",
}
AUDIO_KEYS = {
    "id", "source", "in_frame", "out_frame", "timeline_start", "lane",
    "gain_db", "fade_in_frames", "fade_out_frames",
}
CAPTION_KEYS = {"id", "start_frame", "end_frame", "text", "lane", "max_cps"}
OUTPUT_KEYS = {"path", "container", "video_codec", "audio_codec", "loudness_lufs"}

RIGHTS = {
    "authorized", "public_domain", "cc_by", "cc_by_sa", "cc_by_nc_sa",
    "institutional_license",
}
CONTAINERS = {"mp4", "mov", "webm", "mkv"}
VIDEO_CODECS = {"h264", "hevc", "av1", "vp9", "prores"}
AUDIO_CODECS = {"aac", "opus", "pcm_s16le", "none"}
CONTAINER_VIDEO = {
    "mp4": {"h264", "hevc", "av1"},
    "mov": {"h264", "hevc", "prores"},
    "webm": {"vp9", "av1"},
    "mkv": {"h264", "hevc", "av1", "vp9", "prores"},
}
CONTAINER_AUDIO = {
    "mp4": {"aac", "none"},
    "mov": {"aac", "pcm_s16le", "none"},
    "webm": {"opus", "none"},
    "mkv": {"aac", "opus", "pcm_s16le", "none"},
}
EXTENSION = {"mp4": ".mp4", "mov": ".mov", "webm": ".webm", "mkv": ".mkv"}
CODEC_ALIASES = {
    "avc1": "h264", "h265": "hevc", "hev1": "hevc", "av01": "av1",
    "vp09": "vp9", "mp4a": "aac",
}
CONTAINER_ALIASES = {"matroska": "mkv"}


class PlanError(ValueError):
    """Falha de carga do arquivo, com código estável."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def _item(code: str, path: str, message: str = "") -> dict:
    return {"code": code, "path": path, "message": message or code}


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PlanError("invalid_json", "chave duplicada no JSON")
        result[key] = value
    return result


def _reject_constant(_value):
    raise PlanError("invalid_json", "NaN/Infinity não são aceitos")


def load_plan(path) -> dict:
    """Carrega JSON estrito de arquivo regular local, sem symlink e até 2 MiB."""
    target = Path(path)
    if target.is_symlink():
        raise PlanError("unsafe_file", "plano não pode ser symlink")
    try:
        stat = target.stat()
    except OSError as exc:
        raise PlanError("file_missing", str(exc)) from exc
    if not target.is_file():
        raise PlanError("file_missing", "plano deve ser arquivo regular")
    if stat.st_size > MAX_PLAN_BYTES:
        raise PlanError("file_too_large", f"plano excede {MAX_PLAN_BYTES} bytes")
    try:
        raw = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PlanError("invalid_encoding", str(exc)) from exc
    try:
        document = json.loads(
            raw,
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except PlanError:
        raise
    except (ValueError, TypeError) as exc:
        raise PlanError("invalid_json", str(exc)) from exc
    if not isinstance(document, dict):
        raise PlanError("invalid_json", "documento deve ser objeto JSON")
    return document


class _Validator:
    def __init__(self) -> None:
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def error(self, code: str, path: str, message: str = "") -> None:
        self.errors.append(_item(code, path, message))

    def warn(self, code: str, path: str, message: str = "") -> None:
        self.warnings.append(_item(code, path, message))

    def result(self) -> tuple[list[dict], list[dict]]:
        key = lambda item: (item["path"], item["code"])
        return sorted(self.errors, key=key), sorted(self.warnings, key=key)


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _keys(obj, allowed, path, v: _Validator) -> None:
    for key in obj:
        if key not in allowed:
            v.error("unknown_field", f"{path}.{key}", "campo não reconhecido")


def _identifier(value, path, v: _Validator, seen: set) -> str | None:
    if not _text(value) or not ID_RE.fullmatch(value):
        v.error("invalid_id", path, "id deve ser slug minúsculo")
        return None
    if value in seen:
        v.error("duplicate_id", path, f"id repetido: {value}")
        return None
    seen.add(value)
    return value


def _relative_path(value, path, v: _Validator) -> str | None:
    if not _text(value):
        v.error("missing_field", path, "caminho ausente")
        return None
    if (
        CONTROL_RE.search(value)
        or "\\" in value
        or value.startswith(("/", "~"))
    ):
        v.error("unsafe_path", path, "caminho deve ser relativo e simples")
        return None
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        v.error("unsafe_path", path, "caminho não pode conter vazio, '.' ou '..'")
        return None
    return value


def _int_field(obj, key, path, v: _Validator, minimum=None, maximum=None,
               required=True, default=None):
    if key not in obj:
        if required:
            v.error("missing_field", f"{path}.{key}", "campo obrigatório")
        return default
    value = obj[key]
    if not _is_int(value):
        v.error("invalid_type", f"{path}.{key}", "deve ser inteiro")
        return None
    if (minimum is not None and value < minimum) or (
        maximum is not None and value > maximum
    ):
        v.error("value_out_of_range", f"{path}.{key}", "valor fora do intervalo")
        return None
    return value


def _number_field(obj, key, path, v: _Validator, minimum=None, maximum=None,
                  required=True, default=None):
    if key not in obj:
        if required:
            v.error("missing_field", f"{path}.{key}", "campo obrigatório")
        return default
    value = obj[key]
    if not _is_number(value):
        v.error("invalid_type", f"{path}.{key}", "deve ser número")
        return None
    if (minimum is not None and value < minimum) or (
        maximum is not None and value > maximum
    ):
        v.error("value_out_of_range", f"{path}.{key}", "valor fora do intervalo")
        return None
    return float(value)


def _project(plan, v: _Validator, seen: set):
    path = "$.project"
    obj = plan.get("project")
    if not isinstance(obj, dict):
        v.error("missing_field", path, "projeto obrigatório")
        return None
    _keys(obj, PROJECT_KEYS, path, v)
    ident = _identifier(obj.get("id"), f"{path}.id", v, seen)
    title = obj.get("title")
    if not _text(title):
        v.error("missing_field", f"{path}.title", "título obrigatório")
    fps = _number_field(obj, "fps", path, v, 1, 240)
    width = _int_field(obj, "width", path, v, 16, 16384)
    height = _int_field(obj, "height", path, v, 16, 16384)
    sample_rate = _int_field(obj, "sample_rate", path, v, 8000, 192000,
                             required=False, default=48000)
    if width is not None and width % 2:
        v.warn("odd_dimensions", f"{path}.width", "largura ímpar pode falhar em codecs")
    if height is not None and height % 2:
        v.warn("odd_dimensions", f"{path}.height", "altura ímpar pode falhar em codecs")
    if ident is None or fps is None or width is None or height is None:
        return None
    return {
        "id": ident, "title": title.strip(), "fps": fps,
        "width": width, "height": height, "sample_rate": sample_rate,
    }


def _sources(plan, v: _Validator, seen: set):
    path = "$.sources"
    raw = plan.get("sources")
    if not isinstance(raw, list) or not raw:
        v.error("missing_field", path, "ao menos uma origem é obrigatória")
        return [], {}
    mapping: dict[str, dict] = {}
    order: list[str] = []
    for index, item in enumerate(raw):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            v.error("invalid_type", item_path, "origem deve ser objeto")
            continue
        _keys(item, SOURCE_KEYS, item_path, v)
        ident = _identifier(item.get("id"), f"{item_path}.id", v, seen)
        file_path = _relative_path(item.get("path"), f"{item_path}.path", v)
        digest = item.get("sha256")
        if digest is not None and (
            not isinstance(digest, str) or not SHA_RE.fullmatch(digest.lower())
        ):
            v.error("hash_invalid", f"{item_path}.sha256", "SHA-256 inválido")
            digest = None
        duration = _int_field(item, "duration_frames", item_path, v, 1, 10_000_000)
        width = _int_field(item, "width", item_path, v, 16, 16384)
        height = _int_field(item, "height", item_path, v, 16, 16384)
        rights = item.get("rights")
        if not isinstance(rights, str) or rights not in RIGHTS:
            v.error("rights_unresolved", f"{item_path}.rights", "direitos não resolvidos")
        if ident is None or file_path is None or duration is None:
            continue
        if width is None or height is None:
            continue
        mapping[ident] = {
            "id": ident, "path": file_path,
            "sha256": digest.lower() if isinstance(digest, str) else None,
            "duration_frames": duration, "width": width, "height": height,
            "rights": rights,
        }
        order.append(ident)
    return order, mapping


def _crop(value, source, path, v: _Validator):
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 4 or not all(_is_int(x) for x in value):
        v.error("invalid_crop", path, "crop deve ser [x, y, largura, altura] inteiro")
        return None
    x, y, width, height = value
    if width <= 0 or height <= 0 or x < 0 or y < 0:
        v.error("invalid_crop", path, "crop exige dimensões positivas e origem não negativa")
        return None
    if source and (x + width > source["width"] or y + height > source["height"]):
        v.error("crop_outside_source", path, "crop excede a origem")
        return None
    return [x, y, width, height]


def _scale(value, path, v: _Validator):
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2 or not all(_is_int(x) for x in value):
        v.error("invalid_scale", path, "escala deve ser [largura, altura] inteira")
        return None
    if value[0] <= 0 or value[1] <= 0:
        v.error("invalid_scale", path, "escala deve ser positiva")
        return None
    return list(value)


def _video(plan, v: _Validator, sources: dict, seen: set):
    path = "$.video"
    raw = plan.get("video")
    if not isinstance(raw, list) or not raw:
        v.error("missing_field", path, "ao menos um clipe é obrigatório")
        return 0, []
    clips: list[dict] = []
    for index, item in enumerate(raw):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            v.error("invalid_type", item_path, "clipe deve ser objeto")
            continue
        _keys(item, CLIP_KEYS, item_path, v)
        ident = _identifier(item.get("id"), f"{item_path}.id", v, seen)
        source_id = item.get("source")
        source = sources.get(source_id) if isinstance(source_id, str) else None
        if source is None:
            v.error("source_not_found", f"{item_path}.source", "origem inexistente")
        start_in = _int_field(item, "in_frame", item_path, v)
        end_in = _int_field(item, "out_frame", item_path, v)
        start = _int_field(item, "timeline_start", item_path, v, 0)
        lane = _int_field(item, "lane", item_path, v, 0, required=False, default=0)
        crop = _crop(item.get("crop"), source, f"{item_path}.crop", v)
        scale = _scale(item.get("scale"), f"{item_path}.scale", v)
        if source is not None and start_in is not None and end_in is not None:
            if start_in < 0 or end_in <= start_in or end_in > source["duration_frames"]:
                v.error("source_bounds", item_path, "corte fora da origem")
                continue
        if None in (ident, start_in, end_in, start, lane):
            continue
        clips.append({
            "index": index, "id": ident, "source": source_id,
            "in_frame": start_in, "out_frame": end_in,
            "timeline_start": start, "lane": lane,
            "crop": crop, "scale": scale,
            "end": start + (end_in - start_in),
        })
    by_lane: dict[int, list[dict]] = {}
    for clip in clips:
        by_lane.setdefault(clip["lane"], []).append(clip)
    for lane, items in by_lane.items():
        items.sort(key=lambda clip: (clip["timeline_start"], clip["id"]))
        previous_end = None
        for clip in items:
            if previous_end is not None and clip["timeline_start"] < previous_end:
                v.error(
                    "timeline_overlap", f"$.video[{clip['index']}]",
                    "clipe se sobrepõe na mesma faixa",
                )
            elif lane == 0 and previous_end is not None and clip["timeline_start"] > previous_end:
                v.warn(
                    "timeline_gap", f"$.video[{clip['index']}]",
                    "lacuna na faixa principal",
                )
            previous_end = clip["end"] if previous_end is None else max(previous_end, clip["end"])
    timeline = max((clip["end"] for clip in clips), default=0)
    return timeline, clips


def _audio(plan, v: _Validator, sources: dict, timeline: int, seen: set):
    raw = plan.get("audio", [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        v.error("invalid_type", "$.audio", "áudio deve ser lista")
        return []
    tracks: list[dict] = []
    for index, item in enumerate(raw):
        item_path = f"$.audio[{index}]"
        if not isinstance(item, dict):
            v.error("invalid_type", item_path, "faixa deve ser objeto")
            continue
        _keys(item, AUDIO_KEYS, item_path, v)
        ident = _identifier(item.get("id"), f"{item_path}.id", v, seen)
        source_id = item.get("source")
        source = sources.get(source_id) if isinstance(source_id, str) else None
        if source is None:
            v.error("source_not_found", f"{item_path}.source", "origem inexistente")
        start_in = _int_field(item, "in_frame", item_path, v)
        end_in = _int_field(item, "out_frame", item_path, v)
        start = _int_field(item, "timeline_start", item_path, v, 0)
        lane = _int_field(item, "lane", item_path, v, 0, required=False, default=0)
        gain = _number_field(item, "gain_db", item_path, v, -60, 24,
                             required=False, default=0.0)
        fade_in = _int_field(item, "fade_in_frames", item_path, v, 0,
                             required=False, default=0)
        fade_out = _int_field(item, "fade_out_frames", item_path, v, 0,
                              required=False, default=0)
        if source is not None and start_in is not None and end_in is not None:
            if start_in < 0 or end_in <= start_in or end_in > source["duration_frames"]:
                v.error("source_bounds", item_path, "áudio fora da origem")
                continue
        if None in (ident, start_in, end_in, start, lane, gain, fade_in, fade_out):
            continue
        duration = end_in - start_in
        if fade_in + fade_out > duration:
            v.error("fade_too_long", item_path, "fades excedem a duração")
            continue
        end = start + duration
        if timeline and end > timeline:
            v.warn("audio_beyond_video", item_path, "áudio ultrapassa o vídeo")
        tracks.append({
            "index": index, "id": ident, "source": source_id,
            "in_frame": start_in, "out_frame": end_in,
            "timeline_start": start, "lane": lane, "gain_db": gain,
            "fade_in_frames": fade_in, "fade_out_frames": fade_out, "end": end,
        })
    by_lane: dict[int, list[dict]] = {}
    for track in tracks:
        by_lane.setdefault(track["lane"], []).append(track)
    for lane, items in by_lane.items():
        items.sort(key=lambda track: (track["timeline_start"], track["id"]))
        previous_end = None
        for track in items:
            if previous_end is not None and track["timeline_start"] < previous_end:
                v.error(
                    "audio_overlap", f"$.audio[{track['index']}]",
                    "áudio se sobrepõe na mesma faixa",
                )
            previous_end = track["end"] if previous_end is None else max(previous_end, track["end"])
    return tracks


def _captions(plan, v: _Validator, timeline: int, fps, seen: set):
    raw = plan.get("captions", [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        v.error("invalid_type", "$.captions", "legendas devem ser lista")
        return []
    captions: list[dict] = []
    for index, item in enumerate(raw):
        item_path = f"$.captions[{index}]"
        if not isinstance(item, dict):
            v.error("invalid_type", item_path, "legenda deve ser objeto")
            continue
        _keys(item, CAPTION_KEYS, item_path, v)
        ident = _identifier(item.get("id"), f"{item_path}.id", v, seen)
        start = _int_field(item, "start_frame", item_path, v, 0)
        end = _int_field(item, "end_frame", item_path, v, 1)
        lane = _int_field(item, "lane", item_path, v, 0, required=False, default=0)
        max_cps = _number_field(item, "max_cps", item_path, v, 1, 40,
                                required=False, default=17.0)
        text = item.get("text")
        if not _text(text) or len(text) > 240 or CONTROL_RE.search(text):
            v.error("invalid_caption_text", f"{item_path}.text", "texto inválido")
            text = None
        if end is not None and timeline and end > timeline:
            v.error("caption_beyond_timeline", item_path, "legenda após o fim do vídeo")
        if None in (ident, start, end, lane, max_cps) or text is None:
            continue
        if end <= start:
            v.error("caption_duration_invalid", item_path, "fim deve ser maior que início")
            continue
        if fps:
            visible = sum(1 for char in text if not char.isspace())
            cps = visible / ((end - start) / fps)
            if cps > max_cps + 1e-9:
                v.error(
                    "caption_too_fast", item_path,
                    f"{cps:.1f} CPS acima do limite {max_cps:.1f}",
                )
        captions.append({
            "index": index, "id": ident, "start_frame": start, "end_frame": end,
            "text": text, "lane": lane, "max_cps": max_cps,
        })
    by_lane: dict[int, list[dict]] = {}
    for caption in captions:
        by_lane.setdefault(caption["lane"], []).append(caption)
    for lane, items in by_lane.items():
        items.sort(key=lambda caption: (caption["start_frame"], caption["id"]))
        previous_end = None
        for caption in items:
            if previous_end is not None and caption["start_frame"] < previous_end:
                v.error(
                    "caption_overlap", f"$.captions[{caption['index']}]",
                    "legenda se sobrepõe na mesma faixa",
                )
            previous_end = (
                caption["end_frame"] if previous_end is None
                else max(previous_end, caption["end_frame"])
            )
    return captions


def _output(plan, v: _Validator, source_paths: set):
    path = "$.output"
    obj = plan.get("output")
    if not isinstance(obj, dict):
        v.error("missing_field", path, "saída obrigatória")
        return None
    _keys(obj, OUTPUT_KEYS, path, v)
    file_path = _relative_path(obj.get("path"), f"{path}.path", v)
    container = obj.get("container")
    if not isinstance(container, str) or container not in CONTAINERS:
        v.error("invalid_container", f"{path}.container", "contêiner não suportado")
        container = None
    video_codec = obj.get("video_codec")
    if not isinstance(video_codec, str) or video_codec not in VIDEO_CODECS:
        v.error("invalid_video_codec", f"{path}.video_codec", "codec de vídeo não suportado")
        video_codec = None
    audio_codec = obj.get("audio_codec")
    if not isinstance(audio_codec, str) or audio_codec not in AUDIO_CODECS:
        v.error("invalid_audio_codec", f"{path}.audio_codec", "codec de áudio não suportado")
        audio_codec = None
    loudness = obj.get("loudness_lufs")
    if not _is_number(loudness):
        v.error("invalid_type", f"{path}.loudness_lufs", "loudness deve ser número")
        loudness = None
    elif not -24 <= loudness <= -9:
        v.error("loudness_out_of_range", f"{path}.loudness_lufs", "alvo fora de -24 a -9 LUFS")
        loudness = None
    if file_path is not None:
        if file_path in source_paths:
            v.error("output_overwrites_source", f"{path}.path", "saída sobrescreve origem")
        if container is not None:
            expected = EXTENSION[container]
            if Path(file_path).suffix.lower() != expected:
                v.error(
                    "container_extension_mismatch", f"{path}.path",
                    f"extensão deve ser {expected}",
                )
    if container and video_codec and video_codec not in CONTAINER_VIDEO[container]:
        v.error(
            "codec_container_incompatible", f"{path}.video_codec",
            f"{video_codec} não é compatível com {container}",
        )
    if container and audio_codec and audio_codec not in CONTAINER_AUDIO[container]:
        v.error(
            "codec_container_incompatible", f"{path}.audio_codec",
            f"{audio_codec} não é compatível com {container}",
        )
    if None in (file_path, container, video_codec, audio_codec, loudness):
        return None
    return {
        "path": file_path, "container": container,
        "video_codec": video_codec, "audio_codec": audio_codec,
        "loudness_lufs": loudness,
    }


def _canonical(project, sources, clips, tracks, captions, output):
    return {
        "schema_version": "1.0",
        "project": dict(project),
        "sources": [dict(sources[source_id]) for source_id in sources],
        "video": [
            {
                "id": clip["id"], "source": clip["source"],
                "in_frame": clip["in_frame"], "out_frame": clip["out_frame"],
                "timeline_start": clip["timeline_start"], "lane": clip["lane"],
                "crop": clip["crop"], "scale": clip["scale"],
            }
            for clip in clips
        ],
        "audio": [
            {
                "id": track["id"], "source": track["source"],
                "in_frame": track["in_frame"], "out_frame": track["out_frame"],
                "timeline_start": track["timeline_start"], "lane": track["lane"],
                "gain_db": track["gain_db"],
                "fade_in_frames": track["fade_in_frames"],
                "fade_out_frames": track["fade_out_frames"],
            }
            for track in tracks
        ],
        "captions": [
            {
                "id": caption["id"], "start_frame": caption["start_frame"],
                "end_frame": caption["end_frame"], "text": caption["text"],
                "lane": caption["lane"], "max_cps": caption["max_cps"],
            }
            for caption in captions
        ],
        "output": dict(output),
    }


def _digest(value) -> str:
    blob = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def validate_plan(plan) -> dict:
    """Valida o plano sem mutar a entrada e devolve erros, avisos e digest."""
    v = _Validator()
    if not isinstance(plan, dict):
        v.error("plan_not_object", "$", "plano deve ser objeto")
        errors, warnings = v.result()
        return {
            "status": "invalid", "errors": errors, "warnings": warnings,
            "summary": {}, "digest_sha256": None, "canonical_plan": None,
            "visual_quality_verified": False, "media_opened": False,
            "render_executed": False,
        }
    _keys(plan, TOP_KEYS, "$", v)
    if plan.get("schema_version") != "1.0":
        v.error("unsupported_schema", "$.schema_version", "schema_version deve ser 1.0")
    seen: set[str] = set()
    project = _project(plan, v, seen)
    source_order, sources = _sources(plan, v, seen)
    timeline, clips = _video(plan, v, sources, seen)
    tracks = _audio(plan, v, sources, timeline, seen)
    captions = _captions(plan, v, timeline, project["fps"] if project else None, seen)
    output = _output(plan, v, {item["path"] for item in sources.values()})
    if output and output["audio_codec"] == "none" and tracks:
        v.warn("audio_discarded", "$.output.audio_codec", "faixas de áudio não serão usadas")
    if clips and project and output:
        for clip in clips:
            crop = clip["crop"]
            if crop:
                crop_ratio = crop[2] / crop[3]
                output_ratio = project["width"] / project["height"]
                if abs(crop_ratio - output_ratio) > 0.01:
                    v.warn(
                        "aspect_mismatch", f"$.video[{clip['index']}].crop",
                        "crop e saída têm proporções diferentes",
                    )
    errors, warnings = v.result()
    status = "valid" if not errors else "invalid"
    summary = {
        "fps": project["fps"] if project else None,
        "timeline_frames": timeline,
        "duration_seconds": round(timeline / project["fps"], 6) if project and timeline else 0.0,
        "source_count": len(sources),
        "video_clips": len(clips),
        "audio_clips": len(tracks),
        "captions": len(captions),
        "output": output,
    }
    canonical = None
    digest = None
    if status == "valid" and project and output:
        canonical = _canonical(
            project,
            {source_id: sources[source_id] for source_id in source_order},
            clips, tracks, captions, output,
        )
        digest = _digest(canonical)
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
        "digest_sha256": digest,
        "canonical_plan": canonical,
        "visual_quality_verified": False,
        "media_opened": False,
        "render_executed": False,
    }


def compile_plan(plan) -> dict:
    """Valida e devolve a forma canônica usada para o digest."""
    return validate_plan(plan)


def _alias(value, mapping):
    if not isinstance(value, str) or not value.strip():
        return None
    lowered = value.strip().lower()
    return mapping.get(lowered, lowered)


def verify_render(plan, report) -> dict:
    """Confere metadados de um relatório do usuário; não abre o vídeo."""
    checked = validate_plan(plan)
    if checked["status"] != "valid":
        return {
            "status": "blocked",
            "reasons": [_item("plan_invalid", "$", "plano precisa ser válido")],
            "warnings": [],
            "render_verified": False,
            "visual_quality_verified": False,
            "metadata_only": True,
            "compared": {},
        }
    if not isinstance(report, dict):
        return {
            "status": "blocked",
            "reasons": [_item("report_not_object", "$", "relatório deve ser objeto")],
            "warnings": [],
            "render_verified": False,
            "visual_quality_verified": False,
            "metadata_only": True,
            "compared": {},
        }
    summary = checked["summary"]
    output = summary["output"]
    reasons: list[dict] = []
    warnings: list[dict] = []

    def compare_int(key, expected, code):
        value = report.get(key)
        if not _is_int(value) or value != expected:
            reasons.append(_item(code, f"$.{key}", f"esperado {expected}, recebido {value!r}"))

    compare_int(
        "width", checked["canonical_plan"]["project"]["width"],
        "render_width_mismatch",
    )
    compare_int(
        "height", checked["canonical_plan"]["project"]["height"],
        "render_height_mismatch",
    )

    fps = report.get("fps")
    if not _is_number(fps) or abs(float(fps) - summary["fps"]) > 0.01:
        reasons.append(_item("render_fps_mismatch", "$.fps", "fps divergente"))

    duration = report.get("duration_seconds")
    tolerance = 1.5 / summary["fps"]
    if not _is_number(duration) or abs(float(duration) - summary["duration_seconds"]) > tolerance:
        reasons.append(_item("render_duration_mismatch", "$.duration_seconds", "duração divergente"))

    if _alias(report.get("video_codec"), CODEC_ALIASES) != output["video_codec"]:
        reasons.append(_item("render_video_codec_mismatch", "$.video_codec", "codec de vídeo divergente"))
    if _alias(report.get("audio_codec"), CODEC_ALIASES) != output["audio_codec"]:
        reasons.append(_item("render_audio_codec_mismatch", "$.audio_codec", "codec de áudio divergente"))
    if _alias(report.get("container"), CONTAINER_ALIASES) != output["container"]:
        reasons.append(_item("render_container_mismatch", "$.container", "contêiner divergente"))

    loudness = report.get("loudness_lufs")
    if loudness is None:
        warnings.append(_item("loudness_not_measured", "$.loudness_lufs", "loudness não informado"))
    elif not _is_number(loudness) or abs(float(loudness) - output["loudness_lufs"]) > 2.0:
        reasons.append(_item("loudness_mismatch", "$.loudness_lufs", "loudness fora de ±2 LU"))

    return {
        "status": "render_metadata_matched" if not reasons else "blocked",
        "reasons": reasons,
        "warnings": warnings,
        "render_verified": not reasons,
        "visual_quality_verified": False,
        "metadata_only": True,
        "compared": {
            "width": report.get("width"), "height": report.get("height"),
            "fps": report.get("fps"), "duration_seconds": report.get("duration_seconds"),
            "video_codec": report.get("video_codec"),
            "audio_codec": report.get("audio_codec"),
            "container": report.get("container"),
        },
    }


def _emit(value) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="video-edit-plan",
        description="Valida plano de edição de vídeo e confere metadados de render (sem mídia).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="valida o plano")
    validate.add_argument("plan")
    compile_parser = sub.add_parser("compile", help="valida e imprime a forma canônica")
    compile_parser.add_argument("plan")
    verify = sub.add_parser("verify", help="compara metadados de render com o plano")
    verify.add_argument("plan")
    verify.add_argument("report")
    args = parser.parse_args(argv)
    try:
        plan = load_plan(args.plan)
        if args.command == "verify":
            report = load_plan(args.report)
            result = verify_render(plan, report)
        else:
            result = validate_plan(plan)
    except PlanError as exc:
        _emit({"status": "error", "code": exc.code, "error": str(exc),
               "actions_executed": []})
        return 1
    _emit(result)
    if args.command == "verify":
        return 0 if result["status"] == "render_metadata_matched" else 2
    return 0 if result["status"] == "valid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
