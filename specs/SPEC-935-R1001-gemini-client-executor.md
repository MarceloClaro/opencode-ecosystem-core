---
spec_id: SPEC-935-R1001
title: Ferramenta gemini-client e procedimento de reprodução do conselho no sandbox
component: integrations.gemini_client
status: green
test_file: tests/test_r1001_gemini_client.py
---

# R1001 — executor Gemini portátil e reprodutibilidade do conselho no sandbox

## Objetivo

Persistir no repositório o executor Gemini (`gemini-client`) que substitui o
`agy` (OAuth/keyring) dentro do sandbox OpenShell, e documentar o procedimento
completo de reprodução: instalação OpenShell → build/upload do executor →
política de egress → execução do conselho R989.

## Fatos de contexto (não promessas)

- `agy` usa OAuth de conta com renovação via keyring; em sandbox headless o
  token expira e não renova.
- A API Gemini aceita `GEMINI_API_KEY` (portátil, sem keyring); modelos estáveis
  observados: `gemini-3.5-flash`, `gemini-3.6-flash`, `gemini-3.1-flash-lite`.
- O proxy de rede do OpenShell faz MITM TLS; o cliente precisa aceitar o
  certificado do proxy (skip-verify) DENTRO do sandbox.
- A cota gratuita do Gemini é finita (HTTP 429 ao esgotar).

## Critérios de aceitação

1. `integrations/gemini_client/` contém `Cargo.toml`, `src/main.rs` e `README.md`.
2. O cliente lê `GEMINI_API_KEY` e `GEMINI_MODEL` do ambiente (nenhuma credencial
   hardcoded), lê o prompt de `stdin` e imprime o texto da resposta.
3. O cliente usa skip-verify TLS (`NoVerify`) e documenta que isso é restrito ao
   MITM do proxy OpenShell, não um padrão geral.
4. `docs/PROCEDIMENTO_OPENSHELL_GEMINI_CONSELHO.md` descreve, em ordem:
   instalação OpenShell (deb + `podman.socket` + `OPENSHELL_COMPUTE_DRIVER=podman`),
   build do cliente, upload ao sandbox, política de egress `rest:read-write`,
   e execução do conselho R989 com o executor Gemini.
5. Testes verificam a presença dos arquivos, a ausência de credencial hardcoded e
   a presença dos elementos obrigatórios no código (stdin, env, skip-verify).
6. O artefato compilado (`target/`) não é versionado; somente a fonte.

## Limites

O cliente é um transportador de texto para o modelo; não valida JSON/evidência
(isso é do conselho R989). Skip-verify TLS é inseguro fora do sandbox. Quota da
chave é externa. Inferência real depende de chave/quota válidas; testes de
software aqui são estáticos (não chamam a API).

## Verificação

RED antes da implementação; GREEN local; nenhuma chamada à API Gemini nos testes.

## Evidência de execução

RED: `tdd-a779f9b9591649af8cc1e6d0ae7f53e8` (arquivos ausentes). GREEN:
`tests/test_r1001_gemini_client.py` — **7 passed**; `red_history_valid=true`.

`integrations/gemini_client/` contém a fonte Rust (compilada fora do repositório,
não versionada: `target/` ignorado). Execução real já observada nesta frente:
inferência `OK` dentro do sandbox OpenShell via `GEMINI_API_KEY` e conselho R989
rodando dentro do sandbox (3–7 cientistas antes do esgotamento da cota).
`docs/PROCEDIMENTO_OPENSHELL_GEMINI_CONSELHO.md` documenta o fluxo completo e os
gotchas (integridade de binário, MITM TLS, protocolo `rest`, quota).
