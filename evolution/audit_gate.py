# -*- coding: utf-8 -*-
"""
EvolutionAuditGate — Cadeia de Custódia Auditável (SPEC-935-R462)
================================================================
Fecha o gargalo "produzir IA com IA" (R461) impondo tres condicoes por ciclo:

  (i)   imutabilidade  : cada artefato tem hash SHA-256 registrado no momento
                         da producao (anti-tamper);
  (ii)  verificacao    : todo ciclo precisa de um `external_verdict` aprovado
                         por uma instancia DISTINTA do gerador (quebra
                         gerador=julgador);
  (iii) rastreabilidade: trilha de evidencia (spec, testes, scans) sustenta
                         cada alegacao.

Fail-closed: a verificacao so passa se TODAS as condicoes forem satisfeitas.
Se `verifier_identity == generator_identity`, o ciclo e rejeitado.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence


@dataclass
class AuditResult:
    passed: bool = False
    reason: str = ""
    tampered: bool = False
    hashes: Dict[str, str] = field(default_factory=dict)
    verifier: str = ""
    merkle_root: str = ""  # hash agregado dos artefatos (imutabilidade composta)


class EvolutionAuditGate:
    """Gate fail-closed de auditoria externa sobre um ciclo de evolucao.

    Endurecido (SPEC-935-R462, fase "implemente minuciosamente"):
      - aceita arquivos reais em disco (auto-hash), alem de bytes em memoria;
      - oferece `merkle_root` (hash agregado dos artefatos) como ancora de
        imutabilidade composta;
      - oferece `hash_state` para ancorar o proprio cycles.json (integridade
        do estado evolutivo).
    """

    def _sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _sha256_file(self, path: str) -> str:
        """Hash SHA-256 de um arquivo real em disco (blocos de 64 KiB)."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def resolve_artifacts(
        self, artifact_files: Mapping[str, object]
    ) -> Dict[str, str]:
        """Converte artefatos (bytes OU caminho real) em map {nome: sha256}.

        Se o valor for `bytes`, hasheia diretamente; se for `str`/`Path`,
        hasheia o conteudo do arquivo em disco. Permite uso pratico sem
        carregar tudo em memoria e ancora imutabilidade real do disco.
        """
        hashes: Dict[str, str] = {}
        for name, value in artifact_files.items():
            if isinstance(value, (bytes, bytearray)):
                hashes[name] = self._sha256(bytes(value))
            else:
                hashes[name] = self._sha256_file(str(value))
        return hashes

    def merkle_root(self, hashes: Mapping[str, str]) -> str:
        """Hash agregado (Merkle-like) de um conjunto de artefatos.

        Ordena os (nome, hash) por nome e combina com SHA-256 de forma
        canonica, garantindo que a raiz muda se QUALQUER artefato (nome ou
        conteudo) mudar. E uma ancora unica e compacta de imutabilidade
        composta do ciclo.
        """
        if not hashes:
            return ""
        joined = "\n".join(f"{name}:{hashes[name]}"
                           for name in sorted(hashes))
        return self._sha256(joined.encode("utf-8"))

    def hash_state(self, state_bytes: bytes) -> str:
        """Hash SHA-256 de um estado serializado (ex.: conteudo de cycles.json).

        Permite ancorar o proprio registro evolutivo a um ciclo: prova em que
        estado exato o ciclo foi registrado (imutabilidade do estado).
        """
        return self._sha256(state_bytes)

    def verify_cycle(
        self,
        *,
        objective: str,
        changes: List[str],
        artifact_files: Mapping[str, object],  # bytes OU caminho real
        verifier_identity: str,
        generator_identity: str,
        evidence_trail: Optional[List[str]] = None,
    ) -> AuditResult:
        """Valida um ciclo antes da persistencia. Fail-closed: recusa se
        qualquer condicao de custodio falhar. `artifact_files` aceita bytes
        ou caminhos reais (auto-hash de disco)."""
        # (ii) verificacao externa: gerador != verificador
        if not verifier_identity:
            return AuditResult(passed=False,
                               reason="sem identidade de verificador externo")
        if verifier_identity == generator_identity:
            return AuditResult(
                passed=False,
                reason="verificador == gerador: viola condicao (ii) "
                       "(gerador nao pode julgar a si mesmo)",
            )
        if not artifact_files:
            return AuditResult(passed=False,
                               reason="sem artefatos para ancorar hash")

        # (i) calcular hashes (bytes ou disco)
        hashes = self.resolve_artifacts(artifact_files)
        merkle = self.merkle_root(hashes)
        # (iii) trilha de evidencia
        if not evidence_trail:
            return AuditResult(
                passed=False,
                reason="sem trilha de evidencia (spec/teste/scan) que sustente "
                       "as mudancas",
                tampered=False, hashes=hashes, verifier=verifier_identity,
                merkle_root=merkle,
            )
        return AuditResult(
            passed=True,
            reason="auditoria externa aprovada",
            tampered=False, hashes=hashes, verifier=verifier_identity,
            merkle_root=merkle,
        )

    def verify_tamper(
        self,
        *,
        artifact_files: Mapping[str, object],  # bytes OU caminho real
        registered_hashes: Mapping[str, str],
    ) -> AuditResult:
        """Compara os hashes reais com os registrados. Se divergem =>
        tampered=True (imutabilidade violada). Aceita bytes ou caminhos."""
        real = self.resolve_artifacts(artifact_files)
        mismatches = [
            name for name in real
            if name not in registered_hashes
            or registered_hashes[name] != real[name]
        ]
        if mismatches:
            return AuditResult(
                passed=False,
                tampered=True,
                reason=f"tamper detectado em: {', '.join(mismatches)}",
                hashes=real,
            )
        return AuditResult(
            passed=True,
            tampered=False,
            reason="hashes conferem, sem tamper",
            hashes=real,
        )

    def verify_merkle(
        self,
        *,
        hashes: Mapping[str, str],
        registered_root: str,
    ) -> bool:
        """Confere se o merkle_root calculado dos hashes bate com o ancorado."""
        return registered_root == self.merkle_root(hashes)


def git_head_commit() -> str:
    """Retorna o hash do commit HEAD do repositorio (ancora externa).

    Prova em qual versao do codigo-fonte um ciclo foi registrado. Retorna
    string vazia se o repositorio nao estiver disponivel (nao falsifica).
    """
    try:
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return ""
