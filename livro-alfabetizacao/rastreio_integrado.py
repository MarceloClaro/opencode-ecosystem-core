#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rastreio_integrado.py — SPEC-935-R211
Caderno de Atividades + Rastreio Integrado Sequenciado.

Gera checkpoints (rastreio-u*.tex) para os volumes da coleção Alfabetizar Bem
e injeta os \\input nos pontos entre unidades (idempotente).

Uso:
    python3 rastreio_integrado.py            # gera + injeta Volume 1
    python3 rastreio_integrado.py --dry-run  # mostra o que faria
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VOLUME1 = RAIZ / "Volume1"
SEQUENCIA = VOLUME1 / "parte2-sequencia-didatica.tex"
CHECKPOINT_DIR = VOLUME1 / "checkpoints"


@dataclass(frozen=True)
class Checkpoint:
    """Uma entrada do mapeamento rastreio↔unidade."""

    arquivo: str          # ex.: "rastreio-u1"
    rotulo: str           # título da caixa
    quando: str           # instrução de aplicação
    dominio: str          # domínio da Parte A (sondagem)
    fichas: str           # fichas do Volume Profissional
    itens_auto: list[str] = field(default_factory=list)      # 4 itens (sem vírgulas)
    indicadores: list[str] = field(default_factory=list)     # 5 indicadores (sem vírgulas)
    encaminhamento: str = ""

    def to_latex(self) -> str:
        itens = "\n".join(
            f"  \\item {it} (\\textbf{{SIM}}) (\\textbf{{NÃO}})"
            for it in self.itens_auto
        )
        linhas = "\n".join(
            f"  {ob} & & & & \\\\"
            for ob in self.indicadores
        )
        return (
            "%% Gerado por rastreio_integrado.py (SPEC-935-R211). Nao editar.\n"
            f"\\begin{{rastreio}}[{self.rotulo}]\n"
            f"\\textbf{{Quando aplicar:}} {self.quando}\\par\\smallskip\n"
            f"\\textbf{{Domínio da sondagem:}} {self.dominio}\\quad\n"
            f"\\textbf{{Ficha(s) do Volume Profissional:}} {self.fichas}\\par\\medskip\n\n"
            "\\noindent\\textbf{\\faUserGraduate~Passo 1 --- Eu consigo "
            "(autoavaliação do aluno)}\n"
            "\\begin{itemize}[leftmargin=1.6em, itemsep=2pt]\n"
            f"{itens}\n"
            "\\end{itemize}\n\n"
            "\\noindent\\textbf{\\faUserTie~Passo 2 --- Observação do professor "
            "(S = sim, F = frequentemente, R = raramente, N = não)}\n"
            "\\begin{center}\n"
            "\\renewcommand{\\arraystretch}{1.4}\n"
            "\\begin{tabular}{@{}p{9.4cm}cccc@{}}\n"
            "\\toprule\n"
            "Indicador observável & S & F & R & N \\\\\n"
            "\\midrule\n"
            f"{linhas}\n"
            "\\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{center}\n\n"
            "\\noindent\\textbf{\\faArrowCircleRight~Passo 3 --- Regra de "
            "encaminhamento}\n"
            f"{self.encaminhamento}\\par\\smallskip\n"
            "\\textit{\\faExclamationTriangle~Este rastreio não diagnostica; é "
            "observação pedagógica sequenciada. Sinais persistentes devem ser "
            "discutidos com a família e avaliados pelo profissional habilitado "
            "(Volume Profissional de Sondagem e Rastreio).}\n"
            "\\end{rastreio}\n"
        )


