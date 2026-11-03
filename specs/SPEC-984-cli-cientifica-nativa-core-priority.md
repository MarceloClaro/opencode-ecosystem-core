---
spec_id: SPEC-984
title: Roteamento da CLI científica para a camada nativa do Core
version: 1.0.0
status: green
test_file: tests/test_r984_scientific_cli_routing.py
---

# SPEC-984 — a CLI científica deve encaminhar pesquisa nativa ao Core

## Problema

`scientific_lab/native/cli.py` e seus módulos de busca, revisão e Evidence Graph
já estão no Core (v4.2), mas `python -m marceloclaro.scientific_lab research|review|evidence`
ainda cai no dispatcher externo v4.1. Assim, a interface documentada como nativa
depende de uma instalação cuja própria checagem `doctor` pode falhar. Além disso,
`NATIVE_COMMANDS` atualmente inclui comandos avançados que não têm implementação
nativa, e a CLI anuncia `native_status` sem encaminhá-lo.

A pesquisa precisa ser executável pelo kernel do Core, sem instalar a
supercamada, sem importação de scripts externos e mantendo essa supercamada como
fallback explícito apenas para os módulos ainda não migrados.

## Escopo e limites

- Roteamento de `research`, `articles`, `review` e `evidence` para
  `scientific_lab.native.cli.dispatch`.
- Comando `native-status` para reportar somente a camada nativa e os comandos
  que ainda usam o fallback externo.
- `NATIVE_COMMANDS` deve enumerar somente comandos efetivamente nativos.
- `doctor` expõe separadamente `native_layer` e `scientific_layer`; a ausência,
  hash inválido ou falha de integridade externa não apaga nem reclassifica a
  capacidade nativa. O `doctor` ainda retorna código não zero se a camada externa
  requerida pelo modo completo falhar.
- Os comandos avançados (`mesh`, `mission`, `living`, `synthesis`, `grade`,
  `causal`, `federation`, `production`) continuam encaminhados ao fallback v4.1.
- Não executar chamadas reais de busca, baixar papers, acionar credenciais ou
  importar skills de terceiros nos testes.

## Critérios de aceitação

1. `NATIVE_COMMANDS` corresponde exatamente a `research`, `articles`, `review`,
   `evidence` e `native-status`; nenhum fallback externo é rotulado nativo.
2. `marceloclaro.scientific_lab main` encaminha os quatro comandos nativos ao
   dispatcher local com `argv` preservado; o dispatcher v4.1 não é chamado.
3. `native-status` funciona sem descobrir/validar a camada externa e informa
   `mode=native` e a lista explícita de fallbacks.
4. Um comando avançado continua usando o dispatcher externo, com os argumentos
   inalterados.
5. `doctor` relata a prontidão nativa e a integridade da supercamada em campos
   distintos; falha da supercamada não é escondida nem promovida a sucesso.
6. Testes herméticos confirmam que nenhum downloader, chamada de rede ou executor
   externo é acionado pelo teste de roteamento.

## RED/GREEN

RED deve demonstrar: `native-status` retorna comando desconhecido; `research`
chama o dispatcher externo; e `NATIVE_COMMANDS` inclui comandos ainda não
implementados nativamente. GREEN encaminha ao Core e mantém o fallback avançado
explicitamente separado.

## Evidência de execução

RED: 5 testes novos falharam antes da implementação (`NATIVE_COMMANDS` incluía
fallbacks, `native-status` não era encaminhado e `research/review/evidence`
chamavam o dispatcher externo). GREEN: `tests/test_r984_scientific_cli_routing.py`,
`test_scientific_lab_v42_native.py`, `test_scientific_lab_v41_core_integration.py`,
`test_scientific_governance_contracts.py` e `test_sdd_tdd.py`: 43 passed.
Prova de CLI local: `native-status` informou 5 comandos nativos e 8 fallbacks;
`research search --help` chegou ao parser nativo sem executar busca. Doctor
estrutural do Core: healthy (22/22, zero avisos/falhas). A suíte integral não
foi repetida nesta alteração focal.

## Limites epistemológicos

Este trabalho corrige o despacho da interface. Não torna as fontes, modelos,
resultados de pesquisa ou validações do v4.1 automaticamente confiáveis. O
`scientific_lab doctor` da supercamada instalada continua retornando erro por
referência obrigatória ausente `references/production-hardening-reproducible-distribution.md`;
o código externo não foi reparado nem substituído. Os conectores com autenticação
hospedada continuam sem execução verificada, e a busca nativa usa somente os
contratos/políticas já existentes.
