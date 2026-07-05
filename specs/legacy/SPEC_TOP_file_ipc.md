# SPEC-TOP-006: File IPC
Version: 1.0.0 | Domain: ipc

## Objective
Sistema de comunicacao entre processos via filesystem. Inspirado pelo simulation_ipc.py do MiroFish. Implementa o lado cliente do protocolo File IPC com file locks e archive.

## Acceptance Criteria
- [x] CT-1: FileIPCClient creates necessary directories
- [x] CT-2: send_command returns valid UUID-based ID
- [x] CT-3: send_and_wait handles timeout gracefully
- [x] CT-4: cleanup removes orphan commands

## Assets
- scripts/ipc_client.py
- references/protocol.md
- tests/test_file_ipc.py
