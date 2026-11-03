"""Build documentary index from actual local receipts; no audiovisual claims."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def candidate(name, source_ids, code, model, cpu, decision):
    return dict(name=name, source_ids=source_ids, code_license=code,
                model_license=model, cpu_status=cpu, decision=decision,
                benchmark_executed_this_round=False)


def main():
    index = json.loads((BASE / "source-index.json").read_text())
    successful = {item["id"]: item for item in index if "sha256" in item}
    local = json.loads((BASE / "local-inventory.json").read_text())
    playlist = json.loads((BASE / "playlist-metadata.json").read_text())
    candidates = [
        candidate("Manim Community", ["manim-repo", "manim-readme"], "MIT", "not_applicable", "Cairo software renderer; no benchmark in this machine", "recommend_2d_pilot"),
        candidate("Remotion", ["remotion-repo", "remotion-license", "remotion-transitions"], "Remotion License; eligibility and version must be checked", "not_applicable", "software rendering possible for 2D; no new render", "reuse_existing_project_with_approval"),
        candidate("FFmpeg", ["ffmpeg-filters", "ffmpeg-legal"], "LGPL/GPL depending on build and enabled components", "not_applicable", "CPU filters and software encoding; no new render", "recommend_assembly"),
        candidate("faster-whisper", ["faster-whisper-repo", "faster-whisper-readme", "whisper-model-license"], "MIT", "official OpenAI Whisper MIT; third-party conversions require separate audit", "CPU int8 documented", "benchmark_small_multilingual"),
        candidate("whisper.cpp", ["whisper-cpp-repo", "whisper-cpp-readme", "whisper-model-license"], "MIT", "official OpenAI Whisper MIT; specific converted artifact pending", "CPU-only and quantization documented", "benchmark_as_alternative"),
        candidate("pyannote.audio", ["pyannote-repo", "pyannote-readme", "whisperx-readme"], "MIT", "Community-1 card returned 401; WhisperX mentions CC-BY-4.0 but direct terms/acceptance pending", "local inference configurable; CPU performance unmeasured", "conditional_hf_acceptance_and_pilot"),
        candidate("WhisperX", ["whisperx-repo", "whisperx-readme", "whisperx-alignment-source"], "BSD-2-Clause in observed repository metadata", "ASR, alignment and diarization model licenses separate; selection pending", "--device cpu --compute_type int8 documented", "alignment_and_diarization_pilot"),
        candidate("Chatterbox PT-BR", ["chatterbox-repo", "chatterbox-readme-direct", "chatterbox-ptbr-model", "chatterbox-mtl-source"], "MIT", "MIT declared by PT-BR model card; companion assets and exact versions pending", "CPU path in generic loader; PT-BR t3_pt_br.safetensors and s3gen_v3.pt differ from loader s3gen.pt/ve.pt requirements; compatibility unproven", "compare_only_after_correct_v3_loader_smoke_and_individual_consent"),
        candidate("XTTS v2", ["coqui-repo", "xtts-model", "xtts-license"], "MPL-2.0", "Coqui Public Model License; non-commercial restrictions", "historical CPU usage only; no new multivoice benchmark", "noncommercial_baseline_subject_to_rights"),
        candidate("Piper", ["piper-repo", "piper-readme", "piper-voices"], "GPL-3.0", "per-voice MODEL_CARD; no individual voice approved here", "local ONNX synthesis; no measured speed", "licensed_synthetic_voice_fallback_not_cloning"),
        candidate("audio-separator", ["audio-separator-repo", "audio-separator-readme"], "MIT", "model-specific; no checkpoint selected", "CPU mode documented; quality and processing cost unknown", "fallback_if_no_music_effects_stem"),
        candidate("SoniTranslate", ["sonitranslate-repo", "sonitranslate-readme"], "Apache-2.0", "each TTS/diarization/conversion model has separate terms", "--cpu_mode documented, no end-to-end test", "integrated_pipeline_reference"),
        candidate("pyVideoTrans", ["pyvideotrans-official-repo", "pyvideotrans-official-readme"], "GPL-3.0; provider terms remain separate", "local and remote backends have separate terms", "CPU-dependent backend selection; no smoke test", "optional_interface_no_remote_services_without_permission"),
        candidate("VideoLingo", ["videolingo-repo", "videolingo-readme"], "Apache-2.0", "models and external providers separate", "Linux documented path GPU-oriented; CPU-only pipeline not demonstrated here", "not_first_choice_for_this_cpu"),
        candidate("OpenVoice V2", ["openvoice-repo", "openvoice-readme"], "MIT", "V1/V2 declared MIT; Portuguese base voice would need separate license", "CPU path not benchmarked; no native Portuguese in six-language list", "not_standalone_ptbr_solution"),
        candidate("MuseTalk", ["musetalk-repo", "musetalk-readme"], "GitHub NOASSERTION; exact terms must be audited", "checkpoints/dependencies require separate review", "GPU demonstrations do not prove CPU feasibility", "defer_cpu_lipsync"),
        candidate("LatentSync", ["latentsync-repo", "latentsync-readme"], "Apache-2.0", "weights and dependencies require separate review", "GPU-oriented; no CPU benchmark", "defer_cpu_lipsync"),
        candidate("stable-ts", ["stable-ts-repo", "stable-ts-readme"], "MIT", "selected ASR model license separate", "CPU options depend on backend; repository archived in observed metadata", "not_new_primary_dependency"),
        candidate("Argos Translate", ["argos-repo"], "MIT declared in repository metadata", "specific language package license pending", "offline translation candidate; full README retrieval failed and language pair unverified", "partial_evidence_not_recommended_for_drama_without_validation"),
    ]
    data = {
        "spec_id": "SPEC-935-R1033", "scope": "documentary_research_only",
        "actions": {k: False for k in ("installed", "downloaded_playlist_media", "cloned_new_voices", "rendered", "published")},
        "hardware": {"cpu": "Intel Core i5-1035G1", "physical_cores": 4, "logical_cpus": 8, "wsl_memory_gib_rounded": 11, "gpu_queried_or_used": False},
        "playlist": {"id": "PL2dcm-6042EC788TGxgH3qWF7MjpoJIv9", "title": playlist["title"], "announced_entries": playlist["announced_count"], "enumerated_entries": playlist["enumerated_count"], "complete_inventory": False, "total_duration_seconds": None, "speaker_count": None, "speaker_consent": "not_provided_for_playlist", "rights_verified": False, "source_ids": ["playlist-page"]},
        "sources": list(successful.values()), "candidates": candidates,
        "local_inventory": local["files"], "zip_skills": local["zip_skills"],
        "failures": [{"stage": "source_request", **item} for item in index if "error" in item] + [
            {"stage": "websearch", "error": "HTTP 402; used direct official sources; no bypass"},
            {"stage": "collector_first_run", "error": "RemoteDisconnected escaped catch; recovered already saved bytes with explicit mtime provenance; added HTTPException handler"},
            {"stage": "path_search", "error": "mcp directory absent; found actual integration in integrations/ecosystem_mcp.py"},
            {"stage": "external_workflow", "workflow_id": "r1033-video-cpu-research", "error": "spec_id_required at preflight, zero inference steps; not resumed"},
            {"stage": "native_review_researcher", "session_id": "ses_e62a98124ffeiygzWacPNlJIpT", "error": "active OpenCode Go subscription required; no review produced"},
            {"stage": "native_review_code_reviewer", "session_id": "ses_e62a81801ffeLSqOsIH8WThmYn", "error": "active OpenCode Go subscription required; no review produced"},
            {"stage": "strict_tdd_history", "run_id": "tdd-dabee2c010744c0987b8d76c003f94dd", "error": "180s shell timeout; only spec/test snapshots found, no pytest raw.log or accepted receipt. Plain pytest RED then GREEN captured separately; not retried"},
        ],
        "review": {"independent_status": "textual_readonly_completed", "task_id": "task-1ed85850", "text_spec_id": "TSPEC-094f2d73", "executor": "antigravity", "duration_seconds": 124.75087544298731, "human_audiovisual_review": "not_performed", "quality_certified": False, "summary": "review-summary.md"},
        "historical_lipsync": {"source_log": "/home/marceloclaro/.cache/opencode-pilot/lipsync-cards/middle-whole/run.log", "source_lines": [1,112,113], "audio_seconds": 20, "inference_wall_seconds": 1413, "rtf": 1413/20, "linear_extrapolation_45_minutes_hours": (1413/20)*45/60, "is_new_benchmark": False, "forecast_guaranteed": False},
    }
    (BASE / "evidence.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"sources":len(data["sources"]),"candidates":len(candidates),"local_files":len(local["files"]),"failures":len(data["failures"])},ensure_ascii=False))


if __name__ == "__main__":
    main()
