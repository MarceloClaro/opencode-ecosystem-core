#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as 1000 laudas (100 conceitos x 10 lentes) da edição pixel.

Cada lauda é um arquivo Markdown separado em `secoes/`, com:
- cabeçalho pixel (código, lente, conceito);
- corpo didático;
- caixa de RIGOR CIENTÍFICO (com nota para o professor);
- checkpoint;
- rodapé com a numeração.
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from base.base_chines import CHINES, FRASES, leitura, tons, validar  # noqa: E402
from base.base_conceitos import CONCEITOS  # noqa: E402
from base.base_experimentos import EXPERIMENTOS, MAPA as MAPA_EXPERIMENTOS  # noqa: E402
from base.base_notas import NOTAS, NOTAS_EXPERIMENTO  # noqa: E402

DADOS = RAIZ.parent / "dados_hardware"
DADOS_EXP = RAIZ.parent / "dados_experimentos"

SECOES = RAIZ / "secoes"
SECOES.mkdir(parents=True, exist_ok=True)

PARTES = {
    1: ("Informação e medida", "Do bit ao estado de Bell", "5EEAD4"),
    2: ("A lente de Bohm", "Onda piloto, diálogo e totalidade", "FBBF24"),
    3: ("Circuitos", "Portas, GHZ e QASM 2.0", "34D399"),
    4: ("Ferramentas", "PennyLane, Cirq e Qiskit", "A78BFA"),
    5: ("Hardware e nuvem", "Do chip ao job", "FB7185"),
    6: ("Experimentos", "Simulação, ruído e resultados reais", "F97316"),
    7: ("Matemática", "A linguagem por trás", "60A5FA"),
    8: ("Pedagogia", "Nanoaulas e autodidatismo", "F472B6"),
    9: ("Ética", "Poder, dados e sociedade", "2DD4BF"),
    10: ("Projeto", "Pergunta, evidência, limite", "A3E635"),
}

LENTES = [
    ("ideia", "IDEIA EM 60s", "ideia", "5EEAD4", "60秒概念"),
    ("analogia", "ANALOGIA + LIMITE", "analogia", "FBBF24", "类比与边界"),
    ("pratica", "MÃO NA MASSA", "pratica", "34D399", "动手实践"),
    ("laboratorio", "LABORATÓRIO", "laboratorio", "A78BFA", "实验室"),
    ("erro", "ERRO COMUM", "erro", "FB7185", "常见错误"),
    ("alem", "PARA IR ALÉM", "alem", "60A5FA", "深入一步"),
    ("dialogo", "RODA DE DIÁLOGO", "dialogo", "F472B6", "对话圈"),
    ("etica", "ÉTICA E SOCIEDADE", "etica", "FB923C", "伦理与社会"),
    ("vida", "CONEXÃO COM A VIDA", "vida", "2DD4BF", "与生活连接"),
    ("checkpoint", "CHECKPOINT", "checkpoint", "A3E635", "检查点"),
]

def micro_html(lente_id: str) -> str:
    if lente_id == "laboratorio":
        return ""
    return (f'<p class="micro"><strong>MICROPRÁTICA:</strong> '
            f'{MICROPRATICAS[lente_id]}</p>')


MICROPRATICAS = {
    "ideia": "explique a ideia em uma frase para alguém em 30 segundos.",
    "analogia": "desenhe a analogia e marque o ponto em que ela falha.",
    "pratica": "faça o experimento e anote o que esperava antes.",
    "laboratorio": "leia a tabela e escreva o que o número não prova.",
    "erro": "escreva um contraexemplo em uma frase.",
    "alem": "procure uma fonte e anote uma pergunta que ela não responde.",
    "dialogo": "faça a pergunta a alguém e escute sem interromper.",
    "etica": "liste um grupo afetado e uma medida de mitigação.",
    "vida": "encontre um exemplo em casa ou na escola e descreva em duas frases.",
    "checkpoint": "escreva o que você leva em uma frase, sem consultar.",
}

RIGOR = {
    1: "A descrição usa a regra de Born e a leitura padrão. 'Colapso' é um nome para a atualização do estado; a interpretação segue em debate.",
    2: "Bohm é uma interpretação não local, não um consenso. A ordem implicada é filosófica; não faz previsões testáveis por si só.",
    3: "Circuitos são modelos. A ordem dos qubits, a transpilação e a leitura mudam a implementação física.",
    4: "As bibliotecas simulam. Convenções de bits e versões diferentes podem mudar o desenho e a ordem dos resultados.",
    5: "Backends têm ruído, calibração e deriva. Fidelidade proxy não é prova de emaranhamento.",
    6: "Quatro pontos e 1024 tiros não generalizam. Ruído benéfico é hipótese, não garantia.",
    7: "A matemática é representação; não é o fenômeno. Não confunda o mapa com o território.",
    8: "Pedagogia é contextual. Não há método com efeito garantido para toda turma.",
    9: "Ética envolve valores e poder. Não há resposta automática; há deliberação e consequências.",
    10: "Todo projeto é um recorte. Declare limite, evidência e o que ficou fora.",
}

PROF = {
    1: "Use a notação de ket apenas depois do concreto; verifique P(0)+P(1)=1.",
    2: "Diga 'interpretação', não 'prova'. Compare com a leitura padrão e nomeie o preço: não localidade.",
    3: "Confira a ordem dos qubits e a diferença entre circuito lógico e transpilado.",
    4: "Compare a mesma grandeza nas três bibliotecas; se divergir, verifique convenção antes de concluir erro.",
    5: "T1, T2, erro de leitura e ruído de porta são coisas distintas; não os trate como um número único.",
    6: "A acurácia de 4/4 não é generalized accuracy. Explique o teto e o tamanho da amostra.",
    7: "A fórmula deve vir depois da intuição; use exemplos numéricos pequenos.",
    8: "Nanoaula é unidade de tempo e evidência, não fragmento sem síntese.",
    9: "Não transforme ética em opinião pessoal: peça evidência, afetados e alternativas.",
    10: "Exija um limite específico; 'tem limitações' não é suficiente.",
}

NIVEIS = {
    0: {
        "sigla": "N0",
        "nome": "Leigo e Fundamental",
        "zh": "零级 · 从零开始",
        "desc": "Sem matemática: a ideia, a imagem, o gesto e o resultado.",
    },
    1: {
        "sigla": "N1",
        "nome": "Médio e Graduação",
        "zh": "中级 · 中学与本科",
        "desc": "Com circuito, tabela, fórmula curta e comparação simulado × backend.",
    },
    2: {
        "sigla": "N2",
        "nome": "Pós e PhD",
        "zh": "高级 · 研究生与博士",
        "desc": "Com formalização, limite estatístico, replicação e pergunta aberta.",
    },
}

