# -*- coding: utf-8 -*-
"""
Microsoft APM (Agent Package Manager) Integration — SPEC-935-R440
================================================================
Implementação nativa do padrão Microsoft APM (https://github.com/microsoft/apm)
para o OpenCode Ecosystem Core.

Primitivas Canônicas do APM gerenciadas:
1. Instructions  (regras e diretrizes de agentes)
2. Prompts       (workflows executáveis e templates de raciocínio)
3. Agents        (personas e definições do catálogo com permissões e modelos)
4. Skills        (metaguias modulares com SKILL.md)
5. Hooks         (interceptadores de ciclo de vida de ferramentas)
6. MCP Servers   (servidores Model Context Protocol)
7. Plugins       (extensões de runtime)

Arquivos Canônicos:
- `apm.yml`          → Manifesto canônico do ecossistema
- `apm.lock.yaml`    → Lockfile determinístico com hashes SHA-256
- `apm-policy.yml`   → Regras de governança, segurança e anti-overclaim
"""

from __future__ import annotations

import enum
import glob
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import time
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ============================================================================
# Constantes e Esquema do APM
# ============================================================================

APM_SPEC_VERSION = "1.0.0"
DEFAULT_MANIFEST_FILENAME = "apm.yml"
DEFAULT_LOCK_FILENAME = "apm.lock.yaml"
DEFAULT_POLICY_FILENAME = "apm-policy.yml"

# Faixas de caracteres Unicode de risco de segurança (Trojan Source, Bidi override, Zero-width)
DANGEROUS_UNICODE_CHARS = {
    # Bidi Override & Embedding (Trojan Source CVE-2021-42574)
    '\u202A': "LEFT-TO-RIGHT EMBEDDING [LRE]",
    '\u202B': "RIGHT-TO-LEFT EMBEDDING [RLE]",
    '\u202C': "POP DIRECTIONAL FORMATTING [PDF]",
    '\u202D': "LEFT-TO-RIGHT OVERRIDE [LRO]",
    '\u202E': "RIGHT-TO-LEFT OVERRIDE [RLO]",
    '\u2066': "LEFT-TO-RIGHT ISOLATE [LRI]",
    '\u2067': "RIGHT-TO-LEFT ISOLATE [RLI]",
    '\u2068': "FIRST STRONG ISOLATE [FSI]",
    '\u2069': "POP DIRECTIONAL ISOLATE [PDI]",
    # Zero-width e invisíveis
    '\u200B': "ZERO WIDTH SPACE",
    '\u200C': "ZERO WIDTH NON-JOINER",
    '\u200D': "ZERO WIDTH JOINER",
    '\u200E': "LEFT-TO-RIGHT MARK",
    '\u200F': "RIGHT-TO-LEFT MARK",
    '\uFEFF': "ZERO WIDTH NO-BREAK SPACE (BOM in body)",
    '\u3164': "HANGUL FILLER (Invisible)",
    '\uFFA0': "HALFWIDTH HANGUL FILLER",
    '\u00AD': "SOFT HYPHEN",
}

# Padrões suspeitos de injeção de prompt
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+(system\s+)?instructions", re.IGNORECASE),
    re.compile(r"system\s+override\s*:\s*execute", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?safety\s+filters", re.IGNORECASE),
]

# Padrões de alegações exageradas sem evidência (Anti-Overclaim)
OVERCLAIM_SUSPICIOUS_PATTERNS = [
    re.compile(r"\bsuperhuman\b", re.IGNORECASE),
    re.compile(r"\b100%\s+verificado\b", re.IGNORECASE),
    re.compile(r"\bqualis\s+a1\s+garantido\b", re.IGNORECASE),
    re.compile(r"\bsem\s+nenhum\s+erro\b", re.IGNORECASE),
    re.compile(r"\bperfeito\s+e\s+inviol[aá]vel\b", re.IGNORECASE),
]


class APMPrimitiveType(str, enum.Enum):
    """As 7 primitivas canônicas do padrão Microsoft APM."""
    INSTRUCTION = "instructions"
    PROMPT = "prompts"
    AGENT = "agents"
    SKILL = "skills"
    HOOK = "hooks"
    MCP = "mcps"
    PLUGIN = "plugins"


# ============================================================================
# Helpers de Serialização YAML / JSON
# ============================================================================

