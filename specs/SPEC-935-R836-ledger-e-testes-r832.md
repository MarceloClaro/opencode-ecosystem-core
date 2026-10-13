---
spec_id: SPEC-935-R836
title: Ledger sem identificadores fabricados e contratos tipados R832
status: proposed
component: evolution/cycles_manager.py + protocolos/behavioral_gate.py
test_file: tests/test_r836_ledger_contract.py
---

# R836 — correção da revisão cega R1/R3

## Problema observado

A revisão R834 removeu o deslocamento `+830` e os aliases idênticos. A
implementação restante ainda transforma erro de leitura em ledger vazio,
atribui `R834` sem evidência e inclui uma chave artificial `R: True`.
R832 ainda aceita qualquer status SMT e usa contagem mínima do ambiente.

## Contrato

1. `next_id(state_path=None)` lê uma vez o ledger informado; sem parâmetro,
   respeita `EVOLUTION_STATE_PATH` ou `evolution/cycles.json`.
2. O próximo numeral é o maior numeral de `round_id` mais um. A ordem e a
   quantidade de entradas não determinam o resultado. IDs históricos como
   `R53b` e `R605-final` também reservam o numeral. IDs duplicados já presentes
   não são descartados nem alterados; o retorno informa a quantidade lida.
3. Um ledger válido vazio inicia em `R1`. Arquivo ausente, JSON ilegível,
   estrutura inválida ou identificador inválido devolvem `next: null` e
   `status: unavailable`, sem criar arquivo, reparar histórico ou inventar ID.
4. Não há aliases redundantes, offset, chave artificial `R`, nem escrita no
   ledger. A função informa `status: ready` somente após leitura válida.
5. `protocolos.behavioral_gate.check` é uma fachada de
   `trust.behavioral_gate.allow`, preservando ação, argumentos e resultado.
   A decisão canônica representa o limiar de trust, não a validação de uma
   tarefa ou a autorização para executar agentes.

## Testes e limite de medida

- Fixture retida `tests/fixtures/r836/ledger_sparse.json`: IDs fora de ordem,
  sufixos históricos e lacunas numéricas, com próximo ID literal `R42`.
- Casos de ausência, JSON truncado, formato raiz/ciclos/entrada inválido,
  numeral inválido, ledger vazio e ambiente isolado; bytes preservados.
- R832 separa existência de arquivos de contratos de comportamento. Os
  testes comparam booleanos estritos, ordens, linhas normalizadas, saldos,
  equilíbrios e parâmetros de planos, incluindo negação nos protocolos.
- `describe`, `plan`, `stages` e mapas de regras continuam descritivos.
  Passar esses contratos não demonstra execução de agentes, autenticação,
  inferência, conexão MCP, persistência ou cobertura funcional do ecossistema.
- A fixture é um caso controlado, não uma medição do ledger de produção.
  A sondagem local usa o arquivo real e registra seu hash separadamente.

## Aceite local

RED/GREEN registrados em `outputs/core-r836`; execução focada de R832/R836,
teste fiel da fachada e sondagem do ledger sem alteração. Nenhuma decisão de
aceite externo é delegada aos testes; a decisão final permanece humana.