RIGOR_N0 = {
    1: "Medir produz uma amostra; não é ler um valor escondido.",
    2: "Bohm é uma interpretação entre várias; não é consenso.",
    3: "Circuito é um modelo; a ordem dos qubits importa.",
    4: "Bibliotecas simulam; convenções podem mudar o resultado.",
    5: "Backend tem ruído; um número não prova o estado.",
    6: "Amostra pequena não generaliza; 4 pontos não são um artigo.",
    7: "A matemática é representação; não é o fenômeno.",
    8: "Pedagogia é contextual; não há método garantido.",
    9: "Ética envolve valores e poder; não há resposta automática.",
    10: "Todo projeto é um recorte; declare o limite.",
}

PROF_N0 = {
    1: "Comece pelo concreto; só depois use a notação.",
    2: "Diga 'interpretação', não 'prova'.",
    3: "Confira a ordem dos qubits antes de comparar.",
    4: "Se as bibliotecas divergirem, verifique a convenção.",
    5: "Ruído, leitura e calibração são coisas distintas.",
    6: "Explique o teto e o tamanho da amostra.",
    7: "Use exemplos pequenos antes da fórmula.",
    8: "Nanoaula é tempo e evidência, não fragmento.",
    9: "Peça evidência, afetados e alternativas.",
    10: "Exija um limite específico.",
}

LIMITE = {
    1: "A imagem clássica não captura fase nem correlação.",
    2: "A imagem de Bohm não é uma prova experimental; é uma ontologia possível.",
    3: "O circuito não é o chip; a tradução pode aumentar o ruído.",
    4: "O desenho não é o estado; a amostra não é a distribuição completa.",
    5: "O resultado de hoje não garante o de amanhã; calibração muda.",
    6: "O teste é pequeno; não generaliza para outros dados ou modelos.",
    7: "A equação não explica por que o mundo segue a equação.",
    8: "A técnica não funciona igual para todos os estudantes.",
    9: "Não há consenso moral automático; há trade-offs.",
    10: "O projeto não esgota o problema; escolhe um recorte.",
}

ETICA = {
    1: "Quem define o que é 0 e 1 em um sistema público?",
    2: "Uma interpretação pode ser usada para legitimar autoridade?",
    3: "Quem audita o circuito antes de ele rodar?",
    4: "Quem tem acesso às ferramentas e à formação?",
    5: "Quem paga a conta energética e quem fica na fila?",
    6: "Um resultado de 4 pontos pode enganar uma política pública?",
    7: "Uma métrica pode esconder desigualdades?",
    8: "Quem tem tempo e silêncio para estudar sozinho?",
    9: "Quem ganha e quem perde com esta decisão?",
    10: "Quem participou da pergunta e quem ficou fora?",
}

VIDA = {
    1: "Semáforos, senhas e códigos de barras são bits em ação.",
    2: "Duas pessoas que se entendem sem falar podem parecer 'telepatia'.",
    3: "Fluxogramas, receitas e rotinas também têm portas e medições.",
    4: "Planilhas, mapas e APIs escondem complexidade atrás de interfaces.",
    5: "Serviços de nuvem já mediam nossa confiança e nossos dados.",
    6: "Um treino curto pode dar 100% e não servir para o mundo real.",
    7: "Gráficos e mapas também escolhem o que destacar.",
    8: "Aprender sozinho é uma habilidade, não um dom.",
    9: "Contas de luz, privacidade e emprego são afetados por tecnologia.",
    10: "Todo projeto começa com uma pergunta e termina com um próximo passo.",
}

ALEM = {
    1: "A regra de Born é o elo entre amplitude e probabilidade.",
    2: "A equação do guia de Bohm usa o gradiente da fase da função de onda.",
    3: "A profundidade do circuito cresce com a transpilação e com o número de portas.",
    4: "As três bibliotecas calculam o mesmo estado com convenções diferentes.",
    5: "T1 e T2 são tempos de relaxação e coerência; não são a mesma coisa.",
    6: "A fidelidade proxy mede a população ideal, não a pureza do estado.",
    7: "O produto tensorial faz a dimensão crescer como 2^n.",
    8: "A prática distribuída e a recuperação ativa têm apoio em pesquisa.",
    9: "A LGPD exige base legal, finalidade e transparência.",
    10: "Um bom projeto declara o que não prova.",
}

FIGURAS = {
    "onda_piloto": ("../livro/figuras_geradas/fig01_onda_piloto.png",
                    "Modelo didático de trajetórias guiadas por fase; não é uma solução completa da equação de Bohm."),
    "holograma": ("../livro/figuras_geradas/fig03_holograma.png",
                  "Reconstrução com 1,1% dos coeficientes: analogia da ordem implicada, não holografia física."),
    "pennylane": ("../livro/figuras_geradas/fig05_pennylane.svg",
                  "Circuito de Bell desenhado por PennyLane."),
    "cirq": ("../livro/figuras_geradas/fig06_cirq.svg",
             "Diagrama textual do circuito de Bell em Cirq."),
    "qiskit": ("../livro/figuras_geradas/fig07_qiskit.svg",
               "Circuito de Bell desenhado por Qiskit."),
    "bloch": ("../livro/figuras_geradas/fig10_bloch.png",
              "Esfera de Bloch de H|0⟩, gerada com Qiskit."),
    "ghz_real": ("../livro/figuras_geradas/fig12_ghz4_resultados.png",
                 "GHZ de 4 qubits no Guoji08: 78,8% de fidelidade proxy; 0000 e 1111 dominam, mas 21,2% ficam fora do ideal."),
    "vqc_xor": ("../livro/figuras_geradas/fig13_vqc_xor.png",
                "VQC XOR: ideal, phase damping, depolarização e backend."),
    "ruido_benefico": ("../livro/figuras_geradas/fig14_escada_desafios.png",
                       "A escada do teste quântico real: do fácil ao research-grade."),
    "chsh": ("../livro/figuras_geradas/fig15_chsh.png",
             "CHSH no Guoji08: S ≈ 2,38, acima do limite clássico 2 e abaixo do ideal 2√2."),
    "backends": ("../livro/figuras_geradas/fig16_backends.png",
                 "GHZ de 4 qubits em dois backends: Guoji08 (20 q) e Baihua (156 q)."),
}