def _yaml_dump(data: Any) -> str:
    """Serializa para YAML se PyYAML estiver disponível, ou JSON formatado como fallback."""
    if HAS_YAML:
        return yaml.dump(data, sort_keys=False, allow_unicode=True)
    return json.dumps(data, indent=2, ensure_ascii=False)


def _yaml_load(content: str) -> Any:
    """Desserializa YAML se PyYAML estiver disponível, com fallback seguro para JSON."""
    if HAS_YAML:
        return yaml.safe_load(content) or {}
    try:
        return json.loads(content)
    except Exception:
        # Fallback simples linha a linha para YAML básico se sem PyYAML
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                result[k.strip()] = v.strip().strip('"').strip("'")
        return result


def compute_file_sha256(filepath: Union[str, Path]) -> str:
    """Calcula hash SHA-256 determinístico de um arquivo."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_content_sha256(content: Union[str, bytes]) -> str:
    """Calcula hash SHA-256 de uma string ou bytes."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


# ============================================================================
# Estruturas de Dados do APM
# ============================================================================

@dataclass
class APMPrimitiveDecl:
    name: str
    type: str
    path: str
    description: str = ""
    checksum: Optional[str] = None
    permissions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APMManifest:
    """Representação estruturada de um manifesto apm.yml."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "Marcelo Claro"
    license: str = "MIT"
    repository: str = "https://github.com/MarceloClaro/opencode-ecosystem-core"
    dependencies: Dict[str, str] = field(default_factory=dict)
    primitives: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    registries: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "repository": self.repository,
            "dependencies": self.dependencies,
            "primitives": self.primitives,
            "registries": self.registries,
            "metadata": self.metadata,
        }

    def to_yaml(self) -> str:
        return _yaml_dump(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APMManifest":
        return cls(
            name=data.get("name", "unnamed-package"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", "Marcelo Claro"),
            license=data.get("license", "MIT"),
            repository=data.get("repository", ""),
            dependencies=data.get("dependencies", {}),
            primitives=data.get("primitives", {}),
            registries=data.get("registries", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "APMManifest":
        data = _yaml_load(yaml_str)
        if not isinstance(data, dict):
            raise ValueError("Manifesto APM inválido: raiz deve ser um dicionário.")
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> "APMManifest":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_yaml(f.read())

    def save(self, filepath: Union[str, Path]) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())


@dataclass
class APMLock:
    """Representação de um apm.lock.yaml para reprodutibilidade estrita."""
    version: str = "1.0"
    lockfile_version: int = 1
    manifest_checksum: str = ""
    dependencies: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    primitives: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    generated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "lockfile_version": self.lockfile_version,
            "manifest_checksum": self.manifest_checksum,
            "dependencies": self.dependencies,
            "primitives": self.primitives,
            "generated_at": self.generated_at,
        }

    def to_yaml(self) -> str:
        return _yaml_dump(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APMLock":
        return cls(
            version=data.get("version", "1.0"),
            lockfile_version=data.get("lockfile_version", 1),
            manifest_checksum=data.get("manifest_checksum", ""),
            dependencies=data.get("dependencies", {}),
            primitives=data.get("primitives", {}),
            generated_at=data.get("generated_at", time.time()),
        )

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> "APMLock":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_dict(_yaml_load(f.read()))

    def save(self, filepath: Union[str, Path]) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())


@dataclass
class APMPolicy:
    """Políticas de segurança e governança corporativa para APM."""
    allowed_registries: List[str] = field(default_factory=lambda: ["https://github.com", "local"])
    disallowed_packages: List[str] = field(default_factory=list)
    enforce_unicode_sanitization: bool = True
    enforce_anti_overclaim: bool = True
    allow_unrestricted_bash: bool = False
    allow_unrestricted_edit: bool = False
    required_lockfile: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> "APMPolicy":
        if not os.path.exists(filepath):
            return cls()
        with open(filepath, "r", encoding="utf-8") as f:
            data = _yaml_load(f.read())
            return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})

    def save(self, filepath: Union[str, Path]) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(_yaml_dump(self.to_dict()))


# ============================================================================
# Relatórios de Auditoria
# ============================================================================

@dataclass
class APMAuditIssue:
    severity: str  # "error", "warning", "info"
    category: str  # "unicode_security", "prompt_injection", "overclaim", "integrity", "permission"
    location: str
    description: str
    detail: Optional[str] = None


@dataclass
class APMAuditReport:
    timestamp: float = field(default_factory=time.time)
    status: str = "pass"  # "pass", "warn", "fail"
    issues: List[APMAuditIssue] = field(default_factory=list)
    files_scanned: int = 0
    primitives_scanned: int = 0

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> Dict[str, Any]:
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        return {
            "status": self.status,
            "files_scanned": self.files_scanned,
            "primitives_scanned": self.primitives_scanned,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "total_issues": len(self.issues),
            "issues": [asdict(i) for i in self.issues],
        }


# ============================================================================
# Auditor de Segurança e Integridade (APMAuditor)
# ============================================================================

class APMAuditor:
    """Auditor de segurança, governança e conformidade para pacotes APM."""

    def __init__(self, policy: Optional[APMPolicy] = None):
        self.policy = policy or APMPolicy()

    def scan_unicode_security(self, content: str, location: str) -> List[APMAuditIssue]:
        """Detecta caracteres Unicode de ataque Trojan Source ou ocultação."""
        issues: List[APMAuditIssue] = []
        for index, char in enumerate(content):
            if char in DANGEROUS_UNICODE_CHARS:
                char_name = DANGEROUS_UNICODE_CHARS[char]
                issues.append(
                    APMAuditIssue(
                        severity="error" if "OVERRIDE" in char_name or "EMBEDDING" in char_name else "warning",
                        category="unicode_security",
                        location=f"{location}:offset {index}",
                        description=f"Caractere Unicode perigoso detectado: {char_name} (U+{ord(char):04X})",
                        detail="Pode alterar a ordem visual ou ocultar instruções no prompt (Trojan Source)."
                    )
                )
        return issues

    def scan_prompt_injection(self, content: str, location: str) -> List[APMAuditIssue]:
        """Detecta padrões comuns de bypass e injeção de prompt."""
        issues: List[APMAuditIssue] = []
        for pattern in PROMPT_INJECTION_PATTERNS:
            match = pattern.search(content)
            if match:
                issues.append(
                    APMAuditIssue(
                        severity="error",
                        category="prompt_injection",
                        location=location,
                        description=f"Padrão suspeito de injeção de prompt: '{match.group(0)}'",
                        detail="Instrução tenta quebrar diretrizes do sistema de forma maliciosa."
                    )
                )
        return issues

    def scan_anti_overclaim(self, content: str, location: str) -> List[APMAuditIssue]:
        """Verifica violações da regra de Anti-Overclaim sem validação explícita."""
        issues: List[APMAuditIssue] = []
        if not self.policy.enforce_anti_overclaim:
            return issues

        for pattern in OVERCLAIM_SUSPICIOUS_PATTERNS:
            match = pattern.search(content)
            if match:
                # Se não contém contextualização de calibração ou referência histórica
                if "corrigendum" not in content.lower() and "benchmark" not in content.lower() and "especificação" not in content.lower():
                    issues.append(
                        APMAuditIssue(
                            severity="warning",
                            category="overclaim",
                            location=location,
                            description=f"Potencial alegação sem evidência (Anti-Overclaim): '{match.group(0)}'",
                            detail="Alegações devem possuir verificação externa ou grounding explícito."
                        )
                    )
        return issues

    def scan_file(self, filepath: Union[str, Path]) -> List[APMAuditIssue]:
        """Escaneia um único arquivo de texto."""
        filepath = Path(filepath)
        if not filepath.exists():
            return [APMAuditIssue(severity="error", category="integrity", location=str(filepath), description="Arquivo declarado não existe.")]

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            return [APMAuditIssue(severity="error", category="integrity", location=str(filepath), description=f"Erro ao ler arquivo: {e}")]

        issues: List[APMAuditIssue] = []
        issues.extend(self.scan_unicode_security(content, str(filepath)))
        issues.extend(self.scan_prompt_injection(content, str(filepath)))
        issues.extend(self.scan_anti_overclaim(content, str(filepath)))
        return issues

    def audit_manifest(self, manifest: APMManifest, root_dir: Path) -> APMAuditReport:
        """Executa auditoria completa sobre o manifesto e arquivos do workspace."""
        report = APMAuditReport()
        all_issues: List[APMAuditIssue] = []

        # 1. Validar registros permitidos
        for reg_name, reg_url in manifest.registries.items():
            allowed = any(reg_url.startswith(allowed_prefix) for allowed_prefix in self.policy.allowed_registries)
            if not allowed:
                all_issues.append(
                    APMAuditIssue(
                        severity="error",
                        category="governance",
                        location=f"registries.{reg_name}",
                        description=f"Registro '{reg_url}' não autorizado pelas políticas corporativas.",
                    )
                )

        # 2. Escanear cada primitiva declarada
        scanned_files = 0
        scanned_primitives = 0

        for prim_type, prim_list in manifest.primitives.items():
            if not isinstance(prim_list, list):
                continue
            for prim in prim_list:
                scanned_primitives += 1
                rel_path = prim.get("path") or prim.get("file") or ""
                if not rel_path:
                    continue
                abs_path = root_dir / rel_path
                if abs_path.exists() and abs_path.is_file():
                    scanned_files += 1
                    all_issues.extend(self.scan_file(abs_path))
                elif not abs_path.exists():
                    all_issues.append(
                        APMAuditIssue(
                            severity="error",
                            category="integrity",
                            location=rel_path,
                            description=f"Arquivo da primitiva '{prim.get('name', 'unnamed')}' não encontrado: {rel_path}",
                        )
                    )

                # Verificar permissões perigosas
                perms = prim.get("permissions", {})
                if perms.get("bash") == "allow" and not self.policy.allow_unrestricted_bash:
                    all_issues.append(
                        APMAuditIssue(
                            severity="warning",
                            category="permission",
                            location=rel_path,
                            description=f"Agente '{prim.get('name')}' possui permissão irrestrita de 'bash: allow'.",
                        )
                    )

        report.issues = all_issues
        report.files_scanned = scanned_files
        report.primitives_scanned = scanned_primitives

        if report.has_errors:
            report.status = "fail"
        elif report.has_warnings:
            report.status = "warn"
        else:
            report.status = "pass"

        return report


# ============================================================================
# Compilador Multi-Harness (APMCompiler)
# ============================================================================

class APMCompiler:
    """Compilador de primitivas APM para os formatos de múltiplos harnesses."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def compile_opencode_json(self, manifest: APMManifest) -> Dict[str, Any]:
        """Gera configuração `opencode.json` a partir do manifesto APM."""
        agents_config: Dict[str, Any] = {}
        for prim in manifest.primitives.get(APMPrimitiveType.AGENT.value, []):
            name = prim.get("name")
            if not name:
                continue
            agents_config[name] = {
                "description": prim.get("description", ""),
                "path": prim.get("path", ""),
                "permission": prim.get("permissions", {"edit": "deny", "bash": "deny"}),
                "model": prim.get("metadata", {}).get("model", "default"),
            }

        mcp_servers: Dict[str, Any] = {}
        for prim in manifest.primitives.get(APMPrimitiveType.MCP.value, []):
            name = prim.get("name")
            if not name:
                continue
            mcp_servers[name] = {
                "command": prim.get("metadata", {}).get("command", "python3"),
                "args": prim.get("metadata", {}).get("args", [prim.get("path", "")]),
                "description": prim.get("description", ""),
            }

        config = {
            "$schema": "https://opencode.ai/config.schema.json",
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "instructions": [
                p.get("path") for p in manifest.primitives.get(APMPrimitiveType.INSTRUCTION.value, [])
            ],
            "agent": agents_config,
            "mcp": mcp_servers,
        }
        return config

    def compile_agents_md(self, manifest: APMManifest) -> str:
        """Gera o arquivo `AGENTS.md` (Antigravity e OpenCode CLI)."""
        lines = [
            f"# Instruções para Agentes — {manifest.name} (APM v{manifest.version})",
            "",
            "Este arquivo é gerado e mantido via Microsoft APM (`apm.yml`).",
            "",
            "## Regras Gerais",
            "1. **Idioma**: responda sempre em português brasileiro formal.",
            "2. **Ponto de entrada**: orquestrador primário coordena todos os subagentes via Blackboard e MetaBus.",
            "3. **SDD/TDD**: toda funcionalidade segue especificação e ciclo de testes.",
            "4. **Anti-overclaim**: nunca declare resultados sem validação externa.",
            "",
            "## Catálogo de Primitivas APM Registradas",
            "",
        ]

        for ptype in APMPrimitiveType:
            items = manifest.primitives.get(ptype.value, [])
            if items:
                lines.append(f"### {ptype.value.capitalize()} ({len(items)} declarados)")
                for item in items[:15]:  # Primeiros 15 para síntese
                    lines.append(f"- **{item.get('name')}**: {item.get('description', '')} (`{item.get('path')}`)")
                if len(items) > 15:
                    lines.append(f"- *... e mais {len(items) - 15} itens registrados em `apm.yml`.*")
                lines.append("")

        return "\n".join(lines)

    def compile_claude_md(self, manifest: APMManifest) -> str:
        """Gera o arquivo `CLAUDE.md` para o Claude Code."""
        lines = [
            f"# Diretrizes para Claude Code — {manifest.name}",
            "",
            f"Gerenciado via Microsoft APM (v{manifest.version}).",
            "",
            "## Comandos Úteis",
            "- `python3 -m marceloclaro.cli doctor`: Diagnóstico do ecossistema.",
            "- `python3 -m marceloclaro.cli apm audit`: Auditoria de segurança e integridade.",
            "- `pytest`: Executar a suíte de testes.",
            "",
            "## Primitivas Ativas",
            f"- Agentes: {len(manifest.primitives.get(APMPrimitiveType.AGENT.value, []))}",
            f"- Skills: {len(manifest.primitives.get(APMPrimitiveType.SKILL.value, []))}",
            f"- MCPs: {len(manifest.primitives.get(APMPrimitiveType.MCP.value, []))}",
        ]
        return "\n".join(lines)


