"""Runtime híbrido-nativo do Pesquisador Universal v4.2 dentro do Core."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys
from pathlib import Path
from typing import Iterable

BASELINE_CORE_COMMIT = "8af98945b35af0863b2bf3217651190d98516d8a"
EXTERNAL_BASELINE_CORE_COMMIT = "a5478054ceb8fc34eb0d254a30a3c451d6d864cd"
EXPECTED_EXTERNAL_VERSION = "4.1.0"
EXPECTED_PACKAGE_MANIFEST_SHA256 = "89786fcb9b461d0bffbbbaae962da69bb9ce03e2b4e56178ed2c36f15776b89e"
EXPECTED_SKILL_ARCHIVE_SHA256 = "a805894960e96b7d9aa153a0e8b73c08f5654eef8bb0289867902f9f9612bc78"
NATIVE_VERSION = "4.2.0-core.1"
NATIVE_COMMANDS = {"research", "articles", "review", "evidence"}
EXTERNAL_CONTROLLERS = {
    "mesh":"meshctl.py","mission":"missionctl.py","living":"livingctl.py",
    "synthesis":"synthesisctl.py","grade":"gradectl.py","causal":"causalctl.py",
    "federation":"federationctl.py","production":"productionctl.py",
}
REQUIRED_CORE = (
    "marceloclaro/orchestrator.py","mci/metabus.py","mci/blackboard.py",
    "transformer/attention.py","sdd/spec_engine.py","sdd/tdd_runner.py",
    "integrations/opencode_cli.py","rag/scientific.py","research/searchers.py",
    "research/downloader.py","scientific_lab/native/cli.py",
)
NATIVE_SCHEMAS = (
    "article-search-manifest.schema.json","article-download-receipt.schema.json",
    "systematic-review-protocol.schema.json","study-record.schema.json",
    "screening-decision.schema.json","prisma-flow.schema.json",
    "evidence-annotation.schema.json","evidence-graph.schema.json",
)

def _external_candidates() -> Iterable[Path]:
    explicit=os.environ.get("PESQUISADOR_UNIVERSAL_HOME")
    if explicit: yield Path(explicit).expanduser()
    prefix=os.environ.get("PU_PREFIX")
    if prefix: yield Path(prefix).expanduser()/"skill"
    yield Path.home()/".local/share/pesquisador-universal/skill"

def _valid_external(path: Path) -> bool:
    return path.is_dir() and (path/"SKILL.md").is_file() and (path/"VERSION.json").is_file() and (path/"scripts/validate_contracts.py").is_file()

def discover_external() -> Path|None:
    for candidate in _external_candidates():
        if _valid_external(candidate): return candidate.resolve()
    return None

def _git_head(checkout: Path) -> str|None:
    try: return subprocess.check_output(["git","-C",str(checkout),"rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return None

def _sha256(path: Path) -> str|None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def core_compatibility(checkout: Path) -> dict:
    checks=[{"check":rel,"status":"pass" if (checkout/rel).is_file() else "fail"} for rel in REQUIRED_CORE]
    return {"schema_version":"1.0","mode":"native_scientific_runtime_v4_2","baseline_core_commit":BASELINE_CORE_COMMIT,
            "observed_commit":_git_head(checkout),"checks":checks,"compatible":all(x["status"]=="pass" for x in checks),
            "epistemic_authority":"none"}

def native_status(checkout: Path) -> dict:
    schema_dir=checkout/"scientific_lab/schemas"
    missing=[name for name in NATIVE_SCHEMAS if not (schema_dir/name).is_file()]
    modules=["scientific_lab/native/research.py","scientific_lab/native/review.py","scientific_lab/native/evidence.py","scientific_lab/native/cli.py"]
    missing_modules=[rel for rel in modules if not (checkout/rel).is_file()]
    ready=not missing and not missing_modules
    return {"status":"ready" if ready else "incomplete","version":NATIVE_VERSION,
            "native_commands":sorted(NATIVE_COMMANDS),"schemas":len(NATIVE_SCHEMAS)-len(missing),
            "expected_schemas":len(NATIVE_SCHEMAS),"missing_schemas":missing,"missing_modules":missing_modules,
            "open_science_only":True,"automatic_epistemic_authority":False}

def external_status(home: Path|None=None) -> dict:
    path=home or discover_external()
    if path is None:
        return {"status":"not_installed","home":None,"version":None,"verified_release":False,
                "message":"Camada externa v4.1 não é necessária para research/review/evidence nativos; instale apenas para módulos avançados ainda externos."}
    try: data=json.loads((path/"VERSION.json").read_text(encoding="utf-8"))
    except Exception as exc: return {"status":"invalid","home":str(path),"version":None,"verified_release":False,"error":str(exc)}
    manifest_sha=_sha256(path/"PACKAGE_MANIFEST.sha256"); version=data.get("version")
    verified=version==EXPECTED_EXTERNAL_VERSION and manifest_sha==EXPECTED_PACKAGE_MANIFEST_SHA256
    return {"status":"installed_verified" if verified else "installed_unverified","home":str(path),"version":version,
            "edition":data.get("edition"),"package_manifest_sha256":manifest_sha,
            "expected_package_manifest_sha256":EXPECTED_PACKAGE_MANIFEST_SHA256,
            "expected_skill_archive_sha256":EXPECTED_SKILL_ARCHIVE_SHA256,"verified_release":verified}

def runtime_status(checkout: Path) -> dict:
    return {"runtime_version":NATIVE_VERSION,"architecture":"core_native_plus_optional_external_advanced",
            "core":core_compatibility(checkout),"native":native_status(checkout),"external_advanced":external_status(),
            "advanced_external_commands":sorted(EXTERNAL_CONTROLLERS),"primary_orchestrator":"marceloclaro",
            "automatic_epistemic_authority":False}

def dispatch(command: str, argv: list[str], checkout: Path|None=None, external_home: Path|None=None) -> int:
    if command in NATIVE_COMMANDS:
        from scientific_lab.native.cli import dispatch as native_dispatch
        return native_dispatch(command, argv)
    controller=EXTERNAL_CONTROLLERS.get(command)
    if controller is None:
        print(f"comando científico desconhecido: {command}",file=sys.stderr); return 2
    root=external_home or discover_external()
    status=external_status(root)
    if not status.get("verified_release"):
        print(json.dumps(status,ensure_ascii=False,indent=2),file=sys.stderr); return 5 if root else 4
    script=root/"scripts"/controller
    if not script.is_file(): print(f"controller externo ausente: {script}",file=sys.stderr); return 3
    return subprocess.call([sys.executable,str(script),*argv])