GHZ_TABELA = """
<table class="dados">
<tr><th>Resultado</th><th>Ideal</th><th>Guoji08</th></tr>
<tr><td>|0000⟩</td><td>512</td><td>418</td></tr>
<tr><td>|1111⟩</td><td>512</td><td>389</td></tr>
<tr><td>outros</td><td>0</td><td>217</td></tr>
<tr><td><strong>fidelidade proxy</strong></td><td>100%</td><td><strong>78,8%</strong></td></tr>
</table>
"""

VQC_TABELA = """
<table class="dados">
<tr><th>Entrada</th><th>Rótulo</th><th>Ideal P(1)</th><th>Backend P(1)</th><th>Acertou?</th></tr>
<tr><td>00</td><td>0</td><td>0,00</td><td>0,041</td><td>sim</td></tr>
<tr><td>01</td><td>1</td><td>1,00</td><td>0,967</td><td>sim</td></tr>
<tr><td>10</td><td>1</td><td>1,00</td><td>0,952</td><td>sim</td></tr>
<tr><td>11</td><td>0</td><td>0,00</td><td>0,043</td><td>sim</td></tr>
</table>
<p class="mini">4/4 acertos em 1024 tiros por entrada. Não é generalized accuracy: são quatro pontos e um teto de 100%.</p>
"""

PHASE_TABELA = """
<table class="dados">
<tr><th>Condição</th><th>P(1) em 00</th><th>P(1) em 11</th></tr>
<tr><td>ideal</td><td>0,000</td><td>0,000</td></tr>
<tr><td>phase damping γ=0,05</td><td>0,037</td><td>0,037</td></tr>
<tr><td>depolarizing p=0,05</td><td>0,169</td><td>0,169</td></tr>
<tr><td>depolarizing p=0,20</td><td>0,422</td><td>0,422</td></tr>
</table>
<p class="mini">Phase damping não muda a população Z; depolarização reduz a margem até o limiar.</p>
"""


def _carregar_json(nome: str) -> dict | None:
    caminho = DADOS / nome
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except Exception:
        return None


def _carregar_exp(exp_id: str) -> dict | None:
    caminho = DADOS_EXP / f"{exp_id}.json"
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except Exception:
        return None


def _num(valor: float, casas: int = 3) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _pct(valor: float) -> str:
    return f"{valor * 100:.1f}%".replace(".", ",")


def _contagens(dados: dict) -> tuple[dict[str, int], int]:
    c = {str(k): int(v) for k, v in dados.get("counts", {}).items()}
    return c, sum(c.values())


def _resumo_ghz(dados: dict) -> tuple[dict[str, int], int, float]:
    c, total = _contagens(dados)
    ideal = c.get("0000", 0) + c.get("1111", 0)
    fidelidade = ideal / total if total else 0.0
    return c, total, fidelidade


def _fmt_signed(valor: float, casas: int = 3) -> str:
    sinal = "+" if valor >= 0 else ""
    return f"{sinal}{valor:.{casas}f}".replace(".", ",")


def _gjq_chsh() -> dict | None:
    dados = _carregar_exp("GJQ_CHSH")
    if not dados or "cases" not in dados:
        return None
    return dados


def tabela_chsh() -> str:
    dados = _carregar_json("chsh_guoji08.json")
    if not dados or "E" not in dados:
        return ('<p class="mini">O resultado CHSH ainda não está disponível; '
                'rode <code>executar_nuvem.py --only chsh</code>.</p>')
    E = dados["E"]
    gjq = _gjq_chsh()
    mapa = {"E00": "A0B0", "E01": "A0B1", "E10": "A1B0", "E11": "A1B1"}
    E_gjq = {}
    if gjq:
        for nome, caso in mapa.items():
            if caso in gjq["cases"]:
                E_gjq[nome] = float(gjq["cases"][caso].get("E", 0.0))
    ideais = {"E00": 0.7071, "E01": 0.7071, "E10": 0.7071, "E11": -0.7071}
    linhas = []
    for nome in ("E00", "E01", "E10", "E11"):
        medido = float(E.get(nome, 0.0))
        gjq_txt = _fmt_signed(E_gjq[nome]) if nome in E_gjq else "—"
        linhas.append(
            f"<tr><td>{nome}</td><td>{_fmt_signed(ideais[nome])}</td>"
            f"<td>{_fmt_signed(medido)}</td><td>{gjq_txt}</td></tr>"
        )
    S = float(dados.get("S", 0.0))
    ideal_S = float(dados.get("ideal_S", 2 * (2 ** 0.5)))
    if gjq:
        S_gjq = float(gjq.get("S", 0.0))
        se_gjq = float(gjq.get("S_se", 0.0))
        gjq_txt = (f" No <strong>FAS-GPU</strong> (simulador GJQ), "
                   f"S = <strong>{_num(S_gjq)} ± {_num(se_gjq)}</strong>.")
        leitura = (f"S > 2 nos dois casos; {_num(S_gjq)} é consistente "
                   "com 2√2 dentro de ~1 SE.")
        link = (' <a href="#apendice-gjq">Apêndice GJQ</a>: contas, task IDs '
                'e reprodução.')
    else:
        gjq_txt = ""
        leitura = ("O valor observado viola o limite clássico |S| ≤ 2."
                   if abs(S) > 2 else
                   "O valor observado não viola o limite clássico |S| ≤ 2.")
        link = ""
    return f"""
<table class="dados">
<tr><th>Configuração</th><th>E ideal</th><th>E Guoji08</th><th>E FAS-GPU</th></tr>
{''.join(linhas)}
</table>
<p class="mini">S = E00 + E01 + E10 − E11. Guoji08 (hardware): <strong>{_num(S)}</strong>.{gjq_txt}
Limite clássico 2; ideal quântico 2√2 ≈ {_num(ideal_S)}. {leitura}{link}</p>
"""


def tabela_backends() -> str:
    g = _carregar_json("ghz4_guoji08.json")
    b = _carregar_json("ghz4_baihua.json")
    if not g or not b:
        return ('<p class="mini">A comparação de backends ainda não está disponível; '
                'rode <code>executar_nuvem.py --only ghz</code> nos dois backends.</p>')
    cg, tg, fg = _resumo_ghz(g)
    cb, tb, fb = _resumo_ghz(b)
    linhas = [
        ("|0000⟩", cg.get("0000", 0), cb.get("0000", 0)),
        ("|1111⟩", cg.get("1111", 0), cb.get("1111", 0)),
        ("outros", tg - cg.get("0000", 0) - cg.get("1111", 0),
         tb - cb.get("0000", 0) - cb.get("1111", 0)),
    ]
    corpo = "".join(
        f"<tr><td>{rot}</td><td>{a}</td><td>{c}</td></tr>"
        for rot, a, c in linhas
    )
    return f"""
<table class="dados">
<tr><th>Resultado</th><th>Guoji08 (20 q)</th><th>Baihua (156 q)</th></tr>
{corpo}
<tr><td><strong>fidelidade proxy</strong></td><td><strong>{_pct(fg)}</strong></td>
<td><strong>{_pct(fb)}</strong></td></tr>
</table>
<p class="mini">Mais qubits não significa menos ruído: calibração, acoplamento e
mapeamento importam. O Baihua tem 156 qubits e fidelidade proxy menor que o
Guoji08, de 20 qubits.</p>
"""


