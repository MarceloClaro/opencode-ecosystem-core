# Código completo: os 18 experimentos, da instalação ao resultado {#codigo-experimentos}

Este capítulo existe porque uma referência não basta. Quando a lauda diz
`Script: scripts/experimentos_100.py · E09 · Guoji08`, o leitor tem o direito de
ver o código, saber onde salvá-lo, como instalar o ambiente e como comparar o
resultado com o número impresso no livro. É o que este capítulo faz.

O script abaixo é a **versão standalone** dos 18 experimentos-base. O script
original do projeto, `scripts/experimentos_100.py`, importa a base de conceitos
e a base de experimentos do repositório. Para o leitor que só tem o PDF, esta
versão é autossuficiente: os 18 circuitos estão embutidos, e o programa roda
com dois pacotes (`qiskit` e `numpy`), mais `gjq-client` apenas para o hardware.

> **O que este script faz:** simula os 18 circuitos com 1024 tiros, calcula uma
> leitura pedagógica para cada um, opcionalmente envia ao backend
> Tiangong/Guoji08 e grava JSON + CSV. Ele **não** prova emaranhamento, não
> mede fidelidade de estado e não substitui a calibração do backend.

## 1. O que você precisa {#codigo-pre-requisitos}

- Python 3.12 ou superior.
- `pip` atualizado.
- Internet para instalar os pacotes e, se quiser, para acessar o backend.
- Uma conta na Tiangong para a API key (opcional para a simulação).
- 10 minutos para a primeira execução.

## 2. Instalação {#codigo-instalacao}

### Linux/macOS {#codigo-linux}

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install qiskit qiskit-aer gjq-client numpy scipy matplotlib optuna
```

### Windows (PowerShell) {#codigo-windows}

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install qiskit qiskit-aer gjq-client numpy scipy matplotlib optuna
```

## 3. Salve o script

Crie uma pasta de trabalho e salve o código da seção 8 como
`08_experimentos_18.py`:

```bash
mkdir -p ~/quantica
cd ~/quantica
# abra o editor, cole o código da seção 8 e salve como 08_experimentos_18.py
```

No Windows, use `mkdir %USERPROFILE%\quantica` e salve o arquivo na pasta.

## 4. Rode um experimento: E09

O E09 é a codificação de amplitude: `Ry(2π/3)|0⟩` prepara `P(1)=0,75`. O comando
roda só esse experimento, no simulador local:

```bash
python 08_experimentos_18.py --sim --only E09
```

Saída esperada (a contagem varia com a seed e com 1024 tiros):

```text
== simulação ==
  ✓ E09 Codificação de amplitude: P(1) = 0.738 (ideal 0,750)
```

O script grava `dados/E09.json`. Abra o arquivo: você verá `simulado.counts`
com um dicionário de counts e `simulado.leitura` com a frase acima. A soma dos
counts deve ser 1024.

### 4.1 Compare com o livro

O backend desta edição devolveu, para o E09:

| Resultado | Count | Conta |
|---|---:|---|
| `1` | 761 | 761/1024 = 0,7432 |
| `0` | 263 | 263/1024 = 0,2568 |

O ideal é 0,750. A diferença de 0,0068 é compatível com 1024 tiros e com erro
de porta/leitura. O script mostra o mesmo tipo de número; a seed muda a
contagem simulada, não a fórmula.

## 5. Rode os 18 e gere o relatório

```bash
python 08_experimentos_18.py --sim
python 08_experimentos_18.py --report
```

O primeiro comando grava `dados/E01.json` a `dados/E18.json`. O segundo grava
`dados/RELATORIO_EXPERIMENTOS.md` e `dados/experimentos.csv`. O CSV tem as
colunas `id`, `experimento`, `simulado`, `backend` e `sobreposicao`.

Para repetir com outra seed:

```bash
python 08_experimentos_18.py --sim --seed 7
```

## 6. Rode no hardware

1. Crie a API key em <https://tiangongqs.com/cloud/circuit>.
2. Exporte a chave **apenas no ambiente**:

```bash
export GJQ_API_KEY="sua-chave"        # Linux/macOS
# PowerShell: $env:GJQ_API_KEY = "sua-chave"
```

3. Rode a simulação primeiro; o script exige o JSON simulado antes do backend:

```bash
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --real --backend Guoji08 --only E09
```

