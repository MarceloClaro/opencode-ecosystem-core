# -*- coding: utf-8 -*-
"""Política declarativa de sandbox científico (M2 — OpenShell/NemoClaw adaptado).

Traduz o modelo de 4 camadas do OpenShell (filesystem, network, process,
providers) para decisões locais aplicáveis a tarefas de pesquisa: coleta de
dados, scraping bibliográfico e execução de código estatístico.

Segurança (invariantes da SPEC-935-R471):
- fail-closed: ausência de política ou de matcher ⇒ negação com recibo;
- egresso padrão negado; allowlist de endpoints bibliográficos explícita;
- nenhum despacho de processo com shell/interpolação (invariante 4);
- credenciais jamais aparecem em recibos (invariante 5).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from urllib.parse import urlparse

DEFAULT_BIBLIOGRAPHIC_ENDPOINTS = frozenset({
    # Descoberta e metadados
    "openalex.org",
    "api.crossref.org",
    "europepmc.org",
    "export.arxiv.org",
    "arxiv.org",
    "api.semanticscholar.org",
    "core.ac.uk",
    "api.ncbi.nlm.nih.gov",
    "pubmed.ncbi.nlm.nih.gov",
    "doi.org",
    "api.datacite.org",
    # Ciência aberta em língua portuguesa / latino-americana
    "scielo.org",
    "scielo.br",
    "lilacs.bvsalud.org",
    # Repositórios e dados
    "zenodo.org",
    "api.github.com",
    "huggingface.co",
})

# Prefixos de filesystem sempre negados (superfície sensível).
DENIED_FS_PREFIXES = (
    "/etc",
    "/root",
    "/proc",
    "/sys",
    "/dev",
    "/boot",
    "/usr",
    "/bin",
    "/sbin",
    "/var",
    "/home",
)

# Binários de processo permitidos por padrão; shells interativos negados.
ALLOWED_PROCESS_BINS = frozenset({
    "python3",
    "python",
    "Rscript",
    "uv",
    "pip",
    "pip3",
    "git",
    "make",
    "pytest",
})

BIOLOGRAPHIC_SCHEMES = frozenset({"https", "http"})


SCIENTIFIC_TEMPLATE_YAML = """\
# Política de sandbox científico (SPEC-935-R478 / M2 da R471)
# Modelo OpenShell de 4 camadas adaptado a tarefas de pesquisa.
# Padrão: negação (deny) — tudo que não está na allowlist é bloqueado.
policy_id: scientific-default
version: 1.0.0
network:
  default_egress: deny
  allow_egress:
    - openalex.org
    - api.crossref.org
    - europepmc.org
    - export.arxiv.org
    - arxiv.org
    - api.semanticscholar.org
    - core.ac.uk
    - api.ncbi.nlm.nih.gov
    - pubmed.ncbi.nlm.nih.gov
    - doi.org
    - api.datacite.org
    - scielo.org
    - scielo.br
    - lilacs.bvsalud.org
    - zenodo.org
    - api.github.com
    - huggingface.co
filesystem:
  default_access: allow_workspace
  deny_prefixes:
    - /etc
    - /root
    - /proc
    - /sys
    - /dev
    - /boot
    - /usr
    - /bin
    - /sbin
    - /var
    - /home
process:
  allow_bins:
    - python3
    - python
    - Rscript
    - uv
    - pip
    - pip3
    - git
    - make
    - pytest
  deny_shell_interpolation: true
providers:
  default_access: deny
  allow_endpoints:
    - http://localhost:11434
    - http://127.0.0.1:11434