def linha_baihua() -> str:
    b = _carregar_json("ghz4_baihua.json")
    if not b:
        return ""
    c, total, f = _resumo_ghz(b)
    outros = total - c.get("0000", 0) - c.get("1111", 0)
    return (f"<p><strong>Baihua (156 q):</strong> 0000={c.get('0000', 0)}, "
            f"1111={c.get('1111', 0)}, outros={outros}; fidelidade {_pct(f)}.</p>")


def resultado_html(c: dict) -> str:
    exp_id = MAPA_EXPERIMENTOS.get(c["id"])
    if not exp_id:
        return ""
    d = _carregar_exp(exp_id)
    if not d:
        return ""
    exp = EXPERIMENTOS[exp_id]
    sim = (d.get("simulado") or {}).get("leitura", "—").replace(".", ",")
    real = (d.get("real") or {}).get("leitura", "—").replace(".", ",")
    ov = d.get("sobreposicao")
    ov_txt = f"{ov * 100:.1f}%".replace(".", ",") if isinstance(ov, (int, float)) else "—"
    backend = (d.get("real") or {}).get("backend", "—")
    tarefas = (d.get("real") or {}).get("task_ids") or []
    tarefa = str(tarefas[0])[:8] if tarefas else "—"
    return f"""
<div class="resultado">
<span class="rotulo">RESULTADO · SIMULADO × BACKEND</span>
<p><strong>Experimento:</strong> {exp['nome']} — {exp['descricao']}</p>
<p><strong>Simulado:</strong> {sim}<br>
<strong>Backend:</strong> {real}<br>
<strong>Sobreposição:</strong> {ov_txt} · <strong>task:</strong> {tarefa}</p>
<p class="mini">Sobreposição ≠ fidelidade de estado.</p>
<p class="mini">Script: <code>scripts/experimentos_100.py</code> · {exp_id} · {backend} · <a href="#oficina-{exp_id.lower()}">oficina {exp_id}</a> · <a href="#codigo-{exp_id.lower()}">código {exp_id}</a></p>
</div>
"""


LABS_COM_FIGURA = {"bell", "emaranhamento", "ghz_real", "vqc_xor", "ruido_benefico"}


def mini_barras(c: dict, lente_id: str = "") -> str:
    # Prática e laboratório já têm caixa de resultado/tabela/figura; as barras
    # ficam nas outras lentes para não sobrepor o rodapé.
    if lente_id in ("pratica", "laboratorio"):
        return ""
    exp_id = MAPA_EXPERIMENTOS.get(c["id"])
    if not exp_id:
        return ""
    d = _carregar_exp(exp_id)
    ov = d.get("sobreposicao")
    if not isinstance(ov, (int, float)):
        return ""
    pct = f"{ov * 100:.1f}".replace(".", ",")
    largura = f"{ov * 100:.1f}%"
    return f"""
<div class="mini-barras">
<span class="rotulo-mini">RESULTADO VISUAL · SIMULADO × BACKEND</span>
<div class="linha"><em>sim</em><div class="trilho"><span style="width:100%"></span></div><b>100%</b></div>
<div class="linha"><em>backend</em><div class="trilho"><span style="width:{largura}"></span></div><b>{pct}%</b></div>
</div>
"""


def nota_calculo(c: dict, nivel: int, lente_id: str) -> str:
    """Nota de rodapé de cálculo para N1/N2, em laboratório e 'para ir além'."""
    if nivel == 0 or lente_id not in ("laboratorio", "alem"):
        return ""
    if lente_id == "laboratorio" and c.get("id") == "bell":
        return (
            ' <span class="fn"><strong>NOTA DE CÁLCULO.</strong> '
            'E = (N₀₀+N₁₁−N₀₁−N₁₀)/N; S = E₀₀+E₀₁+E₁₀−E₁₁. '
            'Guoji08: 2,383. FAS-GPU: 2,871±0,044.</span>'
        )
    if lente_id == "laboratorio":
        exp_id = MAPA_EXPERIMENTOS.get(c["id"])
        nota = NOTAS_EXPERIMENTO.get(exp_id) if exp_id else None
    else:
        nota = NOTAS.get(c["id"])
    if not nota:
        return ""
    return (
        ' <span class="fn"><strong>NOTA DE CÁLCULO.</strong><br>'
        f"<strong>Fórmula:</strong> {nota['formula']}<br>"
        f"<strong>Conta:</strong> {nota['conta']}<br>"
        f"<strong>Resultado:</strong> {nota['resultado']}<br>"
        f"<em>Limite:</em> {nota['limite']}</span>"
    )


def inserir_nota_calculo(corpo: str, c: dict, nivel: int, lente_id: str) -> str:
    """Insere a chamada de nota no último parágrafo do corpo."""
    nota = nota_calculo(c, nivel, lente_id)
    if not nota:
        return corpo
    corte = corpo.rfind("</p>")
    if corte == -1:
        return corpo + f"<p>{nota}</p>"
    return corpo[:corte] + nota + corpo[corte:]


def tres_passos_html(c: dict) -> str:
    return f"""
<div class="tres-passos">
<span class="rotulo">LEIA EM 3 PASSOS</span>
<p><strong>1. O que é:</strong> {esc(c['ideia'])}</p>
<p><strong>2. Como testar:</strong> {esc(c['pratica'])}</p>
<p><strong>3. O que não prova:</strong> {esc(c['limite'] or LIMITE[c['parte']])}</p>
</div>
"""


def esc(texto: str) -> str:
    return html.escape(texto or "", quote=False)


def figura(pid: str, classe: str = "fig-pequena") -> str:
    if pid not in FIGURAS:
        return ""
    src, legenda = FIGURAS[pid]
    return (f'<figure class="fig"><img class="{classe}" src="{src}" alt="{esc(legenda)}">'
            f'<figcaption>{esc(legenda)}</figcaption></figure>')


