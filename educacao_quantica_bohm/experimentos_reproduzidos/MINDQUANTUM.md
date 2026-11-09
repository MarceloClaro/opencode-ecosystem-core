# MindQuantum — estado e portabilidade

## O que foi verificado

- Fonte local: `mindquantum-master` (MindQuantum **0.12.0**).
- Requisito declarado em `pyproject.toml`: **Python >=3.9,<3.13**.
- O ambiente principal do projeto usa **Python 3.14**; há Python 3.11 e
  3.12 disponíveis, mas **MindSpore não está instalado** em nenhum deles.
- Não há extensão compilada (`.so`) no checkout; o build exige CMake,
  compilador C++ e MindSpore.
- O índice PyPI não respondeu no ambiente desta execução; não foi possível
  instalar `mindquantum` nem `mindspore`.
- Portanto, **nenhum código MindQuantum foi executado nesta rodada**.
  Não trate esta nota como resultado experimental.

## O que foi executado no lugar

A reprodução E01–E18 e o novo E19 usam **Qiskit 2.3 + Aer 0.18.2**, que já
estão instalados no `.venv-quantum`. Os circuitos são pequenos e compatíveis
com OpenQASM 2.0; a escolha permite reproduzir os resultados agora, sem
declarar uma execução que não aconteceu.

## Caminho de portabilidade (não executado)

O circuito do E19 (GHZ de 3 qubits + rotações de base) pode ser escrito em
MindQuantum assim:

```python
from mindquantum import Circuit

# GHZ de 3 qubits
circ = Circuit().h(0).x(1, 0).x(2, 1)

# Base X em um qubit: H antes da medição.
# Base Y em um qubit: S† seguido de H.
# A medição e a contagem ficam a cargo do simulador/backend escolhido.
```

Para portar de fato, é preciso:

1. Criar um ambiente Python 3.11 ou 3.12.
2. Instalar MindSpore e MindQuantum compatíveis com essa versão.
3. Traduzir as rotações de base e a medição para a API de circuito do
   MindQuantum.
4. Repetir o protocolo de 20 sementes × 4096 tiros e comparar o valor de
   `M` com o resultado Qiskit.
5. Registrar versão, hash do circuito e seed no JSON.

## Limite

Esta nota é um **relatório de bloqueio**, não uma prova de que MindQuantum
funciona ou não funciona no hardware. A ausência de execução local não diz
nada sobre a qualidade do framework.
