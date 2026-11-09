# Resumo executivo — reprodução E01–E18 + E19

## O que foi feito

- 18 experimentos do livro reproduzidos em `AerSimulator` com
  **20 sementes × 4096 tiros** (81.920 tiros por experimento).
- Distribuição ideal por statevector, marginalizada nos bits clássicos.
- TVD contra o ideal, IC95% entre sementes e comparação descritiva com os
  JSON simulados e reais arquivados.
- Novo **E19 — desigualdade de Mermin** para 3 qubits, com IC95%, p-valor e
  varredura de ruído depolarizante.

## Números principais

| Métrica | Resultado |
|---|---:|
| TVD média da reprodução contra o ideal | **0,00444** |
| Pior TVD da reprodução (E12 — QFT) | **0,01670** |
| TVD média do JSON simulado arquivado | **0,01025** |
| TVD média do JSON real arquivado | **0,05150** |
| Pior TVD do JSON real (E06/E15 — GHZ) | **0,21191** |
| E19 ideal | **M = 4,0000** |
| E19 com ruído p = 0,01 | **M = 3,7000** |
| E19 com ruído p = 0,02 | **M = 3,4358** |
| E19 com ruído p = 0,05 | **M = 2,7202** |

## Leitura

1. A reprodução fica mais perto do ideal do que o JSON simulado original,
   como esperado: 81.920 tiros reduzem o erro de amostragem em relação a
   1024 tiros.
2. O JSON real arquivado está mais longe do ideal, especialmente no GHZ de
   4 qubits (TVD ≈ 0,212). Isso é compatível com ruído, leitura e
   calibração, mas **não** prova a causa nem identifica o hardware.
3. O E19 mostra violação ideal de Mermin (M = 4) e uma degradação monotônica
   com ruído depolarizante; em p = 0,05, M ≈ 2,72, ainda acima do limite
   clássico 2 neste modelo simples.
4. O resultado do E19 é uma simulação. Não é uma violação observada em
   hardware nem uma medida de fidelidade de estado.

## O que não foi feito

- Nenhuma submissão ao GJQ/Tiangong ou a hardware quântico.
- Nenhuma execução de MindQuantum: o pacote exige Python <3.13 e MindSpore,
  ausentes no ambiente; o PyPI não respondeu.
- Nenhuma alegação de publicação científica que comprove uso do hardware
  GJQ. A busca bibliográfica não encontrou essa comprovação.

## Onde ler os detalhes

- `SPEC.md` — especificação e critérios.
- `RELATORIO.md` — tabela completa dos E01–E18.
- `E19_MERMIN.md` — desenho, resultados e limites do E19.
- `MINDQUANTUM.md` — bloqueio e caminho de portabilidade.
- `resultados/*.json` — dados brutos e agregados.
