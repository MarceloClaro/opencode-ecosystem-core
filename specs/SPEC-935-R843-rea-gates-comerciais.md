---
spec_id: SPEC-935-R843
title: REA — gates fail-closed das camadas de licença comercial (IDA, Hopper, JEB)
component: integrations/rea_layers, outputs/core-r843
status: implemented
round_id: R843
test_file: tests/test_r843_rea_config_gates.py
---

# SPEC-935-R843 — Gates de configuração das 3 camadas comerciais

## Problema e correção de defeito

A SPEC-935-R842 deixou `native_ida`, `native_hopper` e `jeb` pendentes por
licença/serviço comercial. Uma auditoria dos docs oficiais do REA 6.4.0 revelou
um defeito herdado do R841: `native_hopper` declarava
`REA_HOPPER_CONFORMANCE_MANIFEST_PATH`, que **não existe no runtime do REA** —
aparece apenas nos scripts de verificação (`scripts/verify-real-hopper*.mjs`). A
variável real do provedor Hopper é **`HOPPER_LAUNCHER_PATH`**
(`docs/installation.md#hopper`), com caminhos padrão
`/opt/hopper/bin/Hopper` e `~/.local/share/rea/hopper/bin/Hopper` (e o DMG no
macOS). Classe de defeito idêntica à do R841 (nome inventado).

Também foi fechado um risco de overclaim: `_env_state` marcava uma camada como
pronta apenas com o arquivo/URL **presente**, sem validar o **formato** — um
`REA_IDA_MCP_CONFIG` com JSON inválido ou uma `REA_JEB_MCP_URL` remota
marcariam "pronta" e falhariam na execução.

## Contratos de aceite

1. **native_ida** — `REA_IDA_MCP_CONFIG`: só fica pronta se o arquivo existe
   **e** casa um dos formatos de `docs/ida-provider.md`: registro stdio
   (`command` string + `args` lista de strings), supervisor headless
   (`mode: "headless"`, `env`, `url` http/https local), ou objeto `mcpServers`
   com entrada `ida-pro-mcp`. `{}`, JSON inválido, `args` não-string, `mode`
   desconhecido e `mcpServers` sem `ida-pro-mcp` são rejeitados.
2. **native_hopper** — `HOPPER_LAUNCHER_PATH`: env var corrigida para a real do
   REA; pronta quando há executável (override do operador ou descoberta dos
   caminhos padrão documentados). Nenhum manifesto conformance é inventado.
3. **jeb** — `REA_JEB_MCP_URL`: pronta somente com configuração **explícita** e
   válida segundo `docs/jeb-analysis.md` — http/https absoluto com host literal
   `127.0.0.1` ou `[::1]`, sem credenciais, query ou fragmento. O default do REA
   (`http://127.0.0.1:8425/mcp`) **não** marca pronta sem configuração explícita,
   pois nenhum liveness é sondado (fail-closed).
4. Nenhum provedor é iniciado, nenhum alvo é aberto e nenhuma confiança é
   promovida; as três permanecem **pendentes** sem a licença do operador.
5. Sonda real: 18 camadas, 15 prontas, 3 pendentes; recibo em
   `outputs/core-r843/config-gates.json` com `externally_validated=false`.

## Fontes (documentação oficial do REA 6.4.0 embarcada)

- `docs/ida-provider.md` — formatos de `REA_IDA_MCP_CONFIG`.
- `docs/installation.md#hopper` — `HOPPER_LAUNCHER_PATH` e caminhos padrão.
- `docs/jeb-analysis.md` — `REA_JEB_MCP_URL` e restrições de URL local.

## Remediação para o operador

| Camada | Configuração | Pré-requisito do operador |
|---|---|---|
| native_ida | `REA_IDA_MCP_CONFIG=/abs/ida-mcp.json` | IDA + Hex-Rays licenciados; `mrexodia/ida-pro-mcp` |
| native_hopper | `HOPPER_LAUNCHER_PATH=/abs/Hopper` | Hopper demo/licença; Ubuntu 24.04+/macOS 12+ |
| jeb | `REA_JEB_MCP_URL=http://127.0.0.1:8425/mcp` | JEB 5.x licenciado servindo MCP local |

## Verificação

- `tests/test_r843_rea_config_gates.py`: 20 casos (aceitação/rejeição por
  formato, exigência de configuração explícita, descoberta do launcher,
  presença do recibo).
- Suítes REA R808/R841/R842/R843: 128 verdes; doctor 22/22.