---
spec_id: SPEC-935-R810
title: Doctor estrutural rápido com sondagens operacionais explícitas
component: marceloclaro/doctor, marceloclaro/cli
status: implemented
round_id: R810
test_file: tests/test_r810_doctor_estrutural.py
---

# SPEC-935-R810 — Doctor estrutural

## Problema demonstrado

O contrato R110 exige `run_doctor()` em menos de cinco segundos. O profiling
anterior a esta correção mediu 16,69 segundos, incluindo 3,10 segundos de
importação: as checagens executavam versões de CLIs, sondagens HTTP e exemplos
de provas nativas. Lean/E-Graph consumiu 5,49 segundos, geometria e
autoformalização 3,84 segundos e o inventário com versões de CLIs 2,00 segundos. A instalação
de novos executores aumentava o custo de um diagnóstico anunciado como
estrutural.

## Requisitos

1. R810.1: `run_doctor()` e `doctor` da CLI usam modo estrutural por padrão,
   com os mesmos nomes de checagem e campos agregados anteriores. O relatório
   indica `diagnostic_mode=structural` e `verification=installation_only`.
2. R810.2: o modo estrutural lê configuração, arquivos, registro de evolução,
   specs e instalação de componentes sem subprocessos, sockets, HTTP, provas
   nativas ou cenários sintéticos de diagnóstico clínico.
3. R810.3: a descoberta de uma CLI, biblioteca ou variável de configuração
   não é descrita como prontidão de serviço, inferência realizada ou prova
   executada. Não há consulta remota do instalador runai no modo padrão.
4. R810.4: `run_doctor(live=True)` e `python3 -m marceloclaro.cli doctor --live`
   habilitam explicitamente as sondagens anteriores. O relatório indica
   `diagnostic_mode=live` e `verification=runtime_probes`; a conclusão continua
   delimitada a cada sondagem, sem certificação externa ou inferência inventada.
5. R810.5: opções desconhecidas da CLI são rejeitadas antes de executar checks.
6. R810.6: permanece a asserção original R110 de menos de cinco segundos,
   sem ampliar o limite nem omitir checagens estruturais. REA permanece no
   diagnóstico como inventário local e sua prova MCP permanece separada.
7. R810.7: `ReaBridge.status()` preserva a coleta do commit Git por padrão;
   somente o diagnóstico estrutural usa `include_commit=False`, sem subprocesso.

## Aceite

- RED demonstra efeitos operacionais do modo padrão e ausência da opção
  explícita de sondagem; GREEN preserva os contratos de inventário e de probes.
- Testes R810, R110, R212, R644 e contratos de diagnóstico dos subsistemas
  afetados passam, com credenciais redigidas.
- Logs de profiling e de teste ficam em `outputs/rea-r808`.