def _corpo_lente_base(c: dict, lente_id: str) -> str:
    pid = c["id"]
    titulo = c["titulo"]
    limite = c["limite"] or LIMITE[c["parte"]]
    alem = c["alem"] or ALEM[c["parte"]]
    etica = c["etica"] or ETICA[c["parte"]]
    vida = c["vida"] or VIDA[c["parte"]]
    pratica = c["pratica"]
    codigo = c["codigo"]
    dialogo = c["dialogo"]
    checkpoint = c["checkpoint"]
    erro = c["erro"]

    if lente_id == "ideia":
        return f"""
<p><strong>{esc(titulo)}</strong> em uma frase: {esc(c['ideia'])}</p>
{tres_passos_html(c)}
<p><strong>Pare e pense:</strong> {esc(dialogo)}</p>
"""

    if lente_id == "analogia":
        return f"""
<p>{esc(c['analogia'])}</p>
<p><strong>Onde a imagem quebra:</strong> {esc(limite)}</p>
<p><strong>Teste rápido:</strong> desenhe a analogia e marque com um X o ponto em que ela deixa de explicar o conceito.</p>
"""

    if lente_id == "pratica":
        if pid in ("ghz_real", "vqc_xor"):
            return f"""
<p>{esc(pratica)}</p>
<p><strong>O que observar:</strong> compare a previsão com o dado real e escreva uma frase sobre o limite da amostra.</p>
{resultado_html(c)}
"""
        return f"""
<p>{esc(pratica)}</p>
<ol>
<li>Faça a atividade sem pressa, em 5 minutos.</li>
<li>Anote o que esperava antes de começar.</li>
<li>Compare a previsão com o que observou.</li>
</ol>
<p><strong>O que observar:</strong> a diferença entre o que você esperava e o que aconteceu é o dado mais valioso.</p>
{resultado_html(c)}
"""

    if lente_id == "laboratorio":
        if pid == "bell":
            return f"""
<p>O estado de Bell é a base do teste CHSH. Quatro configurações foram enviadas ao <strong>Guoji08</strong> (hardware) e repetidas no <strong>FAS-GPU</strong> (simulador GJQ), com 1024 tiros cada.</p>
{tabela_chsh()}
{figura("chsh", "fig-pequena fig-mini")}
"""
        if pid == "emaranhamento":
            return f"""
<p>O mesmo GHZ de 4 qubits foi enviado a dois backends supercondutores. Compare as populações: a fidelidade proxy muda com o backend, e mais qubits não garantem melhor resultado.</p>
{tabela_backends()}
{figura("backends")}
"""
        if pid == "ghz_real":
            return f"""
<p>O GHZ de 4 qubits foi enviado ao Guoji08 com 1024 tiros.</p>
{GHZ_TABELA}
{figura(pid)}
{linha_baihua()}
"""
        if pid == "vqc_xor":
            return f"""
<p>Um classificador de 2 qubits foi treinado no simulador e avaliado no <strong>Guoji08</strong>.</p>
{VQC_TABELA}
{figura(pid)}
"""
        if pid == "phase_damping":
            return f"""
<p>Compare o efeito de dois ruídos no mesmo classificador.</p>
{PHASE_TABELA}
<p><strong>Conclusão:</strong> phase damping não muda a população Z; depolarização reduz a margem. O tipo de ruído importa.</p>
"""
        if pid == "depolarizing":
            return f"""
<p>O canal depolarizante mistura o estado com ruído isotrópico.</p>
{PHASE_TABELA}
<p><strong>O que observar:</strong> a margem até 0,5 diminui quando p cresce. Em p=0,20, a decisão ainda acerta, mas fica frágil.</p>
"""
        if pid == "ruido_benefico":
            return f"""
<p>A hipótese do repositório é que um ruído pequeno pode regularizar o treino. Nosso teste com 4 pontos não testa essa hipótese.</p>
{figura(pid)}
<p><strong>Para testar de verdade:</strong> dataset maior, split treino/teste, múltiplas seeds e curva de ruído.</p>
"""
        if codigo:
            evidencia = figura(pid) or resultado_html(c)
            return f"""
<p>No notebook, o código mínimo é:</p>
<pre><code>{esc(codigo)}</code></pre>
{evidencia}
<p><strong>O que observar:</strong> confira a ordem dos qubits, o número de tiros e a diferença entre estado e amostra.</p>
"""
        return f"""
<p><strong>Protocolo de bancada:</strong> escolha um exemplo de <em>{esc(titulo.lower())}</em>, preveja o resultado e teste com um colega.</p>
<ol>
<li>Escreva a previsão em uma frase.</li>
<li>Execute ou observe o fenômeno.</li>
<li>Registre a diferença e uma possível explicação.</li>
</ol>
<p><strong>O que observar:</strong> não basta acertar; é preciso explicar por que acertou.</p>
{resultado_html(c)}
"""

    if lente_id == "erro":
        return f"""
<p><strong>O erro comum:</strong> {esc(erro)}</p>
<p><strong>Por que acontece:</strong> o cérebro procura uma imagem simples e apaga a parte matemática que não se encaixa.</p>
<p><strong>Como testar:</strong> escreva um contraexemplo em uma frase e veja se ele derruba sua explicação.</p>
"""

    if lente_id == "alem":
        return f"""
<p>{esc(alem)}</p>
<p><strong>Conexão científica:</strong> este é o ponto em que a intuição precisa dar lugar a uma definição precisa. A caixa de rigor abaixo guarda essa definição.</p>
<p><strong>Para ir além:</strong> procure um exemplo em que a ideia falha e explique por quê.</p>
"""

    if lente_id == "dialogo":
        return f"""
<p><strong>Pergunta da roda:</strong> {esc(dialogo)}</p>
<p><strong>Roteiro de 9 minutos:</strong> 1 minuto de silêncio; 4 minutos de falas sem interrupção; 2 minutos de respostas ao que foi ouvido; 2 minutos de síntese.</p>
<p><strong>Regra:</strong> não corrija a fala do outro; pergunte o que o levou a dizer aquilo.</p>
<p><strong>Registre:</strong> uma suposição que apareceu e uma pergunta nova.</p>
"""

    if lente_id == "etica":
        return f"""
<p>{esc(etica)}</p>
<p><strong>Quem ganha? Quem perde?</strong> Liste um grupo que se beneficia e um que pode ser prejudicado.</p>
<p><strong>O que a escola pode fazer?</strong> Transforme o dilema em uma pergunta investigável, não em um julgamento pessoal.</p>
"""

    if lente_id == "vida":
        return f"""
<p>{esc(vida)}</p>
<p><strong>Onde isso aparece:</strong> procure um exemplo na sua casa, na escola ou no bairro. Descreva em duas frases.</p>
<p><strong>O que muda no seu jeito de olhar?</strong> A ideia de {esc(titulo.lower())} pode mudar uma decisão cotidiana?</p>
"""

    if lente_id == "checkpoint":
        return f"""
<p><strong>Tarefa:</strong> {esc(checkpoint)}</p>
<p><strong>Diário de bordo:</strong> o que eu entendi? onde eu travei? o que vou testar amanhã?</p>
<p><strong>Próximo passo:</strong> escolha uma lauda da mesma lente e compare as duas respostas.</p>
"""

    return "<p>...</p>"