# ---------------------------------------------------------------------------
# Mapeamento Volume 1 (piloto). Volumes 2–5 usarão o mesmo gerador.
# ---------------------------------------------------------------------------
CHECKPOINTS_V1: list[Checkpoint] = [
    Checkpoint(
        arquivo="rastreio-u1",
        rotulo="Rastreio Integrado 1 --- após a Unidade 1 (Vogais)",
        quando="aplicar ao fim da Unidade 1, antes de iniciar as consoantes do Bloco 1. Tempo: 10--15 minutos.",
        dominio="Consciência Fonológica e Linguagem Oral",
        fichas="Ficha 19 (Desvio Fonológico) e Ficha 18 (TDL)",
        itens_auto=[
            "Digo o nome das vogais A E I O U",
            "Reconheço a vogal inicial de palavras",
            "Separo vogal de consoante no ditado oral",
            "Escrevo as cinco vogais na ordem",
        ],
        indicadores=[
            "Nomeia as vogais sem apoio do cartaz",
            "Identifica vogal inicial em 4 de 5 palavras",
            "Repete sequência oral de 4 vogais sem erro",
            "Segura o lápis com preensão funcional",
            "Mantém atenção na folha por 5 minutos",
        ],
        encaminhamento="Se 2 ou mais respostas NÃO no Passo 1 OU 2+ marcações R/N no Passo 2, "
        "registrar no Registro de Progresso e comunicar à família; o profissional habilitado "
        "avalia com as Fichas 19 e 18 do Volume Profissional.",
    ),
    Checkpoint(
        arquivo="rastreio-u2",
        rotulo="Rastreio Integrado 2 --- após a Unidade 2 (Consonantes do Bloco 1)",
        quando="aplicar ao fim da Unidade 2, antes das sílabas diretas. Tempo: 10--15 minutos.",
        dominio="Leitura e Escrita/Ortografia",
        fichas="Ficha 1 (Dislexia) e Ficha 3 (Disgrafia)",
        itens_auto=[
            "Leio as sílabas MA SA TA RA",
            "Escrevo as sílabas do Bloco 1",
            "Formo palavras de duas sílabas",
            "Leio MAMÃE e SOMA sem soletrar letra a letra",
        ],
        indicadores=[
            "Lê sílabas diretas do Bloco 1 sem apoio",
            "Transcreve sílabas sem espelhar letras",
            "Inverte ou omite letras ao escrever",
            "Faz traçado legível e homogêneo na plancheta",
            "Conclui a folha dentro do tempo previsto",
        ],
        encaminhamento="Se 2+ sinais (NÃO / R ou N), registrar e encaminhar ao profissional habilitado "
        "para as Fichas 1 (leitura) e 3 (traçado) do Volume Profissional.",
    ),
    Checkpoint(
        arquivo="rastreio-u3",
        rotulo="Rastreio Integrado 3 --- após a Unidade 3 (Sílabas Diretas)",
        quando="aplicar ao fim da Unidade 3, antes das primeiras frases. Tempo: 10--15 minutos.",
        dominio="Leitura e Consciência Fonológica",
        fichas="Ficha 1 (Dislexia)",
        itens_auto=[
            "Leio 10 sílabas diretas por minuto",
            "Combino vogal e consoante para ler",
            "Leio palavras dissílabas sem apoio",
            "Percebo o som inicial das palavras",
        ],
        indicadores=[
            "Lê sílabas e palavras sem adivinhar pelo desenho",
            "Troca sonoridades semelhantes (P/B, F/V)",
            "Segmenta palavras em sílabas faladas",
            "Lê com ritmo sem pausa excessiva por sílaba",
            "Persiste diante de palavra desconhecida",
        ],
        encaminhamento="Se 2+ sinais persistentes, registrar e usar a Ficha 1 (Dislexia) do Volume "
        "Profissional com o profissional habilitado; manter a Rota 1A--1D enquanto isso.",
    ),
    Checkpoint(
        arquivo="rastreio-u4",
        rotulo="Rastreio Integrado 4 --- após a Unidade 5 (Consonantes do Bloco 2)",
        quando="aplicar ao fim da Unidade 5, antes das sílabas nasais. Tempo: 10--15 minutos.",
        dominio="Escrita/Ortografia e Consciência Fonológica",
        fichas="Ficha 2 (Disortografia) e Ficha 1 (Dislexia)",
        itens_auto=[
            "Leio sílabas com as letras do Bloco 2",
            "Escrevo palavras novas sem copiar",
            "Troco letras que têm o mesmo som",
            "Respeito espaços entre as palavras",
        ],
        indicadores=[
            "Escreve com correspondência grafema-fonema estável",
            "Confunde letras de traçado similar (b/d, p/q)",
            "Ortografia com omissões ou inversões frequentes",
            "Leitura decodificada sem sentido global",
            "Frequência de erros varia com fadiga e atenção",
        ],
        encaminhamento="Se 2+ sinais, registrar e encaminhar ao profissional habilitado; Ficha 2 "
        "(Disortografia) e Ficha 1 do Volume Profissional.",
    ),
    Checkpoint(
        arquivo="rastreio-u5",
        rotulo="Rastreio Integrado 5 --- após a Unidade 7 (Ditongos Nasais)",
        quando="aplicar ao fim da Unidade 7, antes das letras X, Q, H. Tempo: 10--15 minutos.",
        dominio="Processamento Auditivo e Consciência Fonológica",
        fichas="Ficha 17 (TPAC) e Ficha 6 (TDAH H/I)",
        itens_auto=[
            "Ouço a diferença entre ÃO e ÃE",
            "Percebo quando o som sai pelo nariz",
            "Repito palavras com ditongo nasal",
            "Acompanho instruções de dois passos",
        ],
        indicadores=[
            "Confunde sons nasais em ditado oral",
            "Pede repetição frequente do comando",
            "Responde melhor com apoio visual",
            "Agitação ou impulsividade na fila",
            "Dificuldade para manter atenção em tarefa sonora",
        ],
        encaminhamento="Se 2+ sinais persistentes, registrar e encaminhar à avaliação audiológica e "
        "ao profissional habilitado (Fichas 17 e 6 do Volume Profissional).",
    ),
    Checkpoint(
        arquivo="rastreio-u6",
        rotulo="Rastreio Integrado 6 --- após a Unidade 10 (Ditongos ÃE e ÕE)",
        quando="aplicar ao fim da Unidade 10, ao concluir a sequência didática do Volume 1, antes "
        "dos Exercícios Kumon. Tempo: 10--15 minutos.",
        dominio="Leitura, Fluência e Aprendizagem Geral",
        fichas="Ficha 1 (Dislexia) e Ficha 25 (sinais escolares de DI leve)",
        itens_auto=[
            "Leio com fluência as sílabas do livro",
            "Escrevo frases curtas sozinho",
            "Completo as atividades no tempo",
            "Gosto de ler em voz alta",
        ],
        indicadores=[
            "Lê texto curto com fluência e entonação",
            "Compreende o que leu em perguntas orais",
            "Generaliza o repertório em escrita espontânea",
            "Progresso sustentado ao longo do volume",
            "Curva de aprendizagem consistente nas folhas",
        ],
        encaminhamento="Se 2+ sinais persistentes mesmo com rotas individualizadas, registrar e "
        "encaminhar ao profissional habilitado (Fichas 1 e 25 do Volume Profissional).",
    ),
]


