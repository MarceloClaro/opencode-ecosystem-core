---
spec_id: SPEC-935-R1020
title: Qdrant MCP em servidor HTTP único
component: integrations.federation_sync.runtime
status: implemented
test_file: tests/test_r1020_qdrant_http.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1020-1:
      - "tests/test_r1020_qdrant_http.py::test_qdrant_spec_uses_http_url"
    R1020-2:
      - "tests/test_r1020_qdrant_http.py::test_qdrant_entry_exposes_http_url"
    R1020-3:
      - "tests/test_r1020_qdrant_http.py::test_qdrant_server_command_remains_stdio"
---

# SPEC-935-R1020 — Qdrant MCP em servidor HTTP único

**Estado:** implementado e observado localmente; disponibilidade futura não
garantida.
**Motivo:** o modo local embarcado do Qdrant usa lock exclusivo no diretório
`.opencode/mcp/federated/data/qdrant`; duas sessões do OpenCode que abrem o
mesmo diretório fazem a segunda falhar com “already accessed by another
instance”. A correção é usar um único servidor Qdrant HTTP e apontar o MCP para
`http://127.0.0.1:6333`.

## Escopo

- `integrations/federation_sync/runtime.py`: `QDRANT_URL` em vez de
  `QDRANT_LOCAL_PATH`.
- `federation/activated.json`: reativado por `probe`/`smoke`.
- `opencode.json`: regenerado por `build_config()`.
- Container rootless `qdrant-core` e unidade systemd de usuário
  `~/.config/containers/systemd/qdrant-core.container`.
- Dados persistidos em
  `.opencode/mcp/federated/data/qdrant-server`.

## Contrato

1. O MCP `qdrant` usa `QDRANT_URL=http://127.0.0.1:6333` e não declara
   `QDRANT_LOCAL_PATH`.
2. O comando continua `mcp-server-qdrant --transport stdio`; o transporte MCP
   permanece stdio e o Qdrant é o servidor HTTP de apoio.
3. O container `qdrant-core` é rootless, publica apenas
   `127.0.0.1:6333` e monta o diretório de dados.
4. A unidade systemd de usuário mantém o container ativo; `linger=yes` permite
   a inicialização sem sessão aberta.
5. A telemetria do Qdrant é desativada por
   `QDRANT__TELEMETRY_DISABLED=true`.
6. `probe`, `smoke` e `activate` devem passar depois da migração; a saúde do
   container é observada por `healthz`.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1020-1` — A especificação do servidor qdrant usa `QDRANT_URL` e não contém
  `QDRANT_LOCAL_PATH`.
- `R1020-2` — A entrada derivada do `ServerSpec` publica `QDRANT_URL` e não
  publica o caminho local.
- `R1020-3` — O comando do servidor permanece stdio e aponta para
  `mcp-server-qdrant`.

## Evidência observada

- Imagem `docker.io/qdrant/qdrant:latest` obtida por Podman rootless; ID
  `8a80c5500151`.
- Container `qdrant-core` ativo, porta `127.0.0.1:6333`, volume persistente.
- `healthz` respondeu `healthz check passed`; a coleção
  `core_federation_smoke` foi preservada.
- `probe` e `smoke` do MCP qdrant passaram; `activate` manteve seis servidores.
- `opencode mcp list` mostrou `qdrant connected`.
- Telemetria do Qdrant desativada no log (`Telemetry reporting disabled`).

## Limites

A imagem foi obtida da rede e não está fixada por digest; o uso de `latest`
pode mudar em uma nova obtenção. O container consome memória/CPU e depende do
Podman rootless e do systemd de usuário. O teste verifica a configuração, não a
disponibilidade contínua; `healthz` é uma observação pontual. Nenhum dado
pessoal foi migrado ou apagado; a migração preservou o diretório antigo.
