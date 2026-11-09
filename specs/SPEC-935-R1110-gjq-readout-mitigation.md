# SPEC-935-R1110 — Comparação e mitigação de leitura no hardware GJQ

**Status:** implementação local + execução real no Baihua
**Data:** 2026-11-09
**Depende de:** R1109 (otimizadores para hardware GJQ)

## 1. Contexto

A execução R1109 mostrou que o proxy de erro do otimizador foi otimista:
para o Bell/E05, o proxy previa sucesso de 99,4%, mas a fração de outcomes
correlacionados foi 91,6%. A calibração do backend reporta `readout_error`
muito baixo (0,1–0,2%) e `prob_meas*=1.0` como sentinela, o que não permite
construir uma matriz de leitura confiável a partir das propriedades.

Esta spec adiciona duas etapas em sequência:

1. **comparação real** baseline 0/1 vs layout otimizado 106/107, com os mesmos
   shots, target e `transpile=False`;
2. **mitigação de leitura** por calibração |00> e |11> nos mesmos qubits,
   inversão da submatriz 00/11, clipping e renormalização.

## 2. Requisitos

- **R1.** Criar `gjq_hardware_opt/mitigation.py` com modelo de leitura,
  calibração, inversão e métricas.
- **R2.** Calibrar |00> e |11> nos qubits físicos de cada caso; usar `rx(pi)`
  para preparar |1>, pois `x` não pertence à base do Baihua.
- **R3.** Construir a matriz 2x2 restrita a 00/11, normalizando cada coluna
  dentro do subespaço e registrando o leakage para 01/10.
- **R4.** Implementar mitigação por inversão com clipping de massa negativa e
  renormalização; usar pseudoinversa quando a matriz for mal condicionada.
- **R5.** Implementar também a matriz completa 2^n x 2^n a partir do perfil ou
  de calibração completa, limitada a 6 qubits.
- **R6.** Criar o comando `compare` no harness, com baseline
  trivial-operacional, otimizado noise-aware, mesmos shots e `transpile=False`.
- **R7.** Salvar `comparacao.json` e `RELATORIO_COMPARACAO.md` com task IDs,
  counts, auditoria, matrizes, leakage, condição, massa negativa, correlação
  raw, TVD raw e TVD mitigada.
- **R8.** Reportar explicitamente se o ranking do proxy foi confirmado ou não.
- **R9.** Gates: `confirm=True`, `allow_hardware=True`, credencial disponível,
  shots no limite e circuito com medição.
- **R10.** Criar testes sem rede e sem submissão.
- **R11.** Não declarar fidelidade, emaranhamento, vantagem quântica ou
  superioridade do layout otimizado sem evidência estatística.

## 3. Método

### 3.1 Matriz de leitura

Para cada qubit, com `p(1|0)` e `p(0|1)`:

```text
A_q = [[1 - p(1|0), p(0|1)],
       [p(1|0),     1 - p(0|1)]]
```

A matriz do sistema é o produto de Kronecker na ordem MSB → LSB dos bits
clássicos. Se as propriedades assimétricas forem sentinela (`>= 0.5`), usar
`readout_error` de forma simétrica.

### 3.2 Calibração no hardware

Preparar |00> e |11> nos mesmos qubits físicos do caso, medir e construir a
submatriz:

```text
A[0,0] = P(00|00) / (P(00|00) + P(11|00))
A[1,0] = P(11|00) / (P(00|00) + P(11|00))
A[0,1] = P(00|11) / (P(00|11) + P(11|11))
A[1,1] = P(11|11) / (P(00|11) + P(11|11))
```

O leakage `1 - (P(00|s) + P(11|s))` é reportado separadamente.

### 3.3 Inversão

`p_mit = A^{-1} p_obs`; massas negativas são clipadas e o vetor é
renormalizado. A TVD mitigada no subespaço é
`0,5 * (|p00 - 0,5| + |p11 - 0,5|)`.

## 4. Resultado real

### 4.1 Baseline 0/1

- Bell: `ff6e6d03-5bdc-4a6c-ae58-7f222c38833e`
- Cal |00>: `e3a3f553-0760-461e-88e2-a419879ab562`
- Cal |11>: `2bef6384-e800-4d29-87f7-d9fb5ff6c182`
- Counts: `00=2018`, `11=1803`, `10=120`, `01=155`.
- Correlação raw 00/11: 0,9329.
- TVD raw: 0,0671.
- Mitigado: 00=0,5249, 11=0,4751, TVD=0,0249.
- Leakage |11>: 14,1%.

### 4.2 Otimizado 106/107

- Bell: `96cfb671-678f-40f6-b01b-02358f20478a`
- Cal |00>: `d77f3d58-eddd-4603-b220-d40ffa586b0d`
- Cal |11>: `8a33fd13-c6c4-4187-be7e-1a5d234fc3ea`
- Counts: `00=1961`, `11=1718`, `10=248`, `01=169`.
- Correlação raw 00/11: 0,8982.
- TVD raw: 0,1018.
- Mitigado: 00=0,5277, 11=0,4723, TVD=0,0277.
- Leakage |11>: 15,0%.

### 4.3 Comparação

| Métrica | Baseline | Otimizado | Δ (opt − base) |
|---|---:|---:|---:|
| Correlação raw 00/11 | 0,9329 | 0,8982 | −0,0347 |
| TVD raw | 0,0671 | 0,1018 | +0,0347 |
| TVD mitigada | 0,0249 | 0,0277 | +0,0028 |

O proxy previa erro menor para o otimizado (0,0060 vs 0,0338), mas o ranking
**não foi confirmado** no hardware. O baseline foi ligeiramente melhor na
correlação raw e na TVD mitigada. A diferença mitigada é pequena e não
sustenta vantagem estatística.

## 5. Critérios de aceitação

- 6 jobs submetidos e concluídos (3 por caso: |00>, |11>, Bell);
- counts somam 4096 por job;
- matrizes e leakage registrados;
- mitigação reduz a TVD nos dois casos;
- relatório declara que o ranking do proxy não foi confirmado;
- nenhuma chave em arquivo;
- testes R1110 passam sem rede.

## 6. Não objetivos

- Provar fidelidade de estado ou emaranhamento.
- Implementar ZNE, PEC, DD ou correção quântica de erro.
- Fazer tomografia de estado.
- Declarar vantagem do layout otimizado.
- Generalizar uma execução de 4096 shots.

## 7. Riscos

- **Leakage:** a inversão 00/11 não corrige a população que sai para 01/10.
- **Calibração instável:** |11> tem leakage de 14–15%, muito acima do
  `readout_error` reportado. Parte desse leakage é preparação do |1> com
  `rx(pi)`, não readout puro.
- **Amostra pequena:** uma execução por caso não é estudo estatístico.
- **Overclaim:** TVD mitigada não é fidelidade; um ranking local não é
  vantagem quântica.
- **Custo/fila:** 6 submissões por comparação; confirmar o backend e os shots.

## 8. Testes

`tests/test_r1110_gjq_readout_mitigation.py` verifica:

- matriz simétrica e inversão de um caso conhecido;
- submatriz 00/11 e leakage;
- circuito de calibração com `rx(pi)` e ordem MSB/LSB;
- limite de 6 qubits;
- artefatos reais da comparação;
- ausência de segredos e de overclaim.
