# R1126 — Posto do desenho CB e aumento por ciclos

Análise linear local; nenhum hardware, rede ou submissão.

## Resultado

- Matriz de anticommutação completa: **posto 15**.
- Desenho somente-CZ (profundidades pares): **posto 9**.
- Aumento com ciclos Cliffords sob gerador compartilhado: **posto 15** (sementes [0], condição 15.45).
- Geradores separados (3 ciclos): posto 27 para 45 incógnitas; **não identificável**.
- Submodelo local: posto 6/6.
- Submodelo de dois qubits: posto 9/9.

## Órbitas do CZ

- {IX, ZX}
- {IY, ZY}
- {IZ}
- {XI, XZ}
- {XX, YY}
- {XY, YX}
- {YI, YZ}
- {ZI}
- {ZZ}

## Hipóteses e limites

- O posto 15 com ciclos extras supõe o mesmo gerador (ou conjugado conhecido) em todos os ciclos.
- A identidade também dá posto 15, mas não é um ciclo físico comparável ao CZ; isso mostra que a hipótese é o elemento decisivo.
- Ciclos aleatórios acrescentam portas e ruído próprio; a existência matemática não é um protocolo validado.
- Com um gerador por ciclo, há 15k incógnitas e apenas 9k combinações independentes; a deficiência é 6k.
- Submodelos locais/2q só são identificáveis se as demais taxas forem nulas por hipótese.
- Nenhuma taxa foi medida; PEC 2q permanece bloqueado.

## Próximo passo

GST/processo do par ou modelo estruturado com hipótese física independente. Acrescentar ciclos sem justificar o gerador compartilhado apenas desloca a suposição.

## Artefatos

- `rank_audit.json` — auditoria completa.
- `quantum_mitigation/cb_rank_bounds.py` — implementação.
- `tests/test_r1126_cb_rank_bounds.py` — contraprovas.