"""


@dataclass
class PolicyDecision:
    """Recibo auditável de uma decisão de política (M2)."""

    allowed: bool
    layer: str
    reason: str
    policy_id: str = "scientific-default"
    policy_version: str = "1.0.0"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "layer": self.layer,
            "reason": self.reason,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
        }

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"PolicyDecision(allowed={self.allowed}, layer={self.layer}, reason={self.reason!r})"


class DeclarativePolicy:
    """Validador local de política declarativa YAML (4 camadas).

    Sem política carregada, o comportamento é fail-closed: toda consulta
    resulta em ``PolicyDecision(allowed=False)``.
    """

    def __init__(self, policy: Optional[Dict[str, Any]] = None, policy_id: str = "none") -> None:
        self.policy: Dict[str, Any] = policy or {}
        self.policy_id = str(self.policy.get("policy_id", policy_id))
        self.policy_version = str(self.policy.get("version", "0.0.0"))

    # -- carregamento ------------------------------------------------------

    @classmethod
    def from_yaml(cls, text: str) -> "DeclarativePolicy":
        import yaml

        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("Política YAML inválida: esperado mapeamento raiz.")
        return cls(data, policy_id=str(data.get("policy_id", "custom")))

    # -- helpers -----------------------------------------------------------

    def _deny(self, layer: str, reason: str) -> PolicyDecision:
        return PolicyDecision(False, layer, reason, self.policy_id, self.policy_version)

    def _allow(self, layer: str, reason: str) -> PolicyDecision:
        return PolicyDecision(True, layer, reason, self.policy_id, self.policy_version)

    @property
    def network_default(self) -> str:
        return str(self.policy.get("network", {}).get("default_egress", "deny"))

    # -- camada network ----------------------------------------------------

    def check_egress(self, url: str) -> PolicyDecision:
        """Decide se o egresso de rede para ``url`` é permitido."""
        if not self.policy:
            return self._deny("network", "política ausente: egresso negado por padrão (fail-closed).")
        try:
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
        except ValueError:
            return self._deny("network", "URL inválida: egresso negado.")

        if self.network_default != "deny":
            return self._deny("network", "política sem default_egress=deny não é aceita pelo Core.")

        allow_egress = {str(e).lower() for e in self.policy.get("network", {}).get("allow_egress", [])}
        if not allow_egress:
            return self._deny("network", "allowlist de egresso vazia: egresso negado.")

        if any(host == entry or host.endswith(f".{entry}") for entry in allow_egress):
            return self._allow("network", f"Endereço bibliográfico autorizado ({host}).")
        return self._deny("network", f"Egresso não autorizado para {host} (fora da allowlist bibliográfica).")

    # -- camada filesystem -------------------------------------------------

    def check_filesystem(self, path: str) -> PolicyDecision:
        """Decide se o acesso a ``path`` é permitido."""
        if not self.policy:
            return self._deny("filesystem", "política ausente: acesso negado por padrão (fail-closed).")
        denied = {str(p) for p in self.policy.get("filesystem", {}).get("deny_prefixes", [])}
        for prefix in sorted(denied, key=len, reverse=True):
            if path == prefix or path.startswith(prefix.rstrip("/") + "/"):
                return self._deny("filesystem", f"Caminho sensível negado (prefixo {prefix}).")
        return self._allow("filesystem", "Caminho dentro do workspace de pesquisa.")

    # -- camada process ----------------------------------------------------

    def check_process(self, argv: list) -> PolicyDecision:
        """Decide se o despacho de processo ``argv`` é permitido.

        Invariante 4 da R471: nenhum despacho usa shell=True ou interpolação.
        """
        if not self.policy:
            return self._deny("process", "política ausente: execução negada por padrão (fail-closed).")
        if not argv or not isinstance(argv, list):
            return self._deny("process", "argv vazio ou não-lista: execução negada.")

        bin_name = str(argv[0]).split("/")[-1]
        lower_bins = {b.lower() for b in argv}

        deny_shell = self.policy.get("process", {}).get("deny_shell_interpolation", True)
        shell_bins = {"sh", "bash", "zsh", "fish", "dash", "ksh"}
        if deny_shell and bin_name in shell_bins:
            return self._deny("process", f"Shell interativo/não-despachável negado ({bin_name}).")
        if ";" in argv or "&&" in argv or "||" in argv or "|" in argv:
            return self._deny("process", "Argumentos com metacaracteres de shell negados.")
        if any("$(" in a or "${" in a for a in argv):
            return self._deny("process", "Interpolação de variável/expansão negada.")

        allow_bins = {str(b) for b in self.policy.get("process", {}).get("allow_bins", [])}
        if bin_name not in allow_bins:
            return self._deny("process", f"Binário fora da allowlist ({bin_name}).")
        return self._allow("process", f"Processo autorizado ({argv[0]}).")

    # -- camada providers --------------------------------------------------

    def check_provider(self, endpoint: str, credential_hint: Optional[str] = None) -> PolicyDecision:
        """Decide se o provider de inferência ``endpoint`` é aceito.

        Invariante 5: ``credential_hint`` jamais é incluída em recibo.
        """
        if not self.policy:
            return self._deny("providers", "política ausente: provider negado por padrão (fail-closed).")
        allow_endpoints = {str(e).rstrip("/") for e in self.policy.get("providers", {}).get("allow_endpoints", [])}
        if not allow_endpoints:
            return self._deny("providers", "allowlist de providers vazia: provider negado.")
        if endpoint.rstrip("/") in allow_endpoints:
            return self._allow("providers", "Provider local autorizado.")
        return self._deny("providers", "Provider fora da allowlist: negado.")


# Instância canônica a partir do template científico.
default_scientific_policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)