def ponte_html(c: dict, lente_id: str) -> str:
    item = CHINES.get(c["id"])
    if not item:
        return ""
    zh, py = item
    fzh, fpy, fpt = FRASES[lente_id]
    fzh = fzh.format(zh=zh)
    fpy = fpy.format(py=py)
    fpt = fpt.format(titulo=esc(c["titulo"]))
    fpy = fpy[0].upper() + fpy[1:]
    return (
        '<p class="ponte"><strong>PONTE SONORA · 中文</strong> '
        f'<span class="termo"><strong>Termo:</strong> <span class="hanzi">{zh}</span> '
        f'<em>{py}</em> <span class="tom">· tons {tons(py)} · leitura {leitura(py)}</span>.</span> '
        f'<span class="frase"><strong>Microfrase:</strong> <span class="hanzi">{fzh}</span> '
        f'<em>{fpy}</em> — {fpt}</span></p>'
    )


def inserir_ponte(corpo: str, c: dict, lente_id: str) -> str:
    bloco = ponte_html(c, lente_id)
    if not bloco:
        return corpo
    corte = corpo.find("</p>")
    if corte == -1:
        return corpo + "\n" + bloco
    corte += len("</p>")
    return corpo[:corte] + "\n" + bloco + corpo[corte:]


def corpo_lente(c: dict, lente_id: str) -> str:
    return inserir_ponte(_corpo_lente_base(c, lente_id), c, lente_id)


def corpo_lente_n0(c: dict, lente_id: str) -> str:
    """Nível 0: sem fórmula, com imagem, gesto e uma pergunta."""
    titulo = c["titulo"]
    if lente_id == "ideia":
        return f"""
<p><strong>{esc(titulo)}</strong> em uma frase: {esc(c['ideia'])}</p>
{tres_passos_html(c)}
<p><strong>Pense:</strong> {esc(c['dialogo'])}</p>
"""
    if lente_id == "analogia":
        return f"""
<p>{esc(c['analogia'])}</p>
<p><strong>Onde a imagem não vale:</strong> {esc(c['limite'] or LIMITE[c['parte']])}</p>
<p>Desenhe a imagem e marque com um X o ponto em que ela falha.</p>
"""
    if lente_id == "pratica":
        return f"""
<p>{esc(c['pratica'])}</p>
<p>Faça em 5 minutos; anote o que esperava antes de começar.</p>
{resultado_html(c)}
"""
    if lente_id == "laboratorio":
        return f"""
<p>O experimento comparou a simulação com o backend. Veja os números abaixo.</p>
{resultado_html(c)}
<p><strong>O que isso mostra:</strong> o resultado é uma amostra de medidas, não um retrato mágico do mundo.</p>
"""
    if lente_id == "erro":
        return f"""
<p><strong>O erro comum:</strong> {esc(c['erro'])}</p>
<p><strong>Como não cair:</strong> escreva um contraexemplo e teste com um colega.</p>
"""
    if lente_id == "alem":
        return f"""
<p>{esc(c['alem'] or ALEM[c['parte']])}</p>
<p>Guarde uma pergunta para a próxima aula; não precisa resolver tudo hoje.</p>
"""
    if lente_id == "dialogo":
        return f"""
<p><strong>Pergunta da roda:</strong> {esc(c['dialogo'])}</p>
<p>Ouça sem interromper; anote uma ideia que mudou sua opinião.</p>
"""
    if lente_id == "etica":
        return f"""
<p>{esc(c['etica'] or ETICA[c['parte']])}</p>
<p><strong>Quem ganha? Quem perde?</strong> Cite um grupo para cada lado.</p>
"""
    if lente_id == "vida":
        return f"""
<p>{esc(c['vida'] or VIDA[c['parte']])}</p>
<p><strong>Onde isso aparece:</strong> procure um exemplo na sua casa ou na escola.</p>
"""
    if lente_id == "checkpoint":
        return f"""
<p><strong>Tarefa:</strong> {esc(c['checkpoint'])}</p>
<p><strong>Diário:</strong> o que entendi? onde travei? o que vou testar amanhã?</p>
"""
    return "<p>...</p>"


def corpo_lente_n2(c: dict, lente_id: str) -> str:
    """Nível 2: formalização curta, limite e replicação."""
    titulo = c["titulo"]
    if lente_id == "ideia":
        return f"""
<p><strong>{esc(titulo)}</strong>: {esc(c['ideia'])}</p>
{tres_passos_html(c)}
<p><strong>Conexão:</strong> {esc(c['alem'] or ALEM[c['parte']])}</p>
<p><strong>Pergunta de pesquisa:</strong> {esc(c['dialogo'])}</p>
"""
    if lente_id == "analogia":
        return f"""
<p>{esc(c['analogia'])}</p>
<p><strong>Limite formal:</strong> {esc(c['limite'] or LIMITE[c['parte']])}</p>
<p>Construa um contraexemplo quantitativo e verifique se a analogia sobrevive.</p>
"""
    if lente_id == "pratica":
        return f"""
<p>{esc(c['pratica'])}</p>
<p><strong>Protocolo:</strong> varie um parâmetro, repita com outra seed e compare.</p>
{resultado_html(c)}
"""
    if lente_id == "laboratorio":
        return _corpo_lente_base(c, lente_id)
    if lente_id == "erro":
        return f"""
<p><strong>O erro comum:</strong> {esc(c['erro'])}</p>
<p><strong>Correção formal:</strong> {esc(c['alem'] or ALEM[c['parte']])}</p>
<p>Teste a correção com um exemplo numérico pequeno.</p>
"""
    if lente_id == "alem":
        return f"""
<p>{esc(c['alem'] or ALEM[c['parte']])}</p>
<p><strong>O que ainda não sabemos:</strong> {esc(c['limite'] or LIMITE[c['parte']])}</p>
<p>Procure um artigo que tente responder e anote o desenho experimental.</p>
"""
    if lente_id == "dialogo":
        return f"""
<p><strong>Pergunta de pesquisa:</strong> {esc(c['dialogo'])}</p>
<p><strong>Hipótese rival:</strong> {esc(c['limite'] or LIMITE[c['parte']])}</p>
<p>Desenhe um experimento que separe as duas hipóteses.</p>
"""
    if lente_id == "etica":
        return f"""
<p>{esc(c['etica'] or ETICA[c['parte']])}</p>
<p><strong>Governança:</strong> quem audita, quem responde e como reparar?</p>
<p>Mapeie os afetados e uma medida de mitigação.</p>
"""
    if lente_id == "vida":
        return f"""
<p>{esc(c['vida'] or VIDA[c['parte']])}</p>
<p><strong>Onde medir:</strong> proponha um indicador e uma fonte de dados.</p>
"""
    if lente_id == "checkpoint":
        return f"""
<p><strong>Tarefa:</strong> {esc(c['checkpoint'])}</p>
<p><strong>Replicação:</strong> outra seed, outro backend, a mesma pergunta.</p>
"""
    return "<p>...</p>"


