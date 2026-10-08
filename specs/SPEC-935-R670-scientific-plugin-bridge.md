---
spec_id: SPEC-935-R670
title: Plugins científicos com origem preservada e execução pelo host
status: green
validation_scope: local_runtime_and_host_connectors
component: integrations/scientific_plugins.py
test_file: tests/test_r670_scientific_plugins.py
---

# R670 — Plugins científicos no Core

1. Registrar os doze plugins escolhidos, preservando identidade e versão.
2. Importar os arquivos de instrução e apoio do cache existente sem alterar
   o cache original, executar scripts de terceiros ou transferir credenciais.
3. Skills são lidas pelo orquestrador com política de invocação preservada.
   A existência de uma instrução não prova execução de uma integração.
4. Aplicações hospedadas usam tickets vinculados à ferramenta e argumentos;
   o host autenticado executa sua ferramenta e entrega resposta identificada.
   Um recibo do host é evidência reportada, sem autenticação criptográfica
   independente. Nunca declarar o conector hospedado instalado no WSL.
5. Bloquear ferramentas desconhecidas, payloads ilimitados, NaN, colisões,
   alteração de origem e reuso de recibos. Falhas externas permanecem falhas.
6. SciGrant exige objetivo de redação de projeto; não é sondado como health check.
7. Boltz usa CLI oficial instalada com artefato fixado e checksum; autenticação
   e submissão de trabalhos são estados distintos. Não submeter trabalhos
   científicos sem entradas apropriadas e estimativa de custo.
8. Scripts Python delimitados usam `-B` e PYTHONDONTWRITEBYTECODE; arquivos
   importados permanecem íntegros após a execução. Bytecode gerado na prova
   inicial foi preservado separadamente como evidência da falha corrigida.

## Aceitação

RED antes de implementação; GREEN, regressões e probes de conectores reais
em evidências separadas. Sem publicação de plugin ou material científico.

RED: `docs/evidence/R670_RED.xml` e `R670_IMMUTABLE_SKILL_RED.xml`.
GREEN: `docs/evidence/R667_R671_GREEN.xml`. Conectores/CLI reais:
`docs/evidence/R670_HOST_REAL/probe.json`. Consolidado:
`docs/evidence/R667_R671_RELEASE_GATE.json`.
