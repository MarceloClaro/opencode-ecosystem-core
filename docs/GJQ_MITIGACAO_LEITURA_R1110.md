# Comparação e mitigação de leitura no Baihua — R1110

**Status:** implementação local + 6 jobs reais no Baihua
**Spec:** `specs/SPEC-935-R1110-gjq-readout-mitigation.md`
**Módulos:** `gjq_hardware_opt/mitigation.py`, `gjq_hardware_opt/comparison.py`
**Comando:** `harnesses/gjq-hardware-optimizers/runner.py compare`

## 1. O que foi feito

Em sequência:

1. **Comparação real** do Bell/E05 no baseline 0/1 e no layout otimizado
   106/107, com **4096 shots** por circuito, mesmo target, mesma seed e
   `transpile=False`.
2. **Calibração de leitura** |00> e |11> nos mesmos qubits de cada caso,
   também com 4096 shots.
3. **Mitigação** da submatriz 00/11 por inversão, clipping e renormalização.

Foram 6 jobs no Baihua: 3 por caso (|00>, |11>, Bell).

## 2. Por que a calibração foi necessária

As propriedades do Baihua reportam:

- `readout_error` de 0,1–0,2%;
- `prob_meas0_prep1 = 1.0` e `prob_meas1_prep0 = 1.0`.

Os valores `1.0` são sentinela e não podem virar matriz de leitura. A
calibração no hardware mede a matriz real de |00> e |11> e evita usar um
número que não descreve o dispositivo.

## 3. Resultado bruto

| Caso | Qubits | Erro proxy | Counts 00 | Counts 11 | Counts 10 | Counts 01 | Raw 00+11 |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0, 1 | 3,379e-2 | 2018 | 1803 | 120 | 155 | **0,9329** |
| Otimizado | 106, 107 | 5,985e-3 | 1961 | 1718 | 248 | 169 | **0,8982** |

O baseline teve **93,29%** de outcomes correlacionados; o otimizado, **89,82%**.
A diferença raw foi de **−3,47 pontos percentuais** para o otimizado.

## 4. Calibração e mitigação

### Baseline 0/1

- Matriz 00/11: `[[0,99924, 0,00767], [0,00076, 0,99233]]`.
- Leakage |00>: 3,05%; |11>: **14,06%**.
- Mitigado: 00 = 0,5249; 11 = 0,4751.
- TVD raw: 0,0671 → **0,0249**.

### Otimizado 106/107

- Matriz 00/11: `[[0,99975, 0,01149], [0,00025, 0,98851]]`.
- Leakage |00>: 2,47%; |11>: **15,01%**.
- Mitigado: 00 = 0,5277; 11 = 0,4723.
- TVD raw: 0,1018 → **0,0277**.

A mitigação reduziu a TVD dos dois casos, mas **não** tornou o layout otimizado
melhor: a TVD mitigada do baseline ficou 0,0028 abaixo da do otimizado.

## 5. Interpretação

| Métrica | Baseline | Otimizado | Δ (opt − base) |
|---|---:|---:|---:|
| Correlação raw 00/11 | 0,9329 | 0,8982 | −0,0347 |
| TVD raw | 0,0671 | 0,1018 | +0,0347 |
| TVD mitigada | 0,0249 | 0,0277 | +0,0028 |

O proxy de erro previa o contrário: baseline 0,0338 e otimizado 0,0060. O
ranking do proxy **não foi confirmado** no hardware. Isso não significa que o
layout noise-aware seja inútil; significa que a calibração declarada pelo
backend não foi suficiente para prever o desempenho deste Bell.

O leakage de |11> foi de 14,1% no baseline e 15,0% no otimizado, muito acima do
`readout_error` reportado (0,1–0,2%). Parte desse leakage é preparação do |1>
com `rx(pi)`, não readout puro. A inversão 00/11 corrige flips 00↔11, mas não
corrige a população que sai para 01/10. Essa é a principal limitação da
mitigação implementada: ela reduz a TVD, mas não separa completamente readout
de state preparation.

## 6. Comandos

```bash
# comparação + calibração + mitigação (6 jobs)
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py compare \
  --backend Baihua --circuit E05 --shots 4096 --quick \
  --confirm --allow-hardware --calibrate \
  --use-cached-account \
  --out harnesses/gjq-hardware-optimizers/resultados/baihua/E05_comparacao

# somente comparação, usando a matriz simétrica do perfil (2 jobs)
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py compare \
  --backend Baihua --circuit E05 --shots 4096 --quick \
  --confirm --allow-hardware --no-calibrate \
  --use-cached-account \
  --out harnesses/gjq-hardware-optimizers/resultados/baihua/E05_comparacao_perfil
```

## 7. Artefatos

- `resultados/baihua/E05_comparacao/comparacao.json`;
- `resultados/baihua/E05_comparacao/RELATORIO_COMPARACAO.md`;
- `resultados/baihua/E05_comparacao/baseline/` — QASM, counts, `caso.json`;
- `resultados/baihua/E05_comparacao/otimizado/` — QASM, counts, `caso.json`.

Task IDs:

| Caso | Job | Task ID |
|---|---|---|
| Baseline | Bell | `ff6e6d03-5bdc-4a6c-ae58-7f222c38833e` |
| Baseline | Cal |00> | `e3a3f553-0760-461e-88e2-a419879ab562` |
| Baseline | Cal |11> | `2bef6384-e800-4d29-87f7-d9fb5ff6c182` |
| Otimizado | Bell | `96cfb671-678f-40f6-b01b-02358f20478a` |
| Otimizado | Cal |00> | `d77f3d58-eddd-4603-b220-d40ffa586b0d` |
| Otimizado | Cal |11> | `8a33fd13-c6c4-4187-be7e-1a5d234fc3ea` |

## 8. Limites

- Uma execução por caso não é estudo estatístico.
- A diferença mitigada de 0,0028 não sustenta vantagem.
- A calibração |11> usa `rx(pi)` e inclui preparação do |1>; não separa
  completamente readout de state preparation. Crosstalk, deriva e leakage fora
  do subespaço também não são capturados.
- A TVD mitigada não é fidelidade de estado.
- Não há ZNE, PEC, DD ou correção quântica de erro.
- Custo, fila e calibração podem mudar; o resultado vale para a janela
  registrada.

## 9. Referências de apoio

QISKIT. **Measurement error mitigation**. Disponível em:
https://docs.quantum.ibm.com/run/configure-error-mitigation. Acesso em:
9 nov. 2026.

GJQ. **gjq-client 0.2.1**. Disponível em:
https://github.com/guoji-quantum/gjq_client. Acesso em: 9 nov. 2026.
