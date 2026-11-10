# R1130 — Twirl/frame, ruído das correções e pré-registro

Simulação local; nenhum hardware, rede ou submissão.

## Ruído 1q nas correções

| Twirl | Taxa | Recuperadas | Erro máximo |
|---|---:|---:|---:|
| False | 0.000 | 13/13 | 0.000000 |
| False | 0.001 | 13/13 | 0.002581 |
| False | 0.005 | 13/13 | 0.012870 |
| False | 0.010 | 13/13 | 0.025655 |
| True | 0.000 | 13/13 | 0.000000 |
| True | 0.001 | 13/13 | 0.002581 |
| True | 0.005 | 13/13 | 0.012870 |
| True | 0.010 | 13/13 | 0.025655 |

## Pré-registro

- Jobs planejados: **325**.
- Shots por job: **4096**.
- Shots totais: **1331200**.
- Twirl: **True**; seeds: [1, 2, 3, 4, 5].
- Ruído de correção: **0.002** (depolarização 1q).
- Hash: `4a74762ecd5f7a6a1a46be5472896f62375ee19fb24c7a8d4ef98fd2ca354f83`.
- Submissão de hardware: **False**.

## Limites

- Twirl e ruído são simulados; não são o ruído real do Baihua.
- O twirl preserva a recuperação exata nos testes, mas não foi executado em hardware.
- A taxa 0,005 degrada o erro; o ajuste ainda retorna 13/13, o que não significa precisão suficiente para PEC.
- As 2 funções de corte permanecem não medidas.
- Nenhuma taxa foi medida; PEC 2q continua bloqueado.
