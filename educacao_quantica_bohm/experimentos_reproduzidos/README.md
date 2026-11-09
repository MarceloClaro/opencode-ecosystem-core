# Experimentos reproduzidos — E01–E18 + E19

Esta pasta contém uma reprodução independente, em simulação, dos 18
experimentos do livro e um experimento novo (E19 — desigualdade de Mermin).

## Como rodar

```bash
cd educacao_quantica_bohm/experimentos_reproduzidos
../../.venv-quantum/bin/python reproduzir.py
../../.venv-quantum/bin/python e19_mermin.py
```

Modo rápido (para testes):

```bash
../../.venv-quantum/bin/python reproduzir.py --quick --only E01 E07 E10
../../.venv-quantum/bin/python e19_mermin.py --quick
```

## O que o protocolo faz

- 20 sementes × 4096 tiros por experimento (81.920 tiros no total).
- Distribuição ideal calculada por statevector e marginalizada nos bits
  clássicos efetivamente medidos.
- TVD (distância de variação total) contra o ideal, com IC95% entre sementes.
- Comparação descritiva com o JSON simulado e o JSON real arquivados.
- E19: quatro configurações X/Y, `M = E_XXX − E_XYY − E_YXY − E_YYX`,
  IC95%, p-valor contra o limite clássico 2 e varredura de ruído
  depolarizante (0; 0,01; 0,02; 0,05).

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `SPEC.md` | Especificação e critérios de aceitação. |
| `reproduzir.py` | Harness dos E01–E18. |
| `e19_mermin.py` | Experimento novo E19. |
| `resultados/E01.json` … `E18.json` | Resultados por experimento. |
| `resultados/E19.json` | Resultado do E19. |
| `resultados/RESUMO.json` | Resumo agregado. |
| `RELATORIO.md` | Tabela e leitura dos E01–E18. |
| `E19_MERMIN.md` | Relatório do E19. |
| `RESUMO_EXECUTIVO.md` | Síntese de uma página. |
| `MINDQUANTUM.md` | Bloqueio e caminho de portabilidade. |
| `../tests/test_experimentos_reproduzidos.py` | Contratos automatizados. |

## Limites

- É simulação clássica de circuitos pequenos; não há vantagem quântica.
- Nenhum job foi enviado ao GJQ/Tiangong ou a qualquer hardware.
- O JSON real arquivado é tratado como referência histórica do livro, não
  como replicação de hardware nesta rodada.
- MindQuantum não foi executado: o ambiente não tem MindSpore e o pacote
  exige Python <3.13.
- A TVD mede diferença entre distribuições; não é fidelidade de estado.
