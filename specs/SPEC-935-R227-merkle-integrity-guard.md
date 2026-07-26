---
spec_id: SPEC-935-R227
title: "Guardião de Integridade Merkle Tree de Código-Fonte (Merkle Integrity Guard)"
component: benchmarks/merkle_integrity_guard.py
test_file: tests/test_r227_merkle_integrity_guard.py
status: green
---

# SPEC-935-R227 — Guardião de Integridade Merkle Tree
===================================================

## 1. Visão Geral
Esta especificação introduz o **`MerkleIntegrityGuard`**, uma estrutura de dados de Árvore de Merkle que calcula a raiz de integridade criptográfica SHA-256 de todos os módulos de código do ecossistema (`marceloclaro/`, `sdd/`, `evolution/`, `scanners/`, `research/`, `mci/`, `integrations/`, `benchmarks/`).

## 2. Requisitos Funcionais
- **Raiz da Árvore de Merkle (Merkle Root)**: Agrega o hash individual dos arquivos `.py` e gera a hash do nó raiz imutável.
- **Detecção de Adulteração**: Se qualquer arquivo for alterado sem atualização correspondente de especificação/ciclo, a raiz difere e um evento de alteração não autorizada é emitido.
- **Interface da Classe `MerkleIntegrityGuard`**:
  - `compute_merkle_root(target_dir: Optional[str] = None) -> str`
  - `verify_integrity_snapshot(expected_root: str) -> Dict[str, Any]`
