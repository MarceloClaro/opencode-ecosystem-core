#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a página BLOCH_SUITE.md a partir de bloch_suite_guoji08.json."""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados_hardware" / "bloch_suite_guoji08.json"
LIVRO = RAIZ / "livro_pixel"


def num(v):
    return f"{v:+.3f}".replace(".", ",")


def main():
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    sim = d["simulado"]
    hw = d.get("hardware", {})
    linhas = [
        "# Esfera de Bloch: seis circuitos, simulação e hardware {#bloch-suite}",
        "",
        "<p class=\"parte-zh\">布洛赫球 · bù luò hè qiú</p>",
        "",
        "A esfera de Bloch é o mapa de um qubit. Aqui o **mesmo qubit** é preparado",
        "de seis formas diferentes e medido em três bases (Z, X e Y). O objetivo é",
        "mostrar, lado a lado, o vetor **simulado** e o vetor **de hardware**.",
        "",
        "## Os seis circuitos",
        "",
        "| Estado | Preparação | Vetor esperado |",
        "|---|---|---|",
        "| S1 | nada | +Z |",
        "| S2 | X | −Z |",
        "| S3 | H | +X |",
        "| S4 | H, S | +Y |",
        "| S5 | Ry(π/3) | 0,866 X + 0,5 Z |",
        "| S6 | H, RZ(π/2), H | −Y |",
        "",
        "## A matemática",
        "",
        "Cada componente vem de uma probabilidade medida na base correspondente:",
        "",
        "<div class=\"formula\">x = 2P(0)<sub>X</sub> − 1 &nbsp;&nbsp; y = 2P(0)<sub>Y</sub> − 1 &nbsp;&nbsp; z = 2P(0)<sub>Z</sub> − 1</div>",
        "",
        "O comprimento e os ângulos são:",
        "",
        "<div class=\"formula\">|r| = √(x² + y² + z²) &nbsp;&nbsp; θ = arccos(z) &nbsp;&nbsp; φ = atan2(y, x)</div>",
        "",
        "Para um estado puro, |r| = 1. O hardware encolhe o vetor porque mistura",
        "o estado com ruído; o simulador ideal mantém |r| = 1.",
        "",
        "```python",
        "qc = QuantumCircuit(1, 1)",
        "preparar_estado(qc)",
        "if base == \"X\": qc.h(0)",
        "elif base == \"Y\": qc.sdg(0); qc.h(0)",
        "qc.measure(0, 0)",
        "```",
        "",
        "## Resultados: simulado × hardware",
        "",
        "| Estado | x sim | y sim | z sim | x HW | y HW | z HW | norma HW |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for codigo in sim:
        s = sim[codigo]["componentes"]
        h = hw.get(codigo, {}).get("componentes", {})
        comp = hw.get(codigo, {}).get("comprimento", float("nan"))
        linhas.append(
            f"| {codigo} | {num(s['x'])} | {num(s['y'])} | {num(s['z'])} | "
            f"{num(h.get('x', float('nan')))} | {num(h.get('y', float('nan')))} | "
            f"{num(h.get('z', float('nan')))} | {comp:.3f}".replace(".", ",") + " |"
        )
    linhas += [
        "",
        "![**Figura B1.** Esfera de Bloch com os seis vetores ideais (fortes) e os",
        "vetores de hardware (tracejados). À direita, o comprimento |r|: o ruído",
        "encolhe o vetor.](../livro/figuras_geradas/fig25_bloch_suite.png){#fig-b1}",
        "",
        "**Leitura:** o hardware preserva a direção aproximada de cada estado, mas",
        "encurta o vetor. O erro é maior em S4/S6 (base Y), onde a rotação S† e a",
        "leitura acumulam erro. O simulador é o limite ideal; o hardware é o",
        "resultado físico.",
        "",
        "> **Achado:** S5 deu norma 1,03 > 1. Um vetor de Bloch físico não pode",
        "> passar de 1; o excesso é viés de leitura e estimativa linear com 1024",
        "> tiros. A correção exige calibração de leitura ou máxima verossimilhança",
        "> com restrição. É por isso que a esfera é uma ferramenta, não um",
        "> certificado.",
        "",
        "## Do Bloch à pesquisa PhD",
        "",
        "- **1 qubit:** três bases bastam para reconstruir o vetor (tomografia de",
        "  estado). O Bloch é uma visualização, não uma prova.",
        "- **2+ qubits:** a esfera não basta; use matriz densidade, tomografia e",
        "  entropia. O espaço cresce como 4ⁿ − 1 parâmetros.",
        "- **Ruído:** o comprimento |r| < 1 é um sinal de mistura. Para separar",
        "  erro de porta, leitura e preparação, é preciso calibração e modelos.",
        "- **Pesquisa:** tomografia com máxima verossimilhança, regiões de",
        "  confiança, mitigação de leitura, múltiplas seeds e comparação com",
        "  simulador ruidoso.",
        "",
        "> **O que prova:** o mesmo qubit, preparado de seis formas, foi medido em",
        "> três bases e comparado entre simulação e hardware.",
        "> **O que não prova:** que o estado é puro, que o hardware é fiel em outros",
        "> circuitos ou que a tomografia está completa. Um vetor curto é uma",
        "> fotografia com ruído, não um certificado.",
        "",
        "Dados: `dados_hardware/bloch_suite_guoji08.json`.",
        "",
    ]
    (LIVRO / "BLOCH_SUITE.md").write_text("\n".join(linhas), encoding="utf-8")
    print("BLOCH_SUITE.md gerado")


if __name__ == "__main__":
    main()
