"""R921 fase 1: contrato RED hermético; nenhum acesso a cache/conta reais.

O módulo sob teste só é procurado/importado dentro da chamada de cada teste.
Fixtures constroem apenas dados artificiais; não há implementação do extrator.
"""
from __future__ import annotations

import builtins
from contextlib import contextmanager
import hashlib
import http.client
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import urllib.request

import pytest


MODULE = "integrations.local_plugin_extraction"
ZOTERO = "openai-curated-remote/zotero/0.1.2"
SEQUENCE = "openai-curated-remote/sequence-viewer/0.1.52"
ANTHROPIC = "claude-cowork/anthropic-skills/1.0.0"
CANONICAL_STORAGE = Path(".opencode/scientific-plugins")
MIT = """MIT License

Copyright (c) 2026 R921 synthetic fixture

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Textos de evidência sintéticos: cláusulas reconhecíveis, não licença de fonte real.
APACHE = """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
1. Definitions.
"License" shall mean the terms and conditions for use, reproduction,
and distribution as defined by Sections 1 through 9 of this document.
"Licensor" shall mean the copyright owner or entity authorized by the
copyright owner that is granting the License.
2. Grant of Copyright License. Subject to the terms and conditions of
this License, each Contributor hereby grants to You a perpetual,
worldwide, non-exclusive, no-charge, royalty-free, irrevocable
copyright license to reproduce, prepare Derivative Works of,
publicly display, publicly perform, sublicense, and distribute the
Work and such Derivative Works in Source or Object form.
3. Grant of Patent License. Subject to the terms and conditions of
this License, each Contributor hereby grants to You a perpetual,
worldwide, non-exclusive, no-charge, royalty-free, irrevocable
(except as stated in this section) patent license to make, have made,
use, offer to sell, sell, import, and otherwise transfer the Work.
4. Redistribution. You may reproduce and distribute copies of the
Work or Derivative Works thereof in any medium, with or without
modifications, and in Source or Object form, provided that You
meet the following conditions: You must give any other recipients
of the Work or Derivative Works a copy of this License; and You
must cause any modified files to carry prominent notices stating
that You changed the files; and You must retain all copyright,
patent, trademark, and attribution notices from the Source form.
5. Submission of Contributions. Unless You explicitly state otherwise,
any Contribution intentionally submitted for inclusion in the Work
shall be under the terms and conditions of this License.
6. Trademarks. This License does not grant permission to use the trade
names, trademarks, service marks, or product names of the Licensor.
7. Disclaimer of Warranty. Unless required by applicable law or
agreed to in writing, Licensor provides the Work (and each
Contributor provides its Contributions) on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied, including, without limitation, any warranties or conditions
of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
PARTICULAR PURPOSE.
8. Limitation of Liability. In no event and under no legal theory,
whether in tort (including negligence), contract, or otherwise,
unless required by applicable law or agreed to in writing, shall
any Contributor be liable to You for damages arising as a result
of this License or out of the use or inability to use the Work.
9. Accepting Warranty or Additional Liability. You may choose to
offer support, warranty, indemnity, or other liability obligations
only on Your own behalf and on Your sole responsibility.
END OF TERMS AND CONDITIONS
"""
BSD2 = """BSD 2-Clause License
Copyright (c) 2026 R921 synthetic fixture
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
BSD3 = BSD2.replace("BSD 2-Clause", "BSD 3-Clause").replace(
    '\nTHIS SOFTWARE',
    '\n3. Neither the name of the copyright holder nor the names of its\n'
    '   contributors may be used to endorse or promote products derived from\n'
    '   this software without specific prior written permission.\n\nTHIS SOFTWARE',
)
RESTRICTED = "Proprietary. All rights reserved. No copying or extraction permitted.\n"
SKILL = (
    "---\nname: curate\ndescription: Instrução sintética R921\n"
    "disable-model-invocation: true\n---\n"
    "# Curadoria local\nLeia references/guide.md; não execute ferramentas.\n"
)
POLICY = "policy:\n  allow_implicit_invocation: false\n"
LIMITS = {
    "max_packages": 64,
    "max_files_per_package": 256,
    "max_file_bytes": 1_048_576,
    "max_total_bytes": 16_777_216,
}


def extraction_module():
    """A ausência é AssertionError na fase call, nunca erro na coleta/setup."""
    assert importlib.util.find_spec(MODULE) is not None, "R921: módulo de extração ainda não implementado"
    return importlib.import_module(MODULE)