# ============================================================================
# Gerenciador Principal de Pacotes APM (APMPackageManager)
# ============================================================================

class APMPackageManager:
    """Gerenciador principal do ecossistema Microsoft APM."""

    def __init__(self, root_dir: Optional[Union[str, Path]] = None):
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.manifest_path = self.root_dir / DEFAULT_MANIFEST_FILENAME
        self.lock_path = self.root_dir / DEFAULT_LOCK_FILENAME
        self.policy_path = self.root_dir / DEFAULT_POLICY_FILENAME
        self.auditor = APMAuditor(self.load_policy())
        self.compiler = APMCompiler(self.root_dir)

    def load_manifest(self) -> APMManifest:
        """Carrega o manifesto apm.yml existente ou cria um default."""
        if self.manifest_path.exists():
            return APMManifest.from_file(self.manifest_path)
        return self.scan_and_create_manifest()

    def load_lock(self) -> Optional[APMLock]:
        """Carrega o lockfile apm.lock.yaml se existir."""
        if self.lock_path.exists():
            return APMLock.from_file(self.lock_path)
        return None

    def load_policy(self) -> APMPolicy:
        """Carrega a política apm-policy.yml."""
        if self.policy_path.exists():
            return APMPolicy.from_file(self.policy_path)
        return APMPolicy()

    def scan_and_create_manifest(self) -> APMManifest:
        """Escaneia o repositório e descobre todas as 7 primitivas existentes."""
        primitives: Dict[str, List[Dict[str, Any]]] = {
            APMPrimitiveType.INSTRUCTION.value: [],
            APMPrimitiveType.PROMPT.value: [],
            APMPrimitiveType.AGENT.value: [],
            APMPrimitiveType.SKILL.value: [],
            APMPrimitiveType.HOOK.value: [],
            APMPrimitiveType.MCP.value: [],
            APMPrimitiveType.PLUGIN.value: [],
        }

        # 1. Instructions
        for inst_file in ["AGENTS.md", "CLAUDE.md", "MANUAL.md", ".github/copilot-instructions.md"]:
            p = self.root_dir / inst_file
            if p.exists():
                primitives[APMPrimitiveType.INSTRUCTION.value].append({
                    "name": inst_file,
                    "path": inst_file,
                    "description": f"Instruções canônicas de {inst_file}",
                })

        # 2. Agents (catalog + root)
        for agent_file in sorted(glob.glob(str(self.root_dir / "agents" / "catalog" / "*.md"))):
            rel = os.path.relpath(agent_file, str(self.root_dir))
            stem = Path(agent_file).stem
            primitives[APMPrimitiveType.AGENT.value].append({
                "name": stem,
                "path": rel,
                "description": f"Agente especialista {stem}",
                "permissions": {"edit": "deny", "bash": "deny"},
            })

        for agent_file in sorted(glob.glob(str(self.root_dir / "agents" / "*.md"))):
            rel = os.path.relpath(agent_file, str(self.root_dir))
            stem = Path(agent_file).stem
            primitives[APMPrimitiveType.AGENT.value].append({
                "name": stem,
                "path": rel,
                "description": f"Agente essencial {stem}",
                "permissions": {"edit": "allow" if stem in {"coder", "academic_writer"} else "deny", "bash": "allow" if stem == "coder" else "deny"},
            })

        # 3. Skills
        for skill_dir in sorted(glob.glob(str(self.root_dir / "skills" / "*"))):
            if os.path.isdir(skill_dir):
                skill_md = os.path.join(skill_dir, "SKILL.md")
                rel = os.path.relpath(skill_md if os.path.exists(skill_md) else skill_dir, str(self.root_dir))
                name = os.path.basename(skill_dir)
                primitives[APMPrimitiveType.SKILL.value].append({
                    "name": name,
                    "path": rel,
                    "description": f"Habilidade {name}",
                })

        # 4. MCP Servers
        mci_mcp = self.root_dir / "mci" / "mcp_server.py"
        if mci_mcp.exists():
            primitives[APMPrimitiveType.MCP.value].append({
                "name": "mci",
                "path": "mci/mcp_server.py",
                "description": "Servidor MCP Metacognitive Interconnect (MetaBus / Reflexões)",
                "metadata": {"command": "python3", "args": ["-m", "mci.mcp_server"]},
            })

        agy_mcp = self.root_dir / "integrations" / "antigravity" / "mcp_server.py"
        if agy_mcp.exists():
            primitives[APMPrimitiveType.MCP.value].append({
                "name": "antigravity",
                "path": "integrations/antigravity/mcp_server.py",
                "description": "Servidor MCP Antigravity Bridge",
                "metadata": {"command": "python3", "args": ["-m", "integrations.antigravity.mcp_server"]},
            })

        # 5. Hooks
        apm_hook_file = self.root_dir / "integrations" / "apm.py"
        if apm_hook_file.exists():
            primitives[APMPrimitiveType.HOOK.value].append({
                "name": "audit_gate",
                "path": "integrations/apm.py",
                "description": "PreToolUse Audit Gate para prevenção de injeções Unicode e violações anti-overclaim",
                "metadata": {"event": "PreToolUse"},
            })

        manifest = APMManifest(
            name="opencode-ecosystem-core",
            version=APM_SPEC_VERSION,
            description="OpenCode Ecosystem Core: A2A Blackboard, MetaBus metacognition e catálogo de 209+ agentes",
            author="Marcelo Claro",
            license="MIT",
            repository="https://github.com/MarceloClaro/opencode-ecosystem-core",
            dependencies={
                "microsoft/apm-sample-package": "^1.0.0",
            },
            primitives=primitives,
            registries={
                "github": "https://github.com",
                "local": "local",
            },
        )
        return manifest

    def init(self, overwrite: bool = False) -> Tuple[APMManifest, APMLock]:
        """Inicializa apm.yml, apm.lock.yaml e apm-policy.yml."""
        if self.manifest_path.exists() and not overwrite:
            manifest = self.load_manifest()
        else:
            manifest = self.scan_and_create_manifest()
            manifest.save(self.manifest_path)

        policy = self.load_policy()
        policy.save(self.policy_path)

        lock = self.generate_lockfile(manifest)
        lock.save(self.lock_path)

        return manifest, lock

    def generate_lockfile(self, manifest: APMManifest) -> APMLock:
        """Gera lockfile determinístico calculando os hashes SHA-256 de todas as primitivas."""
        manifest_raw = manifest.to_yaml()
        manifest_checksum = compute_content_sha256(manifest_raw)

        primitives_locked: Dict[str, Dict[str, Any]] = {}

        for ptype, items in manifest.primitives.items():
            primitives_locked[ptype] = {}
            for item in items:
                name = item.get("name", "unnamed")
                rel_path = item.get("path", "")
                full_path = self.root_dir / rel_path
                file_hash = ""
                if full_path.exists() and full_path.is_file():
                    file_hash = compute_file_sha256(full_path)
                elif full_path.exists() and full_path.is_dir():
                    # Hash agregado do diretório
                    dir_hashes = []
                    for f in sorted(glob.glob(str(full_path / "**" / "*"), recursive=True)):
                        if os.path.isfile(f):
                            dir_hashes.append(compute_file_sha256(f))
                    file_hash = compute_content_sha256("".join(dir_hashes))

                primitives_locked[ptype][name] = {
                    "path": rel_path,
                    "sha256": file_hash,
                    "locked_at": time.time(),
                }

        lock = APMLock(
            version=manifest.version,
            lockfile_version=1,
            manifest_checksum=manifest_checksum,
            dependencies={
                dep: {"version": ver, "sha256": compute_content_sha256(f"{dep}:{ver}")}
                for dep, ver in manifest.dependencies.items()
            },
            primitives=primitives_locked,
        )
        return lock

    def install(self) -> APMLock:
        """Valida e instala dependências declaradas, atualizando o lockfile."""
        manifest = self.load_manifest()
        lock = self.generate_lockfile(manifest)
        lock.save(self.lock_path)
        return lock

    def compile(self, target: str = "all") -> Dict[str, Any]:
        """Compila o manifesto APM para os harnesses especificados."""
        manifest = self.load_manifest()
        results: Dict[str, Any] = {}

        if target in {"all", "opencode", "opencode.json"}:
            opencode_cfg = self.compiler.compile_opencode_json(manifest)
            opencode_path = self.root_dir / "opencode.json"
            with open(opencode_path, "w", encoding="utf-8") as f:
                json.dump(opencode_cfg, f, indent=2, ensure_ascii=False)
            results["opencode.json"] = str(opencode_path)

        if target in {"all", "agents", "AGENTS.md"}:
            agents_content = self.compiler.compile_agents_md(manifest)
            agents_path = self.root_dir / "AGENTS.md"
            with open(agents_path, "w", encoding="utf-8") as f:
                f.write(agents_content)
            results["AGENTS.md"] = str(agents_path)

        if target in {"all", "claude", "CLAUDE.md"}:
            claude_content = self.compiler.compile_claude_md(manifest)
            claude_path = self.root_dir / "CLAUDE.md"
            with open(claude_path, "w", encoding="utf-8") as f:
                f.write(claude_content)
            results["CLAUDE.md"] = str(claude_path)

        return results

    def audit(self) -> APMAuditReport:
        """Executa auditoria completa de segurança, governança e conformidade."""
        manifest = self.load_manifest()
        return self.auditor.audit_manifest(manifest, self.root_dir)

    def pack(self, output_file: Optional[Union[str, Path]] = None) -> Path:
        """Empacota o projeto em um pacote APM redistribuível (.tar.gz)."""
        manifest = self.load_manifest()
        if not output_file:
            output_file = self.root_dir / f"{manifest.name}-{manifest.version}.apm.tar.gz"
        else:
            output_file = Path(output_file)

        with tarfile.open(output_file, "w:gz") as tar:
            for fname in [DEFAULT_MANIFEST_FILENAME, DEFAULT_LOCK_FILENAME, DEFAULT_POLICY_FILENAME, "AGENTS.md", "CLAUDE.md"]:
                fpath = self.root_dir / fname
                if fpath.exists():
                    tar.add(fpath, arcname=fname)

            # Adicionar pasta agents e skills
            for dname in ["agents", "skills", "mci", "integrations"]:
                dpath = self.root_dir / dname
                if dpath.exists():
                    tar.add(dpath, arcname=dname)

        return output_file

    def list_primitives(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lista todas as primitivas registradas no manifesto."""
        manifest = self.load_manifest()
        return manifest.primitives


# ============================================================================
# Hook de Ciclo de Vida do APM para o Orquestrador
# ============================================================================

def apm_pre_tool_use_hook(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Hook PreToolUse executado antes de qualquer ferramenta externa."""
    auditor = APMAuditor()
    args_str = json.dumps(arguments, ensure_ascii=False)
    issues = auditor.scan_unicode_security(args_str, f"tool:{tool_name}")
    if any(i.severity == "error" for i in issues):
        return False, f"APM Security Gate: Injeção de Unicode perigoso detectada nos argumentos da ferramenta '{tool_name}'."
    return True, None