Saída esperada (o task ID e os counts mudam):

```text
== backend ==
  ✓ E09 Codificação de amplitude: P(1) = 0.743 (ideal 0,750)
```

O JSON passa a ter `real.counts`, `real.task_ids`, `real.backend`,
`real.shots` e `real.timestamp`. Se a execução falhar, o campo `real_erro`
registra a exceção; a simulação permanece intacta.

> **Nunca** grave a chave no script, no caderno ou no repositório. Se ela
> vazar, revogue, apague o cache `~/.gjq_client/gjq_client_account.json` e
> audite as tarefas.

## 7. O que o número significa

A leitura do E09 é `P(1) = N1/N`. Para o backend, `761/1024 = 0,7432`. A
simulação usa o mesmo cálculo, com os counts amostrados do statevector. A
métrica `sobreposicao`, quando existe, é
`Σ_b min(p_sim[b], p_real[b])`: ela mede semelhança entre distribuições, não
fidelidade de estado nem emaranhamento.

## 8. Código por experimento

Cada seção abaixo é o recorte executável do experimento. O script
completo, com o CLI e o relatório, está na seção 9.

> Os recortes usam as funções auxiliares `_p` e `_soma`, definidas
> no script completo (seção 9). Para executar um recorte isolado,
> copie também essas duas funções.

### E01 — Base |0⟩ {#codigo-e01}

```python
def qc_basis0() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.measure(0, 0); return qc
```

```python
def leitura_p0(cs): return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E01
python 08_experimentos_18.py --real --backend Guoji08 --only E01
```

### E02 — Base |1⟩ e leitura {#codigo-e02}

```python
def qc_basis1() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.x(0); qc.measure(0, 0); return qc
```

```python
def leitura_p1(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E02
python 08_experimentos_18.py --real --backend Guoji08 --only E02
```

### E03 — Superposição H|0⟩ {#codigo-e03}

```python
def qc_superposicao() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc
```

```python
def leitura_superposicao(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"
```

```bash
python 08_experimentos_18.py --sim --only E03
python 08_experimentos_18.py --real --backend Guoji08 --only E03
```

### E04 — Interferência H-Z-H {#codigo-e04}

```python
def qc_fase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.z(0); qc.h(0); qc.measure(0, 0); return qc
```

```python
def leitura_fase(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E04
python 08_experimentos_18.py --real --backend Guoji08 --only E04
```

### E05 — Estado de Bell {#codigo-e05}

```python
def qc_bell() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1]); return qc
```

```python
def leitura_bell(cs): return f"P(00)+P(11) = {_soma(cs[0], ('00', '11')):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E05
python 08_experimentos_18.py --real --backend Guoji08 --only E05
```

### E06 — GHZ de 4 qubits {#codigo-e06}

```python
def qc_ghz4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4); qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3]); return qc
```

```python
def leitura_ghz(cs): return f"P(0000)+P(1111) = {_soma(cs[0], ('0000', '1111')):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E06
python 08_experimentos_18.py --real --backend Guoji08 --only E06
```

### E07 — CHSH {#codigo-e07}

```python
CHSH = [("E00", 0, -np.pi / 4), ("E01", 0, np.pi / 4),
        ("E10", 1, -np.pi / 4), ("E11", 1, np.pi / 4)]
```

```python
def qc_chsh(a1: int, angulo: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(angulo, 1); qc.measure([0, 1], [0, 1]); return qc
```

```python
def qcs_chsh() -> list[QuantumCircuit]:
    return [qc_chsh(a1, float(ang)) for _, a1, ang in CHSH]
```

```python
def leitura_chsh(cs):
    E = [_p(c, "00") + _p(c, "11") - _p(c, "01") - _p(c, "10") for c in cs]
    return f"S = {E[0] + E[1] + E[2] - E[3]:.3f} (ideal 2,828)"
```

```bash
python 08_experimentos_18.py --sim --only E07
python 08_experimentos_18.py --real --backend Guoji08 --only E07
```

### E08 — Gerador quântico de números {#codigo-e08}

```python
def qc_qrng() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc
```

```python
def leitura_qrng(cs):
    return f"|P(0)-P(1)| = {abs(_p(cs[0], '0') - _p(cs[0], '1')):.3f} (ideal 0,000)"
```

```bash
python 08_experimentos_18.py --sim --only E08
python 08_experimentos_18.py --real --backend Guoji08 --only E08
```

