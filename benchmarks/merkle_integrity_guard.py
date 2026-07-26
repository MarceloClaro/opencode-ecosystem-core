# -*- coding: utf-8 -*-
"""
MerkleIntegrityGuard — Árvore de Merkle para Integridade Criptográfica do Código
================================================================================
Calcula a Merkle Root dos arquivos python do repositório para garantir imutabilidade
e detecção de adulterações em tempo real.
"""

from __future__ import annotations

import os
import glob
import hashlib
from typing import List, Dict, Any, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MerkleIntegrityGuard:
    """Gerenciador de Árvore de Merkle para o código-fonte do ecossistema."""

    def __init__(self, root_dir: str = REPO_ROOT):
        self.root_dir = root_dir

    def _hash_file(self, filepath: str) -> str:
        """Calcula o hash SHA-256 individual de um arquivo."""
        h = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _build_merkle_root_from_hashes(self, hashes: List[str]) -> str:
        """Calcula a raiz da Árvore de Merkle a partir de uma lista de hashes."""
        if not hashes:
            return ""
        if len(hashes) == 1:
            return hashes[0]

        # Garante contagem par duplicando o último se necessário
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i + 1]
            parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            next_level.append(parent_hash)

        return self._build_merkle_root_from_hashes(next_level)

    def compute_merkle_root(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """Varre os arquivos Python no diretório alvo e gera a Merkle Root."""
        base_dir = target_dir or self.root_dir
        file_hashes: Dict[str, str] = {}

        # Coleta arquivos .py nos diretórios principais
        subdirs = ["marceloclaro", "sdd", "evolution", "scanners", "research", "mci", "integrations", "benchmarks"]
        py_files = []
        for sd in subdirs:
            p = os.path.join(base_dir, sd)
            if os.path.exists(p):
                for filepath in sorted(glob.glob(os.path.join(p, "**", "*.py"), recursive=True)):
                    py_files.append(filepath)

        for filepath in sorted(py_files):
            rel_path = os.path.relpath(filepath, base_dir)
            file_hashes[rel_path] = self._hash_file(filepath)

        sorted_hashes = [file_hashes[k] for k in sorted(file_hashes.keys())]
        root_hash = self._build_merkle_root_from_hashes(sorted_hashes)

        return {
            "merkle_root": root_hash,
            "total_files": len(file_hashes),
            "file_hashes": file_hashes,
        }

    def verify_integrity_snapshot(self, expected_root: str) -> Dict[str, Any]:
        """Verifica se a Merkle Root atual coincide com a raiz esperada."""
        current = self.compute_merkle_root()
        matched = current["merkle_root"] == expected_root
        return {
            "matched": matched,
            "current_root": current["merkle_root"],
            "expected_root": expected_root,
            "status": "integrity_verified" if matched else "tampering_detected",
        }


merkle_integrity_guard = MerkleIntegrityGuard()
