"""Worker R850: só é aceito dentro de namespaces de rede e PID privados."""
from __future__ import annotations

from contextlib import nullcontext, redirect_stdout
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


class LocalHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.counts = {"script": 0, "form": 0, "a": 0, "input": 0}
        self.references = []
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in self.counts:
            self.counts[tag] += 1
        if tag == "title":
            self.in_title = True
        for key, value in attrs:
            if key in ("src", "href", "action") and value and len(self.references) < 100:
                self.references.append({"tag": tag, "attribute": key, "value": value[:1000]})

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and sum(len(x) for x in self.title) < 1000:
            self.title.append(data[:1000])


def main():
    request = json.loads(sys.stdin.buffer.read(65537))
    config = request["config"]
    network = os.readlink("/proc/self/ns/net")
    if network == request["parent_namespace"] or os.getpid() != 1:
        raise ValueError("Worker exige namespaces privados de rede/PID.")
    subprocess.run(["/usr/sbin/ip", "link", "set", "lo", "up"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    interfaces = sorted(name for _, name in socket.if_nameindex())
    if interfaces != ["lo"]:
        raise ValueError("Rede do worker possui interface externa.")
    privacy = {"mode": "isolated_local_analysis", "network_namespace": network,
        "pid_namespace": os.readlink("/proc/self/ns/pid"), "interfaces": interfaces,
        "external_route_available": False, "host_probe_connected": False,
        "scope": "analytical_worker_and_descendants; trusted_local_MCP_client_required"}
    if config["operation"] == "probe":
        port = config.get("probe_port")
        if port is not None:
            if type(port) is not int or not 1 <= port <= 65535:
                raise ValueError("Porta de contraprova inválida.")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    privacy["host_probe_connected"] = True
            except OSError:
                pass
        print(json.dumps({"success": True, "operation": "probe", "privacy": privacy,
                          "externally_validated": False}))
        return
    # Imports do Core podem emitir avisos legados; jamais contaminam stdout IPC.
    with redirect_stdout(sys.stderr):
        from integrations.rea_assistant import worker_environment, target_digest, prepare_javascript_target, provider_findings
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from integrations.rea_bridge import ReaBridge
    workspace = Path(request["workspace"]).resolve()
    environment = worker_environment(os.environ, root=workspace)
    os.environ.clear()
    os.environ.update(environment)
    path = Path(config["path"]).resolve(strict=True)
    kind = config["kind"]
    before = target_digest(path)
    limitations = ["A aplicação alvo não foi executada; achados são estáticos.",
        "Inspeção e metadados não recuperam necessariamente o código-fonte original.",
        "A garantia local cobre o worker; clientes de inferência em nuvem não fazem parte deste modo."]
    if kind == "html":
        file = path / "index.html" if path.is_dir() else path
        data = file.read_bytes()
        if len(data) > 1024 * 1024:
            raise ValueError("HTML excede 1 MiB.")
        parser = LocalHTML()
        parser.feed(data.decode("utf-8", errors="replace"))
        evidence_id = "ev_core_html_" + before["sha256"][:24]
        result = {"success": True, "evidence_id": evidence_id,
            "operation": "inspect_local_html", "title": "".join(parser.title),
            "declared_elements": parser.counts, "references": parser.references}
        findings = [{"description": "Título declarado: " + (result["title"] or "ausente") + ".", "evidence_id": evidence_id},
                    {"description": f"HTML declara {parser.counts['form']} formulário(s) e {parser.counts['script']} script(s).", "evidence_id": evidence_id}]
        limitations.append("Links e scripts foram enumerados, sem acesso aos destinos nem execução de JavaScript.")
    else:
        mapping = {"dotnet": "managed_dotnet", "plist": "apple", "android": "android_jadx",
                   "firmware": "firmware", "elf-layout": "native_offline_elf"}
        operation = "analyze_binary" if kind == "native" else "analyze" if kind == "javascript" else "layer"
        action = {"operation": operation, "path": str(path), "timeout_seconds": config.get("timeout_seconds", 60)}
        if operation == "layer":
            action["layer"] = mapping[kind]
        if operation == "analyze_binary":
            action["procedure"] = config.get("procedure", "main")
        prepared = prepare_javascript_target(path) if kind == "javascript" else nullcontext(path)
        with prepared as provider_path, redirect_stdout(sys.stderr):
            action["path"] = str(provider_path)
            result = MarceloClaroOrchestrator(auto_load_agents=False).rea_action(action)
        if kind == "javascript" and path.is_file() and path.suffix.lower() != ".asar":
            limitations.append("Arquivo JavaScript avulso copiado sem alteração para diretório temporário: imports e arquivos vizinhos não foram incluídos.")
        if result.get("success") is not True:
            result.update(privacy=privacy, target_kind=kind, target_digest=before,
                          limitations=limitations, externally_validated=False)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
            return
        response = result.get("response", {})
        value = ReaBridge._structured(response.get("analysis", {})) if kind == "native" else ReaBridge._structured(response)
        if not isinstance(value, dict) or not value.get("evidence_id"):
            raise ValueError("Provider não entregou Evidence identificada.")
        evidence_id = value["evidence_id"]
        normalized = value.get("normalized_result", {})
        subject = value.get("subject", {})
        subject_sha = subject.get("digest", {}).get("sha256") if isinstance(subject, dict) and isinstance(subject.get("digest"), dict) else None
        adapted_javascript = kind == "javascript" and path.is_file() and path.suffix.lower() != ".asar"
        if path.is_file() and not adapted_javascript and subject_sha is not None and subject_sha != before["sha256"]:
            raise ValueError("Evidence do provider identifica bytes diferentes do alvo solicitado.")
        if subject_sha is None:
            limitations.append("Provider não declara digest de bytes do alvo; o recibo usa digest independente antes/depois.")
        findings = [{"description": "O provider realizou " + str(value.get("operation")) + ".", "evidence_id": evidence_id}]
        statistics = normalized.get("statistics", {}) if isinstance(normalized, dict) else {}
        for key, item in list(statistics.items())[:8]:
            if isinstance(item, (int, str, float)) and not isinstance(item, bool):
                findings.append({"description": f"Contagem/medida declarada pelo provider — {key}: {item}.", "evidence_id": evidence_id})
        findings.extend(provider_findings(value))
        limitations.extend(str(item) for item in value.get("limitations", [])[:20])
        if isinstance(normalized, dict) and isinstance(normalized.get("limitations"), list):
            limitations.extend(str(item) for item in normalized["limitations"][:20] if str(item) not in limitations)
        if kind == "dotnet":
            limitations.append("Metadados .NET identificam estruturas declaradas; não equivalem à decompilação completa.")
    after = target_digest(path)
    if after != before:
        raise ValueError("Alvo mudou durante a análise; resultado recusado.")
    print(json.dumps({"schema": "core-rea-local-v1", "success": True, "status": "completed",
        "operation": "inspect", "target_kind": kind, "target_path": str(path),
        "target_digest": before, "target_unchanged": True, "privacy": privacy,
        "findings": findings, "limitations": limitations, "provider_report": result,
        "externally_validated": False}, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"success": False, "status": "failed", "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
