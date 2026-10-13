---
spec_id: SPEC-935-R844
title: REA — instalação verificada do Hopper demo e prova real de análise
component: integrations/rea_layers, outputs/core-r844
status: implemented
round_id: R844
test_file: tests/test_r844_hopper_install.py
---

# SPEC-935-R844 — Hopper demo instalado e provado

## Contexto e decisão

O operador autorizou explicitamente a instalação do Hopper demo. A ação veio do
próprio REA, no plano `install_hopper` (`rea setup --yes --install-hopper
--dry-run`), com origem de rede e integridade declaradas: baixar
`https://www.hopperapp.com/downloader/public/Hopper-6.4.2-Linux-demo.deb`
(35.755.772 bytes, SHA-1 `e4f79dff602648a8ff4a88b773875b6bfac0dc65`) e instalar
com as dependências de sessão demo.

Ao aplicar, o REA retornou `status=needs_human`,
`code=authorization_or_package_manager_failed`: o comando planejado usa `pkexec`,
que não encontrou agente polkit/sessão gráfica. A remediação **do próprio REA**
autoriza instalar o pacote planejado e as dependências, e então repetir o setup.
Foi o que se fez, com `sudo apt-get install` (sudo sem senha neste host) após
verificação independente de bytes e SHA-1.

## Contratos de aceite

1. Baixar o `.deb` oficial replicando os cabeçalhos do REA
   (`accept: application/json`, `user-agent: rea-installer`) e **verificar
   bytes e SHA-1** antes de instalar; divergência aborta.
2. Instalar o `.deb` verificado + `xvfb xauth python3 libx11-6 libxtst6` com
   `sudo apt-get install -y` (substituindo o `pkexec` que falhou).
3. Launcher detectável em `/opt/hopper/bin/Hopper` e `rea doctor --provider
   hopper --json` saudável (hopper, hopper-version, hopper-demo-runtime).
4. Sonda do Core: `native_hopper` pronta por descoberta real
   (`engine_environment` → `/opt/hopper/bin/Hopper`).
5. **Prova real de análise** via REA com `--provider hopper`, com Evidence
   preservada: `evidence_id`, pseudocódigo, assembly, chamadores, authority e
   limitations do engine.
6. Nada é promovido: `externally_validated=false`, `confidence_promoted=false`.

## Resultado

- Integridade: bytes 35755772 ✓, SHA-1 `e4f79dff602648a8ff4a88b773875b6bfac0dc65` ✓.
- `rea doctor --provider hopper`: healthy — `/opt/hopper/bin/Hopper`,
  runtime demo `user-mount-namespace` (`/tmp/.X11-unix` mode 0777).
- Prova real (`rea function /tmp/hopper_probe soma --provider hopper`):
  `evidence_id ev_f4cb73bba8405de06cc72368bc1da74d98eb15e8ba920f769ab7ff4dba8b251b`,
  pseudocódigo `rax = arg1 + arg0; return rax;`, assembly `endbr64…ret`,
  `callers: [main]`, `authority=shipped-artifact`, `confidence=observed`,
  `response_sha256 57ee39265faf0a40c297be76aad39b0b3aa004dac810ad25cf8fb404f52cc91c`.
- Sonda final: **18 camadas, 16 prontas, 2 pendentes** (`native_ida`, `jeb`).

## Limites e remanescente

O Hopper é **demo** com limites definidos pelo fornecedor e exige seleção de modo
demo por sessão; a doc do engine registra facetas indisponíveis (body ranges,
CFG, xrefs modernos). `native_ida` e `jeb` continuam pendentes por exigirem
licença/serviço comercial — não há caminho de instalação automatizável neste
host, e nenhuma camada é marcada pronta sem motor real.