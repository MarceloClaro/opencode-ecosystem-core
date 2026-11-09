# E19 — Desigualdade de Mermin para três qubits

Gerado em 2026-11-09T00:51:27-0300.

## Desenho

- Estado: `|GHZ⟩ = (|000⟩ + |111⟩)/√2`.
- Operador: `M = XXX − XYY − YXY − YYX`.
- Limite clássico: `|M| ≤ 2`; valor quântico ideal: `M = 4`.
- 20 sementes × 4096 tiros por configuração.

## Resultado principal

| Configuração | E medido | IC95 |
|---|---:|---:|
| XXX | +1.0000 | [+1.0000, +1.0000] |
| XYY | -1.0000 | [-1.0000, -1.0000] |
| YXY | -1.0000 | [-1.0000, -1.0000] |
| YYX | -1.0000 | [-1.0000, -1.0000] |

- **M = 4.0000**
- Erro padrão: 0.0000
- IC95: [4.0000, 4.0000]
- p-valor para M > 2: 0.000e+00
- Significância: não estimável (sem variação entre sementes no caso ideal)

O valor ideal é 4; o limite clássico é 2. O resultado acima é uma simulação e não prova violação em hardware.

No caso ideal, o GHZ é autoestado dos quatro correlatores; por isso não há variação entre sementes e o p-valor é 0 por convenção. A parte informativa é a varredura de ruído, que mostra M caindo de 4 para 2,72 em p = 0,05.

## Varredura de ruído

| p (depolarizante) | M | IC95 |
|---|---:|---:|
| 0.000 | +4.0000 | [+4.0000, +4.0000] |
| 0.010 | +3.7000 | [+3.6924, +3.7077] |
| 0.020 | +3.4358 | [+3.4192, +3.4524] |
| 0.050 | +2.7202 | [+2.7003, +2.7401] |

## Limites

- Simulação clássica; não há vantagem quântica nem execução em hardware.
- O modelo de ruído é depolarizante de porta; não é a calibração de um backend específico.
- O IC de M usa a variância de M entre sementes (cálculo pareado); é uma aproximação normal/t de Student, não um bootstrap.
- Nenhum job foi enviado ao GJQ/Tiangong.
