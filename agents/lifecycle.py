"""R894: definições persistentes e gate local, sem simular execução de agentes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
import uuid
from contextlib import ExitStack
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"[a-z][a-z0-9_-]{2,79}\Z")
MAX_CARD_BYTES = 128 * 1024
OUTPUT_CONTRACT = {
    "required_fields": ["status", "findings", "evidence", "limitations"],
    "evidence_required": True,
    "external_validation": False,
}


class _UniqueLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValueError("Aliases YAML não são aceitos em perfis gerenciados")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        result = {}
        for key, value in node.value:
            key = self.construct_object(key, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError("Chave YAML inválida ou duplicada")
            result[key] = self.construct_object(value, deep=deep)
        return result


def _slug(value):
    if not isinstance(value, str) or not SLUG.fullmatch(value) or value == "marceloclaro":
        raise ValueError("Identificador de especialista inválido ou reservado")
    return value


def _text(value, label, maximum):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or "\x00" in value:
        raise ValueError(f"{label} exige texto não vazio e delimitado")
    return value.strip()


def _safe_file(root, relative):
    if not isinstance(relative, str) or "\\" in relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Referência deve permanecer no repositório")
    path = root / relative
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("Symlink não é aceito em perfil ou referência")
        if part == root:
            break
    try:
        info = path.stat()
    except OSError as exc:
        raise ValueError("Referência de perfil inexistente") from exc
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_CARD_BYTES:
        raise ValueError("Referência não regular ou excessiva")
    path.resolve().relative_to(root)
    return path


def _metadata(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_CARD_BYTES:
        raise ValueError("Perfil vazio ou excessivo")
    try:
        text = raw.decode("utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise ValueError("Frontmatter obrigatório")
        header, body = text[4:].split("\n---\n", 1)
        meta = yaml.load(header, Loader=_UniqueLoader)
    except (UnicodeError, yaml.YAMLError, RecursionError) as exc:
        raise ValueError("Frontmatter inválido") from exc
    if not isinstance(meta, dict) or not body.strip():
        raise ValueError("Metadados e instruções obrigatórios")
    return meta, body


def _permissions(test_file, allow_edit):
    return {"read": "allow", "glob": "allow", "grep": "allow",
            "edit": "allow" if allow_edit else "deny", "webfetch": "deny", "task": "deny",
            "bash": {"*": "deny", "python3 -m marceloclaro.cli doctor": "allow",
                     f"python3 -m pytest {test_file} -q": "allow"}}


def _managed_capability(agent_id):
    # O baseline histórico continua aceitando seus IDs originais. Perfis novos
    # usam hífens: a conversão para tags não pode colidir com IDs com underscore.
    _slug(agent_id)
    if "_" in agent_id:
        raise ValueError("Identificadores gerenciados usam hífens, sem underscore")
    return "profile_" + agent_id.replace("-", "_")


def _confined_card_path(root, path):
    path.relative_to(root)
    if path.parent not in {root / "agents", root / "agents/catalog"}:
        raise ValueError("Perfil deve permanecer no catálogo canônico")
    for current in (path, *path.parents):
        if current.is_symlink():
            raise ValueError("Symlink não é aceito em perfil ou ancestral")
        if current == root:
            break
    if not path.resolve().is_relative_to(root):
        raise ValueError("Perfil fora do repositório")


def _publish_card(root, path, raw):
    """Publica sem substituir destino; descritores ancoram os pais no POSIX."""
    _confined_card_path(root, path)
    if not path.parent.is_dir():
        raise ValueError("Catálogo regular existente obrigatório")
    descriptor_api = (os.open in os.supports_dir_fd and os.link in os.supports_dir_fd
                      and os.unlink in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW"))
    if descriptor_api:
        with ExitStack() as stack:
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            folder = os.open(root, flags)
            stack.callback(os.close, folder)
            for component in ("agents", "catalog"):
                folder = os.open(component, flags, dir_fd=folder)
                stack.callback(os.close, folder)
            temporary = ".profile-" + uuid.uuid4().hex + ".tmp"
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=folder)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
                    os.fchmod(stream.fileno(), 0o644)
                os.link(temporary, path.name, src_dir_fd=folder, dst_dir_fd=folder,
                        follow_symlinks=False)
            finally:
                os.unlink(temporary, dir_fd=folder)
        return
    # Plataformas sem dir_fd preservam a publicação exclusiva e revalidam todos
    # os ancestrais antes de criar/publicar; não apenas o último diretório.
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".profile-", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        _confined_card_path(root, path)
        os.link(temporary, path, follow_symlinks=False)
    finally:
        Path(temporary).unlink(missing_ok=True)


def validate_managed_card(root, path, raw):
    root, path = Path(root).resolve(), Path(path)
    _confined_card_path(root, path)
    meta, _ = _metadata(raw)
    required = {"agent_id", "name", "description", "version", "type", "category", "language",
                "lifecycle", "parent", "spec_file", "test_file", "source", "allow_edit",
                "tags", "skills", "capabilities", "permission", "tools", "output_contract"}
    if set(meta) != required:
        raise ValueError("Contrato de perfil incompleto ou contém campos desconhecidos")
    aid = _slug(meta["agent_id"])
    if path.stem != aid or path.parent.name not in {"catalog", "agents"}:
        raise ValueError("ID e arquivo do perfil divergem")
    for key, limit in (("name", 160), ("description", 1200), ("source", 300)):
        _text(meta[key], key, limit)
    if (meta["parent"] != "marceloclaro" or meta["lifecycle"] != "managed-v1"
            or meta["language"] != "pt-BR" or meta["type"] != "specialist"
            or meta["version"] != "1.0.0" or meta["category"] not in {"audit", "engineering", "integration"}
            or type(meta["allow_edit"]) is not bool):
        raise ValueError("Hierarquia, tipo, versão ou idioma de perfil inválido")
    for key, pattern in (("spec_file", r"specs/SPEC-935-R[0-9]+[a-zA-Z0-9_.-]*\.md"),
                         ("test_file", r"tests/test_r[0-9]+_[a-z0-9_]+\.py")):
        if not isinstance(meta[key], str) or not re.fullmatch(pattern, meta[key]):
            raise ValueError("Referência SDD/TDD inválida")
        _safe_file(root, meta[key])
    tags = meta["tags"]
    unique = _managed_capability(aid)
    if (not isinstance(tags, list) or not 1 <= len(tags) <= 32
            or not all(isinstance(t, str) and re.fullmatch(r"[a-z][a-z0-9_]{1,99}", t) for t in tags)
            or len(tags) != len(set(tags))
            or unique not in tags
            or any(tag.startswith("profile_") and tag != unique for tag in tags)):
        raise ValueError("Capacidades tipadas e capacidade exclusiva obrigatórias")
    if (meta["capabilities"] != {"extendedAgentCard": True}
            or meta["capabilities"]["extendedAgentCard"] is not True):
        raise ValueError("Contrato A2A obrigatório")
    expected_skill = {"id": aid, "name": meta["name"], "description": meta["description"],
                      "tags": tags, "examples": ["Execute o escopo solicitado e cite os arquivos e limites observados."]}
    if (meta["skills"] != [expected_skill] or meta["output_contract"] != OUTPUT_CONTRACT
            or meta["output_contract"]["evidence_required"] is not True
            or meta["output_contract"]["external_validation"] is not False):
        raise ValueError("Contrato de skill ou saída alterado")
    if meta["permission"] != _permissions(meta["test_file"], meta["allow_edit"]):
        raise ValueError("Permissões excedem o contrato autorizado")
    tools = {"read": True, "glob": True, "grep": True, "bash": True,
             "edit": meta["allow_edit"], "write": meta["allow_edit"]}
    if meta["tools"] != tools or not all(type(v) is bool for v in meta["tools"].values()):
        raise ValueError("Ferramentas divergentes da política")
    return {"mode": "managed-v1", "agent_id": aid, "definition_validated": True,
            "validation_scope": "definition_policy_and_references", "executed": False,
            "source_file": str(path.relative_to(root)),
            "source_sha256": hashlib.sha256(raw).hexdigest(), "profile": meta,
            "unique_capability": unique, "external_validation": False}


def enforce_catalog_contract(path, raw, *, repo_root=None):
    """Baseline só conserva os bytes históricos; arquivos novos exigem contrato."""
    root = Path(repo_root).resolve() if repo_root is not None else ROOT
    path = Path(path).absolute()
    if path.parent not in {root / "agents", root / "agents/catalog"}:
        return {"mode": "external_test_catalog", "definition_validated": False}
    relative = str(path.relative_to(root))
    _safe_file(root, relative)
    baseline = root / "agents/lifecycle_baseline.json"
    files = json.loads(baseline.read_text())["files"] if baseline.is_file() else {}
    if files.get(relative) == hashlib.sha256(raw).hexdigest():
        return {"mode": "legacy_baseline", "definition_validated": False,
                "legacy_preserved": True, "source_sha256": files[relative]}
    return validate_managed_card(root, path, raw)


class AgentLifecycleService:
    def __init__(self, repo_root=ROOT):
        self.root = Path(repo_root).resolve()

    def validate(self, agent_id):
        _slug(agent_id)
        path = _safe_file(self.root, f"agents/catalog/{agent_id}.md")
        raw = path.read_bytes()
        return enforce_catalog_contract(path, raw, repo_root=self.root)

    def inventory(self):
        rows, rejected = [], []
        for p in sorted((self.root / "agents/catalog").glob("*.md")):
            try:
                result = self.validate(p.stem)
                result.pop("profile", None)
                rows.append({"agent_id": p.stem, **result})
            except (ValueError, OSError) as exc:
                rejected.append({"agent_id": p.stem, "reason": str(exc)})
        return {"status": "blocked" if rejected else "completed", "profiles": rows,
                "rejected": rejected, "executed": False, "registered": False}

    def create(self, document):
        allowed = {"agent_id", "name", "description", "capabilities", "spec_file", "test_file", "prompt", "allow_edit", "source"}
        if not isinstance(document, dict) or set(document) - allowed:
            raise ValueError("Campos de criação desconhecidos")
        aid = _slug(document.get("agent_id"))
        name = _text(document.get("name"), "name", 160)
        description = _text(document.get("description"), "description", 1200)
        prompt = _text(document.get("prompt"), "prompt", 32000)
        source = _text(document.get("source", "user_requested_core_profile"), "source", 300)
        edit = document.get("allow_edit", False)
        caps = document.get("capabilities")
        if (type(edit) is not bool or not isinstance(caps, list) or not caps or len(caps) > 30
                or not all(isinstance(c, str) and re.fullmatch(r"[a-z][a-z0-9_]{1,99}", c) for c in caps)):
            raise ValueError("Capacidades ou decisão de edição inválidas")
        unique = _managed_capability(aid)
        if any(cap.startswith("profile_") and cap != unique for cap in caps):
            raise ValueError("Capacidade exclusiva de outro perfil é reservada")
        tags = list(dict.fromkeys([unique, *caps]))
        meta = {"agent_id": aid, "name": name, "description": description, "version": "1.0.0",
                "type": "specialist", "category": "engineering" if edit else "audit", "language": "pt-BR",
                "lifecycle": "managed-v1", "parent": "marceloclaro", "spec_file": document.get("spec_file"),
                "test_file": document.get("test_file"), "source": source, "allow_edit": edit,
                "tags": tags, "skills": [{"id": aid, "name": name, "description": description,
                    "tags": list(tags), "examples": ["Execute o escopo solicitado e cite os arquivos e limites observados."]}],
                "capabilities": {"extendedAgentCard": True},
                "permission": _permissions(document.get("test_file"), edit),
                "tools": {"read": True, "glob": True, "grep": True, "bash": True, "edit": edit, "write": edit},
                "output_contract": OUTPUT_CONTRACT}
        raw = ("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n# " + name +
               "\n\n" + prompt + "\n\n## Coordenação e evidência\n\n" +
               "Receba tarefas pelo MarceloClaro. Leia a spec e o contexto compartilhado antes de atuar. " +
               "Apresente status, findings, evidence (arquivo/hash/linhas ou recibo) e limitations. " +
               "Declarar instalação, atribuição ou análise estática não comprova inferência, execução, qualidade científica ou aprovação externa. " +
               "Sem evidência suficiente, devolva blocked ou partial. Não delegue fora do primário nem eleve confiança pela própria avaliação.\n").encode()
        path = self.root / "agents/catalog" / (aid + ".md")
        result = validate_managed_card(self.root, path, raw)
        try:
            _publish_card(self.root, path, raw)
        except OSError as exc:
            raise ValueError("Perfil já existe ou destino indisponível") from exc
        return result


def validate_lifecycle_request(config):
    if not isinstance(config, dict):
        raise ValueError("Configuração de agentes deve ser objeto")
    op = config.get("operation")
    fields = {"inventory": {"operation"}, "validate": {"operation", "agent_id"},
              "register": {"operation", "agent_id"}, "activate": {"operation", "agent_id", "task"},
              "create": {"operation", "profile"}}
    if op not in fields or set(config) != fields[op]:
        raise ValueError("Operação de perfil ou campos inválidos")
    if "agent_id" in config:
        _slug(config["agent_id"])
    if op == "activate":
        _text(config["task"], "task", 4000)
    if op == "create" and not isinstance(config["profile"], dict):
        raise ValueError("Perfil exige objeto")
    return dict(config)