### E09 — Codificação de amplitude {#codigo-e09}

```python
def qc_amplitude() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.ry(2 * np.pi / 3, 0); qc.measure(0, 0); return qc
```

```python
def leitura_amplitude(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,750)"
```

```bash
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --real --backend Guoji08 --only E09
```

### E10 — Classificador XOR (VQC) {#codigo-e10}

> O E10 é o classificador XOR: quatro entradas, quatro
> medições e uma acurácia. O treino completo está no
> `07_vqc_ruido.py`; aqui o circuito usa os parâmetros já
> treinados.

```python
XOR = [(0, 0), (0, 1), (1, 0), (1, 1)]
```

```python
THETA = [1.5708, 1.5708, -1.5708, 2.819]
```

```python
def qc_vqc(x: tuple[int, int]) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * x[0], 0); qc.ry(np.pi * x[1], 1)
    qc.ry(THETA[0], 0); qc.ry(THETA[1], 1)
    qc.cx(0, 1)
    qc.ry(THETA[2], 0); qc.ry(THETA[3], 1)
    qc.measure(0, 0); return qc
```

```python
def qcs_vqc() -> list[QuantumCircuit]:
    return [qc_vqc(x) for x in XOR]
```

```python
def leitura_vqc(cs):
    acertos = 0
    for c, x in zip(cs, XOR):
        y = 1 if x[0] != x[1] else 0
        pred = 1 if _p(c, "1") >= 0.5 else 0
        acertos += int(pred == y)
    return f"Acurácia = {acertos}/4"
```

```bash
python 08_experimentos_18.py --sim --only E10
python 08_experimentos_18.py --real --backend Guoji08 --only E10
```

### E11 — Interferência de dois qubits {#codigo-e11}

```python
def qc_interferencia2() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.h(1); qc.cz(0, 1); qc.h(0)
    qc.measure([0, 1], [0, 1]); return qc
```

```python
def leitura_interferencia2(cs): return f"P(00) = {_p(cs[0], '00'):.3f} (ideal 0,500)"
```

```bash
python 08_experimentos_18.py --sim --only E11
python 08_experimentos_18.py --real --backend Guoji08 --only E11
```

### E12 — QFT de 3 qubits {#codigo-e12}

```python
def qc_qft3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3); qc.x(2); qc.append(QFTGate(3), range(3))
    qc.measure([0, 1, 2], [0, 1, 2]); return qc
```

```python
def leitura_qft3(cs): return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,125)"
```

```bash
python 08_experimentos_18.py --sim --only E12
python 08_experimentos_18.py --real --backend Guoji08 --only E12
```

### E13 — Produto tensorial |01⟩ {#codigo-e13}

```python
def qc_tensor01() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.x(0); qc.measure([0, 1], [0, 1]); return qc
```

```python
def leitura_tensor01(cs): return f"P(01) = {_p(cs[0], '01'):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E13
python 08_experimentos_18.py --real --backend Guoji08 --only E13
```

### E14 — Ruído de fase {#codigo-e14}

```python
def qc_ruido_phase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.x(0); qc.h(0); qc.measure(0, 0); return qc
```

```python
def leitura_ruido(cs): return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E14
python 08_experimentos_18.py --real --backend Guoji08 --only E14
```

### E15 — GHZ via QASM 2.0 {#codigo-e15}

> A versão standalone monta o GHZ com `qc_ghz4()`; o
> script original carrega o mesmo circuito de um texto QASM 2.0.

```python
def qc_ghz4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4); qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3]); return qc
```

```python
def leitura_ghz(cs): return f"P(0000)+P(1111) = {_soma(cs[0], ('0000', '1111')):.3f} (ideal 1,000)"
```

```bash
python 08_experimentos_18.py --sim --only E15
python 08_experimentos_18.py --real --backend Guoji08 --only E15
```

### E16 — Esfera de Bloch {#codigo-e16}

```python
def qc_superposicao() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc
```

```python
def qc_basis0() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.measure(0, 0); return qc
```

```python
def leitura_bloch(cs):
    return f"⟨Z⟩ = {2*_p(cs[0], '0')-1:+.3f}, ⟨X⟩ = {2*_p(cs[1], '0')-1:+.3f} (ideal 0, +1)"
```

