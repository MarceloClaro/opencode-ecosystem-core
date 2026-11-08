#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o manual do leitor com instalação, API, código, CSV, circuitos e saídas."""
from __future__ import annotations

import json
from pathlib import Path

from qiskit import QuantumCircuit

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
LAB = RAIZ / "laboratorio_leitor"
DADOS = RAIZ / "dados_hardware"
QUALIS = RAIZ / "dados_qualis"


def codigo(nome: str) -> str:
    p = LAB / nome
    return p.read_text(encoding="utf-8").rstrip()


def circ_texto(qc: QuantumCircuit) -> str:
    return str(qc.draw("text"))


def bell():
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1); qc.measure([0, 1], [0, 1])
    return qc


def ghz():
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    for q in (1, 2, 3):
        qc.cx(0, q)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def chsh():
    import numpy as np
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1); qc.ry(-np.pi / 4, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def swap():
    qc = QuantumCircuit(3, 1)
    qc.ry(1.0, 2); qc.h(0); qc.cswap(0, 1, 2); qc.h(0)
    qc.measure(0, 0)
    return qc


def vqc():
    import numpy as np
    theta = [1.5708, 1.5708, -1.5708, 2.819]
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * 0, 0); qc.ry(np.pi * 0, 1)
    qc.ry(theta[0], 0); qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 0); qc.ry(theta[3], 1)
    qc.measure(0, 0)
    return qc


