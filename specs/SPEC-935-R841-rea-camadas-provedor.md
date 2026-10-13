---
spec_id: SPEC-935-R841
title: REA completo — motores das camadas de provedor e inspeção coordenada
component: integrations/rea_layers, integrations/rea_bridge, marceloclaro/rea_cli, marceloclaro/rea_reports, integrations/ecosystem_mcp
status: implemented
round_id: R841
test_file: tests/test_r841_rea_layers.py
---

# SPEC-935-R841 — Camadas de provedor do REA

## Objetivo e arquitetura

Tornar o REA completo utilizável pelo orquestrador. O REA 6.4.0 descreve, em
`docs/architecture.mermaid`, um subgrafo **Provider Layers** (Ghidra/IDA/Hopper,
Android/JADX, firmware binwalk/unblob, pwntools/pwndbg, EVM/evmole, dotnet,
browser, inspector, sourcemaps, referência). Antes desta rodada o Core expunha
`status`, `catalog`, `session`, `analyze` (JavaScript) e `analyze_binary`
(Ghidra). Faltavam os motores externos das demais camadas e uma via coordenada
para (a) mapear a prontidão de cada camada e (b) inspecionar estaticamente um
caminho com a ferramenta real da camada.

`MarceloClaroOrchestrator.rea_action` permanece a única entrada. A operação
`layers` devolve um mapa de prontidão local; a operação `layer` despacha a
inspeção estática por caminho da camada escolhida. Nenhuma das duas abre alvo
fora da ferramenta REA, executa aplicação, promove confiança ou substitui
validação externa.

## Contratos de aceite

1. `layers` não inicia transporte MCP nem toca alvo. Reporta, por camada, id,
   título, tipo (embarcada/engine), motor, requisito de versão, ferramenta de
   inspeção, prontidão da sonda e a resolução de cada variável de ambiente.
   `verification=local_readiness_probe`; sucesso não alega execução da camada.
2. `layer` exige identificador de camada conhecida, caminho local explícito
   existente (arquivo ou diretório) e, apenas para a camada EVM, `encoding` em
   `raw|hex` (padrão `raw`). Camadas sem inspeção por caminho (ex.: `native_ghidra`,
   que usa `analyze_binary`) são rejeitadas antes do transporte. Campos
   desconhecidos, `procedure`, `path` em operações não-analíticas e `encoding`
   fora de camada que o exige são rejeitados sem iniciar processo.
3. O registro mapeia **somente** nomes de ferramenta anunciados pelo catálogo MCP
   real do REA 6.4.0. Cada camada declara a(s) `surface`(s) do REA a que pertence,
   e um teste ancora cada ferramenta declarada ao conjunto de ferramentas daquelas
   superfícies no catálogo preservado. Antes de chamar, a ponte confirma no
   handshake real que a ferramenta existe e que o campo de caminho, os campos
   fixos e o `encoding` estão no `inputSchema`; caso contrário, falha sem sucesso.
4. A descoberta de motores exporta `REA_UNBLOB_COMMAND`, `REA_BINWALK_COMMAND`,
   `REA_APKTOOL_COMMAND` e `REA_JADX_MCP_JAR` ao processo filho **somente** quando
   os artefatos isolados existem; overrides do operador vencem e nenhum caminho é
   inventado. A mudança não altera o comportamento das operações já existentes.
5. Falha, erro estruturado, `isError`, timeout e cancelamento nunca viram sucesso;
   resposta integral e `response_sha256` são preservados e a limpeza do processo
   MCP permanece. MetaBus registra observação **sem** promover confiança
   (`confidence_promoted=false`, `externally_validated=false`).
6. O gateway compac­ta `layers` para contexto finito; CLI, MCP e o comando `/rea`
   expõem `layers`/`layer`. Testes herméticos RED/GREEN; instalação real e recibos
   ficam em `outputs/core-r841`.

## Fontes e limites

REA: https://github.com/MarceloClaro/rea (commit instalado rastreado). Docs de
camada: `docs/architecture.mermaid`, `docs/firmware-analysis.md`,
`docs/android-analysis.md`, `docs/apktool-resource-analysis.md`,
`docs/binary-diagnostics.md`, `docs/recorded-crashes.md`. Motores:
unblob (MIT, 26.6.4), binwalk (MIT, 3.1.0 compilado de fonte), apktool
(Apache-2.0, 2.7.0-dirty do sistema), jadx-headless-mcp (Apache-2.0, 0.7.1
compilado de sub­módulo). O catálogo MCP preservado por hash em
`.opencode/rea/evidence/` é a **cópia resumida** do REA: traz nome, `annotations`,
`effects` e `surface` de cada uma das 170 ferramentas — **não** o `inputSchema`
integral. Os nomes das ferramentas vêm dessa cópia (não são inventados) e a
`surface` ancora a que camada cada ferramenta pertence; os `inputSchema` são
conferidos ao vivo no handshake, antes de qualquer chamada.

A prontidão é sonda de configuração local: não prova execução da camada. As
camadas `native_ida`, `native_hopper`, `android_adb`, `jeb` e `browser`
dependem de registro/serviço externo ou de `adb` ausente no host; as camadas
`native_offline_elf` e `native_core_crash` dependem de um interpretador com
pwntools 4.15.0/Unicorn, indisponível no Python 3.14 do host. Essas permanecem
**pendentes** e assim são reportadas — não há alegação de cobertura total.

## Evidência executada

Submódulos git inicializados (superficial): `third_party/binwalk`
`4fdab3d464d97b68e0af9088df3f9e2e1545b21c`, `third_party/ghidra-nativeaot`
`effeb734fc570c32650f88b159608979dc7b423e`, `third_party/jadx-headless-mcp`
`5844800a486d2248fa949b74c9896285f5b54de2`, `third_party/unblob`
`1fcc7a0a584a70a96c31f5a276c20944d199a089`, `third_party/wakaru`
`8219bf5016a063d7fb215101a8c45d5959ec733f`.

Motores instalados no prefixo isolado `~/.local/share/opencode-core/native-rea`:
`bin/unblob` (wrapper para unblob 26.6.4 em `py-unblob`), `bin/binwalk`
(3.1.0, `cargo build --release`), `bin/apktool` (2.7.0-dirty do sistema),
`jadx-headless-mcp-0.7.1-all.jar` (42.619.858 bytes, `./gradlew shadowJar` com
JDK 17 de toolchain). `REA_JADX_HEAP_MIB` e prazos permanecem por conta do REA.

Sonda real (`operation=layers`): 18 camadas, 11 prontas, 7 pendentes, 11
inspecionáveis por caminho; `verification=local_readiness_probe`. A resposta MCP
real do launcher do Core confirmou o catálogo de 170 ferramentas (hash em
`.opencode/rea/evidence/`). Recibos de instalação em `outputs/core-r841`.

O gate de catálogo reprovou o registro inicial em `native_ghidra`, que listava
`decompile` e `list_functions` — nomes inexistentes no catálogo real (as
ferramentas equivalentes são `batch_decompile` e `list_procedures`). O defeito foi
corrigido e o teste `test_declared_tools_match_recorded_catalog_when_available`
ancora cada camada às `surface`s do REA (14 superfícies cobertas), de modo que
novos nomes inventados falham o build.