```bash
python 08_experimentos_18.py --sim --only E16
python 08_experimentos_18.py --real --backend Guoji08 --only E16
```

### E17 — Interferência de três qubits {#codigo-e17}

```python
def qc_walk3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3); qc.h(0); qc.h(1); qc.h(2)
    qc.cz(0, 1); qc.cz(1, 2); qc.h(0); qc.h(1); qc.h(2)
    qc.measure([0, 1, 2], [0, 1, 2]); return qc
```

```python
def leitura_walk3(cs): return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,250)"
```

```bash
python 08_experimentos_18.py --sim --only E17
python 08_experimentos_18.py --real --backend Guoji08 --only E17
```

### E18 — Amostragem binomial {#codigo-e18}

```python
def qc_superposicao() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc
```

```python
def leitura_amostragem(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"
```

```bash
python 08_experimentos_18.py --sim --only E18
python 08_experimentos_18.py --real --backend Guoji08 --only E18
```


## 9. Código completo {#codigo-script-completo}

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Versão standalone dos 18 experimentos-base do livro.

Roda a simulação local (statevector + amostragem), envia ao backend
Tiangong/Guoji quando solicitado e grava JSON + CSV em `dados/`.

Uso:
    python 08_experimentos_18.py --sim
    python 08_experimentos_18.py --sim --only E09
    python 08_experimentos_18.py --real --backend Guoji08 --only E09
    python 08_experimentos_18.py --report

A chave é lida somente de GJQ_API_KEY. O script nunca grava a chave.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Statevector

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

XOR = [(0, 0), (0, 1), (1, 0), (1, 1)]
THETA = [1.5708, 1.5708, -1.5708, 2.819]
CHSH = [("E00", 0, -np.pi / 4), ("E01", 0, np.pi / 4),
        ("E10", 1, -np.pi / 4), ("E11", 1, np.pi / 4)]


def agora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _p(counts: dict, chave: str) -> float:
    total = sum(int(v) for v in counts.values())
    return int(counts.get(chave, 0)) / total if total else 0.0


def _soma(counts: dict, chaves: tuple[str, ...]) -> float:
    return sum(_p(counts, c) for c in chaves)


# ---------------------------------------------------------------- circuitos

def qc_basis0() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.measure(0, 0); return qc


def qc_basis1() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.x(0); qc.measure(0, 0); return qc


def qc_superposicao() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc


def qc_fase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.z(0); qc.h(0); qc.measure(0, 0); return qc


def qc_bell() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1]); return qc


def qc_ghz4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4); qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3]); return qc


def qc_chsh(a1: int, angulo: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(angulo, 1); qc.measure([0, 1], [0, 1]); return qc


def qcs_chsh() -> list[QuantumCircuit]:
    return [qc_chsh(a1, float(ang)) for _, a1, ang in CHSH]


def qc_qrng() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0, 0); return qc


def qc_amplitude() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.ry(2 * np.pi / 3, 0); qc.measure(0, 0); return qc


def qc_vqc(x: tuple[int, int]) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * x[0], 0); qc.ry(np.pi * x[1], 1)
    qc.ry(THETA[0], 0); qc.ry(THETA[1], 1)
    qc.cx(0, 1)
    qc.ry(THETA[2], 0); qc.ry(THETA[3], 1)
    qc.measure(0, 0); return qc


def qcs_vqc() -> list[QuantumCircuit]:
    return [qc_vqc(x) for x in XOR]


def qc_interferencia2() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.h(0); qc.h(1); qc.cz(0, 1); qc.h(0)
    qc.measure([0, 1], [0, 1]); return qc


def qc_qft3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3); qc.x(2); qc.append(QFTGate(3), range(3))
    qc.measure([0, 1, 2], [0, 1, 2]); return qc


def qc_tensor01() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2); qc.x(0); qc.measure([0, 1], [0, 1]); return qc


def qc_ruido_phase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1); qc.h(0); qc.x(0); qc.h(0); qc.measure(0, 0); return qc


def qc_walk3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3); qc.h(0); qc.h(1); qc.h(2)
    qc.cz(0, 1); qc.cz(1, 2); qc.h(0); qc.h(1); qc.h(2)
    qc.measure([0, 1, 2], [0, 1, 2]); return qc


# ---------------------------------------------------------------- leituras

