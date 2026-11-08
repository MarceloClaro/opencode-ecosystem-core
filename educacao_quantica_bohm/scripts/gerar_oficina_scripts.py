#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a Oficina de scripts: 18 experimentos, código, linha a linha e cálculo.

Cada página mostra:
- o script e o ID do experimento;
- um trecho de código Qiskit;
- o que cada linha faz;
- a fórmula usada;
- o resultado simulado × backend;
- o que prova e o que não prova.
"""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
DADOS = RAIZ / "dados_experimentos"

OFICINA = {
    "E01": {
        "titulo": "Base |0⟩",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.measure(0, 0)""",
        "linhas": [
            ("QuantumCircuit(1, 1)", "cria 1 qubit e 1 bit clássico"),
            ("qc.measure(0, 0)", "mede o qubit 0 e grava no bit clássico 0"),
        ],
        "calculo": "P(0) = N0/N; P(1) = N1/N; P(0)+P(1)=1.",
        "prova": "mede a distribuição do estado |0⟩ e o ruído de leitura.",
        "nao_prova": "não caracteriza a leitura de |1⟩ nem a fidelidade de portas.",
    },
    "E02": {
        "titulo": "Base |1⟩ e leitura",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.x(0)
qc.measure(0, 0)""",
        "linhas": [
            ("QuantumCircuit(1, 1)", "cria 1 qubit e 1 bit clássico"),
            ("qc.x(0)", "aplica X: |0⟩ → |1⟩"),
            ("qc.measure(0, 0)", "mede o qubit e grava no bit clássico"),
        ],
        "calculo": "P(1) = N1/N. O erro de leitura é aproximadamente 1 − P(1).",
        "prova": "mede a taxa de leitura correta do estado |1⟩.",
        "nao_prova": "não é uma calibração completa: um qubit, um estado, uma execução.",
    },
    "E03": {
        "titulo": "Superposição H|0⟩",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)""",
        "linhas": [
            ("QuantumCircuit(1, 1)", "cria 1 qubit e 1 bit clássico"),
            ("qc.h(0)", "Hadamard: |0⟩ → (|0⟩+|1⟩)/√2"),
            ("qc.measure(0, 0)", "amostra 0 ou 1"),
        ],
        "calculo": "P(1)=|amplitude de |1⟩|²=0,5. Erro padrão: √(p(1−p)/N).",
        "prova": "mostra que a medição é estatística e que H cria superposição.",
        "nao_prova": "não mede a fase relativa nem prova emaranhamento.",
    },
    "E04": {
        "titulo": "Interferência H-Z-H",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0); qc.z(0); qc.h(0)
