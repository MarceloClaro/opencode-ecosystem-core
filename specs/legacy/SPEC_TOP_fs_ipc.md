# SPEC-TOP-007: FS-IPC (Refined)
Version: 1.0.0 | Domain: ipc

## Objective
Comunicacao entre processos via filesystem (refinado). Refina o padrao P2 file-ipc com arquitetura Client/Server completa, CommandType enum, env_status heartbeat, e demo integrado.

## Acceptance Criteria
- [x] CT-1: IPCClient initialization creates dirs
- [x] CT-2: CommandType enum has INTERVIEW, CUSTOM, CLOSE_ENV
- [x] CT-3: IPCCommand serialization round-trip
- [x] CT-4: Demo mode completes full cycle without errors

## Assets
- scripts/ipc_client.py
- references/protocol.md
- tests/test_fs_ipc.py
