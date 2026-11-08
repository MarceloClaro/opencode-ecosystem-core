#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o capítulo com o código completo dos 18 experimentos."""
from __future__ import annotations

import ast
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "laboratorio_leitor" / "08_experimentos_18.py"
SAIDA = RAIZ / "livro_pixel" / "CODIGO_EXPERIMENTOS.md"


MAPA = {
    "E01": ("Base |0⟩", ["qc_basis0", "leitura_p0"]),
    "E02": ("Base |1⟩ e leitura", ["qc_basis1", "leitura_p1"]),
    "E03": ("Superposição H|0⟩", ["qc_superposicao", "leitura_superposicao"]),
    "E04": ("Interferência H-Z-H", ["qc_fase", "leitura_fase"]),
    "E05": ("Estado de Bell", ["qc_bell", "leitura_bell"]),
    "E06": ("GHZ de 4 qubits", ["qc_ghz4", "leitura_ghz"]),
    "E07": ("CHSH", ["CHSH", "qc_chsh", "qcs_chsh", "leitura_chsh"]),
    "E08": ("Gerador quântico de números", ["qc_qrng", "leitura_qrng"]),
    "E09": ("Codificação de amplitude", ["qc_amplitude", "leitura_amplitude"]),
    "E10": ("Classificador XOR (VQC)", ["XOR", "THETA", "qc_vqc", "qcs_vqc", "leitura_vqc"]),
    "E11": ("Interferência de dois qubits", ["qc_interferencia2", "leitura_interferencia2"]),
    "E12": ("QFT de 3 qubits", ["qc_qft3", "leitura_qft3"]),
    "E13": ("Produto tensorial |01⟩", ["qc_tensor01", "leitura_tensor01"]),
    "E14": ("Ruído de fase", ["qc_ruido_phase", "leitura_ruido"]),
    "E15": ("GHZ via QASM 2.0", ["qc_ghz4", "leitura_ghz"]),
    "E16": ("Esfera de Bloch", ["qc_superposicao", "qc_basis0", "leitura_bloch"]),
    "E17": ("Interferência de três qubits", ["qc_walk3", "leitura_walk3"]),
    "E18": ("Amostragem binomial", ["qc_superposicao", "leitura_amostragem"]),
}


def extrair(codigo: str) -> dict[str, str]:
    blocos: dict[str, str] = {}
    arvore = ast.parse(codigo)
    for node in arvore.body:
        if isinstance(node, ast.FunctionDef):
            blocos[node.name] = ast.get_source_segment(codigo, node) or ""
    for nome in ("XOR", "THETA", "CHSH"):
        m = re.search(rf"^{nome} = .*?(?=\n\S)", codigo, re.M | re.S)
        if m:
            blocos[nome] = m.group(0).rstrip()
    return blocos


def por_experimento(codigo: str) -> str:
    blocos = extrair(codigo)
    saida = ["## 8. Código por experimento", "",
             "Cada seção abaixo é o recorte executável do experimento. O script",
             "completo, com o CLI e o relatório, está na seção 9.", "",
             "> Os recortes usam as funções auxiliares `_p` e `_soma`, definidas",
             "> no script completo (seção 9). Para executar um recorte isolado,",
             "> copie também essas duas funções.", ""]
    for exp_id, (nome, nomes) in MAPA.items():
        saida += [f"### {exp_id} — {nome} {{#codigo-{exp_id.lower()}}}", ""]
        if exp_id == "E15":
            saida += ["> A versão standalone monta o GHZ com `qc_ghz4()`; o",
                      "> script original carrega o mesmo circuito de um texto QASM 2.0.", ""]
        if exp_id == "E10":
            saida += ["> O E10 é o classificador XOR: quatro entradas, quatro",
                      "> medições e uma acurácia. O treino completo está no",
                      "> `07_vqc_ruido.py`; aqui o circuito usa os parâmetros já",
                      "> treinados.", ""]
        for nome_funcao in nomes:
            bloco = blocos.get(nome_funcao, "")
            if bloco:
                saida += ["```python", bloco, "```", ""]
        saida += ["```bash",
                  f"python 08_experimentos_18.py --sim --only {exp_id}",
                  f"python 08_experimentos_18.py --real --backend Guoji08 --only {exp_id}",
                  "```", ""]
    return "\n".join(saida)


def main() -> None:
    codigo = SCRIPT.read_text(encoding="utf-8").rstrip()
    recortes = por_experimento(codigo)
    texto = f"""# Código completo: os 18 experimentos, da instalação ao resultado {{#codigo-experimentos}}

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

## 1. O que você precisa {{#codigo-pre-requisitos}}

- Python 3.12 ou superior.
- `pip` atualizado.
- Internet para instalar os pacotes e, se quiser, para acessar o backend.
- Uma conta na Tiangong para a API key (opcional para a simulação).
- 10 minutos para a primeira execução.

## 2. Instalação {{#codigo-instalacao}}

### Linux/macOS {{#codigo-linux}}

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install qiskit qiskit-aer gjq-client numpy scipy matplotlib optuna
```

### Windows (PowerShell) {{#codigo-windows}}

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
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

No Windows, use `mkdir %USERPROFILE%\\quantica` e salve o arquivo na pasta.

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

{recortes}

## 9. Código completo {{#codigo-script-completo}}

```python
{codigo}
```

## 10. Se algo der errado {{#codigo-troubleshooting}}

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
"""
    SAIDA.write_text(texto, encoding="utf-8")
    print(f"Capítulo: {SAIDA}")


if __name__ == "__main__":
    main()