qc.measure(0, 0)""",
        "linhas": [
            ("qc.h(0)", "cria superposição"),
            ("qc.z(0)", "inverte a fase do ramo |1⟩"),
            ("qc.h(0)", "recombina os ramos: HZH = X"),
            ("qc.measure(0, 0)", "resultado deve ser 1"),
        ],
        "calculo": "HZH = X, logo P(1)=1. O ruído reduz P(1).",
        "prova": "a fase muda a interferência e o resultado final.",
        "nao_prova": "não lê a fase diretamente; só o efeito no resultado.",
    },
    "E05": {
        "titulo": "Estado de Bell",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])""",
        "linhas": [
            ("qc.h(0)", "coloca q0 em superposição"),
            ("qc.cx(0, 1)", "CNOT: |10⟩ vira |11⟩; cria correlação"),
            ("qc.measure(...)", "mede os dois qubits"),
        ],
        "calculo": "Fidelidade proxy = (N00+N11)/N. Ideal: 1,000.",
        "prova": "mede a correlação 00/11 do estado de Bell.",
        "nao_prova": "não prova emaranhamento; para isso, CHSH ou tomografia.",
    },
    "E06": {
        "titulo": "GHZ de 4 qubits",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(4, 4)
qc.h(0)
for q in (1, 2, 3):
    qc.cx(0, q)
qc.measure([0,1,2,3], [0,1,2,3])""",
        "linhas": [
            ("qc.h(0)", "coloca q0 em superposição"),
            ("qc.cx(0, q)", "espalha a correlação para q1, q2, q3"),
            ("qc.measure(...)", "mede os quatro qubits"),
        ],
        "calculo": "Fidelidade proxy = (N0000+N1111)/N. Ideal: 1,000.",
        "prova": "mede a população 0000/1111 do GHZ.",
        "nao_prova": "não prova emaranhamento genuíno multipartite.",
    },
    "E07": {
        "titulo": "CHSH",
        "codigo": """for a1, ang in [(0,-pi/4),(0,pi/4),(1,-pi/4),(1,pi/4)]:
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    if a1: qc.h(0)
    qc.ry(ang, 1)
    qc.measure([0,1], [0,1])""",
        "linhas": [
            ("qc.h(0); qc.cx(0,1)", "prepara o estado de Bell"),
            ("if a1: qc.h(0)", "escolhe a base de Alice (Z ou X)"),
            ("qc.ry(ang, 1)", "escolhe o ângulo de Bob"),
            ("qc.measure(...)", "mede as duas bases"),
        ],
        "calculo": "E=(N00+N11−N01−N10)/N; S=E00+E01+E10−E11. Clássico: |S|≤2; ideal: 2√2≈2,828.",
        "prova": "se S>2, as correlações não são explicáveis por um modelo local.",
        "nao_prova": "não é loophole-free; uma execução não é prova estatística.",
    },
    "E08": {
        "titulo": "Gerador quântico de números",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)""",
        "linhas": [
            ("qc.h(0)", "cria 0 e 1 com amplitudes iguais"),
            ("qc.measure(0, 0)", "cada execução produz um bit"),
        ],
        "calculo": "Equilíbrio = |P(0)−P(1)|. Ideal: 0.",
        "prova": "mostra que a medição de H|0⟩ é aproximadamente equilibrada.",
        "nao_prova": "não é um gerador criptográfico certificado; o backend pode ter viés.",
    },
    "E09": {
        "titulo": "Codificação de amplitude",
        "codigo": """import numpy as np
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.ry(2*np.pi/3, 0)
qc.measure(0, 0)""",
        "linhas": [
            ("qc.ry(θ, 0)", "rotação de amplitude: |0⟩ → cos(θ/2)|0⟩ + sen(θ/2)|1⟩"),
            ("qc.measure(0, 0)", "amostra 0 ou 1"),
        ],
        "calculo": "P(1)=sen²(θ/2). Para θ=2π/3, P(1)=0,75.",
        "prova": "mostra como um ângulo codifica uma probabilidade.",
        "nao_prova": "não prepara um estado arbitrário de vários qubits.",
    },
    "E10": {
        "titulo": "Classificador XOR (VQC)",
        "codigo": """XOR = [(0,0),(0,1),(1,0),(1,1)]
for x in XOR:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi*x[0], 0); qc.ry(np.pi*x[1], 1)
    qc.ry(theta[0], 0); qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 0); qc.ry(theta[3], 1)
    qc.measure(0, 0)""",
        "linhas": [
            ("qc.ry(pi*x[q], q)", "codifica as duas features nos qubits"),
            ("qc.ry(theta[...], q)", "aplica os parâmetros treinados"),
            ("qc.cx(0,1)", "cria a interação entre os qubits"),
            ("qc.measure(0,0)", "lê a classe prevista"),
        ],
        "calculo": "pred=1[P(1)≥0,5]; acurácia=(1/4)Σ 1[pred=y].",
        "prova": "mostra o pipeline de codificação, treino e avaliação.",
        "nao_prova": "4/4 não é generalização; o teste é pequeno e o teto é 100%.",
    },
    "E11": {
        "titulo": "Interferência de dois qubits",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0); qc.h(1)
