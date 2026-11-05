"""Adaptadores Core-native para skills externas, sem copiar código de terceiros.

O registro descreve licença, caminho, dependências e entrypoint de cada skill.
`status` é somente leitura; `plan` prepara um comando/entrega sem executar;
`probe` usa o REA em escopo reduzido e grava a evidência fora do repositório.

Nenhum adapter executa OAuth, coletor, render ou comando de terceiro sem
consentimento explícito; a execução real continua sob o orquestrador.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".cache" / "opencode-pilot" / "external-skills"
STATUS_TTL_SECONDS = 15.0
_STATUS_CACHE: dict[str, tuple[float, dict]] = {}
REA_CANDIDATES = (
    Path.home() / ".local/share/opencode-core/rea-6.8.0/scripts/rea.mjs",
    Path.home() / ".local/share/opencode-core/rea/scripts/rea.mjs",
)


@dataclass(frozen=True)
class ExternalSkill:
    skill_id: str
    path: Path
    license: str
    kind: str
    entrypoint: str
    dependencies: tuple[str, ...] = ()
    requires_consent: bool = False
    license_file: str = "LICENSE"
    rea_sources: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    safe_argv: tuple[str, ...] = ()
    readiness_argv: tuple[str, ...] = ()
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "path": str(self.path),
            "license": self.license,
            "kind": self.kind,
            "entrypoint": self.entrypoint,
            "dependencies": list(self.dependencies),
            "requires_consent": self.requires_consent,
            "license_file": self.license_file,
            "rea_sources": list(self.rea_sources),
            "prerequisites": list(self.prerequisites),
            "keywords": list(self.keywords),
            "safe_argv": list(self.safe_argv),
            "readiness_argv": list(self.readiness_argv),
            "notes": self.notes,
        }


def _expand(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def load_registry() -> Dict[str, ExternalSkill]:
    """Registro explícito; não descobre nem instala nada sozinho."""
    entries = (
        ExternalSkill(
            skill_id="archify",
            path=_expand("~/.agents/skills/archify"),
            license="Apache-2.0",
            kind="diagram-skill",
            entrypoint="bin/archify.mjs",
            dependencies=("node",),
            rea_sources=("bin/archify.mjs",),
            keywords=("diagrama", "diagramas", "arquitetura", "fluxo", "erd", "html"),
            notes="Diagramas HTML interativos; doctor e render são os entrypoints seguros.",
        ),
        ExternalSkill(
            skill_id="imagegen",
            path=_expand("~/.agents/skills/imagegen"),
            license="Core-native",
            license_file="",
            kind="image-generation",
            entrypoint="scripts/image_gen.py",
            dependencies=("python3",),
            requires_consent=True,
            keywords=("imagem", "geracao", "gerar", "imagegen", "ilustracao", "comic", "personagem"),
            safe_argv=("python3", str(_expand("~/.agents/skills/imagegen") / "scripts/image_gen.py"), "--help"),
            notes="Gera imagem via endpoint OpenAI-compatible; consome conta e exige OPENAI_API_KEY.",
        ),
        ExternalSkill(
            skill_id="code-video-visual-qa",
            path=_expand(ROOT / ".opencode/skills/code-video-visual-qa"),
            license="Core-native",
            license_file="",
            kind="video-qa",
            entrypoint="SKILL.md",
            dependencies=("python3", "ffmpeg", "ffprobe"),
            keywords=("qa", "legendas", "silencio", "loudness", "quadros", "qualidade", "revisao"),
            safe_argv=("python3", str(ROOT / "integrations/video_qa.py"), "--help"),
            notes="QA técnico de MP4: metadados, black frames, silêncio, loudness e frames.",
        ),
        ExternalSkill(
            skill_id="hyperframes",
            path=_expand("~/.agents/skills/hyperframes"),
            license="Apache-2.0",
            license_file="",
            kind="video-skill",
            entrypoint="SKILL.md",
            dependencies=("node", "ffmpeg"),
            keywords=("video", "hyperframes", "render", "renderizar", "animacao", "motion", "html"),
            notes="Skill oficial HyperFrames; usar hyperframes-cli para scaffold e render.",
        ),
        ExternalSkill(
            skill_id="image-story-video-wizard",
            path=_expand("~/.agents/skills/image-story-video-wizard"),
            license="MIT",
            kind="state-machine-skill",
            entrypoint="scripts/project_state.py",
            dependencies=("python3",),
            keywords=("imagem", "historia", "narracao", "video", "audio"),
            notes="Máquina de estados de 16 fases; não renderiza sozinha.",
        ),
        ExternalSkill(
            skill_id="hbg-life-simulation",
            path=_expand("~/.cache/opencode-pilot/external-evals/hbg-life-simulation"),
            license="MIT",
            kind="video-pipeline",
            entrypoint="scripts/setup_local_cliproxyapi.sh",
            dependencies=("node", "ffmpeg", "ffprobe"),
            requires_consent=True,
            prerequisites=("hyperframes", "media-use", "code-video-visual-qa", "imagegen"),
            keywords=("video", "narracao", "tts", "legendas", "hyperframes", "hyper", "frames"),
            readiness_argv=("bash", "scripts/setup_local_cliproxyapi.sh", "ready"),
            notes="Exige skills /hyperframes, /media-use, /code-video-visual-qa, /imagegen e proxy local.",
        ),
        ExternalSkill(
            skill_id="opus-video-skills",
            path=_expand("~/.cache/opencode-pilot/external-evals/opus-video-skills"),
            license="MIT",
            kind="video-skill-collection",
            entrypoint="skills/kinetic-reel/template/render.mjs",
            dependencies=("node", "ffmpeg", "google-chrome"),
            rea_sources=("skills/kinetic-reel/template/render.mjs",),
            keywords=("video", "animacao", "p5", "three", "reel", "motion"),
            notes="p5.js/three.js; usa Chrome/Chromium do cache Playwright e ffmpeg.",
        ),
        ExternalSkill(
            skill_id="reel-video",
            path=_expand("~/.local/share/opencode-core/reel-video"),
            license="MIT",
            kind="external-video-tool",
            entrypoint="bin/canvas.js",
            dependencies=("node", "ffmpeg"),
            requires_consent=True,
            rea_sources=("src/cli.ts", "src/still-motion.ts"),
            keywords=("video", "storyboard", "keyframes", "reel", "still-motion", "motion"),
            safe_argv=("node", "--import", "tsx", "--input-type=module", "-e",
                       "await import('./src/still-motion.ts'); await import('./src/runner.ts');"),
            notes="Grok opcional; provider still-motion usa ffmpeg; Codex opcional para stills.",
        ),
        ExternalSkill(
            skill_id="distilly",
            path=_expand("~/.cache/opencode-pilot/external-evals/distilly"),
            license="MIT",
            kind="person-profile-skill",
            entrypoint="bin/distilly.mjs",
            dependencies=("python3",),
            requires_consent=True,
            rea_sources=("bin/distilly.mjs",),
            keywords=("perfil", "pessoa", "voz", "consentimento"),
            notes="Perfis de pessoa exigem consentimento, privacidade e direito de exclusão.",
        ),
        ExternalSkill(
            skill_id="kdense-scientific-agent-skills",
            path=_expand(ROOT / "external/kdense-scientific-agent-skills"),
            license="MIT",
            kind="catalog",
            entrypoint="CATALOG.json",
            dependencies=(),
            license_file="LICENSE.md",
            keywords=("ciencia", "pesquisa", "dados", "laboratorio"),
            notes="Catálogo espelhado de 177 SKILL.md, sem scripts vendorizados.",
        ),
    )
    return {entry.skill_id: entry for entry in entries}


def _dependency_available(name: str) -> bool:
    if name == "codex":
        if shutil.which("codex"):
            return True
        return (Path.home() / ".local/share/opencode-core/codex-cli/"
                "node_modules/.bin/codex").is_file()
    if name == "google-chrome":
        if any(shutil.which(candidate) for candidate in
               ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")):
            return True
        for pattern in (".cache/ms-playwright/chromium-*/chrome-linux64/chrome",
                        ".cache/puppeteer/chrome/*/chrome-linux64/chrome"):
            if any(path.is_file() for path in Path.home().glob(pattern)):
                return True
        return False
    return shutil.which(name) is not None


def _skill_available(name: str) -> bool:
    candidates = (
        Path.home() / ".agents" / "skills" / name / "SKILL.md",
        Path.home() / ".config" / "opencode" / "skills" / name / "SKILL.md",
        ROOT / ".opencode" / "skills" / name / "SKILL.md",
        Path.home() / ".codex" / "skills" / ".system" / name / "SKILL.md",
    )
    return any(candidate.is_file() for candidate in candidates)


def _commit(path: Path) -> str | None:
    if not (path / ".git").exists() or not shutil.which("git"):
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=3, shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and len(commit) in (40, 64) else None


def _readiness(entry: ExternalSkill) -> Dict[str, Any] | None:
    """Executa somente um check read-only declarado, com cwd do adaptador."""
    if not entry.readiness_argv:
        return None
    argv = [str(part) for part in entry.readiness_argv]
    if not argv or any("\x00" in part for part in argv):
        return {"state": "invalid", "ready": False, "returncode": None}
    try:
        result = subprocess.run(argv, cwd=str(entry.path), capture_output=True,
                                text=True, timeout=20, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"state": "check_failed", "ready": False, "returncode": None,
                "error": type(exc).__name__}
    output = (result.stdout or "").strip().splitlines()
    state = output[-1].strip() if output else ""
    return {"state": state, "ready": state == "ready",
            "returncode": result.returncode}


def _registry_fingerprint(registry: Dict[str, ExternalSkill]) -> str:
    payload = {key: entry.to_dict() for key, entry in sorted(registry.items())}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def status(skill_id: str | None = None,
           registry: Dict[str, ExternalSkill] | None = None,
           *, refresh: bool = False) -> Dict[str, Any]:
    """Checagem somente leitura de caminho, licença, entrypoint e dependências.

    O resultado é cacheado por 15 s para evitar repetir git/subprocessos no
    caminho de cada passo do Centro de Produção. ``refresh=True`` força nova
    leitura (por exemplo, após iniciar o proxy local).
    """
    registry = registry or load_registry()
    if skill_id is not None:
        if skill_id not in registry:
            raise ValueError(f"skill externa desconhecida: {skill_id}")
        registry = {skill_id: registry[skill_id]}
    cache_key = _registry_fingerprint(registry)
    if not refresh:
        cached = _STATUS_CACHE.get(cache_key)
        if cached is not None and time.monotonic() - cached[0] < STATUS_TTL_SECONDS:
            return copy.deepcopy(cached[1])
    rows = []
    for key, entry in sorted(registry.items()):
        missing: List[str] = []
        if not entry.path.is_dir():
            missing.append("path_missing")
        if not (entry.path / entry.entrypoint).exists():
            missing.append("entrypoint_missing")
        if entry.license_file and not (entry.path / entry.license_file).is_file():
            missing.append("license_missing")
        missing.extend(f"dependency_missing:{name}" for name in entry.dependencies
                       if not _dependency_available(name))
        missing.extend(f"prerequisite_missing:{name}" for name in entry.prerequisites
                       if not _skill_available(name))
        readiness = _readiness(entry)
        if readiness is not None and not readiness.get("ready"):
            missing.append("readiness:" + str(readiness.get("state", "unknown")))
        rows.append({
            **entry.to_dict(),
            "ready": not missing,
            "status": "ready" if not missing else "blocked",
            "missing": missing,
            "readiness": readiness,
            "commit": _commit(entry.path),
            "consent_required": entry.requires_consent,
        })
    payload = {"status": "completed", "count": len(rows), "adapters": rows,
               "read_only": True, "executed": False}
    _STATUS_CACHE[cache_key] = (time.monotonic(), copy.deepcopy(payload))
    return payload


def _find(skill_id: str, registry: Dict[str, ExternalSkill]) -> ExternalSkill:
    if not isinstance(skill_id, str) or skill_id not in registry:
        raise ValueError(f"skill externa desconhecida: {skill_id}")
    return registry[skill_id]


def plan(skill_id: str, task: str, *, consent: bool = False,
         registry: Dict[str, ExternalSkill] | None = None) -> Dict[str, Any]:
    """Prepara handoff/argv sem executar. Nunca cria consentimento."""
    if not isinstance(task, str) or not task.strip():
        raise ValueError("a tarefa deve conter texto não vazio")
    registry = registry or load_registry()
    entry = _find(skill_id, registry)
    current = status(skill_id, registry)["adapters"][0]
    if not current["ready"]:
        return {"status": "blocked", "adapter": skill_id,
                "missing": current["missing"], "executed": False}
    base = entry.path
    if entry.safe_argv:
        safe_argv = [str(part) for part in entry.safe_argv]
    elif skill_id == "archify":
        safe_argv = ["node", str(base / "bin/archify.mjs"), "doctor"]
    elif skill_id == "image-story-video-wizard":
        safe_argv = ["python3", str(base / "scripts/project_state.py"), "--help"]
    elif skill_id == "hbg-life-simulation":
        safe_argv = ["bash", str(base / "scripts/setup_local_cliproxyapi.sh"), "ready"]
    else:
        safe_argv = []
    if entry.requires_consent and consent is not True:
        return {"status": "consent_required", "adapter": skill_id,
                "reason": "a skill exige consentimento explícito para esta operação",
                "cwd": str(base), "safe_argv": safe_argv,
                "safe_checks": bool(safe_argv), "executed": False}
    if skill_id == "archify":
        mode = "skill"
        argv = ["node", str(base / "bin/archify.mjs"), "doctor"]
        handoff = ("Carregar ~/.agents/skills/archify/SKILL.md e executar a tarefa "
                   f"com o renderer Archify; tarefa: {task[:500]}")
    elif skill_id == "imagegen":
        mode = "skill"
        argv = ["python3", str(base / "scripts/image_gen.py"), "--help"]
        handoff = ("Carregar a skill imagegen e gerar a imagem com OPENAI_API_KEY/"
                   f"OPENAI_BASE_URL já configurados; tarefa: {task[:500]}")
    elif skill_id == "code-video-visual-qa":
        mode = "cli"
        argv = ["python3", str(ROOT / "integrations/video_qa.py"), "probe", "<video>"]
        handoff = ("Rodar python3 integrations/video_qa.py probe no MP4 final e "
                   f"inspecionar os frames; tarefa: {task[:500]}")
    elif skill_id == "hyperframes":
        mode = "skill"
        argv = []
        handoff = ("Carregar a skill hyperframes e o hyperframes-cli; criar projeto "
                   f"com scaffold, validar e renderizar; tarefa: {task[:500]}")
    elif skill_id == "image-story-video-wizard":
        mode = "skill"
        argv = ["python3", str(base / "scripts/project_state.py"), "--help"]
        handoff = ("Carregar ~/.agents/skills/image-story-video-wizard/SKILL.md e "
                   f"iniciar o estado do projeto; tarefa: {task[:500]}")
    elif skill_id == "hbg-life-simulation":
        mode = "skill"
        argv = ["bash", str(base / "scripts/setup_local_cliproxyapi.sh"), "ready"]
        handoff = ("Ler SKILL.md, rodar apenas o check read-only `ready` e pedir "
                   "consentimento antes de proxy/OAuth/render")
    elif skill_id == "opus-video-skills":
        mode = "skill"
        argv = ["node", str(base / "skills/kinetic-reel/template/render.mjs")]
        handoff = ("Carregar a skill kinetic-reel ou painted-animation; criar projeto "
                   "com o template e renderizar somente após validar Chrome/ffmpeg")
    elif skill_id == "reel-video":
        mode = "cli"
        argv = ["node", str(base / "bin/canvas.js")]
        handoff = ("Usar o CLI local do reel-video com --video-provider still-motion "
                   "para motion determinístico; Grok é opcional e Codex é opcional "
                   "para stills; consentimento para workspace-write")
    elif skill_id == "distilly":
        mode = "skill"
        argv = ["node", str(base / "bin/distilly.mjs")]
        handoff = ("Carregar SKILL.md e exigir consentimento verificável antes de "
                   "criar qualquer perfil de pessoa")
    else:
        mode = "catalog"
        argv = []
        handoff = "Consultar o catálogo local, sem executar scripts."
    return {
        "status": "planned", "adapter": skill_id, "mode": mode,
        "task": task[:1000], "cwd": str(base), "argv": argv, "handoff": handoff,
        "safe_argv": safe_argv, "safe_checks": bool(safe_argv),
        "license": entry.license, "commit": current.get("commit"),
        "requires_consent": entry.requires_consent,
        "gates": ["license_preserved", "path_within_adapter", "no_shell"],
        "executed": False,
        "limitations": ["plano não é execução", "dependências externas podem consumir conta"],
    }


def _rea_launcher() -> Path | None:
    for candidate in REA_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def probe(skill_id: str, *, timeout: int = 90,
          registry: Dict[str, ExternalSkill] | None = None) -> Dict[str, Any]:
    """Analisa fontes JS/TS selecionadas com o REA, em escopo reduzido."""
    if type(timeout) is not int or not 10 <= timeout <= 180:
        raise ValueError("timeout deve estar entre 10 e 180 segundos")
    registry = registry or load_registry()
    entry = _find(skill_id, registry)
    if not entry.rea_sources:
        return {"status": "unsupported", "adapter": skill_id,
                "reason": "adapter não declara fontes JS/TS para o REA", "executed": False}
    launcher = _rea_launcher()
    if launcher is None:
        return {"status": "blocked", "adapter": skill_id,
                "reason": "REA não instalado", "executed": False}
    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    token = hashlib.sha256(f"{skill_id}:{time.time_ns()}".encode()).hexdigest()[:12]
    summary_path = CACHE / f"{skill_id}-{stamp}-{token}.json"
    evidence_path = CACHE / f"{skill_id}-{stamp}-{token}.evidence.json"
    argv = [shutil.which("node") or "node", str(launcher),
            "analyze-javascript-application", str(entry.path),
            "--detail", "summary", "--evidence_output", str(evidence_path),
            "--analysis-timeout-ms", str(timeout * 1000), "--format", "json"]
    for source in entry.rea_sources:
        argv.extend(["--source-path", source])
    try:
        with summary_path.open("w", encoding="utf-8") as stream:
            result = subprocess.run(argv, stdout=stream, stderr=subprocess.PIPE,
                                    text=True, timeout=timeout + 15, shell=False,
                                    cwd=str(entry.path))
    except subprocess.TimeoutExpired:
        return {"status": "blocked", "adapter": skill_id,
                "reason": "REA excedeu o tempo limite", "executed": False}
    except OSError as exc:
        return {"status": "blocked", "adapter": skill_id,
                "reason": f"falha ao iniciar REA: {type(exc).__name__}", "executed": False}
    if result.returncode != 0:
        return {"status": "blocked", "adapter": skill_id,
                "reason": "REA retornou erro", "returncode": result.returncode,
                "stderr": (result.stderr or "")[-2000:], "executed": False}
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "blocked", "adapter": skill_id,
                "reason": f"resumo REA inválido: {type(exc).__name__}", "executed": False}
    summary = payload.get("summary") if isinstance(payload, dict) else None
    if not isinstance(summary, dict):
        summary = payload if isinstance(payload, dict) else {}
    normalized = summary.get("normalized_result")
    if not isinstance(normalized, dict):
        normalized = {}
    return {
        "status": "completed", "adapter": skill_id,
        "summary_path": str(summary_path),
        "evidence_path": str(evidence_path) if evidence_path.is_file() else None,
        "evidence_sha256": (hashlib.sha256(evidence_path.read_bytes()).hexdigest()
                            if evidence_path.is_file() else None),
        "evidence_id": summary.get("evidence_id"),
        "subject": summary.get("subject"),
        "coverage": normalized.get("coverage"),
        "limitations": (summary.get("limitations") or normalized.get("limitations")),
        "executed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="external-skills", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    status_cmd = sub.add_parser("status")
    status_cmd.add_argument("skill_id", nargs="?")
    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("skill_id")
    plan_cmd.add_argument("--task", required=True)
    plan_cmd.add_argument("--consent", action="store_true")
    probe_cmd = sub.add_parser("probe")
    probe_cmd.add_argument("skill_id")
    probe_cmd.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            payload = {"status": "completed",
                       "adapters": list(load_registry())}
        elif args.command == "status":
            payload = status(args.skill_id)
        elif args.command == "plan":
            payload = plan(args.skill_id, args.task, consent=args.consent)
        else:
            payload = probe(args.skill_id, timeout=args.timeout)
    except (ValueError, OSError) as exc:
        payload = {"status": "blocked", "error": str(exc), "executed": False}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") in {"completed", "planned", "unsupported"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
