---
spec_id: SPEC-935-R842
title: REA — fechamento das pendências de motores com provas reais
component: integrations/rea_layers, integrations/rea_bridge, outputs/core-r842
status: implemented
round_id: R842
test_file: tests/test_r842_rea_engines.py
---

# SPEC-935-R842 — Fechamento das pendências de motores do REA

## Objetivo e arquitetura

A SPEC-935-R841 deixou 7 das 18 camadas do REA pendentes. Esta rodada fecha as
que podem ser resolvidas por vias legais e isoladas, sem alterar defaults do
sistema nem executar licenças de terceiros: **android_adb**, **browser**,
**native_offline_elf** e **native_core_crash**. Ficam documentadas como
explicitamente não instaláveis aqui as camadas que exigem licença ou serviço
comercial do operador (**native_ida**, **native_hopper**, **jeb**).

`integrations/rea_layers.engine_environment()` é a única porta de descoberta:
exporta ao processo filho REA somente caminhos que existem; override do operador
sempre vence; nada é inventado. A sonda de prontidão nasce da mesma função e
permanece `verification=local_readiness_probe`.

## Contratos de aceite

1. **android_adb**: `REA_ADB_PATH` é satisfeito por descoberta do `adb` em PATH
   quando instalado pelo sistema (apt); override do operador vence. A camada fica
   pronta só quando um executável real é encontrado.
2. **browser**: `REA_BROWSER_EXECUTABLE` passa a ser obrigatório (o REA o exige);
   a descoberta aproveita o Chromium Playwright do SPEC-935-R824
   (`~/.local/share/opencode-core/playwright-mcp/browsers/chromium-*/chrome-linux*/chrome`
   ou `CORE_BROWSER_HOME`). Nenhum navegador é iniciado pela sonda.
3. **native_offline_elf**: `REA_PWNTOOLS_PYTHON` aponta para um interpretador
   Python 3.12 isolado (uv/python-build-standalone) com pwntools, pyelftools 0.33
   e Unicorn 2.1.2 — as versões exigidas pelo REA; inexistentes no Python 3.14 do
   host, daí o interpretador dedicado. Nenhum import é executado na sonda.
4. **native_core_crash**: `REA_PWNDBG_GDB` (gdb 17.x), `REA_PWNDBG_GDBINIT`
   (gdbinit.py do pwndbg clonado) e `REA_PWNDBG_VENV_PATH` (venv do pwndbg) são
   descobertos juntos; a camada só fica pronta com os quatro presentes. O
   `setup.sh` do pwndbg NÃO altera `~/.gdbinit` do operador (efeito colateral
   revertido) — a invocação usa o gdbinit isolado.
5. **Restam pendentes, sem instalação automatizada**: `native_ida`
   (REA_IDA_MCP_CONFIG), `native_hopper`
   (REA_HOPPER_CONFORMANCE_MANIFEST_PATH) e `jeb` (REA_JEB_MCP_URL) — licença ou
   serviço comercial do operador. O relatório as lista com esse motivo; nenhuma
   dessas camadas é dada como pronta.
6. Testes herméticos RED/GREEN e testes de host que pulam quando o artefato não
   existe. Provas reais de inspeção (pwntools/ELF, EVM, firmware) ficam em
   `outputs/core-r842/live-evidence.json` com `externally_validated=false`.

## Fontes e limites

- adb 34.0.5: pacote Ubuntu (`apt install adb`).
- Python 3.12.14: `uv python install 3.12` (python-build-standalone, rede
  github.com); pwntools/unicorn 2.1.2/pyelftools 0.33 via `uv pip` no venv
  isolado `native-rea/py-pwntools`.
- pwndbg 2026.9.15, commit `b5162e66edbd` (Apache-2.0), shallow clone;
  `./setup.sh` criou venv isolado; o `~/.gdbinit` global foi revertido.
- Chromium 1247: instalado pelo Playwright MCP 0.0.83 (SPEC-935-R824), Apache-2.0.
- Evidência real de execução é só para as camadas inspecionadas; prontidão não
  prova execução. IDA/Hopper/JEB não são instaláveis sem licença do operador;
  nenhuma alegação de cobertura total é feita.

## Evidência executada

Sonda real: **18 camadas, 15 prontas, 3 pendentes** (native_ida, native_hopper,
jeb), 11 inspecionáveis. Inspeções reais executadas sob MarceloClaro:

- `native_offline_elf` → `inspect_binary_layout` em `/tmp/pw` (ELF x86_64):
  evidence `ev_ab3af30f…`, response_sha256 `b1410295…`, subject digest
  sha256 `233eec3c…` (pwntools).
- `evm` → `inspect_evm_interface` em `/tmp/evm.hex`: evidence `ev_088ef500…`,
  response_sha256 `f6fb0466…`, subject digest `75708f8c…`.
- `firmware` → `inspect_firmware_regions` em imagem sintética
  (cabeçalho+gzip+cauda): evidence `ev_3f5917bf…`, response_sha256 de prova,
  subject digest `ded03aaa…` (binwalk+unblob).

Recibos de instalação em `outputs/core-r842/install-receipt.json`.