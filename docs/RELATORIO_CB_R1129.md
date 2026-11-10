# R1129 — CB intercalado: 13 funções recuperadas em simulação

**Status:** implementação local, sem hardware.
**Depende de:** R1128.
**Artefato:** `harnesses/quantum-error-mitigation/resultados/r1129_interleaved/`.

## Resultado

O desenho com **7 ciclos individuais** e **6 ciclos de pares** forma uma base
de **13 funções** aprendíveis do CZ:

- individuais: `IZ, ZI, XX, XY, YX, YY, ZZ`;
- pares: `IX·ZX, IX·ZY, IY·ZX, XI·XZ, XI·YZ, YI·XZ`.

A matriz de desenho é 13×15, tem posto **13** e nulidade **2**. O resíduo
`B @ D.T` é zero: os ciclos estão no espaço de ciclos do grafo de padrões.
As **2 funções de corte** continuam não medidas.

Na simulação exata com ruído de Pauli antes de cada CZ, as 13 funções foram
recuperadas com erro absoluto máximo de **3,33×10⁻¹⁶**. Isso valida o desenho
e a aritmética; **não** valida o hardware nem o ruído das correções.

## Como o circuito funciona

Para um ciclo de rótulos `P1, ..., Pk`:

1. prepara-se o autoestado de `P1`;
2. para cada `Pi`, aplica-se uma correção de 1 qubit se o Pauli atual não for
   `Pi`, depois o CZ; o ruído Pauli é aplicado antes do CZ e o Pauli seguinte
   é `CZ(Pi)`;
3. ao fechar o ciclo, corrige-se o Pauli de volta a `P1`;
4. mede-se `P1`; a paridade decai como o produto das fidelidades do ciclo.

Para `[XX]`, por exemplo, o CZ leva `XX` a `YY`; a correção `YY→XX` fecha o
ciclo. Para `[IX, ZY]`, o CZ leva `IX` a `ZX`, a correção `ZX→ZY` permite o
segundo CZ, e `IY→IX` fecha o ciclo. Os ciclos cruzados têm sinal `−1` em
profundidade ímpar; por isso o piloto usa profundidades pares.

## Limites

- Ruído de Pauli **antes** do CZ, como no modelo do artigo. O caminho GJQ
  atual aplica ruído depois do CZ; uma execução direta aprenderia fidelidades
  conjugadas, não as mesmas.
- As correções de 1 qubit são ideais no simulador; o ruído delas não foi
  modelado nem medido.
- Não há twirl de Pauli neste piloto; o canal já é Pauli. Hardware exige
  twirl/compensação e auditoria da compilação.
- As 2 funções de corte exigem GST, preparação perfeita ou restrição física.
- Nenhuma taxa foi medida; PEC 2q continua bloqueado.

## Próximo passo

1. Adicionar twirl de Pauli e rastreamento de frame ao desenho intercalado.
2. Simular com ruído nas correções de 1 qubit e verificar a degradação.
3. Pré-registrar shots, seeds, ordem e hipótese de ruído das correções.
4. Só então considerar hardware; as 2 funções de corte continuam fora do CB.

## Reprodução

```bash
.venv-quantum/bin/python - <<'PY'
from quantum_mitigation.interleaved_cb import audit
import json
print(json.dumps(audit(), indent=2, ensure_ascii=False))
PY
```

Ou:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/cb_protocol.py \
  interleaved --out /tmp/opencode/interleaved.json
```

Testes: `tests/test_r1129_interleaved_cb.py`.