def _rigor_prof(nivel: int, c: dict, parte: int) -> tuple[str, str, str]:
    if nivel == 0:
        return RIGOR_N0[parte], PROF_N0[parte], "Para o professor"
    if nivel == 2:
        rigor = c["limite"] or LIMITE[parte]
        prof = "repita com outra seed/backend."
        return rigor, prof, "Para pesquisa"
    return c["alem"] or RIGOR[parte], PROF[parte], "Para o professor"


PODA_REPETICAO = (
    r"\n<p><strong>Teste rápido:</strong>.*?</p>",
    r"\n<ol>\n<li>Faça a atividade sem pressa.*?</ol>\n<p><strong>O que observar:</strong> a diferença.*?</p>",
    r"\n<p><strong>Por que acontece:</strong>.*?</p>",
    r"\n<p><strong>Como testar:</strong>.*?</p>",
    r"\n<p><strong>Conexão científica:</strong>.*?</p>",
    r"\n<p><strong>Para ir além:</strong>.*?</p>",
    r"\n<p><strong>Roteiro de 9 minutos:</strong>.*?</p>",
    r"\n<p><strong>Regra:</strong> não corrija.*?</p>",
    r"\n<p><strong>Registre:</strong> uma suposição.*?</p>",
    r"\n<p><strong>Quem ganha\? Quem perde\?</strong>.*?</p>",
    r"\n<p><strong>O que a escola pode fazer\?</strong>.*?</p>",
    r"\n<p><strong>Onde isso aparece:</strong>.*?</p>",
    r"\n<p><strong>O que muda no seu jeito de olhar\?</strong>.*?</p>",
    r"\n<p><strong>Diário de bordo:</strong>.*?</p>",
    r"\n<p><strong>Próximo passo:</strong>.*?</p>",
    r"\n<p><strong>Desenhe a imagem e marque.*?</p>",
    r"\n<p>Faça em 5 minutos;.*?</p>",
    r"\n<p><strong>O que isso mostra:</strong>.*?</p>",
    r"\n<p><strong>Como não cair:</strong>.*?</p>",
    r"\n<p>Guarde uma pergunta.*?</p>",
    r"\n<p>Ouça sem interromper.*?</p>",
    r"\n<p><strong>Diário:</strong>.*?</p>",
    r"\n<p>Construa um contraexemplo.*?</p>",
    r"\n<p><strong>Protocolo:</strong> varie.*?</p>",
    r"\n<p>Teste a correção.*?</p>",
    r"\n<p>Procure um artigo.*?</p>",
    r"\n<p>Desenhe um experimento.*?</p>",
    r"\n<p>Mapeie os afetados.*?</p>",
    r"\n<p><strong>Onde medir:</strong>.*?</p>",
    r"\n<p><strong>Replicação:</strong>.*?</p>",
    r"\n<p class=\"prof\">.*?</p>",
)


def podar_repeticao(texto: str) -> str:
    """Remove micropráticas e notas genéricas repetidas em todas as laudas."""
    for pattern in PODA_REPETICAO:
        texto = re.sub(pattern, "", texto, flags=re.S)
    return texto


def gerar(nivel: int = 0) -> tuple[list[dict], list[dict]]:
    mapa = []
    laudas = []
    n = nivel * 1000
    for parte in range(1, 11):
        conceitos = [c for c in CONCEITOS if c["parte"] == parte]
        for ci, c in enumerate(conceitos, 1):
            primeiro = n + 1
            for li, (lente_id, lente_nome, sprite, cor, lente_zh) in enumerate(LENTES):
                n += 1
                codigo = f"L{n:04d}"
                titulo = f"{c['titulo']} — {lente_nome.lower()}"
                if nivel == 0:
                    corpo = inserir_ponte(corpo_lente_n0(c, lente_id), c, lente_id)
                elif nivel == 2:
                    corpo = inserir_ponte(corpo_lente_n2(c, lente_id), c, lente_id)
                else:
                    corpo = corpo_lente(c, lente_id)
                corpo = podar_repeticao(corpo)
                corpo = inserir_nota_calculo(corpo, c, nivel, lente_id)
                zh_conceito = CHINES[c["id"]][0]
                xp = "".join(
                    f'<span class="{"on" if j == li else ""}"></span>'
                    for j in range(10)
                )
                rigor, _, _ = _rigor_prof(nivel, c, parte)
                gab_id = (parte - 1) * 10 + ci
                ico_conceito = (f'<img class="ico-conceito" '
                                f'src="sprites_conceitos/C{gab_id:03d}.png" alt="">')
                arquivo = SECOES / f"{n:04d}_{c['id']}_{lente_id}.md"
                texto = f"""::: {{.lauda .lente-{lente_id} .nivel-{nivel}}}
<div class="topo">
  <span class="cod">{codigo}</span>
  <span class="lente"><img class="ico" src="sprites/{sprite}.png" alt=""> {lente_nome}</span>
  <span class="conc">{ico_conceito} {NIVEIS[nivel]['sigla']} · C{(parte-1)*10+ci:03d} · {esc(c['titulo']).upper()}</span>
</div>
<div class="xp">{xp}</div>
<h2 id="l-{n:04d}" class="titulo">{esc(titulo)}</h2>
<div class="corpo">
{corpo}
</div>
<div class="rigor">
<span class="rotulo">RIGOR CIENTÍFICO</span>
<p>{esc(rigor)}</p>
</div>
<div class="check">
<span class="rotulo">CHECKPOINT</span>
<p>{esc(c['checkpoint'])}</p>
</div>
{mini_barras(c, lente_id)}
<div class="rodape">P{parte:02d} · C{(parte-1)*10+ci:03d}/100 · {codigo}/3000 · <a class="gab" href="#g-{gab_id:03d}">[G{gab_id:03d}]</a> · <a class="ficha-link" href="#f-{gab_id:03d}">[F{gab_id:03d}]</a></div>
:::
"""
                arquivo.write_text(texto, encoding="utf-8")
                laudas.append({
                    "lauda": codigo,
                    "nivel": nivel,
                    "parte": parte,
                    "conceito": c["titulo"],
                    "id": c["id"],
                    "lente": lente_id,
                    "arquivo": arquivo.name,
                })
            mapa.append({
                "lauda": f"L{primeiro:04d}",
                "nivel": nivel,
                "parte": parte,
                "conceito": c["titulo"],
                "id": c["id"],
                "arquivo": f"{primeiro:04d}_{c['id']}_ideia.md",
                "n_laudas": 10,
            })
    return mapa, laudas