def json_dados(nome: str, pasta: Path = DADOS) -> dict:
    p = pasta / nome
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main() -> None:
    bell_hw = json_dados("hardware_check_2026.json")
    ghz_g = json_dados("ghz4_guoji08.json")
    ghz_b = json_dados("ghz4_baihua.json")
    chsh_d = json_dados("chsh_guoji08.json")
    vqc_d = json_dados("vqc_xor_guoji08.json")
    bloch = json_dados("bloch_suite_guoji08.json")
    swap_d = json_dados("swap_test_guoji08.json")

    linhas = [
        "# Manual do leitor: instalar, criar API e rodar {#laboratorio-leitor}",
        "",
        "Este manual é autossuficiente: o código, os comandos, as tabelas CSV e as",
        "saídas esperadas estão **no livro**. Você não precisa acessar o repositório",
        "para começar. Copie os blocos, execute na ordem e compare com as tabelas.",
        "",
        "## 1. O que você precisa",
        "",
        "- Python 3.12 ou superior.",
        "- Internet para instalar pacotes e, se quiser, acessar o hardware.",
        "- Uma conta gratuita na Tiangong para a API key (opcional para o simulador).",
        "- 30 minutos para a primeira execução.",
        "",
        "## 2. Instalação",
        "",
        "### Linux/macOS",
        "",
        "```bash",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install --upgrade pip",
        "pip install qiskit qiskit-aer gjq-client numpy scipy matplotlib optuna",
        "```",
        "",
        "### Windows (PowerShell)",
        "",
        "```powershell",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\Activate.ps1",
        "python -m pip install --upgrade pip",
        "pip install qiskit qiskit-aer gjq-client numpy scipy matplotlib optuna",
        "```",
        "",
        "## 3. Criar a API key",
        "",
        "1. Abra <https://tiangongqs.com/cloud/circuit>.",
        "2. Entre ou crie uma conta.",
        "3. Gere uma **API key** no perfil/conta.",
        "4. No terminal, defina a variável de ambiente:",
        "",
        "```bash",
        "export GJQ_API_KEY=\"sua-chave\"        # Linux/macOS",
        "# PowerShell: $env:GJQ_API_KEY = \"sua-chave\"",
        "```",
        "",
        "O `gjq-client` grava o cache em:",
        "",
        "- Linux/macOS: `~/.gjq_client/gjq_client_account.json`",
        "- Windows: `%USERPROFILE%\\.gjq_client\\gjq_client_account.json`",
        "",
        "Proteja o cache:",
        "",
        "```bash",
        "chmod 600 ~/.gjq_client/gjq_client_account.json",
        "```",
        "",
        "> **Nunca** grave a chave no código, no caderno ou no repositório. Se ela",
        "> vazar, revogue, apague o cache e audite `list_tasks()`.",
        "",
        "## 4. Circuitos que você vai montar",
        "",
        "### Circuito de Bell",
        "",
        "```text",
        circ_texto(bell()),
        "```",
        "",
        "### Circuito GHZ de 4 qubits",
        "",
        "```text",
        circ_texto(ghz()),
        "```",
        "",
        "### Circuito CHSH — configuração E00",
        "",
        "```text",
        circ_texto(chsh()),
        "```",
        "",
        "### Circuito SWAP test",
        "",
        "```text",
        circ_texto(swap()),
        "```",
        "",
        "### Circuito VQC XOR — entrada 00",
        "",
        "```text",
        circ_texto(vqc()),
        "```",
        "",
        "## 5. Notebook do leitor",
        "",
        "### Célula 1 — Bell no simulador",
        "",
        "```python",
        codigo("01_bell_simulador.py"),
        "```",
        "",
        "**Saída esperada:** counts próximos de `{'00': 512, '11': 512}` e",
        "`P(00)+P(11) ≈ 1,000`.",
        "",
        "### Célula 2 — Bell no hardware",
        "",
        "```python",
        codigo("02_bell_hardware.py"),
        "```",
        "",
        "**Saída real desta edição:**",
        "",
        "| Backend | `00` | `11` | `01` | `10` | fidelidade | task ID |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for nome, d in bell_hw.get("resultados", {}).items():
        c = d.get("counts", {})
        tot = sum(c.values()) if c else 0
        fid = (c.get("00", 0) + c.get("11", 0)) / tot if tot else 0
        linhas.append(f"| {nome} | {c.get('00',0)} | {c.get('11',0)} | {c.get('01',0)} | {c.get('10',0)} | {fid*100:.1f}% | `{str(d.get('task_id',''))[:8]}…` |".replace(".", ","))
    linhas += [
        "",
        "### Célula 3 — GHZ no hardware",
        "",
        "```python",
        codigo("03_ghz_hardware.py"),
        "```",
        "",
        "**Saída real desta edição:**",
        "",
        "| Backend | `0000` | `1111` | outros | fidelidade |",
        "|---|---:|---:|---:|---:|",
    ]
    for nome, d in (("Guoji08", ghz_g), ("Baihua", ghz_b)):
        c = d.get("counts", {})
        tot = sum(c.values()) if c else 0
        ideal = c.get("0000", 0) + c.get("1111", 0)
        linhas.append(f"| {nome} | {c.get('0000',0)} | {c.get('1111',0)} | {tot-ideal} | {ideal/tot*100:.1f}% |".replace(".", ","))
    linhas += [
        "",
        "### Célula 4 — CHSH",
        "",
        "```python",
        codigo("04_chsh_hardware.py"),
        "```",
        "",
        "**Saída real desta edição:**",
        "",
        "| Configuração | E |",
        "|---|---:|",
    ]
    for k, v in chsh_d.get("E", {}).items():
        linhas.append(f"| {k} | {v:+.4f} |".replace(".", ","))
    linhas += [
        "",
        f"**S = {chsh_d.get('S', 0):.4f}** (clássico ≤ 2; ideal 2,828).".replace(".", ","),
        "",
        "### Célula 5 — Esfera de Bloch",
        "",
        "```python",
        codigo("05_bloch_suite.py"),
        "```",
        "",
        "**Componentes medidos:**",
        "",
        "| Estado | x sim | y sim | z sim | x HW | y HW | z HW | norma HW |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for codigo_e, s in bloch.get("simulado", {}).items():
        v = s["componentes"]
        h = bloch.get("hardware", {}).get(codigo_e, {})
        w = h.get("componentes", {})
        n = h.get("comprimento", 0)
        linhas.append(
            f"| {codigo_e} | {v['x']:+.3f} | {v['y']:+.3f} | {v['z']:+.3f} | "
            f"{w.get('x',0):+.3f} | {w.get('y',0):+.3f} | {w.get('z',0):+.3f} | {n:.3f} |".replace(".", ",")
        )
    linhas += [
        "",
        "### Célula 6 — SWAP test",
        "",
        "```python",
        codigo("06_swap_test.py"),
        "```",
        "",
        "**Saída real desta edição:**",
        "",
        "| Condição | P(0) | sobreposição |",
        "|---|---:|---:|",
        f"| ideal | 0,8851 | 0,7702 |",
        f"| simulado | {swap_d.get('p0_sim',0):.4f} | {swap_d.get('overlap_sim',0):.4f} |",
        f"| backend | {swap_d.get('real',{}).get('p0',0):.4f} | {swap_d.get('real',{}).get('overlap',0):.4f} |",
        "",
        "### Célula 7 — VQC com ruído",
        "",
        "```python",
        codigo("07_vqc_ruido.py"),
        "```",
        "",
        "**Saída esperada:** acurácia de teste por configuração; o baseline desta",
        "edição ficou em 97,0% (2 qubits) e 95,0% (4 qubits); phase damping é",
        "idêntico ao baseline; depolarizing/amplitude não melhoram.",
        "",
        "## 6. Galeria de resultados",
        "",
        "As figuras abaixo foram produzidas pelos scripts desta edição. Elas não",
        "são ilustrações de catálogo: cada uma tem código, dados e uma legenda que",
        "diz o que mostra e o que não mostra.",
        "",
        "![**Figura L1.** Circuito de Bell desenhado pelo Qiskit. O mesmo circuito aparece em PennyLane e Cirq na seção de ferramentas.](../livro/figuras_geradas/fig07_qiskit.png){#fig-l1}",
        "",
        "![**Figura L2.** GHZ de 4 qubits no Guoji08: populações ideais e observadas. A fidelidade proxy é 78,8%; os erros não são uniformes.](../livro/figuras_geradas/fig12_ghz4_resultados.png){#fig-l2}",
        "",
        "![**Figura L3.** VQC XOR: ideal, phase damping, depolarização e hardware. O hardware separa os quatro pontos; a depolarização reduz a margem; phase damping não muda a população Z.](../livro/figuras_geradas/fig13_vqc_xor.png){#fig-l3}",
        "",
        "![**Figura L4.** CHSH no Guoji08: S ≈ 2,38, acima do limite clássico 2 e abaixo do ideal 2√2 ≈ 2,828. Uma execução não é prova estatística.](../livro/figuras_geradas/fig15_chsh.png){#fig-l4}",
        "",
        "![**Figura L5.** Calibração do backend: T1, T2 e erro de leitura. Números de uma fotografia; a calibração muda com o tempo.](../livro/figuras_geradas/fig23_calibracao.png){#fig-l5}",
        "",
        "![**Figura L6.** SWAP test: P(0) ideal, simulado e de hardware. A sobreposição cai de 0,770 para 0,629 no backend.](../livro/figuras_geradas/fig24_swap_test.png){#fig-l6}",
        "",
        "![**Figura L7.** Seis estados na esfera de Bloch, ideal e hardware. O ruído encolhe o vetor; S5 chega a |r| = 1,03, acima do limite físico, por viés de leitura.](../livro/figuras_geradas/fig25_bloch_suite.png){#fig-l7}",
        "",
        "![**Figura L8.** As mesmas seis esferas em projeção XZ/YZ. O traço forte é o ideal; o tracejado, o hardware. S4 e S6 usam o plano YZ.](../livro/figuras_geradas/fig27_bloch_paineis.png){#fig-l8}",
        "",
        "![**Figura L9.** Circuito do GHZ de 4 qubits. A ordem de leitura é da esquerda para a direita; a medição aparece no fim.](../livro/figuras_geradas/fig29_circuito_ghz.png){#fig-l9}",
        "",
        "![**Figura L10.** Circuito do CHSH na configuração E00. A rotação Ry(−π/4) define a base de medida de um dos qubits.](../livro/figuras_geradas/fig30_circuito_chsh.png){#fig-l10}",
        "",
        "![**Figura L11.** Circuito do SWAP test. O qubit de controle é preparado em H; a medida do controle revela a sobreposição.](../livro/figuras_geradas/fig31_circuito_swap.png){#fig-l11}",
        "",
        "![**Figura L12.** Circuito mínimo do VQC XOR. O treino descrito na Célula 7 usa três camadas; o desenho mostra uma camada para caber na página.](../livro/figuras_geradas/fig32_circuito_vqc.png){#fig-l12}",
        "",
        "## 7. Como ler os counts no console",
        "",
        "1. Abra **Task Management**.",
        "2. Clique na tarefa.",
        "3. Veja o gráfico de distribuição.",
        "4. Baixe **CSV/TXT** no menu da figura.",
        "5. No CSV, a coluna do bitstring e a coluna do count são o que você precisa.",
        "6. Copie para a planilha e aplique as fórmulas do capítulo **Cálculo manual**.",
        "",
        "## 8. Se algo der errado",
        "",
        "| Sintoma | Causa provável | O que fazer |",
        "|---|---|---|",
        "| `GJQ_API_KEY` ausente | variável não definida | exporte a chave e reabra o terminal |",
        "| SSL/EOF | rede ou proxy | tente outra rede; o simulador local continua |",
        "| fila longa | backend ocupado | use `Baihua` ou um simulador |",
        "| `cswap` não definido | parser Qiskit 2.x | monte com `qc.cswap` em vez de `qasm2.loads` |",
        "| resultado diferente | calibração/leitura | repita e compare com o intervalo de confiança |",
        "| cache com chave | primeira execução | `chmod 600` e não faça commit |",
        "",
        "## 9. Código completo",
        "",
        "Os blocos acima são os arquivos completos. Se quiser separá-los, crie",
        "`01_bell_simulador.py` a `07_vqc_ruido.py` na mesma pasta e execute:",
        "",
        "```bash",
        "python 01_bell_simulador.py",
        "python 02_bell_hardware.py",
        "python 03_ghz_hardware.py",
        "python 04_chsh_hardware.py",
        "python 05_bloch_suite.py --only all",
        "python 06_swap_test.py",
        "python 07_vqc_ruido.py --qubits 2 4 --seeds 0 1 2 3 4",
        "```",
        "",
        "> **Regra:** o livro contém o código, os dados e a conta. Se você chegar ao",
        "> mesmo número com lápis e papel, o experimento é seu.",
        "",
    ]
    (LIVRO / "LABORATORIO_LEITOR.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"Manual: {LIVRO / 'LABORATORIO_LEITOR.md'}")


if __name__ == "__main__":
    main()