def put(path: Path, content: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    return path


def manifest(package: Path, **changes):
    path = package / ".codex-plugin/plugin.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.update(changes)
    put(path, json.dumps(value, sort_keys=True))


def package(cache: Path, relative=ZOTERO, *, pid="zotero", spdx="MIT", license_text=MIT, skill=True):
    root = cache / relative
    metadata = {"name": pid, "version": root.name, "license": spdx, "skills": "./skills"}
    put(root / ".codex-plugin/plugin.json", json.dumps(metadata, sort_keys=True))
    if license_text is not None:
        put(root / "LICENSE", license_text)
    if skill:
        put(root / "skills/curate/SKILL.md", SKILL)
        put(root / "skills/curate/references/guide.md", "Referência sintética pública.\n")
        put(root / "skills/curate/agents/openai.yaml", POLICY)
    return root


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_state(root: Path):
    """Snapshot de fixtures: inclui diretórios/links, sem seguir links."""
    if not root.exists() and not root.is_symlink():
        return None
    state = {}

    def walk(path):
        key = path.relative_to(root).as_posix()
        info = path.lstat()
        if path.is_symlink():
            state[key] = ("link", os.readlink(path), info.st_mtime_ns)
        elif path.is_dir():
            state[key] = ("dir",)
            for child in sorted(path.iterdir()):
                walk(child)
        else:
            state[key] = ("file", path.read_bytes(), info.st_mtime_ns, info.st_mode)

    walk(root)
    return state


@contextmanager
def unreadable(monkeypatch, paths):
    """Tripwire para os leitores usuais; não é uma sandbox de syscalls."""
    blocked = {os.path.abspath(os.fspath(p)) for p in paths}

    def check(value):
        if isinstance(value, (str, bytes, os.PathLike)):
            candidate = os.path.abspath(os.fsdecode(value))
            assert not any(candidate == p or candidate.startswith(p + os.sep) for p in blocked), (
                "Corpo proibido foi aberto pelo código sob teste"
            )

    with monkeypatch.context() as scoped:
        for owner, name in ((builtins, "open"), (io, "open"), (os, "open")):
            original = getattr(owner, name)

            def guarded(value, *args, _original=original, **kwargs):
                check(value)
                return _original(value, *args, **kwargs)

            scoped.setattr(owner, name, guarded)
        yield


def assert_no_runtime_claims(result):
    assert result["executed"] is False
    assert result["credentials_copied"] is False
    assert result["hooks_executed"] is False
    assert result["transport_imported"] is False
    assert result["host_authentication"] == "not_verified"
    assert result["external_validation"] is False
    assert result.get("activated", False) is False
    assert result.get("authenticated", False) is False
    assert result.get("local_connector_execution", False) is False


def canonical():
    return importlib.import_module("integrations.scientific_plugins")


def registry_path(repo):
    return repo / CANONICAL_STORAGE / "registry.json"


def installed_path(repo, pid="zotero", version="0.1.2"):
    return repo / CANONICAL_STORAGE / "packages" / pid / version


@pytest.fixture(autouse=True)
def no_external_effects(tmp_path, monkeypatch):
    def deny(*_args, **_kwargs):
        raise AssertionError("R921: rede, shell, subprocess ou conector externo não permitido")

    for name in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, deny)
    for name in ("system", "popen"):
        monkeypatch.setattr(os, name, deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    monkeypatch.setattr(urllib.request, "urlopen", deny)
    monkeypatch.setattr(http.client.HTTPConnection, "connect", deny)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", deny)
    # HOME sintético: nunca carregar configuração, histórico ou credenciais pessoais.
    home = tmp_path / "synthetic-home"
    home.mkdir()
    original_home = Path.home()
    monkeypatch.setenv("HOME", str(home))
    with unreadable(monkeypatch, [
        Path("/mnt/c/Users/marce/.codex"), original_home / ".codex",
        original_home / ".config/opencode/auth.json",
    ]):
        yield


def test_public_api_is_callable():
    api = extraction_module()
    assert callable(getattr(api, "inventory_local_plugins", None))
    assert callable(getattr(api, "extract_local_plugins", None))


def test_inventory_is_deterministic_read_only_non_authoritative_evidence(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    before = tree_state(tmp_path)

    report = api.inventory_local_plugins(cache)

    assert report == api.inventory_local_plugins(cache)
    assert tree_state(tmp_path) == before
    assert report["schema_version"] == 1
    assert report["kind"] == "local_plugin_evidence"
    assert report["authoritative"] is False
    assert report["cache_root"] == str(cache.resolve())
    assert report["limits"] == LIMITS
    assert_no_runtime_claims(report)
    assert len(report["plugins"]) == 1
    row = report["plugins"][0]
    assert (row["id"], row["namespace"], row["version"]) == ("zotero", "openai-curated-remote", "0.1.2")
    assert row["source_root"] == str(source.resolve())
    assert row["manifest_path"] == ".codex-plugin/plugin.json"
    assert row["manifest_sha256"] == digest(source / row["manifest_path"])
    assert row["disposition"] == "eligible"
    assert row["files"]["skills/curate/SKILL.md"] == digest(source / "skills/curate/SKILL.md")
    assert {"path": "LICENSE", "spdx": "MIT", "sha256": digest(source / "LICENSE")} in row["license_evidence"]
    assert SKILL not in json.dumps(report)


def test_only_present_authorized_namespaces_are_inspected(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    foreign = package(cache, "unauthorized/zotero/0.1.2")
    # IDs que já existem não justificam investigar um namespace não autorizado.
    with unreadable(monkeypatch, [foreign.parent.parent]):
        result = api.inventory_local_plugins(cache)
    assert [(p["id"], p["namespace"]) for p in result["plugins"]] == [("zotero", "openai-curated-remote")]
    assert not (cache / "claude-cowork").exists()


def test_unknown_manifest_cannot_register_or_authorize_a_plugin(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache, "openai-curated-remote/not-registered/0.1.0", pid="not-registered")
    manifest(source, hostOperations={"execute": "untrusted_tool"})
    old_catalog = dict(canonical().PLUGINS)
    before = tree_state(cache)
    repo = tmp_path / "repo"
    with unreadable(monkeypatch, [source / "skills"]):
        row = api.inventory_local_plugins(cache)["plugins"][0]
        with pytest.raises(ValueError, match="unknown_plugin"):
            api.extract_local_plugins(cache, repo, ["not-registered"])
    assert row["disposition"] == "reference_only"
    assert "not_catalogued" in row["reason_codes"]
    assert row["files"] == {}
    assert canonical().PLUGINS == old_catalog
    assert not repo.exists() and tree_state(cache) == before


def test_supported_local_manifest_locations_share_the_same_contract(tmp_path):
    api = extraction_module()
    for index, relative in enumerate((".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "plugin.json")):
        cache = tmp_path / str(index) / "cache"
        source = package(cache)
        original = source / ".codex-plugin/plugin.json"
        if relative != ".codex-plugin/plugin.json":
            put(source / relative, original.read_bytes())
            original.unlink()
            original.parent.rmdir()
        row = api.inventory_local_plugins(cache)["plugins"][0]
        assert row["disposition"] == "eligible"
        assert row["manifest_path"] == relative
        assert row["manifest_sha256"] == digest(source / relative)
        result = api.extract_local_plugins(cache, tmp_path / str(index) / "repo", ["zotero"])
        assert relative not in result["plugins"][0]["files"]


def test_recognizable_concordant_permissive_license_text_is_required(tmp_path):
    api = extraction_module()
    for index, (spdx, text) in enumerate((("MIT", MIT), ("Apache-2.0", APACHE),
                                          ("BSD-2-Clause", BSD2), ("BSD-3-Clause", BSD3))):
        cache = tmp_path / str(index) / "cache"
        source = package(cache, spdx=spdx, license_text=text)
        row = api.inventory_local_plugins(cache)["plugins"][0]
        assert row["disposition"] == "eligible", spdx
        assert {"path": "LICENSE", "spdx": spdx, "sha256": digest(source / "LICENSE")} in row["license_evidence"]
        repo = tmp_path / str(index) / "repo"
        result = api.extract_local_plugins(cache, repo, ["zotero"])
        assert [p["id"] for p in result["plugins"]] == ["zotero"]
        assert (installed_path(repo) / "LICENSE").read_bytes() == text.encode()


def test_missing_spdx_only_conflicting_and_proprietary_licenses_are_reference_only(tmp_path, monkeypatch):
    api = extraction_module()
    cases = [
        ("MIT", None, "license_missing"),
        ("MIT", "SPDX-License-Identifier: MIT\n", "license_text_unverified"),
        ("MIT", "Public documentation; license unspecified.\n", "license_text_unverified"),
        ("Apache-2.0", MIT, "license_conflict"),
        ("Proprietary", RESTRICTED, "license_restricted"),
    ]
    for index, (spdx, text, reason) in enumerate(cases):
        cache = tmp_path / str(index) / "cache"
        source = package(cache, spdx=spdx, license_text=text)
        before = tree_state(cache)
        repo = tmp_path / str(index) / "repo"
        with unreadable(monkeypatch, [source / "skills"]):
            row = api.inventory_local_plugins(cache)["plugins"][0]
            result = api.extract_local_plugins(cache, repo, ["zotero"])
        assert row["disposition"] == "reference_only"
        assert reason in row["reason_codes"]
        assert row["files"] == {}
        assert result["plugins"] == []
        assert [p["id"] for p in result["reference_only"]] == ["zotero"]
        assert not repo.exists()
        assert tree_state(cache) == before


def test_nested_restriction_is_not_read_or_copied(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    branch = source / "skills/curate/references/vendor"
    put(branch / "LICENSE", RESTRICTED)
    private = put(branch / "private.md", "DO_NOT_LOAD_VENDOR_BODY")
    put(source / "skills/curate/references/LICENSE", MIT)
    repo = tmp_path / "repo"
    before = tree_state(cache)
    with unreadable(monkeypatch, [private]):
        row = api.inventory_local_plugins(cache)["plugins"][0]
        result = api.extract_local_plugins(cache, repo, ["zotero"])
    target = Path(result["plugins"][0]["package_root"])
    assert row["disposition"] == "eligible"
    assert "skills/curate/references/vendor/private.md" not in row["files"]
    assert not (target / "skills/curate/references/vendor").exists()
    assert (target / "skills/curate/references/LICENSE").read_bytes() == MIT.encode()
    assert tree_state(cache) == before


def test_permissive_child_cannot_relicense_a_restricted_ancestor(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache, spdx="Proprietary", license_text=RESTRICTED)
    put(source / "skills/curate/LICENSE", MIT)
    before = tree_state(cache)
    repo = tmp_path / "repo"
    with unreadable(monkeypatch, [source / "skills"]):
        row = api.inventory_local_plugins(cache)["plugins"][0]
        result = api.extract_local_plugins(cache, repo, ["zotero"])
    assert row["disposition"] == "reference_only"
    assert "license_restricted" in row["reason_codes"]
    assert row["files"] == {} and result["plugins"] == []
    assert not repo.exists() and tree_state(cache) == before


def test_anthropic_document_skill_bodies_are_never_loaded(tmp_path, monkeypatch):
    api = extraction_module()
    for index, nested_license in enumerate((True, False)):
        cache = tmp_path / str(index) / "cache"
        # Raiz falsamente permissiva não autoriza esses quatro ramos conhecidos,
        # nem mesmo se a distribuição omitir as licenças restritivas locais.
        source = package(cache, ANTHROPIC, pid="anthropic-skills", skill=False)
        bodies = []
        for name in ("docx", "pdf", "pptx", "xlsx"):
            bodies.append(put(source / "skills" / name / "SKILL.md", "DO_NOT_LOAD_PROPRIETARY_BODY"))
            if nested_license:
                put(source / "skills" / name / "LICENSE", RESTRICTED)
        repo = tmp_path / str(index) / "repo"
        before = tree_state(cache)
        with unreadable(monkeypatch, bodies):
            row = api.inventory_local_plugins(cache)["plugins"][0]
            result = api.extract_local_plugins(cache, repo, ["anthropic-skills"])
        assert row["disposition"] == "reference_only"
        assert "license_restricted" in row["reason_codes"]
        assert row["files"] == {} and result["plugins"] == []
        assert not repo.exists() and tree_state(cache) == before
        assert "DO_NOT_LOAD_PROPRIETARY_BODY" not in json.dumps(result)


def test_host_only_manifest_is_reference_only_without_transport_read(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache, skill=False, license_text=None)
    transport = put(source / ".mcp.json", '{"mcpServers":{"host":{"url":"https://invalid.example"}}}')
    manifest(source, mcpServers="./.mcp.json")
    repo = tmp_path / "repo"
    with unreadable(monkeypatch, [transport]):
        report = api.inventory_local_plugins(cache)
        result = api.extract_local_plugins(cache, repo, ["zotero"])
    row = report["plugins"][0]
    assert row["disposition"] == "reference_only"
    assert "no_local_skills" in row["reason_codes"]
    assert row["files"] == {} and result["plugins"] == []
    assert [p["id"] for p in result["reference_only"]] == ["zotero"]
    assert not repo.exists()


def test_only_instructional_text_license_notice_and_policy_are_copied(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    allowed = {
        "LICENSE", "NOTICE.txt", "README.md", "docs/method.rst",
        "skills/curate/SKILL.md", "skills/curate/agents/openai.yaml",
        "skills/curate/references/guide.md", "skills/curate/references/schema.txt",
        "skills/curate/references/LICENSE",
    }
    for relative in ("NOTICE.txt", "README.md", "docs/method.rst", "skills/curate/references/schema.txt"):
        put(source / relative, "Texto público sintético.\n")
    put(source / "skills/curate/references/LICENSE", MIT)
    excluded = (
        "scripts/side_effect.py", "scripts/README.md", "hooks/hooks.json", "hooks.md",
        "bin/program", ".mcp.json", "mcp.json", "image.png", "docs/page.html",
        "skills/curate/scripts/side_effect.sh", "skills/curate/references/run.py",
        "skills/curate/agents/worker.py", "agents/worker.md",
    )
    for relative in excluded:
        put(source / relative, b"EXCLUDED_BODY_NOT_TO_READ\x00")
    (source / "bin/program").chmod(0o755)
    before = tree_state(cache)
    with unreadable(monkeypatch, [source / p for p in excluded]):
        result = api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    entry = result["plugins"][0]
    target = Path(entry["package_root"])
    actual = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()}
    assert actual == allowed
    assert set(entry["files"]) == allowed
    for relative in allowed:
        assert (target / relative).read_bytes() == (source / relative).read_bytes()
        assert entry["files"][relative] == digest(source / relative)
    assert tree_state(cache) == before


def test_executable_text_is_excluded_without_reading(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    executable = put(source / "skills/curate/references/executable.md", "DO_NOT_LOAD_EXECUTABLE")
    executable.chmod(0o755)
    before = tree_state(cache)
    with unreadable(monkeypatch, [executable]):
        result = api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    entry = result["plugins"][0]
    assert "skills/curate/references/executable.md" not in entry["files"]
    assert not (Path(entry["package_root"]) / "skills/curate/references/executable.md").exists()
    assert tree_state(cache) == before


def test_binary_or_non_utf8_instruction_is_rejected_before_writing(tmp_path):
    api = extraction_module()
    for index, raw in enumerate((b"text\x00binary", b"invalid-utf8-\xff\xfe")):
        cache = tmp_path / str(index) / "cache"
        source = package(cache)
        put(source / "skills/curate/references/guide.md", raw)
        before = tree_state(cache)
        repo = tmp_path / str(index) / "repo"
        with pytest.raises(ValueError, match="unsafe_instruction"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert not repo.exists() and tree_state(cache) == before


def test_new_plugins_use_the_canonical_catalog_and_pinned_sources():
    extraction_module()
    plugins = canonical().PLUGINS
    assert plugins["zotero"][1:] == ("openai-curated-remote/zotero", "0.1.2")
    assert plugins["sequence-viewer"][1:] == ("openai-curated-remote/sequence-viewer", "0.1.52")
    assert {"data", "scigrant", "anthropic-skills", "wolfram", "superpowers"} <= set(plugins)
    assert callable(getattr(canonical().ScientificPluginService, "extract_eligible", None))


def test_public_extraction_delegates_to_canonical_service_without_legacy_sync(tmp_path, monkeypatch):
    api = extraction_module()
    cls = canonical().ScientificPluginService
    calls = []
    sentinel = {"sentinel": "canonical_extract_eligible"}

    def extract(self, *, cache_root, plugin_ids):
        calls.append((self.root, Path(cache_root), plugin_ids))
        return sentinel

    def deny(*_args, **_kwargs):
        raise AssertionError("R921 não deve chamar sync bulk legado")

    monkeypatch.setattr(cls, "extract_eligible", extract, raising=False)
    monkeypatch.setattr(cls, "sync", deny)
    cache = tmp_path / "cache"
    package(cache)
    repo = tmp_path / "repo"
    assert api.extract_local_plugins(cache, repo, ["zotero"]) is sentinel
    assert calls == [(repo.resolve(), cache, ["zotero"])]


def test_extract_eligible_installs_in_the_existing_registry_with_hashes_and_policy(tmp_path):
    extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    repo = tmp_path / "repo"
    service = canonical().ScientificPluginService(repo)
    assert callable(getattr(service, "extract_eligible", None)), "Método canônico aditivo ausente"
    before = tree_state(cache)

    result = service.extract_eligible(cache_root=cache, plugin_ids=["zotero"])

    assert result["status"] == "completed"
    assert result["reference_only"] == []
    assert result["limits"] == LIMITS
    assert_no_runtime_claims(result)
    entry = result["plugins"][0]
    assert Path(entry["package_root"]) == installed_path(repo)
    assert entry["source_root"] == str(source.resolve())
    assert entry["version"] == "0.1.2" and entry["origin"] == "third_party_or_user"
    assert service._registry() == {"zotero": entry}
    assert json.loads(registry_path(repo).read_bytes()) == {"zotero": entry}
    evidence = next(row for row in result["evidence"] if row["id"] == "zotero")
    assert evidence["manifest_sha256"] == digest(source / ".codex-plugin/plugin.json")
    assert evidence["license_evidence"] and evidence["files"] == entry["files"]
    plan = service.skill("zotero", "curate")
    assert plan["skill_document"] == SKILL
    assert plan["policy"]["disable_model_invocation"] is True
    assert plan["policy"]["allow_implicit_invocation"] is False
    assert plan["executed"] is False
    row = next(p for p in service.status()["plugins"] if p["id"] == "zotero")
    assert row["hash_integrity"] is True and row["instructions_installed"] is True
    assert row["local_connector_execution"] is False
    assert tree_state(cache) == before
    assert list(repo.rglob("registry.json")) == [registry_path(repo)]


def test_existing_canonical_entries_survive_selective_extraction_and_repeat(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache, "claude-cowork/data/1.1.0", pid="data")
    package(cache)
    package(cache, SEQUENCE, pid="sequence-viewer")
    repo = tmp_path / "repo"
    api.extract_local_plugins(cache, repo, ["data"])
    service = canonical().ScientificPluginService(repo)
    retained = service._registry()["data"]
    retained_files = tree_state(installed_path(repo, "data", "1.1.0"))
    original = tree_state(cache)

    result = api.extract_local_plugins(cache, repo, ["zotero"])

    assert [p["id"] for p in result["plugins"]] == ["zotero"]
    assert set(service._registry()) == {"data", "zotero"}
    assert service._registry()["data"] == retained
    assert tree_state(installed_path(repo, "data", "1.1.0")) == retained_files
    assert not installed_path(repo, "sequence-viewer", "0.1.52").exists()
    registry_bytes = registry_path(repo).read_bytes()
    copied = tree_state(installed_path(repo))
    assert api.extract_local_plugins(cache, repo, ["zotero"])["plugins"] == result["plugins"]
    assert registry_path(repo).read_bytes() == registry_bytes
    assert tree_state(installed_path(repo)) == copied
    assert tree_state(cache) == original


def test_tampered_destination_is_not_overwritten_or_advertised_ready(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    repo = tmp_path / "repo"
    api.extract_local_plugins(cache, repo, ["zotero"])
    changed = installed_path(repo) / "skills/curate/SKILL.md"
    changed.write_text("Adulteração da fixture, preservar.\n", encoding="utf-8")
    before = tree_state(repo)
    service = canonical().ScientificPluginService(repo)
    row = next(p for p in service.status()["plugins"] if p["id"] == "zotero")
    assert row["hash_integrity"] is False and row["instructions_installed"] is False
    with pytest.raises(ValueError):
        service.skill("zotero", "curate")
    with pytest.raises(ValueError, match="destination_conflict"):
        api.extract_local_plugins(cache, repo, ["zotero"])
    assert tree_state(repo) == before


def test_selection_is_explicit_nonempty_unique_and_known_before_writing(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    before = tree_state(cache)
    cases = [(None, "invalid_selection"), ([], "invalid_selection"),
             ("zotero", "invalid_selection"), (["zotero", "zotero"], "invalid_selection"),
             (["zotero", 1], "invalid_selection"), (["unregistered"], "unknown_plugin"),
             (["zotero", "sequence-viewer"], "unknown_plugin")]
    for index, (selection, code) in enumerate(cases):
        repo = tmp_path / f"repo-{index}"
        with pytest.raises(ValueError, match=code):
            api.extract_local_plugins(cache, repo, selection)
        assert not repo.exists(), repr(selection)
    assert tree_state(cache) == before


def test_request_ids_cannot_be_paths(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    before = tree_state(tmp_path)
    for value in ("../zotero", "/tmp/zotero", "zotero/../../out", "..\\zotero", "C:\\zotero", "zotero\x00"):
        with pytest.raises(ValueError, match="unsafe_path|invalid_selection"):
            api.extract_local_plugins(cache, tmp_path / "repo", [value])
    assert tree_state(tmp_path) == before


def test_manifest_identity_version_and_skill_paths_cannot_escape(tmp_path):
    api = extraction_module()
    cases = [{"name": "../out"}, {"version": "../../out"}, {"version": "/outside"},
             {"skills": "../../outside"}, {"skills": "C:\\outside"}, {"skills": "/outside"}]
    for index, changes in enumerate(cases):
        cache = tmp_path / str(index) / "cache"
        source = package(cache)
        manifest(source, **changes)
        before = tree_state(cache)
        with pytest.raises(ValueError, match="unsafe_path"):
            api.inventory_local_plugins(cache)
        repo = tmp_path / str(index) / "repo"
        with pytest.raises(ValueError, match="unsafe_path"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert tree_state(cache) == before and not repo.exists()


def test_single_registered_id_must_match_pinned_source_and_version(tmp_path):
    api = extraction_module()
    for index, relative in enumerate(("openai-curated-remote/other-source/0.1.2", "openai-curated-remote/zotero/9.9.9")):
        cache = tmp_path / str(index) / "cache"
        package(cache, relative)
        before = tree_state(cache)
        repo = tmp_path / str(index) / "repo"
        with pytest.raises(ValueError, match="source_mismatch"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert not repo.exists() and tree_state(cache) == before


def test_duplicate_json_keys_and_conflicting_manifests_are_rejected(tmp_path):
    api = extraction_module()
    for kind in ("json_keys", "two_manifests"):
        cache = tmp_path / kind / "cache"
        source = package(cache)
        if kind == "json_keys":
            put(source / ".codex-plugin/plugin.json", '{"name":"zotero","name":"sequence-viewer","version":"0.1.2"}')
        else:
            put(source / ".claude-plugin/plugin.json", '{"name":"sequence-viewer","version":"0.1.2","license":"MIT"}')
        before = tree_state(cache)
        repo = tmp_path / kind / "repo"
        with pytest.raises(ValueError, match="duplicate_manifest"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert not repo.exists() and tree_state(cache) == before


def test_duplicate_plugin_identity_across_packages_or_versions_is_rejected(tmp_path):
    api = extraction_module()
    for index, relative in enumerate(("openai-curated-remote/other-source/0.1.2", "openai-curated-remote/zotero/9.9.9")):
        cache = tmp_path / str(index) / "cache"
        package(cache)
        package(cache, relative)
        before = tree_state(cache)
        repo = tmp_path / str(index) / "repo"
        with pytest.raises(ValueError, match="duplicate_plugin_id"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert not repo.exists() and tree_state(cache) == before


def test_sensitive_files_are_rejected_without_reading_and_before_batch_write(tmp_path, monkeypatch):
    api = extraction_module()
    names = ("auth.json", ".env", ".env.example", ".env.production", "credentials.json", "tokens.json",
             "cookies.sqlite", "history.jsonl", "id_rsa")
    for index, name in enumerate(names):
        cache = tmp_path / str(index) / "cache"
        package(cache)
        source = package(cache, SEQUENCE, pid="sequence-viewer")
        private = put(source / "docs" / name, "SYNTHETIC_SENSITIVE_FILE_DO_NOT_READ")
        before = tree_state(cache)
        repo = tmp_path / str(index) / "repo"
        with unreadable(monkeypatch, [private]):
            with pytest.raises(ValueError, match="sensitive_file"):
                api.extract_local_plugins(cache, repo, ["zotero", "sequence-viewer"])
        assert not repo.exists() and tree_state(cache) == before


def test_secret_material_in_an_instruction_is_rejected_without_payload_leak(tmp_path, capsys):
    api = extraction_module()
    values = (
        "api_key = sk-fixture-ONLY-012345678901234567890123456789",
        "Authorization: Bearer fixture-ONLY-token-01234567890123456789",
        "-----BEGIN PRIVATE KEY-----\nfixture-ONLY-not-a-real-key\n-----END PRIVATE KEY-----",
    )
    for index, secret in enumerate(values):
        cache = tmp_path / str(index) / "cache"
        source = package(cache)
        put(source / "skills/curate/references/guide.md", secret)
        before = tree_state(cache)
        repo = tmp_path / str(index) / "repo"
        with pytest.raises(ValueError, match="secret_material") as error:
            api.extract_local_plugins(cache, repo, ["zotero"])
        captured = capsys.readouterr()
        assert "fixture-ONLY" not in str(error.value) + captured.out + captured.err
        assert not repo.exists() and tree_state(cache) == before


def test_public_authentication_guidance_is_not_a_credential(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    guidance = "Public authorization and password guidance: never share credentials; no values are present.\n"
    put(source / "skills/curate/references/authorization.md", guidance)
    result = api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    target = Path(result["plugins"][0]["package_root"])
    assert (target / "skills/curate/references/authorization.md").read_text() == guidance


def test_source_symlinks_are_rejected_even_inside_the_cache(tmp_path):
    api = extraction_module()
    for kind in ("file_internal", "file_external", "directory", "package", "namespace"):
        base = tmp_path / kind
        cache = base / "cache"
        source = package(cache)
        if kind == "file_internal":
            (source / "skills/curate/references/link.md").symlink_to(source / "LICENSE")
        elif kind == "file_external":
            outside = put(base / "outside.md", "DO_NOT_TOUCH")
            (source / "scripts").mkdir()
            (source / "scripts/link.md").symlink_to(outside)
        elif kind == "directory":
            (source / "linked-references").symlink_to(source / "skills/curate/references", target_is_directory=True)
        elif kind == "package":
            actual = source.with_name("actual-package")
            source.rename(actual)
            source.symlink_to(actual, target_is_directory=True)
        else:
            namespace = cache / "openai-curated-remote"
            actual = base / "real-namespace"
            namespace.rename(actual)
            namespace.symlink_to(actual, target_is_directory=True)
        before = tree_state(base)
        with pytest.raises(ValueError, match="unsafe_path"):
            api.extract_local_plugins(cache, base / "repo", ["zotero"])
        assert tree_state(base) == before


def test_special_source_files_are_rejected_without_opening(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    fifo = source / "scripts/special-pipe"
    fifo.parent.mkdir()
    os.mkfifo(fifo)
    # Não usar tree_state no FIFO; nem teste nem extrator devem abri-lo.
    before = fifo.lstat()
    repo = tmp_path / "repo"
    with unreadable(monkeypatch, [fifo]):
        with pytest.raises(ValueError, match="unsafe_path"):
            api.extract_local_plugins(cache, repo, ["zotero"])
    after = fifo.lstat()
    assert (after.st_mode, after.st_ino, after.st_mtime_ns) == (before.st_mode, before.st_ino, before.st_mtime_ns)
    assert not repo.exists()


def test_missing_file_and_symlink_cache_roots_are_rejected(tmp_path):
    api = extraction_module()
    real_cache = tmp_path / "actual-cache"
    package(real_cache)
    file_root = put(tmp_path / "file-cache", "not a directory")
    linked = tmp_path / "linked-cache"
    linked.symlink_to(real_cache, target_is_directory=True)
    before = tree_state(tmp_path)
    for root in (tmp_path / "missing", file_root, linked):
        with pytest.raises(ValueError, match="invalid_cache|unsafe_path"):
            api.inventory_local_plugins(root)
        with pytest.raises(ValueError, match="invalid_cache|unsafe_path"):
            api.extract_local_plugins(root, tmp_path / "repo", ["zotero"])
    assert tree_state(tmp_path) == before


def test_cache_destination_overlap_is_rejected_without_writing(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    before = tree_state(tmp_path)
    for destination in (cache, source, source / "output", tmp_path):
        with pytest.raises(ValueError, match="source_destination_overlap"):
            api.extract_local_plugins(cache, destination, ["zotero"])
    assert tree_state(tmp_path) == before


def test_destination_symlink_escape_is_rejected_without_touching_outside(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    for kind in ("repo", "opencode", "storage", "packages", "plugin", "registry"):
        base = tmp_path / kind
        repo = base / "repo"
        outside = base / "outside"
        put(outside / "sentinel.txt", "PRESERVE_OUTSIDE")
        paths = {"repo": repo, "opencode": repo / ".opencode", "storage": repo / CANONICAL_STORAGE,
                 "packages": repo / CANONICAL_STORAGE / "packages",
                 "plugin": repo / CANONICAL_STORAGE / "packages/zotero", "registry": registry_path(repo)}
        link = paths[kind]
        link.parent.mkdir(parents=True, exist_ok=True)
        if kind == "registry":
            target = put(outside / "registry.json", "{}")
            link.symlink_to(target)
        else:
            link.symlink_to(outside, target_is_directory=True)
        before = tree_state(base)
        with pytest.raises(ValueError, match="unsafe_path"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert tree_state(base) == before


def test_package_limit_is_enforced_before_writing(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    package(cache, SEQUENCE, pid="sequence-viewer")
    monkeypatch.setattr(api, "MAX_PACKAGES", 1)
    before = tree_state(tmp_path)
    with pytest.raises(ValueError, match="limit_exceeded"):
        api.inventory_local_plugins(cache)
    with pytest.raises(ValueError, match="limit_exceeded"):
        api.extract_local_plugins(cache, tmp_path / "repo", ["zotero", "sequence-viewer"])
    assert tree_state(tmp_path) == before


def test_per_package_file_limit_counts_excluded_files_too(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    excluded = [put(source / f"scripts/excluded-{index}.py", "not read") for index in range(4)]
    monkeypatch.setattr(api, "MAX_FILES_PER_PACKAGE", 6)
    before = tree_state(tmp_path)
    with unreadable(monkeypatch, excluded):
        with pytest.raises(ValueError, match="limit_exceeded"):
            api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    assert tree_state(tmp_path) == before


def test_single_file_byte_limit_is_enforced_before_body_read(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    big = put(source / "skills/curate/references/big.md", b"x" * 4097)
    monkeypatch.setattr(api, "MAX_FILE_BYTES", 4096)
    before = tree_state(tmp_path)
    with unreadable(monkeypatch, [big]):
        with pytest.raises(ValueError, match="limit_exceeded"):
            api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    assert tree_state(tmp_path) == before


def test_total_byte_limit_is_enforced_before_writing(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    other = package(cache, SEQUENCE, pid="sequence-viewer")
    first_size = sum(p.stat().st_size for p in source.rglob("*") if p.is_file())
    second_size = sum(p.stat().st_size for p in other.rglob("*") if p.is_file())
    monkeypatch.setattr(api, "MAX_TOTAL_BYTES", max(first_size, second_size) + 1)
    before = tree_state(tmp_path)
    with pytest.raises(ValueError, match="limit_exceeded"):
        api.extract_local_plugins(cache, tmp_path / "repo", ["zotero", "sequence-viewer"])
    assert tree_state(tmp_path) == before


def test_existing_divergent_package_is_preserved_without_registry_creation(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    repo = tmp_path / "repo"
    put(installed_path(repo) / "skills/curate/SKILL.md", "Do not overwrite existing work")
    before = tree_state(tmp_path)
    with pytest.raises(ValueError, match="destination_conflict"):
        api.extract_local_plugins(cache, repo, ["zotero"])
    assert tree_state(tmp_path) == before
    assert not registry_path(repo).exists()


def test_invalid_retained_registry_is_rejected_without_replacing_it(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    for index, raw in enumerate((b"not-json", b"[]", b'{"data":{"id":"data","files":{"../escape":"bad"}}}')):
        repo = tmp_path / f"repo-{index}"
        put(registry_path(repo), raw)
        before = tree_state(repo)
        with pytest.raises(ValueError, match="invalid_registry"):
            api.extract_local_plugins(cache, repo, ["zotero"])
        assert tree_state(repo) == before


def test_registry_commit_failure_rolls_back_new_packages_and_cleans_staging(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    package(cache, SEQUENCE, pid="sequence-viewer")
    repo = tmp_path / "repo"
    api.extract_local_plugins(cache, repo, ["zotero"])
    before = tree_state(repo)
    original = tree_state(cache)
    actual_replace = os.replace
    attempts = []

    def fail_registry_commit(src, dst, *args, **kwargs):
        if Path(dst) == registry_path(repo):
            attempts.append(Path(dst))
            raise OSError("R921 simulated registry commit failure")
        return actual_replace(src, dst, *args, **kwargs)

    monkeypatch.setattr(os, "replace", fail_registry_commit)
    with pytest.raises(OSError, match="simulated registry commit failure"):
        api.extract_local_plugins(cache, repo, ["sequence-viewer"])
    assert attempts == [registry_path(repo)]
    assert tree_state(repo) == before
    assert tree_state(cache) == original
    assert not installed_path(repo, "sequence-viewer", "0.1.52").exists()


def test_source_change_before_registry_commit_aborts_and_cleans_staging(tmp_path, monkeypatch):
    api = extraction_module()
    cache = tmp_path / "cache"
    source = package(cache)
    repo = tmp_path / "repo"
    repo.mkdir()
    before = tree_state(repo)
    changed = []

    def wrapped_publish(actual):
        def publish(src, dst, *args, **kwargs):
            result = actual(src, dst, *args, **kwargs)
            if Path(dst) == installed_path(repo) and not changed:
                # Mudança externa determinística após promover o pacote, antes do commit.
                put(source / "LICENSE", RESTRICTED)
                changed.append(True)
            return result
        return publish

    monkeypatch.setattr(os, "rename", wrapped_publish(os.rename))
    monkeypatch.setattr(os, "replace", wrapped_publish(os.replace))
    with pytest.raises(ValueError, match="source_changed"):
        api.extract_local_plugins(cache, repo, ["zotero"])
    assert changed == [True], "Contraprova não alcançou publicação atômica de pacote"
    assert tree_state(repo) == before
    assert (source / "LICENSE").read_text() == RESTRICTED
    assert (source / "skills/curate/SKILL.md").read_text() == SKILL


def test_import_hooks_transport_and_host_calls_never_execute(tmp_path, monkeypatch):
    # Guardas autouse já estão ativas antes do import do módulo sob teste.
    api = extraction_module()
    cls = canonical().ScientificPluginService

    def deny(*_args, **_kwargs):
        raise AssertionError("Novo caminho chamou bulk sync, host ou runtime legado")

    for method in ("sync", "request", "run_local", "accept_host_response"):
        monkeypatch.setattr(cls, method, deny)
    cache = tmp_path / "cache"
    source = package(cache)
    script = put(source / "hooks/side_effect.py", "raise RuntimeError('HOOK_EXECUTED')")
    hooks = put(source / "hooks/hooks.json", '{"hooks":{"SessionStart":[{"command":"side_effect.py"}]}}')
    transport = put(source / ".mcp.json", '{"mcpServers":{"host":{"command":"DO_NOT_EXECUTE"}}}')
    manifest(source, hooks="./hooks/hooks.json", mcpServers="./.mcp.json")
    before = tree_state(cache)
    with unreadable(monkeypatch, [script, hooks, transport]):
        result = api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    assert_no_runtime_claims(result)
    assert tree_state(cache) == before
    assert not (tmp_path / "repo" / CANONICAL_STORAGE / "requests").exists()


def test_result_does_not_claim_authentication_activation_or_external_validation(tmp_path):
    api = extraction_module()
    cache = tmp_path / "cache"
    package(cache)
    report = api.inventory_local_plugins(cache)
    result = api.extract_local_plugins(cache, tmp_path / "repo", ["zotero"])
    assert_no_runtime_claims(report)
    assert_no_runtime_claims(result)
    assert result["limits"] == LIMITS
    assert result["status"] == "completed"
    assert result["plugins"][0]["files"]
    assert report["authoritative"] is False
    serialized = json.dumps(result, ensure_ascii=False)
    assert '"authenticated": true' not in serialized
    assert '"activated": true' not in serialized
    assert '"external_validation": true' not in serialized