def indice_csv(laudas: list[dict]) -> None:
    with (RAIZ / "INDICE_3000.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["lauda", "nivel", "parte", "conceito", "id", "lente", "arquivo"],
        )
        w.writeheader()
        w.writerows(laudas)


def mapa_md(mapas: list[list[dict]]) -> None:
    linhas = [
        "# Mapa dos 100 conceitos × 3 níveis {#mapa}",
        "",
        "Cada linha aponta para a primeira lauda do conceito no nível. Use o link ou o marcador do PDF.",
        "",
    ]
    for nivel, mapa in enumerate(mapas):
        linhas.append(f"## Nível {nivel} — {NIVEIS[nivel]['nome']} {{#mapa-nivel-{nivel}}}")
        linhas.append("")
        linhas.append(f"*{NIVEIS[nivel]['desc']}*")
        linhas.append("")
        linhas.append("::: {.tabela-longa}")
        linhas.append("")
        linhas.append("| Parte | Conceito | Primeira lauda | Experimento |")
        linhas.append("|---|---|---|---|")
        for m in mapa:
            exp = MAPA_EXPERIMENTOS.get(m["id"], "—")
            numero = int(m["lauda"][1:])
            linhas.append(
                f"| P{m['parte']:02d} | {m['conceito']} | "
                f"[L{numero:04d}](#l-{numero:04d}){{.ref}} | {exp} |"
            )
        linhas.append("")
        linhas.append(":::")
        linhas.append("")
    (RAIZ / "MAPA.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def niveis_md(mapas: list[list[dict]]) -> None:
    pasta = RAIZ / "niveis"
    pasta.mkdir(parents=True, exist_ok=True)
    for nivel, mapa in enumerate(mapas):
        inicio = nivel * 1000 + 1
        fim = (nivel + 1) * 1000
        linhas = [
            f"# Nível {nivel} — {NIVEIS[nivel]['nome']} {{#nivel-{nivel}}}",
            "",
            NIVEIS[nivel]["desc"],
            "",
            f"**Faixa:** L{inicio:04d}–L{fim:04d}.",
            "",
            "| Parte | Comece em |",
            "|---|---|",
        ]
        for parte in range(1, 11):
            m = next(x for x in mapa if x["parte"] == parte)
            numero = int(m["lauda"][1:])
            linhas.append(
                f"| P{parte:02d} — {PARTES[parte][0]} | "
                f"[L{numero:04d}](#l-{numero:04d}) |"
            )
        linhas += [
            "",
            "> **Como usar:** leia a lauda de ideia, faça a prática e só depois",
            "> avance para a próxima lente. O mapa completo está no início do livro.",
            "",
        ]
        (pasta / f"nivel_{nivel}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def glossario_chines(mapa: list[dict]) -> None:
    linhas = [
        "# Glossário sonoro: 100 conceitos em chinês {#glossario-chines}",
        "",
        "Cada linha reúne o hanzi, o pinyin com tons, a leitura de apoio em",
        "grafia portuguesa (aproximada, não IPA) e a primeira lauda do conceito.",
        "",
        "::: {.tabela-longa}",
        "",
        "| Hanzi | Pinyin | Tons | Sentido | Lauda |",
        "|---|---|---|---|---|",
    ]
    for m in mapa:
        zh, py = CHINES[m["id"]]
        numero = int(m["lauda"][1:])
        linhas.append(
            f"| {zh} | {py} | {tons(py)} | {m['conceito']} | "
            f"[L{numero:04d}](#l-{numero:04d}) |"
        )
    linhas += [
        "",
        ":::",
        "",
        "> **Como usar:** leia o pinyin em voz alta, marque o contorno dos tons com",
        "> a mão e só depois olhe o hanzi. O objetivo é criar uma ponte sonora,",
        "> não decorar uma lista. A repetição espaçada vale mais que a pressa.",
        "",
    ]
    (RAIZ / "GLOSSARIO_CHINES.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> None:
    faltando = validar([c["id"] for c in CONCEITOS])
    if faltando:
        raise SystemExit(f"Conceitos sem entrada chinesa: {faltando}")
    faltando_exp = [c["id"] for c in CONCEITOS if c["id"] not in MAPA_EXPERIMENTOS]
    if faltando_exp:
        raise SystemExit(f"Conceitos sem experimento: {faltando_exp}")
    print("Gerando 3000 laudas (100 conceitos × 10 lentes × 3 níveis)…")
    # limpar apenas arquivos numerados antigos
    for p in SECOES.glob("[0-9][0-9][0-9][0-9]_*.md"):
        p.unlink()
    pares = [gerar(nivel) for nivel in range(3)]
    mapas = [p[0] for p in pares]
    laudas = [x for p in pares for x in p[1]]
    indice_csv(laudas)
    mapa_md(mapas)
    glossario_chines(mapas[0])
    niveis_md(mapas)
    print(f"Laudas: {len(list(SECOES.glob('[0-9][0-9][0-9][0-9]_*.md')))}")
    print(f"Conceitos: {len(mapas[0])} por nível")
    print(f"Índice: {RAIZ / 'INDICE_3000.csv'}")
    print(f"Mapa: {RAIZ / 'MAPA.md'}")
    print(f"Glossário chinês: {RAIZ / 'GLOSSARIO_CHINES.md'}")
    print(f"Níveis: {RAIZ / 'niveis'}")


if __name__ == "__main__":
    main()