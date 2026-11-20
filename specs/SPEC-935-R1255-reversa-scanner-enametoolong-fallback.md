---
spec_id: SPEC-935-R1255
title: Fallback textual do ReversaScanner diante de caminhos ENAMETOOLONG
component: scanners.reversa_scanner
status: red
test_file: tests/test_r1255_reversa_scanner_path_guard.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1255-PATH-GUARD:
      - tests/test_r1255_reversa_scanner_path_guard.py::test_overlong_relative_path_with_code_falls_back_to_text
      - tests/test_r1255_reversa_scanner_path_guard.py::test_overlong_absolute_path_falls_back_without_exception
    R1255-COMPATIBILITY:
      - tests/test_r1255_reversa_scanner_path_guard.py::test_existing_path_still_uses_universal_engine
      - tests/test_r1255_reversa_scanner_path_guard.py::test_plain_text_scanning_remains_unchanged
---

# SPEC-935-R1255 — Fallback textual diante de `ENAMETOOLONG`

## Problema observado

`ReversaScanner.scan` tenta reconhecer caminhos antes da detecção textual. As
chamadas `Path.exists()` ocorrem fora do bloco de tolerância do mecanismo
universal. Em Linux, uma string relativa com um componente de 260 caracteres
reproduziu `OSError(ENAMETOOLONG)`, impedindo o scanner de concluir o fallback
textual.

## Contrato

1. A sondagem de existência de caminhos candidatos deve tratar `OSError` como
   “não confirmado como caminho” e prosseguir para a análise textual; não pode
   encerrar a chamada de `scan` por erros de filesystem como `ENAMETOOLONG`.
2. O fallback conserva o conteúdo original do corpus: construções de código
   nele presentes continuam detectáveis e pontuadas pela lógica textual já
   existente.
3. Caminhos existentes continuam sendo enviados ao `ReversaUniversalEngine`,
   sem alterar seu resultado ou suas recomendações.
4. Corpus textual comum mantém o comportamento anterior. A correção limita-se
   à sondagem de caminho e não amplia filesystem traversal, rede, instalação ou
   execução de código.

## Critérios de aceitação executáveis

- `R1255-PATH-GUARD` — componente relativo e caminho absoluto acima do limite do
  filesystem não propagam `ENAMETOOLONG`; a análise cai para texto e identifica
  código quando ele está presente.
- `R1255-COMPATIBILITY` — caminho existente ainda chama o mecanismo universal e
  corpus textual comum continua sendo analisado sem mudança.

## Limites

Os testes não validam a completude da análise universal nem a qualidade de
TSPECs geradas. Apenas verificam a fronteira de probing de caminhos e o
comportamento de fallback local.