def leitura_p0(cs): return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"
def leitura_p1(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"
def leitura_superposicao(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"
def leitura_fase(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"
def leitura_bell(cs): return f"P(00)+P(11) = {_soma(cs[0], ('00', '11')):.3f} (ideal 1,000)"
def leitura_ghz(cs): return f"P(0000)+P(1111) = {_soma(cs[0], ('0000', '1111')):.3f} (ideal 1,000)"


def leitura_chsh(cs):
    E = [_p(c, "00") + _p(c, "11") - _p(c, "01") - _p(c, "10") for c in cs]
    return f"S = {E[0] + E[1] + E[2] - E[3]:.3f} (ideal 2,828)"


def leitura_qrng(cs):
    return f"|P(0)-P(1)| = {abs(_p(cs[0], '0') - _p(cs[0], '1')):.3f} (ideal 0,000)"


def leitura_amplitude(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,750)"


def leitura_vqc(cs):
    acertos = 0
    for c, x in zip(cs, XOR):
        y = 1 if x[0] != x[1] else 0
        pred = 1 if _p(c, "1") >= 0.5 else 0
        acertos += int(pred == y)
    return f"Acurácia = {acertos}/4"


def leitura_interferencia2(cs): return f"P(00) = {_p(cs[0], '00'):.3f} (ideal 0,500)"
def leitura_qft3(cs): return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,125)"
def leitura_tensor01(cs): return f"P(01) = {_p(cs[0], '01'):.3f} (ideal 1,000)"
def leitura_ruido(cs): return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"


def leitura_bloch(cs):
    return f"⟨Z⟩ = {2*_p(cs[0], '0')-1:+.3f}, ⟨X⟩ = {2*_p(cs[1], '0')-1:+.3f} (ideal 0, +1)"


def leitura_walk3(cs): return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,250)"
def leitura_amostragem(cs): return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"


EXPERIMENTOS = {
    "E01": ("Base |0⟩", "Prepara |0⟩ e mede 1024 vezes.", lambda: [qc_basis0()], leitura_p0),
    "E02": ("Base |1⟩ e leitura", "Prepara |1⟩ e mede; a discrepância é erro de leitura.", lambda: [qc_basis1()], leitura_p1),
    "E03": ("Superposição H|0⟩", "H cria uma superposição; a medição produz 0 ou 1.", lambda: [qc_superposicao()], leitura_superposicao),
    "E04": ("Interferência H-Z-H", "A fase Z inverte a interferência: o resultado vira |1⟩.", lambda: [qc_fase()], leitura_fase),
    "E05": ("Estado de Bell", "H + CNOT criam uma correlação 00/11.", lambda: [qc_bell()], leitura_bell),
    "E06": ("GHZ de 4 qubits", "Quatro qubits compartilham 0000/1111.", lambda: [qc_ghz4()], leitura_ghz),
    "E07": ("CHSH", "Quatro configurações medem S.", qcs_chsh, leitura_chsh),
    "E08": ("Gerador quântico de números", "H + medição produzem bits aproximadamente equilibrados.", lambda: [qc_qrng()], leitura_qrng),
    "E09": ("Codificação de amplitude", "Ry(2π/3) prepara P(1)=0,75.", lambda: [qc_amplitude()], leitura_amplitude),
    "E10": ("Classificador XOR (VQC)", "Quatro entradas, quatro medições, uma acurácia.", qcs_vqc, leitura_vqc),
    "E11": ("Interferência de dois qubits", "H, CZ e H concentram a distribuição em 00/11.", lambda: [qc_interferencia2()], leitura_interferencia2),
    "E12": ("QFT de 3 qubits", "A transformada de Fourier quântica uniformiza a saída.", lambda: [qc_qft3()], leitura_qft3),
    "E13": ("Produto tensorial |01⟩", "X no qubit 1 prepara |01⟩.", lambda: [qc_tensor01()], leitura_tensor01),
    "E14": ("Ruído de fase", "H-X-H deveria devolver P(0)=1; o backend perde coerência.", lambda: [qc_ruido_phase()], leitura_ruido),
    "E15": ("GHZ via QASM 2.0", "O mesmo GHZ carregado de um texto OpenQASM 2.0.", lambda: [qc_ghz4()], leitura_ghz),
    "E16": ("Esfera de Bloch", "Mede Z e X do estado H|0⟩.", lambda: [qc_superposicao(), qc_basis0()], leitura_bloch),
    "E17": ("Interferência de três qubits", "Uma caminhada curta distribui amplitude em 000/010/101/111.", lambda: [qc_walk3()], leitura_walk3),
    "E18": ("Amostragem binomial", "H + medição; o desvio de P(1) cai com o número de tiros.", lambda: [qc_superposicao()], leitura_amostragem),
}


def circuitos(exp_id: str) -> list[QuantumCircuit]:
    return EXPERIMENTOS[exp_id][2]()


def leitura(exp_id: str, counts: list[dict]) -> str:
    return EXPERIMENTOS[exp_id][3](counts)


# ---------------------------------------------------------------- simulação

def simular(qc: QuantumCircuit, shots: int, rng: np.random.Generator) -> dict[str, int]:
    medidas = []
    for instr in qc.data:
        if instr.operation.name == "measure":
            q = qc.find_bit(instr.qubits[0]).index
            c = qc.find_bit(instr.clbits[0]).index
            medidas.append((q, c))
    limpo = qc.remove_final_measurements(inplace=False)
    probs = Statevector(limpo).probabilities_dict()
    chaves = [str(k) for k in probs]
    pesos = np.array([float(probs[k]) for k in probs], dtype=float)
    pesos = pesos / pesos.sum()
    amostras = rng.choice(chaves, size=shots, p=pesos)
    if not medidas:
        return dict(Counter(str(x) for x in amostras))
    n, m = qc.num_qubits, qc.num_clbits
    counts: Counter[str] = Counter()
    for amostra in amostras:
        s = str(amostra)
        bits = ["0"] * m
        for q, c in medidas:
            bits[m - 1 - c] = s[n - 1 - q]
        counts["".join(bits)] += 1
    return dict(counts)


def rodar_sim(shots: int, seed: int, apenas: list[str] | None) -> None:
    rng = np.random.default_rng(seed)
    for exp_id in (apenas or list(EXPERIMENTOS)):
        nome, desc, _, _ = EXPERIMENTOS[exp_id]
        counts = [simular(qc, shots, rng) for qc in circuitos(exp_id)]
        dados = {
            "id": exp_id, "nome": nome, "descricao": desc,
            "simulado": {"counts": counts, "leitura": leitura(exp_id, counts),
                         "shots": shots, "metodo": "statevector + amostragem"},
            "real": None, "sobreposicao": None, "timestamp": agora(),
        }
        caminho = SAIDA / f"{exp_id}.json"
        anterior = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
        if anterior.get("real"):
            dados["real"] = anterior["real"]
            dados["sobreposicao"] = anterior.get("sobreposicao")
        caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✓ {exp_id} {nome}: {dados['simulado']['leitura']}")


def chave_api() -> str:
    chave = os.environ.get("GJQ_API_KEY", "").strip()
    if not chave:
        raise SystemExit("GJQ_API_KEY ausente; defina a chave apenas no ambiente.")
    return chave


def probabilidades(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total else {}


def sobreposicao(a: dict[str, int], b: dict[str, int]) -> float:
    pa, pb = probabilidades(a), probabilidades(b)
    return sum(min(pa.get(k, 0.0), pb.get(k, 0.0)) for k in set(pa) | set(pb))


def sobreposicao_lista(a: list[dict], b: list[dict]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(sobreposicao(x, y) for x, y in zip(a, b)) / len(a)


def rodar_real(backend_nome: str, shots: int, timeout: float, seed: int,
               nivel: int, apenas: list[str] | None) -> None:
    from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

    servico = GJQRuntimeService(api_key=chave_api())
    backend = servico.backend(backend_nome)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=nivel,
                                      seed_transpiler=seed)
    for exp_id in (apenas or list(EXPERIMENTOS)):
        nome, _, _, _ = EXPERIMENTOS[exp_id]
        caminho = SAIDA / f"{exp_id}.json"
        if not caminho.exists():
            raise SystemExit(f"Rode --sim antes de --real ({exp_id} sem JSON).")
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if dados.get("real") and dados["real"].get("backend") == backend_nome:
            print(f"  · {exp_id} já tem resultado real em {backend_nome}; pulando.")
            continue
        try:
            counts, task_ids = [], []
            for qc in circuitos(exp_id):
                job = Sampler(backend=backend).run(pm.run(qc), shots=shots)
                task_ids.append(getattr(job, "_job_id", None))
                counts.append({str(k): int(v) for k, v in dict(
                    job.result(timeout=timeout)["counts"]).items()})
            dados["real"] = {"counts": counts, "leitura": leitura(exp_id, counts),
                             "task_ids": task_ids, "backend": backend.name,
                             "shots": shots, "timestamp": agora()}
            if dados.get("simulado"):
                dados["sobreposicao"] = sobreposicao_lista(dados["simulado"]["counts"], counts)
            caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✓ {exp_id} {nome}: {dados['real']['leitura']}")
        except Exception as exc:
            dados["real_erro"] = f"{type(exc).__name__}: {exc}"
            caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✗ {exp_id} falhou: {type(exc).__name__}: {exc}", file=sys.stderr)


def relatorio() -> None:
    def celula(texto) -> str:
        return str(texto).replace("|", "&#124;")

    linhas = ["# Relatório dos 18 experimentos", "",
              "| ID | Experimento | Simulado | Backend | Sobreposição |",
              "|---|---|---|---|---:|"]
    csv_linhas = [["id", "experimento", "simulado", "backend", "sobreposicao"]]
    for exp_id, (nome, _, _, _) in EXPERIMENTOS.items():
        caminho = SAIDA / f"{exp_id}.json"
        d = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else {}
        sim = (d.get("simulado") or {}).get("leitura", "—")
        real = (d.get("real") or {}).get("leitura", "—")
        ov = d.get("sobreposicao")
        ov_txt = f"{ov:.1%}" if isinstance(ov, (int, float)) else "—"
        linhas.append(
            f"| {exp_id} | {celula(nome)} | {celula(sim)} | "
            f"{celula(real)} | {ov_txt} |"
        )
        csv_linhas.append([exp_id, nome, sim, real, ov_txt])
    (SAIDA / "RELATORIO_EXPERIMENTOS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    with (SAIDA / "experimentos.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(csv_linhas)
    print(f"Relatório: {SAIDA / 'RELATORIO_EXPERIMENTOS.md'}")
    print(f"CSV: {SAIDA / 'experimentos.csv'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default="Guoji08")
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--optimization-level", type=int, default=2, choices=[0, 1, 2, 3])
    ap.add_argument("--only", nargs="+", choices=list(EXPERIMENTOS), default=None)
    args = ap.parse_args()

    if args.dry_run:
        print(f"Experimentos: {len(EXPERIMENTOS)} | shots: {args.shots}")
        for exp_id in EXPERIMENTOS:
            print(f"  {exp_id} {EXPERIMENTOS[exp_id][0]}: {len(circuitos(exp_id))} circuito(s)")
        print("Circuitos válidos; nenhuma submissão foi feita.")
        return 0
    if not (args.sim or args.real or args.all or args.report):
        ap.print_help()
        return 2
    if args.sim or args.all:
        print("== simulação ==")
        rodar_sim(args.shots, args.seed, args.only)
    if args.real or args.all:
        print("== backend ==")
        rodar_real(args.backend, args.shots, args.timeout, args.seed,
                   args.optimization_level, args.only)
    if args.report:
        relatorio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 10. Se algo der errado {#codigo-troubleshooting}

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `ModuleNotFoundError: qiskit` | ambiente não ativado | ative o `.venv` e reinstale |
| `GJQ_API_KEY ausente` | variável não definida | exporte a chave e reabra o terminal |
| `Rode --sim antes de --real` | falta o JSON simulado | rode `--sim` primeiro |
| `timeout` no backend | fila ou rede | aumente `--timeout` ou tente outro backend |
| `QFTGate` não encontrado | Qiskit antigo | `pip install --upgrade qiskit` |
| soma dos counts ≠ 1024 | backend devolveu menos tiros | registre o valor real e repita |
| resultado diferente do livro | seed, calibração e fila | compare com a incerteza, não com um número único |

## 11. O que este script não prova

- Não prova que o estado é puro, emaranhado ou fiel ao ideal.
- Não mede a fidelidade do backend; mede contagens e semelhança.
- Não substitui a calibração, a tomografia ou a replicação com outras seeds.
- Não transforma uma execução em evidência estatística: 1024 tiros têm
  incerteza, e uma execução não é uma curva.

> **Regra:** se você rodou o script e conferiu a conta à mão, o experimento é
> seu. Se apenas viu o número na tela, você ainda está no começo.
