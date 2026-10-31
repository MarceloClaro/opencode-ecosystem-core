---
spec_id: SPEC-935-R992
title: Piloto OpenShell com instalação e validação reais de isolamento
component: integrations.openshell_pilot
status: green
test_file: tests/test_r992_openshell_pilot.py
---

# R992 — Piloto OpenShell (sandbox) com execução real validada

## Objetivo

Instalar o runtime OpenShell (NVIDIA, Apache-2.0) e validar, com execução real
observada, os atributos de isolamento: egress de rede, acesso a filesystem,
telemetria (opt-out), limpeza e recuperação. Distinguir, a cada passo,
instalação/inventário de execução observada e de isolamento comprovado.

## Contexto de ambiente (não promessas)

- WSL2 (`microsoft-standard-WSL2`), glibc 2.43, sudo passwordless, dpkg/apt.
- Podman 5.7.0 rootless funcional (`podman ps` ok); Docker ausente.
- OpenShell CLI/SDK ausentes no início; instalador oficial baixa .deb e instala
  via dpkg/apt (root). O README marca WSL2 como "experimental".
- Telemetria anônima do gateway é padrão; opt-out via `OPENSHELL_TELEMETRY_ENABLED=false`.

## Critérios de aceitação

1. `preflight()` inventaria CLI/versão, runtime de contêiner, saúde e SDK sem
   iniciar processos nem rede; declara `sandbox_executed=false` e
   `isolation_verified=false` sempre.
2. `isolation_test_plan()` lista ensaios reais com controles positivos e
   negativos para egress (hostname/IP/IPv6/DNS), filesystem (leitura/escrita
   fora do sandbox), credenciais sintéticas, telemetria opt-out, timeout/cleanup
   e recuperação.
3. `record_evidence()` persiste um recibo com hashes e nunca promove confiança,
   validação externa nem certifica isolamento por si.
4. Instalação real somente pelo caminho documentado do fornecedor, com versão
   resolvida e registrada; sem `curl|sh` cego (script inspecionado antes).
5. Validação real executa os ensaios e registra o resultado observado de cada um,
   inclusive falhas e bloqueios. Isolamento só é reportado como observado,
   nunca inferido de presença de binário ou documento.
6. Testes unitários são herméticos (fixtures), não exigem Podman/OpenShell; a
   execução real fica em recibos separados, não no gate de software.

## Limites

OpenShell não é motor de raciocínio nem validação científica; é fronteira de
execução. SDK PyPI não instala o CLI. WSL2 é experimental. Recibos do CLI são
relatos do processo local, não autenticação criptográfica independente.
Sandbox aprovado não torna a saída do agente dentro dele verdadeira ou confiável.

## Verificação

RED antes da implementação; testes de software locais; execução real em recibos
com hashes. Nenhuma alegação de isolamento sem observação executada.

## Evidência de execução (software local)

RED: `tdd-c6fada03b71e4c73b940067bb48071b1` (módulo ausente). GREEN:
`tests/test_r992_openshell_pilot.py` — **5 passed**; `red_history_valid=true`.
A execução real do OpenShell (instalação, criação de sandbox e ensaios de
isolamento) fica em recibos separados — não faz parte deste gate de software.

## Evidência de execução real (piloto)

Instalação e validação reais observadas (recibo `docs/evidence/R992_OPENSHELL_REAL.json`,
sha256 `a5641339…`):

- **Instalação**: `openshell 0.1.6-1` (deb) pelo instalador oficial (Apache-2.0,
  sha256 `04c1a437…`). Gateway registrado e ativo (mTLS).
- **Compute driver**: `OPENSHELL_COMPUTE_DRIVER=podman` (rootless 5.7.0) — a
  detecção automática falhou sem Docker; fixado via drop-in systemd após ativar
  `podman.socket`.
- **Isolamento observado**: leitura de caminho do host **negada** (Landlock);
  escrita em `/etc` (read-only) **negada**; escrita em `/tmp` **permitida**;
  TCP para `1.1.1.1:443` e `93.184.216.34:443` **bloqueado** (egress deny,
  sem bypass via IP); DNS resolve mas o egress TCP é negado.
- **Telemetria**: `OPENSHELL_TELEMETRY_ENABLED=false` configurado no gateway.
- **Ciclo de vida**: limpeza (sem container residual) e recuperação (recriação)
  **observadas**.

Limitações honestas: WSL2 é "experimental" no README; a negação de egress foi
inferida do comportamento (não de payload de rede explícito na política default,
que só expõe filesystem/Landlock); o opt-out de telemetria está *configurado*,
mas não fiz captura de pacotes para provar ausência de egress do próprio gateway.
Sandbox aprovado não torna a saída de um agente dentro dele verdadeira.
