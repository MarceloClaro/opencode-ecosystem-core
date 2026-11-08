# Prática Tiangong: SWAP test {#swap-test}


O **SWAP test** estima a sobreposição entre dois estados quânticos,
|ψ†φ|², usando uma ancilla e uma porta CSWAP. É um
teste pequeno, mas útil: aparece em verificação de estados, kernels quânticos e
comparação de representações.

## O circuito

- `q0`: ancilla;
- `q1`: |ψ⟩ = |0⟩;
- `q2`: |φ⟩ = Ry(1,0)|0⟩;
- H, CSWAP, H, medir `q0`.

A probabilidade de medir `0` na ancilla é

<div class="formula">P(0) = (1 + |ψ†φ|²) / 2</div>

Logo,

<div class="formula">|ψ†φ|² = 2P(0) − 1</div>

### QASM 2.0

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[1];
ry(1.000000) q[2];
h q[0];
cswap q[0],q[1],q[2];
h q[0];
measure q[0] -> c[0];
```

> **Nota de compatibilidade:** o editor da Tiangong aceita `cswap` no QASM 2.0.
> O parser do Qiskit 2.x usado nesta edição não resolve `cswap` no `qasm2.loads`;
> por isso o script monta o circuito com a porta nativa `qc.cswap`.

## Resultados do SWAP {#swap-resultados}

O script `scripts/pratica_swap_test.py` simula e envia ao **Guoji08** com 1024
tiros. O task ID fica em `dados_hardware/swap_test_guoji08.json`.

| Condição | P(0) | Sobreposição estimada |
|---|---:|---:|
| ideal | 0,8851 | 0,7702 |
| simulado | 0,8851 | 0,7702 |
| backend Guoji08 | 0,8145 | 0,6289 |

![**Figura S1.** SWAP test: P(0) e sobreposição estimada. O backend reduz a
sobreposição de 0,7702 para 0,6289; a diferença é ruído de porta, leitura e
preparação.](../livro/figuras_geradas/fig24_swap_test.png){#fig-s1}

**Leitura:** o hardware preserva a tendência (P(0) > 0,5; sobreposição > 0),
mas erra o valor ideal. Com 1024 tiros, a incerteza estatística de P(0) é da
ordem de 1%, não de 7%. A diferença observada é **sistêmica**, não só amostral.

## Prática de 10 minutos

1. Abra o editor QASM da Tiangong e cole o código.
2. Selecione `Guoji No.8` e 1024 tiros.
3. Calcule P(0) = N0/N e a sobreposição 2P(0) − 1.
4. Compare com a tabela acima.
5. Repita com Ry(0,5) e Ry(2,0); a sobreposição deve mudar.

## O que o SWAP test não prova

- **Não é tomografia.** Um escalar não reconstrói o estado.
- **Não é fidelidade de processo.** Ele compara dois estados preparados, não
  mede a qualidade das portas.
- **A preparação importa.** Se |φ⟩ já vem com erro, a sobreposição
  estimada mistura erro de preparação e erro do teste.
- **Ruído de leitura engana.** Um erro assimétrico em `0`/`1` desloca P(0).
- **Um número não é uma certificação.** Para verificação, repita com seeds,
  estados e backend diferentes.

> **Para o professor:** use o SWAP test como “primeiro experimento de
> comparação”. Ele cabe em uma aula, tem uma fórmula simples e produz um número
> que o aluno pode calcular à mão.