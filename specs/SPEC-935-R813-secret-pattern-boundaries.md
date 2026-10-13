---
spec_id: SPEC-935-R813
title: Fronteiras de token e exceções sintéticas exatas no gate de segredos
component: tests/test_r453_precommit_security_closure.py
status: green
round_id: R813
test_file: tests/test_r453_precommit_security_closure.py
---

# SPEC-935-R813 — Precisão do gate de padrões de segredos

## Problema demonstrado

A auditoria local do índice identificou 59 ocorrências anteriores à integração
REA, também presentes em HEAD e na árvore de trabalho. Elas correspondem a três
hashes distintos: dois exemplos artificiais de documentação/testes e um sufixo
de identificador comum capturado pela regex sem fronteira esquerda. Esta revisão
não autenticou credenciais e não indica exposição real nesses candidatos.

## Requisitos

1. R813.1: os seis padrões preservam detecção no início, em texto entre aspas
   JSON, após `token=` e após espaço de Bearer. Cada prefixo exige uma fronteira
   de token à esquerda, impedindo captura dentro de identificadores.
2. R813.2: `_has_high_confidence_secret` examina todas as correspondências e
   ignora somente os dois SHA256 artificiais exatos auditados. Não existe
   exceção geral por repetição, entropia, fornecedor, caminho ou extensão.
3. R813.3: exemplos variados, repetidos não registrados, alterações dos
   exemplos permitidos e texto que combina exemplo permitido com outro
   candidato continuam bloqueados.
4. R813.4: `_tracked_text_blobs` continua lendo exclusivamente os blobs stage 0
   do índice; a regressão de índice divergente da árvore de trabalho permanece
   intacta. Nenhuma mudança no índice ou em evidências históricas é necessária
   para corrigir esta classificação de falsos positivos.
5. R813.5: relatórios registram tipos, comprimentos e hashes, sem valores de
   candidatos. A prova é hermética e local, sem validação externa ou
   autenticação dos padrões examinados.

## Aceite e evidência

- RED: regressões R813 exigem o helper e a política de fronteiras/exceções.
- GREEN: regressões R813 e todos os contratos R453 passam, incluindo a leitura
  do índice atual e o teste isolado de índice divergente.
- Logs e resumo ficam em `outputs/rea-r808/r813-*`; hashes auditados e a
  justificativa da exceção são explícitos no código.
- Execução local: RED registrou 8 falhas esperadas por ausência do helper;
  GREEN aprovou os 26 testes R453/R813 em 45,39 segundos. Esta classificação
  não acrescenta validação externa nem autenticação de credenciais.