qc.cz(0, 1)
qc.h(0)
qc.measure([0,1], [0,1])""",
        "linhas": [
            ("qc.h(0); qc.h(1)", "cria superposição nos dois qubits"),
            ("qc.cz(0,1)", "adiciona fase controlada"),
            ("qc.h(0)", "recombina o qubit 0"),
            ("qc.measure(...)", "mede a distribuição final"),
        ],
        "calculo": "P(00)=N00/N. Ideal: 0,500.",
        "prova": "mostra interferência de dois qubits.",
        "nao_prova": "não prova emaranhamento nem vantagem computacional.",
    },
    "E12": {
        "titulo": "QFT de 3 qubits",
        "codigo": """from qiskit.circuit.library import QFTGate
qc = QuantumCircuit(3, 3)
qc.x(2)
qc.append(QFTGate(3), range(3))
qc.measure([0,1,2], [0,1,2])""",
        "linhas": [
            ("qc.x(2)", "prepara |100⟩"),
            ("QFTGate(3)", "aplica a transformada de Fourier quântica"),
            ("qc.measure(...)", "mede a distribuição uniforme"),
        ],
        "calculo": "P(000)=N000/N. Ideal: 1/8=0,125.",
        "prova": "mostra a QFT como mudança de base.",
        "nao_prova": "não prova speedup; a QFT é parte de algoritmos maiores.",
    },
    "E13": {
        "titulo": "Produto tensorial |01⟩",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.x(0)
qc.measure([0,1], [0,1])""",
        "linhas": [
            ("qc.x(0)", "prepara q0=1 e q1=0"),
            ("qc.measure(...)", "mede os dois qubits"),
        ],
        "calculo": "P(01)=N01/N. Ideal: 1,000.",
        "prova": "mostra que operações locais não criam correlação.",
        "nao_prova": "não prova emaranhamento; o estado é produto.",
    },
    "E14": {
        "titulo": "Ruído de fase",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0); qc.x(0); qc.h(0)
qc.measure(0, 0)""",
        "linhas": [
            ("qc.h(0); qc.x(0); qc.h(0)", "HXH = Z; o estado deveria voltar a |0⟩"),
            ("qc.measure(0,0)", "mede a população que sobrou"),
        ],
        "calculo": "P(0)=N0/N. Ideal: 1,000; o ruído reduz.",
        "prova": "mostra perda de coerência em uma sequência curta.",
        "nao_prova": "não separa T1, T2, leitura e erro de porta.",
    },
    "E15": {
        "titulo": "GHZ via QASM 2.0",
        "codigo": """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4]; creg c[4];
h q[0];
cx q[0],q[1]; cx q[0],q[2]; cx q[0],q[3];
measure q[0]->c[0]; measure q[1]->c[1];
measure q[2]->c[2]; measure q[3]->c[3];""",
        "linhas": [
            ("qreg/creg", "declara 4 qubits e 4 bits clássicos"),
            ("h q[0]", "cria superposição"),
            ("cx q[0],q[k]", "espalha a correlação"),
            ("measure ...", "mede os quatro qubits"),
        ],
        "calculo": "Mesmo cálculo do E06: (N0000+N1111)/N.",
        "prova": "mostra que o mesmo circuito pode ser escrito em QASM 2.0.",
        "nao_prova": "não garante que o editor/backend executou sem erro.",
    },
    "E16": {
        "titulo": "Esfera de Bloch",
        "codigo": """# base Z
qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0,0)
# base X
qc = QuantumCircuit(1, 1); qc.h(0); qc.h(0); qc.measure(0,0)""",
        "linhas": [
            ("qc.h(0)", "prepara (|0⟩+|1⟩)/√2"),
            ("qc.h(0); qc.h(0)", "H²=I: mede na base X"),
            ("qc.measure(0,0)", "amostra Z ou X"),
        ],
        "calculo": "⟨Z⟩=P0−P1; ⟨X⟩=P0−P1 na base X.",
        "prova": "estima dois componentes do vetor de Bloch.",
        "nao_prova": "não é tomografia completa; falta ⟨Y⟩.",
    },
    "E17": {
        "titulo": "Interferência de três qubits",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(3, 3)
for q in range(3): qc.h(q)
qc.cz(0,1); qc.cz(1,2)
for q in range(3): qc.h(q)
qc.measure([0,1,2], [0,1,2])""",
        "linhas": [
            ("qc.h(q)", "cria superposição nos três qubits"),
            ("qc.cz(0,1); qc.cz(1,2)", "adiciona fases controladas"),
            ("qc.h(q)", "recombina"),
            ("qc.measure(...)", "mede a distribuição"),
        ],
        "calculo": "P(000)=N000/N. Ideal: 0,250.",
        "prova": "mostra interferência de três qubits.",
        "nao_prova": "não é uma caminhada quântica completa.",
    },
    "E18": {
        "titulo": "Amostragem binomial",
        "codigo": """from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)""",
        "linhas": [
            ("qc.h(0)", "cria p=0,5"),
            ("qc.measure(0,0)", "cada tiro é Bernoulli(p)"),
        ],
        "calculo": "P(1)=N1/N; erro padrão=√(p(1−p)/N).",
        "prova": "mostra que a estimativa melhora com N.",
        "nao_prova": "não prova independência entre tiros.",
    },
}


def carregar(exp_id: str) -> dict:
    p = DADOS / f"{exp_id}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def top_counts(counts, k=3):
    if not counts:
        return "—"
    itens = sorted(counts.items(), key=lambda kv: -kv[1])[:k]
    return ", ".join(f"{chave}={valor}" for chave, valor in itens)


def resumo_saida(counts, leitura):
    if isinstance(counts, list):
        if len(counts) == 1:
            return f"{top_counts(counts[0])} → {leitura}"
        return f"{len(counts)} circuitos → {leitura}"
    return f"{top_counts(counts)} → {leitura}"


def pagina(exp_id: str, d: dict) -> str:
    dados = carregar(exp_id)
    sim = (dados.get("simulado") or {}).get("leitura", "—").replace(".", ",")
    real = (dados.get("real") or {}).get("leitura", "—").replace(".", ",")
    sim_counts = (dados.get("simulado") or {}).get("counts")
    real_counts = (dados.get("real") or {}).get("counts")
    saida_sim = resumo_saida(sim_counts, sim)
    saida_real = resumo_saida(real_counts, real)
    ov = dados.get("sobreposicao")
    ov_txt = f"{ov*100:.1f}%".replace(".", ",") if isinstance(ov, (int, float)) else "—"
    task = ((dados.get("real") or {}).get("task_ids") or ["—"])[0]
    def celula(x):
        return str(x).replace("|", "&#124;")

    linhas = "\n".join(
        f"| `{celula(codigo)}` | {celula(explicacao)} |"
        for codigo, explicacao in d["linhas"]
    )
    return f"""## {exp_id} — {d['titulo']}

**Script:** `scripts/experimentos_100.py` · `{exp_id}` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
{d['codigo']}
```

| Linha | O que faz |
|---|---|
{linhas}

**Cálculo matemático:** {d['calculo']}

**Saída simulada:** {saida_sim}
**Saída no backend:** {saida_real}; sobreposição: {ov_txt}; task: `{task}`.

**O que prova:** {d['prova']}

**O que não prova:** {d['nao_prova']}

"""


def main() -> None:
    linhas = [
        "# Oficina de scripts: 18 experimentos, linha a linha {#oficina}",
        "",
        "Esta oficina mostra, para cada experimento, **o código que foi rodado**, o",
        "que cada linha faz, o cálculo matemático e o resultado simulado × backend.",
        "Os scripts completos estão em `educacao_quantica_bohm/scripts/experimentos_100.py`.",
        "",
    ]
    for exp_id, d in OFICINA.items():
        linhas.append(pagina(exp_id, d))
    (LIVRO / "OFICINA_SCRIPTS.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"Oficina: {LIVRO / 'OFICINA_SCRIPTS.md'}")


if __name__ == "__main__":
    main()