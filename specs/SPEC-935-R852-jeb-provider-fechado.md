---
spec_id: SPEC-935-R852
title: REA — JEB Community Edition instalada e provider `jeb` fechado com prova real
component: integrations/rea_layers, outputs/core-r852
status: implemented
round_id: R852
test_file: tests/test_r852_jeb_provider.py
---

# SPEC-935-R852 — JEB CE instalada e provedor `jeb` verificado

## Contexto e decisão

A camada `jeb` estava pendente por depender de um serviço/engine comercial do
operador (`REA_JEB_MCP_URL`). A documentação do REA 6.4.0 verifica o provider
contra **JEB 5.48.0** servindo **`jeb-mcp-server` 1.3.0**. A PNF Software
distribui a **JEB Community Edition (JEB CE) inteiramente grátis**, para x86/
x86-64, com o MCP nativo embutido — **sem exigir conta** no download.

Decisão: instalar a JEB CE a partir da fonte oficial, ativar a licença gratuita
(preservando o aceite da EULA como ato do operador), subir o MCP headless e
provar leitura real de um ELF. Nada é promovido.

Correção de rota registrada: o IDA está fora de escopo aqui — `ida-pro-mcp` não
suporta IDA Free (sem IDAPython/plugins). O IDA exige licença paga; a via nativa
gratuita já é coberta pela camada `native_ghidra` (já pronta).

## Contratos de aceite

1. Baixar o ZIP oficial (`https://www.pnfsoftware.com/dl?jeb4ce`, redireciona
   para o S3 da PNF) **sem conta** e verificar **bytes e SHA-256**; divergência
   aborta. ZIP íntegro antes de extrair.
2. Extrair para `~/.local/share/opencode-core/native-rea/jeb-ce-5.48.0` e
   satisfazer o requisito de **JRE ≥ 21**.
3. Ativação **somente com o aceite da EULA pelo operador**; a chave de licença
   (gratuita, ligada à máquina) é obtida pelo endpoint oficial de geração e
   **não é gravada** em nenhum artefato do Core.
4. Subir o MCP headless (`-c --mcp --interface=127.0.0.1 --port=8425`) e
   confirmar `serverInfo` = `jeb-mcp-server 1.3.0`.
5. O gate do Core (`REA_JEB_MCP_URL`, fail-closed de `_validate_local_mcp_url`)
   deve marcar `jeb` como pronta.
6. **Prova real** via REA: `inspect-jeb-client`, `list-jeb-units` e
   `decompile-jeb-item` com `evidence_id` preservado.
7. Nada é promovido: `externally_validated=false`, `confidence_promoted=false`.
8. Nenhum nome de variável/caminho inventado: só `REA_JEB_MCP_URL` (documentado)
   e locais oficialmente definidos.

## Resultado

- Integridade: bytes 697549250 ✓, SHA-256
  `709e7fe8e88bb0e9e2bc03b028f8b9fc78cec0289d04abe54fc26cda6369e175` ✓.
- Licença: build `jeb-ce` (`release/full/individual/air-gap/any-client/core-api/
  perpetual`); chave de máquina gerada via endpoint oficial e **não registrada**.
- `inspect-jeb-client`: `version 5.48.0.202610071539`, `gui_client false`,
  `evidence_id ev_81d15d2a…`.
- `list-jeb-units`: `soma/soma` (elf), `soma/soma/metadata`,
  `soma/soma/x86_64-image`; `evidence_id ev_5aa858e1…`; `coverage complete`.
- `decompile-jeb-item`:
  - `soma` → `long soma(int param0, int param1) { return (uint64_t)(param1 + param0); }`
    (`ev_874890ad…`);
  - `main` → `int main() { return (int)soma(2, 3); }` (`ev_a561ce57…`);
  - `sub_11026` → `long sub_11026() { return gvar_13FD0(); }` (`ev_c0e24909…`).
- Sonda final: **18 camadas, 17 prontas, 1 pendente** (`native_ida`).

## Limites e remanescente

O JEB 5.48.0 **headless não anuncia** `open_project`; o alvo é selecionado na
partida do engine (`--infile`), e o REA preserva essa recusa em vez de falhar em
silêncio. Restam limites declarados pelo engine (identidade de artefato, teto de
100 unidades por página). `native_ida` continua pendente por exigir licença paga
do operador; a alternativa nativa gratuita (`native_ghidra`) já está pronta.
