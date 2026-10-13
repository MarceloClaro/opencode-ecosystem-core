---
spec_id: SPEC-935-R809
title: Revisão de integridade dos gates estruturais e do diagnóstico por gaps
component: marceloclaro/core_check, scanners/diagnostic_pipeline
status: implemented
round_id: R809
test_file: tests/test_r809_integridade.py
---

# SPEC-935-R809 — Revisão de integridade

## Problema

O gate de hermeticidade reduz imports a seu pacote raiz e, por isso, deixa
passar `urllib.request`, embora esse módulo conste da lista de proibições.
O diagnóstico por gaps agrupa falhas pelo ID sem exigir IDs válidos e
exclusivos: duas checagens malsucedidas podem aparecer como uma aprovação.
O teste de cobertura entre Lean e SPEC compara os artefatos na direção
contrária à cobertura que declara examinar.

## Requisitos

1. R809.1: o gate estrutural identifica imports de `urllib.request`, inclusive
   aliases, `from urllib.request import ...` e `from urllib import request`.
   Imports de `urllib.parse` e de outros módulos permitidos não são proibidos.
   Permanecem as proibições existentes de `subprocess` e `socket`.
2. R809.2: cada checagem de diagnóstico exige um ID textual não vazio após
   remoção de espaços nas extremidades. IDs repetidos após essa normalização,
   ausentes ou de tipo inválido tornam o plano inválido e geram `ValueError`.
   A validação dos IDs ocorre antes de ler os artefatos.
3. R809.3: planos válidos preservam a contagem por checagem: duas checagens
   distintas malsucedidas produzem `total_checks=2`, `falharam=2`, `passaram=0`.
4. R809.4: a auditoria de cobertura dos teoremas usa Lean como origem e SPEC
   como referência; teorema ausente na SPEC, inclusive SPEC vazia, gera gap
   de cobertura. Identificadores com maiúsculas mantêm sua grafia e são
   reconhecidos no índice documental. Marcadores de rodada ausentes no índice
   da SPEC R755 recebem referência explícita sem substituir o conteúdo anterior.
5. R809.5: importar o módulo de diagnóstico por gaps não quebra a API legada
   `from scanners import diagnostic_pipeline; diagnostic_pipeline.run(...)`.
   O módulo oferece delegação explícita ao pipeline original e o orquestrador
   importa seu singleton diretamente de `scanners.pipeline`, sem depender da
   ordem de importação do pacote. A compatibilidade é testada em processos
   Python locais novos, sem rede ou agentes externos.

## Aceite

- Testes locais com arquivos temporários demonstram RED antes das correções.
- `tests/test_r809_integridade.py`, `tests/test_r767_diagnostic_pipeline.py`
  e `tests/test_r481_core_check.py` passam após as correções.
- Sem rede, LLM ou execução de agentes externos nos testes novos.
- Sem alterações de ciclos de evolução, configuração gerada ou trabalho
  pré-existente de outras frentes.
- As contagens comprovam somente os testes executados, sem certificação
  externa nem alegação de validação científica.