# ---------------------------------------------------------------------------
# Injeção idempotente no parte2-sequencia-didatica.tex
# ---------------------------------------------------------------------------
# (âncora regex, arquivo de checkpoint)
ANCLAS_V1: list[tuple[str, str]] = [
    (r"\\chapter\{Unidade 2 --- Consonantes do Bloco 1\}", "rastreio-u1"),
    (r"\\chapter\{Unidade 3 --- Silabas Diretas\}", "rastreio-u2"),
    (r"\\chapter\{Unidade 4 --- Primeiras Frases\}", "rastreio-u3"),
    (r"\\chapter\{Unidade 6 --- Silabas Nasais\}", "rastreio-u4"),
    (r"\\chapter\{Unidade 8 --- Letras X, Q, H\}", "rastreio-u5"),
    (r"%% FIM DA PARTE II -- SEQUENCIA DIDATICA", "rastreio-u6"),
]


def _input_line(nome: str) -> str:
    return f"\\input{{checkpoints/{nome}}}\n"


def gerar_checkpoints(destino: Path = CHECKPOINT_DIR, cps: list[Checkpoint] | None = None) -> list[Path]:
    """Gera os arquivos checkpoints/rastreio-u*.tex. Retorna os caminhos criados."""
    cps = cps or CHECKPOINTS_V1
    destino.mkdir(parents=True, exist_ok=True)
    gerados: list[Path] = []
    for cp in cps:
        arquivo = destino / f"{cp.arquivo}.tex"
        arquivo.write_text(cp.to_latex(), encoding="utf-8")
        gerados.append(arquivo)
    return gerados


def injetar(arquivo: Path = SEQUENCIA, ancoras: list[tuple[str, str]] | None = None, dry_run: bool = False) -> list[str]:
    """Insere \\input{checkpoints/...} antes de cada âncora, de forma idempotente."""
    if ancoras is None:
        ancoras = ANCLAS_V1
    texto = arquivo.read_text(encoding="utf-8")
    acoes: list[str] = []
    for padrao, nome in ancoras:
        marcado = _input_line(nome)
        if marcado.strip() in texto:
            acoes.append(f"OK (já presente): {nome}")
            continue
        m = re.search(padrao, texto)
        if not m:
            acoes.append(f"FALHA (âncora não encontrada): {padrao}")
            continue
        texto = texto[: m.start()] + marcado + texto[m.start():]
        acoes.append(f"INJETADO: {nome} antes de {padrao}")
    if not dry_run:
        arquivo.write_text(texto, encoding="utf-8")
    return acoes


def main() -> int:
    parser = argparse.ArgumentParser(description="SPEC-935-R211 — Rastreio Integrado Sequenciado")
    parser.add_argument("--dry-run", action="store_true", help="apenas mostra o que seria feito")
    args = parser.parse_args()

    gerados = gerar_checkpoints()
    print(f"Gerados {len(gerados)} checkpoints em {CHECKPOINT_DIR}")

    acoes = injetar(SEQUENCIA, dry_run=args.dry_run)
    for a in acoes:
        print(f"  - {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())