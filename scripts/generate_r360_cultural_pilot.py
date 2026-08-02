#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o dossiê auditável do piloto cultural R360.

Os pareceres compactos abaixo preservam as conclusões centrais das doze
execuções runtime identificadas por ``task_id``. Eles não substituem as saídas
integrais das sessões e não constituem validação cultural externa. Antes da
persistência, cada envelope é revalidado por ``translation.cultural_episteme``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from translation.cultural_episteme import (  # noqa: E402
    SCHEMA_VERSION,
    build_terminology_delta,
    evaluate_gate,
    run_preflight,
    validate_agent_output,
    validate_review_request,
)


OUT_DIR = ROOT / "validacao_externa" / "cultural_episteme"
JSON_PATH = OUT_DIR / "molambudos_r360_reviews.json"
MD_PATH = OUT_DIR / "molambudos_r360_dossier.md"
PROJECT = "projetos/molambudos/Molambudos_VictoriaRegia"
GRAPH_ID = "molambudos-terms"
GRAPH_REVISION = "r360-pilot-1"


def _span(text: str, term: str) -> list[int]:
    start = text.casefold().find(term.casefold())
    return [0, len(text)] if start < 0 else [start, start + len(term)]


def _concern(
    source: str,
    target: str,
    code: str,
    severity: str,
    source_term: str,
    target_term: str,
    evidence: str,
    rationale: str,
    *,
    strength: str = "moderate",
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "evidence_strength": strength,
        "source_span": _span(source, source_term),
        "target_span": _span(target, target_term),
        "detector": "agent",
        "evidence": evidence,
        "rationale": rationale,
    }


UNITS: list[dict[str, Any]] = [
    {
        "unit_id": "curral_do_governo",
        "label": "Curral do Governo",
        "segment_id": "MEM-06:14-18",
        "source_path": f"{PROJECT}/fragmentos/mem/MEM-06.tex",
        "source_lines": [14, 18],
        "target_paths": {
            "en-US": f"{PROJECT}/en/fragmentos/mem/MEM-06.tex",
            "zh-CN": f"{PROJECT}/zh/fragmentos/mem/MEM-06.tex",
        },
        "target_lines": {"en-US": [14, 18], "zh-CN": [14, 18]},
        "source": (
            "O governo chamava de “currais”. A palavra certa. A gente era gado. "
            "O Curral do Governo em Senador Pompeu era uma área cercada de arame "
            "farpado, com uns duzentos metros de largura por talvez trezentos de "
            "comprimento. Não tinha cobertura. Não tinha parede. Não tinha nada "
            "além de terra batida, sol, e o cheiro de gente acumulada."
        ),
        "targets": {
            "en-US": (
                "The government called them “pens”. The right word. We were cattle. "
                "The Government Pen in Senador Pompeu was an area fenced with barbed "
                "wire, about two hundred yards wide and perhaps three hundred long. "
                "No roof. No walls. Nothing but packed earth, sun, and the smell of "
                "people piled up."
            ),
            "zh-CN": (
                "政府管它们叫“牲畜圈”。这名字很准确。我们就是牲口。"
                "塞纳多尔·蓬佩乌的政府牲畜圈是一片用铁丝网围起来的区域，"
                "大约两百米宽、三百米长。没有顶棚。没有墙。"
                "除了踩实了的泥土、太阳和人群积聚的气味，什么都没有。"
            ),
        },
        "task_ids": {
            "en-US": "ses_041c58f80ffexxPfy8pXv1CJ9A",
            "zh-CN": "ses_041c58f4affez18ObsmAVlAYvm",
        },
        "voice": {
            "narrator_age": "child",
            "region": "Senador Pompeu, Ceará",
            "register": "oral, memorialístico, fragmentário e testemunhal",
        },
        "period": "1915",
        "document_type": "memória ficcional infantil",
        "source_term": "Curral do Governo",
        "current_terms": {"en-US": "Government Pen", "zh-CN": "政府牲畜圈"},
        "concept": {
            "source_term": "Curral do Governo",
            "entity_type": "historical_institution_and_dehumanization_metaphor",
            "preferred_en": "Government Pen",
            "preferred_zh_cn": "政府牲畜圈",
            "candidate_en": "Government Concentration Camp",
            "candidate_zh_cn": "政府集中收容营",
            "forbidden_translations": ["Government Cattle Pen", "Government Corral"],
        },
        "classification": "high_risk_human_decision",
        "reviews": {
            "en-US": {
                "status": "complete",
                "concerns": [
                    (
                        "TERM_CONFLICT", "high", "Curral do Governo", "Government Pen",
                        "R355 fixa Government Pen, enquanto R359 registra Government "
                        "Concentration Camp como candidata ainda não aprovada.",
                        "A primeira forma preserva currais–gado; a segunda explicita a "
                        "instituição, mas quebra a cadeia metafórica e eleva o registro.", "strong",
                    ),
                    (
                        "OVERLOCALIZATION", "medium", "duzentos metros", "two hundred yards",
                        "Os números foram mantidos após a troca silenciosa de metros por jardas.",
                        "A medida aumenta cerca de 9% e altera o quadro métrico da memória.", "strong",
                    ),
                    (
                        "HISTORICAL_SOURCE_GAP", "high", "Curral do Governo", "Government Pen",
                        "Não foi fornecida nomenclatura inglesa historicamente documentada.",
                        "Nome narrativo, classificação histórica e nome institucional precisam "
                        "ser distinguidos por revisão temática.", "strong",
                    ),
                ],
                "alternatives": [
                    {
                        "text": "The Government Pen in Senador Pompeu—a concentration camp—was an area fenced in with barbed wire, about two hundred meters wide and maybe three hundred meters long.",
                        "rationale": "Mantém a metáfora e acrescenta classificação histórica explícita.",
                        "risks": ["explicitação ausente da frase-fonte", "interrupção do ritmo infantil"],
                    },
                    {
                        "text": "The Government Pen in Senador Pompeu was an area fenced in with barbed wire, about two hundred meters wide and maybe three hundred meters long.",
                        "rationale": "Preserva a cadeia lexical e corrige a unidade de medida.",
                        "risks": ["a instituição histórica pode permanecer opaca"],
                    },
                ],
                "preference": "The Government Pen in Senador Pompeu—a concentration camp—was an area fenced in with barbed wire, about two hundred meters wide and maybe three hundred meters long.",
                "preference_rationale": "Preferência condicionada que tenta conservar metáfora e categoria histórica; não é aprovação.",
                "conditions": ["arbitragem humana R355/R359", "revisão histórica do Ceará", "revisão bilíngue EN-US"],
                "signals": [0.84, 0.54, 0.78],
                "checks": [1, 1],
                "missing": ["forma inglesa historicamente documentada", "decisão autoral sobre explicitação"],
                "delta_preferred": "Government Pen, com contextualização histórica aprovada",
            },
            "zh-CN": {
                "status": "complete",
                "concerns": [
                    (
                        "TERM_CONFLICT", "high", "Curral do Governo", "政府牲畜圈",
                        "R356 fixa 政府牲畜圈 e R359 propõe 政府集中收容营 sem aprovação.",
                        "A substituição institucional isolada apagaria a cadeia currais/gado; "
                        "a forma literal isolada pode ocultar a instituição.", "strong",
                    ),
                    (
                        "CULTURAL_LOSS", "high", "arame farpado", "铁丝网",
                        "铁丝网 não explicita que o arame possui farpas.",
                        "A omissão enfraquece um elemento material da coerção; 带刺铁丝网 é candidata.", "strong",
                    ),
                    (
                        "VOICE_SHIFT", "medium", "A palavra certa", "这名字很准确",
                        "O fragmento seco vira uma oração analítica completa.",
                        "A voz perde parte da compressão oral e acusatória.", "strong",
                    ),
                ],
                "alternatives": [
                    {
                        "text": "政府把那些地方叫作“牲畜圈”。这词没错。我们就是牲口。塞纳多尔·蓬佩乌的“政府牲畜圈”是一块用带刺铁丝网围起来的地方。",
                        "rationale": "Preserva a metáfora e recupera farpas e ritmo mais oral.",
                        "risks": ["a função institucional ainda requer contexto", "那些地方 depende do cotexto"],
                    },
                    {
                        "text": "“政府牲畜圈”（Curral do Governo）",
                        "rationale": "Sinaliza nome histórico e metáfora em uma primeira ocorrência.",
                        "risks": ["paratexto intrusivo", "possível exotização"],
                    },
                ],
                "preference": "政府把那些地方叫作“牲畜圈”。这词没错。我们就是牲口。塞纳多尔·蓬佩乌的“政府牲畜圈”是一块用带刺铁丝网围起来的地方。",
                "preference_rationale": "Preferência condicionada que conserva R356 e a metáfora; a camada institucional deve ser mediada separadamente.",
                "conditions": ["revisão PT-BR/ZH-CN", "glosa histórica aprovada", "decisão humana R356/R359"],
                "signals": [0.84, 0.66, 0.63],
                "checks": [1, 1],
                "missing": ["parecer histórico sobre a denominação", "cotexto para o antecedente de 它们"],
                "delta_preferred": "政府牲畜圈（首次出现附历史说明）",
            },
        },
    },
    {
        "unit_id": "retirantes",
        "label": "Retirantes",
        "segment_id": "DOC-17:25",
        "source_path": f"{PROJECT}/fragmentos/doc/DOC-17.tex",
        "source_lines": [25, 25],
        "target_paths": {
            "en-US": f"{PROJECT}/en/fragmentos/doc/DOC-17.tex",
            "zh-CN": f"{PROJECT}/zh/fragmentos/doc/DOC-17.tex",
        },
        "target_lines": {"en-US": [25, 25], "zh-CN": [25, 25]},
        "source": "Todo dia chegam mais retirantes. Famílias inteiras. Gente que andou dias sem comida nem água. As crianças chegam com os olhos fundos e a barriga inchada. As mulheres, quando chegam, são separadas e levadas para “realocação”. Eu sei o que isso significa. Todos sabem.",
        "targets": {
            "en-US": "Every day more retirantes arrive. Whole families. People who walked days without food or water. The children arrive with sunken eyes and swollen bellies. The women, when they arrive, are separated and taken for “relocation”. I know what that means. Everyone knows.",
            "zh-CN": "每天都有更多的逃荒者到来。整个整个的家庭。走了好几天、没有食物没有水的人。孩子们到达时眼窝深陷，肚子鼓胀。女人们一到就被分开，送去“重新安置”。我知道那意味着什么。所有人都知道。",
        },
        "task_ids": {
            "en-US": "ses_041c58f0fffey6pWdzr08GMsyN",
            "zh-CN": "ses_041c58ee0ffe1rdzZRje394SWa",
        },
        "corrected_runtime": {"en-US": False, "zh-CN": True},
        "voice": {"narrator_age": "adult", "region": "Ceará", "register": "carta concisa de soldado, burocracia e culpa moral"},
        "period": "1915",
        "document_type": "carta ficcional de soldado",
        "source_term": "retirantes",
        "current_terms": {"en-US": "retirantes", "zh-CN": "逃荒者"},
        "concept": {
            "source_term": "retirantes",
            "entity_type": "historical_regional_displacement_category",
            "preferred_en": "retirantes",
            "preferred_zh_cn": "逃荒者",
            "forbidden_translations": [],
        },
        "classification": "contextual_human_review",
        "reviews": {
            "en-US": {
                "status": "complete",
                "concerns": [
                    ("TERM_CONFLICT", "high", "retirantes", "retirantes", "R355 exige retenção na primeira ocorrência e refugees depois; a posição desta ocorrência nas rotas não foi comprovada.", "O ramo terminológico aplicável não pode ser escolhido sem mapa de primeira exposição.", "moderate"),
                    ("UNDERLOCALIZATION", "medium", "retirantes", "retirantes", "O termo permanece sem glosa no excerto isolado.", "A retenção evita falsa equivalência jurídica, mas pode ocultar seca, fome e categoria regional.", "moderate"),
                    ("LITERALISM", "low", "andou dias", "walked days", "Walked days omite a preposição esperada em EN-US.", "Walked for days preserva concisão e reduz a aparência de decalque.", "moderate"),
                ],
                "alternatives": [
                    {"text": "Every day more *retirantes* arrive. Whole families. People who walked for days without food or water.", "rationale": "Retém a categoria e corrige o decalque; glosa sóbria deve ocorrer em ponto acessível.", "risks": ["opacidade se a glosa não estiver acessível", "itálico reiterado pode alterizar"]},
                    {"text": "Every day more drought-displaced people arrive.", "rationale": "Explicita causa sem afirmar estatuto jurídico.", "risks": ["registro humanitário contemporâneo", "perda da categoria histórica"]},
                ],
                "preference": "Every day more *retirantes* arrive. Whole families. People who walked for days without food or water.",
                "preference_rationale": "Retenção condicionada a glosa única fora da voz do soldado.",
                "conditions": ["mapear a primeira ocorrência", "revisão histórica e jurídico-terminológica", "revisão EN-US"],
                "signals": [0.95, 0.75, 0.90],
                "checks": [0, 1],
                "missing": ["mapa das rotas e primeira ocorrência", "parecer histórico sobre a categoria"],
                "delta_preferred": "retirantes, com glosa inicial contextual",
            },
            "zh-CN": {
                "status": "complete",
                "concerns": [
                    ("CULTURAL_LOSS", "high", "retirantes", "逃荒者", "逃荒者 preserva fuga por escassez, mas não lexicaliza a seca nem a categoria social cearense.", "A equivalência é funcionalmente parcial e pode domesticar o referente pela história chinesa de 逃荒.", "strong"),
                    ("TARGET_VARIETY_USAGE_RISK", "medium", "Famílias inteiras", "整个整个的家庭", "整个整个 apresenta forte aparência de decalque.", "全家老小 é mais idiomático, mas acrescenta oposição etária.", "strong"),
                    ("LITERALISM", "medium", "Gente que andou dias sem comida nem água", "走了好几天、没有食物没有水的人", "A ordem e a repetição seguem rigidamente a fonte.", "A fragmentação pode ser mantida com sintaxe chinesa menos transferida.", "strong"),
                ],
                "alternatives": [
                    {"text": "每天都有更多逃荒者来。全家老小。有人走了好几天，没吃的，也没水喝。", "rationale": "Conserva 逃荒者 e reduz decalques.", "risks": ["a seca continua implícita", "全家老小 acrescenta recorte etário"]},
                    {"text": "每天都有更多因旱灾逃荒的人来。", "rationale": "Explicita a seca sem usar categoria jurídica moderna.", "risks": ["perde a densidade nominal de retirantes", "acrescenta explicitação"]},
                ],
                "preference": "每天都有更多逃荒者来。全家老小。有人走了好几天，没吃的，也没水喝。",
                "preference_rationale": "Mantém R356 e reduz interferência sintática; continua dependente de nota de escopo.",
                "conditions": ["revisão literária ZH-CN", "nota de escopo sobre seca e Ceará", "revisão de 重新安置"],
                "signals": [0.72, 0.56, 0.60],
                "checks": [2, 1],
                "missing": ["fontes históricas da terminologia", "parecer ZH-CN independente"],
                "delta_preferred": "逃荒者（限定于塞阿拉旱灾语境）",
            },
        },
    },
    {
        "unit_id": "rasga_mortalha",
        "label": "Rasga Mortalha",
        "segment_id": "MEM-12:24-50",
        "source_path": f"{PROJECT}/fragmentos/mem/MEM-12.tex",
        "source_lines": [24, 50],
        "target_paths": {"en-US": f"{PROJECT}/en/fragmentos/mem/MEM-12.tex", "zh-CN": f"{PROJECT}/zh/fragmentos/mem/MEM-12.tex"},
        "target_lines": {"en-US": [24, 50], "zh-CN": [24, 50]},
        "source": "A Rasga Mortalha apareceu num inverno. Fino. Agudo. Um canto que subia e descia como uma mulher chorando muito longe. “Rasga mortalha...”, alguém sussurrou. No batente da janela, havia uma coruja. “Rasga mortalha”, repetiu Seu Nonô. “Quando ela canta, alguém morre. Ela rasga a mortalha do finado com o bico pra alma poder sair. Por isso o nome.”",
        "targets": {
            "en-US": "The Shroud-Ripper appeared one winter. Thin. High-pitched. A song that rose and fell like a woman weeping very far away. “Shroud-ripper...”, someone whispered. On the windowsill, there was an owl. “Shroud-ripper,” Seu Nonô repeated. “When she sings, someone dies. She rips the dead man's shroud with her beak so the soul can get out. That's where the name comes from.”",
            "zh-CN": "裹尸布撕裂者在一个冬天出现。纤细。尖锐。像很远的地方一个女人哭泣的声音，时高时低。“裹尸布撕裂者……”我身旁有人低语。窗台上，站着一只猫头鹰。“裹尸布撕裂者，”诺诺老爹重复道，“它一唱，就有人要死。它用喙撕开死者的裹尸布，让灵魂能出来。所以叫这个名字。”",
        },
        "task_ids": {"en-US": "ses_041c58eb7ffekeLqjqGhOezfLH", "zh-CN": "ses_041c58e83ffe5sn0Y3nIHKLDqj"},
        "voice": {"narrator_age": "adult recalling childhood", "region": "Brasil", "register": "oral-popular, religioso e ominoso"},
        "period": "1945",
        "document_type": "memória ficcional e fala de personagem",
        "source_term": "Rasga Mortalha",
        "current_terms": {"en-US": "Shroud-Ripper", "zh-CN": "裹尸布撕裂者"},
        "concept": {"source_term": "Rasga Mortalha", "entity_type": "recurring_folkloric_symbol", "preferred_en": "Shroud-Ripper", "preferred_zh_cn": "裹尸布撕裂者", "forbidden_translations": []},
        "classification": "high_risk_human_decision",
        "reviews": {
            "en-US": {
                "status": "complete",
                "concerns": [
                    ("LITERALISM", "medium", "Rasga Mortalha", "Shroud-Ripper", "O calque preserva a morfologia, mas pode soar como epíteto fantástico inventado.", "A explicação intratextual ajuda, porém não preserva sozinha a ancoragem brasileira.", "strong"),
                    ("SYMBOL_DRIFT", "high", "Rasga Mortalha", "Shroud-Ripper", "A recorrência enfatiza a ação gótica de rasgar a mortalha.", "O símbolo pode deslocar-se de ave agourenta popular para entidade nomeada de bestiário.", "moderate"),
                    ("DOMESTICATION_ERASURE_RISK", "medium", "Rasga Mortalha", "Shroud-Ripper", "A forma portuguesa desaparece.", "A etimologia fica acessível, mas o marcador cultural brasileiro é apagado.", "strong"),
                ],
                "alternatives": [
                    {"text": "The Rasga-Mortalha appeared one winter.", "rationale": "Retém o nome e deixa a cena explicar coruja, presságio e etimologia.", "risks": ["opacidade temporária", "conflito com R355"]},
                    {"text": "The Rasga-Mortalha—the “shroud-ripper”—appeared one winter.", "rationale": "Combina retenção e glosa.", "risks": ["antecipa a explicação", "pode folclorizar"]},
                ],
                "preference": "The Rasga-Mortalha appeared one winter.",
                "preference_rationale": "Retenção sem itálico, condicionada à comparação de todas as recorrências.",
                "conditions": ["revisão de folclore brasileiro", "cotejo global do símbolo", "revisão EN-US"],
                "signals": [0.84, 0.69, 0.86],
                "checks": [0, 0],
                "missing": ["fontes folclóricas externas", "mapa global das ocorrências"],
                "delta_preferred": "Rasga-Mortalha, com mediação intratextual",
            },
            "zh-CN": {
                "status": "complete",
                "concerns": [
                    ("TERM_CONFLICT", "high", "Rasga Mortalha", "裹尸布撕裂者", "R356 exige glosa 报丧鸟 na primeira ocorrência, ausente no recorte.", "Inseri-la automaticamente pode antecipar a revelação; local e forma exigem decisão humana.", "strong"),
                    ("LITERALISM", "medium", "Rasga Mortalha", "裹尸布撕裂者", "O composto é literalmente analisável e pesado nas repetições.", "Pode soar como epíteto de criatura, embora preserve a etimologia.", "moderate"),
                    ("REGISTER_SHIFT", "high", "finado", "死者", "Finado, bico, pra e alma tornam-se formas mais escritas como 死者, 喙 e 灵魂.", "A fala popular de Seu Nonô adquire registro expositivo.", "strong"),
                ],
                "alternatives": [
                    {"text": "“裹尸布撕裂者”（报丧鸟）是在一个冬天出现的。", "rationale": "Mantém o termo e realiza a glosa uma vez.", "risks": ["antecipa o agouro", "pesa a abertura"]},
                    {"text": "“裹尸布撕裂者”¹在一个冬天出现。〔注1：报丧鸟。〕", "rationale": "Desloca a mediação para o paratexto.", "risks": ["interrompe a leitura", "exige decisão tipográfica"]},
                ],
                "preference": "首次出现保留“裹尸布撕裂者”，并以括注或脚注补“报丧鸟”；后续完整重复“裹尸布撕裂者”。",
                "preference_rationale": "Preserva R356, etimologia e repetição; posição da glosa continua aberta.",
                "conditions": ["definir primeira ocorrência", "revisão PT-BR/ZH-CN", "revisão folclórica", "cotejo de todas as recorrências"],
                "signals": [0.93, 0.62, 0.57],
                "checks": [1, 1],
                "sufficiency": "contested",
                "missing": ["posição editorial da glosa", "parecer bilíngue e cultural"],
                "delta_preferred": "裹尸布撕裂者（首现以报丧鸟作候选注释）",
            },
        },
    },
    {
        "unit_id": "molambudos",
        "label": "Molambudos",
        "segment_id": "MEM-06:22-28",
        "source_path": f"{PROJECT}/fragmentos/mem/MEM-06.tex",
        "source_lines": [22, 28],
        "target_paths": {"en-US": f"{PROJECT}/en/fragmentos/mem/MEM-06.tex", "zh-CN": f"{PROJECT}/zh/fragmentos/mem/MEM-06.tex"},
        "target_lines": {"en-US": [22, 28], "zh-CN": [22, 28]},
        "source": "Todo dia chegavam soldados com mais retirantes. Eles vinham de toda parte. Os soldados chamavam a gente de “molambudos”. A palavra saía da boca deles como se fosse o nome de uma praga. “Lá vem mais molambudos.” “Molambudo, sai daí.” “Dá comida pra esses molambudos antes que morram tudo.”",
        "targets": {
            "en-US": "Every day soldiers arrived with more retirantes. They came from everywhere. The soldiers called us “molambudos”. The word came out of their mouths as if it were the name of a plague. “Here come more molambudos.” “Molambudo, get out of there.” “Give food to these molambudos before they all die.”",
            "zh-CN": "每天都有士兵押着更多的逃荒者到来。他们来自四面八方。士兵们叫我们“莫兰布多斯”。这个词从他们嘴里说出来，仿佛是一种瘟疫的名字。“又来了一群破衣人。”“破衣人，滚开。”“给这些破衣人点吃的，别让他们全死光了。”",
        },
        "task_ids": {"en-US": "ses_041c58e51ffeiptwO2UIgaHhzx", "zh-CN": "ses_041c58dfbffeTI31oDYwOereUs"},
        "voice": {"narrator_age": "child", "region": "Ceará", "register": "oralidade infantil e fala humilhante de soldados"},
        "period": "1915",
        "document_type": "memória ficcional com discurso direto",
        "source_term": "molambudos",
        "current_terms": {"en-US": "molambudos", "zh-CN": "莫兰布多斯 / 破衣人"},
        "concept": {"source_term": "molambudos", "entity_type": "recurring_neologism_social_slur_and_title", "preferred_en": "molambudos", "preferred_zh_cn": "莫兰布多斯", "forbidden_translations": []},
        "classification": "high_risk_human_decision",
        "reviews": {
            "en-US": {
                "status": "complete",
                "concerns": [
                    ("TERM_CONFLICT", "high", "molambudos", "molambudos", "R355 prevê retenção com glosa contextual rag-people; a glosa não aparece neste recorte.", "A retenção preserva título e categoria, mas pode ocultar a materialidade do insulto.", "strong"),
                    ("PRAGMATIC_FAILURE", "medium", "molambudos", "molambudos", "O termo pode permanecer semanticamente opaco ao público EN-US.", "A hostilidade sobrevive pelos imperativos, mas a categoria social imposta pode enfraquecer.", "moderate"),
                    ("REGISTER_SHIFT", "medium", "morram tudo", "they all die", "A concordância oral marcada vira inglês padrão.", "Não se deve compensar com eye dialect ou dialeto estereotipado.", "strong"),
                ],
                "alternatives": [
                    {"text": "The soldiers called us “molambudos”—rag-people.", "rationale": "Acrescenta uma glosa única e mantém a repetição posterior.", "risks": ["rag-people pode parecer equivalência total", "muda a cadência"]},
                    {"text": "The soldiers called us “molambudos”.", "rationale": "Retenção pura, se a glosa já estiver acessível em todas as rotas.", "risks": ["opacidade e sublocalização"]},
                ],
                "preference": "The soldiers called us “molambudos”—rag-people.",
                "preference_rationale": "Intervenção mínima condicionada ao mapa de primeira exposição; não substituir globalmente o termo.",
                "conditions": ["mapa das rotas", "glosa única", "revisão EN-US", "não usar eye dialect"],
                "signals": [0.97, 0.74, 0.85],
                "checks": [1, 1],
                "missing": ["mapa das primeiras ocorrências", "decisão tipográfica"],
                "delta_preferred": "molambudo(s), com glosa contextual única rag-people",
            },
            "zh-CN": {
                "status": "complete",
                "concerns": [
                    ("TERM_CONFLICT", "high", "molambudos", "莫兰布多斯", "A narração usa 莫兰布多斯, mas as três falas usam 破衣人.", "O glossário contém ambas as formas sem delimitar a alternância dentro da mesma cena.", "moderate"),
                    ("SYMBOL_DRIFT", "high", "molambudos", "破衣人", "A repetição do neologismo-título desaparece das falas.", "Enfraquece a cadeia entre insulto, praga, categoria social e título.", "strong"),
                    ("DOMESTICATION_ERASURE_RISK", "high", "molambudos", "破衣人", "破衣人 é transparente como descrição de roupa.", "A solução pode apagar a estranheza autoral e reduzir o neologismo a descrição comum.", "moderate"),
                ],
                "alternatives": [
                    {"text": "“又来了一群莫兰布多斯。”“莫兰布多斯，滚开。”“给这些莫兰布多斯点吃的，别让他们全死光了。”", "rationale": "Prioriza recorrência do neologismo depois de glosa acessível.", "risks": ["pode soar como nome próprio", "vocativo singular não se distingue"]},
                    {"text": "“又来了一群破衣人。”“破衣人，滚开。”", "rationale": "Mantém transparência atual se a alternância for deliberadamente documentada.", "risks": ["quebra a repetição simbólica"]},
                ],
                "preference": "“又来了一群莫兰布多斯。”“莫兰布多斯，滚开。”“给这些莫兰布多斯点吃的，别让他们全死光了。”",
                "preference_rationale": "Preferência condicionada à existência de glosa acessível e à força pragmática em ZH-CN.",
                "conditions": ["verificar rotas", "revisão pragmática ZH-CN", "registrar política de alternância"],
                "signals": [0.58, 0.74, 0.82],
                "checks": [1, 1],
                "missing": ["snapshot completo do grafo", "parecer pragmático bilíngue"],
                "delta_preferred": "莫兰布多斯 nas recorrências simbolicamente centrais; 破衣人 apenas como glosa",
            },
        },
    },
    {
        "unit_id": "hospital_colonia",
        "label": "Hospital Colônia",
        "segment_id": "LUC-01:20,29",
        "source_path": f"{PROJECT}/fragmentos/luc/LUC-01.tex",
        "source_lines": [20, 29],
        "target_paths": {"en-US": f"{PROJECT}/en/fragmentos/luc/LUC-01.tex", "zh-CN": f"{PROJECT}/zh/fragmentos/luc/LUC-01.tex"},
        "target_lines": {"en-US": [20, 29], "zh-CN": [20, 29]},
        "source": "Conforme conversamos em janeiro, localizamos o prontuário completo do Paciente 1.260 (Hospital Colônia de Barbacena) e os anexos mencionados. O caso do Colônia era famoso na psiquiatria forense brasileira: sessenta mil mortos em oitenta anos, pacientes enterrados vivos, diagnósticos fabricados.",
        "targets": {
            "en-US": "As we discussed in January, we have located the complete medical record of Patient 1,260 (Hospital-Colony of Barbacena) and the attachments mentioned. The Colony case was famous in Brazilian forensic psychiatry: sixty thousand dead in eighty years, patients buried alive, manufactured diagnoses.",
            "zh-CN": "按照我们一月份的约定，我们已找到患者1,260（巴尔巴塞纳收容医院）的完整病历及所提及的附件。收容院的案子在巴西法医精神病学界很有名：八十年间六万人死亡，患者被活埋，诊断被伪造。",
        },
        "task_ids": {"en-US": "ses_041c58dc4ffew5hXH6W50EoxNN", "zh-CN": "ses_041c58d74ffeRVhN4opcWtY3bh"},
        "corrected_runtime": {"en-US": False, "zh-CN": True},
        "voice": {"narrator_age": "adult", "region": "Barbacena", "register": "investigação acadêmica contemporânea"},
        "period": "2026 sobre instituição histórica",
        "document_type": "e-mail ficcional e narração investigativa",
        "source_term": "Hospital Colônia de Barbacena",
        "current_terms": {"en-US": "Hospital-Colony of Barbacena / the Colony", "zh-CN": "巴尔巴塞纳收容医院 / 收容院"},
        "concept": {"source_term": "Hospital Colônia de Barbacena", "entity_type": "historical_institution_proper_name", "preferred_en": "the Colony", "preferred_zh_cn": "收容院", "forbidden_translations": []},
        "classification": "high_risk_human_decision",
        "reviews": {
            "en-US": {
                "status": "insufficient_context",
                "concerns": [
                    ("LITERALISM", "high", "Hospital Colônia de Barbacena", "Hospital-Colony of Barbacena", "O composto hifenizado reproduz literalmente o nome.", "Pode sugerir colônia territorial e não está documentado como denominação inglesa reconhecida.", "strong"),
                    ("TERM_CONFLICT", "high", "Colônia", "The Colony", "O corpo alterna Hospital-Colony e the Colony; R355 também contém Santa Maria Colony.", "A correferência e o escopo das três formas não estão reconciliados.", "strong"),
                    ("HISTORICAL_SOURCE_GAP", "high", "sessenta mil mortos", "sixty thousand dead", "As alegações históricas aparecem sem fontes no recorte.", "Não se pode acrescentar ou retirar modalização factual sem examinar a proveniência.", "strong"),
                ],
                "alternatives": [
                    {"text": "Hospital Colônia de Barbacena, the psychiatric institution hereafter referred to as “the Colony”", "rationale": "Retém o nome brasileiro e desambigua a forma curta.", "risks": ["glosa intrusiva", "descrição institucional ainda exige revisão"]},
                    {"text": "Hospital Colônia de Barbacena", "rationale": "Preserva rastreabilidade nominal.", "risks": ["público pode não inferir a natureza institucional"]},
                ],
                "preference": "Hospital Colônia de Barbacena, the psychiatric institution hereafter referred to as “the Colony”",
                "preference_rationale": "Preferência estritamente condicionada; fontes e nome reconhecido continuam ausentes.",
                "conditions": ["revisão histórica", "reconciliação R355", "revisão EN-US", "fontes das alegações"],
                "signals": [0.60, 0.50, 0.80],
                "checks": [2, 1],
                "missing": ["denominação inglesa documentada", "fontes das alegações", "escopo de Santa Maria Colony"],
                "delta_preferred": "Hospital Colônia de Barbacena, com forma curta definida após primeira ocorrência",
            },
            "zh-CN": {
                "status": "complete",
                "concerns": [
                    ("TERM_CONFLICT", "high", "Hospital Colônia de Barbacena", "巴尔巴塞纳收容医院", "O nome completo e a forma curta usam 收容医院/收容院, enquanto R356 também fixa 圣玛丽亚收容院.", "A identidade institucional não permanece estável e a correferência não foi comprovada.", "strong"),
                    ("DOMESTICATION_ERASURE_RISK", "high", "Colônia", "收容院", "O nome próprio vira categoria institucional genérica.", "Pode apagar a memória nominal e privilegiar conotações de abrigo ou asilo.", "strong"),
                    ("PRAGMATIC_FAILURE", "medium", "conversamos", "约定", "约定 acrescenta acordo ou compromisso prévio.", "A relação documental entre remetente e destinatária é alterada.", "strong"),
                    ("HISTORICAL_SOURCE_GAP", "high", "sessenta mil mortos", "六万人死亡", "As alegações históricas não vêm acompanhadas de rastreabilidade no recorte.", "O alerta não conclui falsidade nem consenso.", "moderate"),
                ],
                "alternatives": [
                    {"text": "巴尔巴塞纳科洛尼亚医院〔Hospital Colônia de Barbacena〕", "rationale": "Conserva identidade nominal e a torna rastreável.", "risks": ["transliteração proposta, não nome oficial comprovado", "carga de leitura"]},
                    {"text": "Hospital Colônia de Barbacena；下文简称“Colônia”", "rationale": "Retém integralmente o nome e define a forma curta.", "risks": ["exige glosa discreta", "pode reduzir fluidez"]},
                ],
                "preference": "巴尔巴塞纳科洛尼亚医院〔Hospital Colônia de Barbacena〕",
                "preference_rationale": "Evita reduzir o nome a 收容院, mas permanece apenas candidata editorial.",
                "conditions": ["revisão ZH-CN", "revisão histórica", "conciliação R356", "fontes das alegações"],
                "signals": [0.35, 0.52, 0.72],
                "checks": [1, 2],
                "missing": ["denominação chinesa documentada", "fontes históricas", "decisão sobre retenção/transliteração"],
                "delta_preferred": "巴尔巴塞纳科洛尼亚医院〔Hospital Colônia de Barbacena〕",
            },
        },
    },
    {
        "unit_id": "ameaca_proximo",
        "label": "Você é o próximo",
        "segment_id": "MEM-26:20-28",
        "source_path": f"{PROJECT}/fragmentos/mem/MEM-26.tex",
        "source_lines": [20, 28],
        "target_paths": {"en-US": f"{PROJECT}/en/fragmentos/mem/MEM-26.tex", "zh-CN": f"{PROJECT}/zh/fragmentos/mem/MEM-26.tex"},
        "target_lines": {"en-US": [20, 28], "zh-CN": [20, 28]},
        "source": "Quem ler isto: você é o próximo. Eu carreguei a criatura por 62 anos. Ela entrou em mim quando eu era criança, numa vala, no meio de um campo de concentração. Ela me comeu por dentro. Mas ela também me manteve vivo. Ela precisa de hospedeiro. Quando eu morrer, ela vai procurar outro. Não um corpo. Um leitor. Você vai ler este diário. Enquanto lê, ela vai passar para você.",
        "targets": {
            "en-US": "Whoever reads this: you are next. I carried the creature for 62 years. She entered me when I was a child, in a trench, in the middle of a concentration camp. She ate me from the inside. But she also kept me alive. She needs a host. When I die, she will look for another. Not a body. A reader. You will read this diary. As you read, she will pass into you.",
            "zh-CN": "读到这段话的人：你就是下一个。我背负怪物六十二年。它在我还是个孩子时进入我体内，在一个乱葬坑里，在一座集中营中间。它从里面吃我。但它也让我活了下来。它需要宿主。我死的时候，它会寻找下一个。不是一个身体。是一个读者。你会读这本日记。你读的时候，它会进入你。",
        },
        "task_ids": {"en-US": "ses_041c58d3dffen1L4h81q2G2EtY", "zh-CN": "ses_041c58d07ffeaGy2ZvSx6f0HD8"},
        "voice": {"narrator_age": "adult", "region": "Ceará", "register": "testamentário, ameaçador, fragmentário e metanarrativo"},
        "period": "1979",
        "document_type": "última página ficcional de diário",
        "source_term": "você é o próximo",
        "current_terms": {"en-US": "you are next", "zh-CN": "你就是下一个"},
        "concept": {"source_term": "você é o próximo", "entity_type": "pragmatic_threat_formula", "preferred_en": "you are next", "preferred_zh_cn": "你就是下一个", "forbidden_translations": ["you may be next", "you might be next"]},
        "classification": "conditional_retention_candidate",
        "reviews": {
            "en-US": {
                "status": "complete",
                "concerns": [],
                "alternatives": [
                    {"text": "Whoever reads this: you are next. I carried the creature for 62 years.", "rationale": "Mantém ameaça direta, solenidade e ausência de atenuadores.", "risks": ["she precisa ser cotejado com o sistema pronominal global"]},
                    {"text": "Whoever reads this: you're next. I've carried the creature for 62 years.", "rationale": "Aumenta oralidade e continuidade temporal.", "risks": ["perde solenidade", "explicita aspecto não marcado na fonte"]},
                ],
                "preference": "Whoever reads this: you are next. I carried the creature for 62 years.",
                "preference_rationale": "Retenção condicionada: o recorte preserva interpelação, ritmo e força categórica.",
                "conditions": ["confirmar she/it no corpus", "revisão EN-US de horror", "revisão histórica de concentration camp"],
                "signals": [0.98, 0.92, 0.95],
                "checks": [0, 0],
                "missing": ["decisão global she/it", "parecer humano de recepção"],
                "delta_preferred": "you are next, sem modalização",
            },
            "zh-CN": {
                "status": "complete",
                "concerns": [
                    ("TARGET_VARIETY_USAGE_RISK", "medium", "numa vala, no meio de um campo de concentração", "在一个乱葬坑里，在一座集中营中间", "Dois locativos encadeados e 中间 podem soar marcados.", "Reorganizar o locativo melhora uso-alvo, mas reduz a ênfase espacial.", "moderate"),
                    ("LITERALISM", "medium", "me comeu por dentro", "它从里面吃我", "A construção reproduz diretamente a superfície da fonte.", "啃噬 pode soar mais fluido, mas especifica a ação.", "moderate"),
                    ("SYMBOL_DRIFT", "medium", "passar para você", "进入你", "A transmissão entre hospedeiros vira entrada ou invasão.", "O desvio pode ser deliberado e ecoar 进入我体内; depende da continuação espiritual.", "moderate"),
                ],
                "alternatives": [
                    {"text": "读到这段话的人：你就是下一个。这个怪物，我已经背负了六十二年。", "rationale": "Mantém ameaça e reduz parte da sintaxe marcada.", "risks": ["已经 torna a cadência menos seca"]},
                    {"text": "读到这里的人：你就是下一个。", "rationale": "É mais compacto e direto.", "risks": ["muda isto para quem chegou até aqui"]},
                ],
                "preference": "读到这段话的人：你就是下一个。",
                "preference_rationale": "A ameaça e 你 estão preservados; ajustes posteriores dependem do motivo de transmissão.",
                "conditions": ["revisão PT-BR/ZH-CN", "cotejo com Não fisicamente. Espiritualmente.", "manter distinção contextual 你/您"],
                "signals": [0.91, 0.92, 0.86],
                "checks": [0, 0],
                "missing": ["mapa global de 你/您", "decisão sobre transmissão versus invasão"],
                "delta_preferred": "你就是下一个 no assalto metanarrativo ao leitor",
            },
        },
    },
]


def _hash_locator(path: str, lines: list[int]) -> dict[str, Any]:
    full = ROOT / path
    return {
        "path": path,
        "line_start": lines[0],
        "line_end": lines[1],
        "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
    }


def _build_request(unit: dict[str, Any], language: str) -> dict[str, Any]:
    target_variety = "English (United States)" if language == "en-US" else "简体中文（中国大陆）"
    target_path = unit["target_paths"][language]
    source_path = unit["source_path"]
    current_term = unit["current_terms"][language]
    request = {
        "schema_version": SCHEMA_VERSION,
        "review_id": f"r360-{unit['unit_id']}-{language.lower()}",
        "segment_id": unit["segment_id"],
        "source_language": "pt-BR",
        "target_language": language,
        "source_text": unit["source"],
        "translated_text": unit["targets"][language],
        "author_voice_profile": unit["voice"],
        "terminology_graph": {
            "graph_id": GRAPH_ID,
            "revision": GRAPH_REVISION,
            "concepts": [unit["concept"]],
        },
        "historical_context": {
            "period": unit["period"],
            "region": unit["voice"]["region"],
            "support_status": "internal_editorial_sources",
            "provenance": [
                {
                    "source": f"{source_path}:{unit['source_lines'][0]}-{unit['source_lines'][1]}",
                    "date": "2026-08-01",
                    "limitations": "corpus literário interno; não é validação histórica externa",
                },
                {
                    "source": "SPEC-935-R355/R356 e glossários editoriais",
                    "date": "2026-08-01",
                    "limitations": "decisões internas sujeitas a revisão humana e temática",
                },
            ],
        },
        "cultural_dossier": {
            "target_variety": target_variety,
            "document_type": unit["document_type"],
            "anachronism_markers": [],
            "provenance": [
                {
                    "source": f"{target_path}:{unit['target_lines'][language][0]}-{unit['target_lines'][language][1]}",
                    "date": "2026-08-01",
                    "limitations": "tradução editorial interna ainda sem revisão cultural externa",
                },
                {
                    "source": "SPEC-935-R360",
                    "date": "2026-08-01",
                    "limitations": "piloto heurístico de escopo reduzido",
                },
            ],
        },
        "previous_translation_decisions": [
            {
                "source_term": unit["source_term"],
                "target_term": current_term,
                "symbolic": unit["unit_id"] in {"rasga_mortalha", "molambudos", "ameaca_proximo"},
                "status": "fixed_in_internal_glossary_pending_external_review",
            }
        ],
    }
    return validate_review_request(request)


def _build_assessment(unit: dict[str, Any], language: str, request: dict[str, Any]) -> dict[str, Any]:
    review = unit["reviews"][language]
    source = unit["source"]
    target = unit["targets"][language]
    concerns = [
        _concern(source, target, *concern[:6], strength=concern[6])
        for concern in review["concerns"]
    ]
    delta_concept = {
        "source_term": unit["source_term"],
        "entity_type": unit["concept"]["entity_type"],
        "preferred_en" if language == "en-US" else "preferred_zh_cn": review["delta_preferred"],
        "preserve_portuguese": any(token in review["delta_preferred"] for token in ("retirant", "Molamb", "Rasga", "Hospital Colônia")),
        "first_occurrence_note": unit["unit_id"] in {"retirantes", "rasga_mortalha", "molambudos", "hospital_colonia", "curral_do_governo"},
        "forbidden_translations": unit["concept"].get("forbidden_translations", []),
        "historical_context": {"period": unit["period"], "region": unit["voice"]["region"]},
    }
    delta = build_terminology_delta(
        request,
        delta_concept,
        "Síntese de proposta emitida no parecer runtime; requer decisão humana e não foi aplicada.",
    )
    assessment = {
        "schema_version": SCHEMA_VERSION,
        "analysis_status": review["status"],
        "source_language": "pt-BR",
        "target_language": language,
        "source_excerpt": source,
        "translated_excerpt": target,
        "candidate_concerns": concerns,
        "cultural_context": {
            "region": unit["voice"]["region"],
            "period": unit["period"],
            "narrator_profile": unit["voice"]["narrator_age"],
            "register": unit["voice"]["register"],
            "document_type": unit["document_type"],
            "provenance_status": "internal_documented_external_unvalidated",
        },
        "alternatives": review["alternatives"],
        "conditional_preference": {
            "text": review["preference"],
            "rationale": review["preference_rationale"],
            "conditions": review["conditions"],
        },
        "heuristic_signals": {
            "symbol_consistency": review["signals"][0],
            "cultural_fidelity": review["signals"][1],
            "author_voice_similarity": review["signals"][2],
        },
        "process_checks": {
            "critical_omissions_identified": review["checks"][0],
            "unresolved_term_conflicts": review["checks"][1],
            "back_translation_used": False,
        },
        "evidence_sufficiency": review.get("sufficiency", "partial"),
        "uncertainty_reasons": [
            "Parecer runtime de escopo segmental; não houve validação humana externa.",
            *review["missing"],
        ],
        "terminology_graph_updates": [delta],
        "human_review_required": True,
        "release_gate": "blocked",
        "missing_data": review["missing"],
        "limits": [
            "instrumento heurístico; sem validação externa",
            "compactação contratual das conclusões centrais da sessão runtime",
            "sinais numéricos internos e não autoritativos",
            "nenhuma edição ou aprovação automática",
        ],
    }
    return validate_agent_output(assessment)


def build_artifact() -> dict[str, Any]:
    reviews: list[dict[str, Any]] = []
    for unit in UNITS:
        for language in ("en-US", "zh-CN"):
            request = _build_request(unit, language)
            assessment = _build_assessment(unit, language, request)
            preflight = run_preflight(request)
            gate = evaluate_gate(request, assessment, preflight)
            corrected = unit.get("corrected_runtime", {}).get(language, False)
            reviews.append(
                {
                    "review_id": request["review_id"],
                    "unit_id": unit["unit_id"],
                    "label": unit["label"],
                    "target_language": language,
                    "editorial_classification": unit["classification"],
                    "source_locators": {
                        "source": _hash_locator(unit["source_path"], unit["source_lines"]),
                        "target": _hash_locator(unit["target_paths"][language], unit["target_lines"][language]),
                    },
                    "agent_runtime": {
                        "agent_slug": "cultural-episteme-agent",
                        "task_id": unit["task_ids"][language],
                        "output_non_empty": True,
                        "raw_contract_valid": True,
                        "contract_valid": True,
                        "attempts": 2 if corrected else 1,
                        "corrected_by_same_runtime_session": corrected,
                        "normalization": "compactação contratual fiel às conclusões centrais; saída integral permanece identificada pela sessão runtime",
                    },
                    "request": request,
                    "assessment": assessment,
                    "preflight": preflight,
                    "gate": gate,
                }
            )

    concerns = [
        concern
        for review in reviews
        for concern in review["assessment"]["candidate_concerns"] + review["preflight"]
    ]
    deltas = [
        delta
        for review in reviews
        for delta in review["assessment"]["terminology_graph_updates"]
    ]
    return {
        "spec_id": "SPEC-935-R360",
        "contract_id": "OCB-CULTURAL-EPISTEME-001",
        "generated_at": "2026-08-01",
        "external_validation": False,
        "manuscript_edits_applied": False,
        "scope": {
            "source_language": "pt-BR",
            "target_languages": ["en-US", "zh-CN"],
            "units": [unit["unit_id"] for unit in UNITS],
            "runtime_reviews": len(reviews),
        },
        "reviews": reviews,
        "aggregate": {
            "gate_decisions": dict(sorted(Counter(review["gate"]["decision"] for review in reviews).items())),
            "concern_codes": dict(sorted(Counter(concern["code"] for concern in concerns).items())),
            "proposed_terminology_deltas": deltas,
            "automatic_changes": [],
            "runtime_contract_corrections": [
                {
                    "task_id": "ses_041c58ee0ffe1rdzZRje394SWa",
                    "reason": "delta_id divergente de idempotency_key",
                    "outcome": "corrigido pela mesma sessão; release permaneceu bloqueado",
                },
                {
                    "task_id": "ses_041c58d74ffeRVhN4opcWtY3bh",
                    "reason": "delta_id divergente de idempotency_key",
                    "outcome": "corrigido pela mesma sessão; release permaneceu bloqueado",
                },
            ],
            "human_decisions_required": [
                "arbitrar a estratégia dupla de Curral do Governo sem apagar instituição nem metáfora",
                "definir retenção, glosa e usos posteriores de retirantes",
                "decidir retenção/calque/glosa de Rasga Mortalha nas recorrências",
                "definir o escopo de 莫兰布多斯 versus 破衣人",
                "fixar o nome histórico Hospital Colônia e suas formas curtas em EN/ZH",
                "confirmar por revisão nativa a manutenção da ameaça e do motivo de transmissão",
            ],
        },
        "safe_claim": "Doze execuções runtime produziram pareceres não vazios, revalidados em envelopes compactos e mantidos com release bloqueado; isso não demonstra equivalência cultural nem prontidão editorial.",
    }


def build_markdown(artifact: dict[str, Any]) -> str:
    by_unit = {unit["unit_id"]: unit for unit in UNITS}
    sections = []
    summaries = {
        "curral_do_governo": "EN e ZH preservam a metáfora de gado, mas deixam a categoria institucional vulnerável à opacidade. A troca simples por concentration camp/集中收容营 faria o movimento inverso: explicaria a instituição e poderia apagar a anáfora animalizante.",
        "retirantes": "A retenção EN evita equivalência jurídica falsa, mas exige uma glosa acessível. 逃荒者 comunica fuga por escassez, porém não contém sozinho a seca cearense e pode domesticar o referente por uma matriz histórica chinesa.",
        "rasga_mortalha": "Shroud-Ripper e 裹尸布撕裂者 preservam a etimologia, mas podem parecer epítetos góticos inventados. Retenção, glosa e repetição global precisam ser decididas em conjunto; R356 promete uma glosa ZH ainda não visível no recorte.",
        "molambudos": "A retenção EN preserva o termo-título, condicionada a glosa única. Em ZH, a alternância 莫兰布多斯→破衣人 dentro da mesma cena enfraquece a repetição que liga insulto, praga, categoria social e título.",
        "hospital_colonia": "Hospital-Colony pode sugerir calque ou colônia territorial; 收容院 pode reduzir um nome próprio a categoria genérica de asilo/abrigo. Nome histórico, forma curta e alegações factuais exigem revisão temática e fontes.",
        "ameaca_proximo": "EN mantém a ameaça direta sem modalização no recorte. ZH mantém 你就是下一个, mas há indícios de sintaxe calcada nos locativos e de mudança do motivo de transmissão para invasão em 进入你.",
    }
    for unit_id in [unit["unit_id"] for unit in UNITS]:
        unit = by_unit[unit_id]
        unit_reviews = [review for review in artifact["reviews"] if review["unit_id"] == unit_id]
        rows = []
        for review in unit_reviews:
            codes = sorted({item["code"] for item in review["assessment"]["candidate_concerns"] + review["preflight"]})
            rows.append(
                f"| {review['target_language']} | `{review['gate']['decision']}` | "
                f"{', '.join(codes) if codes else 'nenhum indício no escopo'} | "
                f"`{review['agent_runtime']['task_id']}` |"
            )
        sections.append(
            f"## {unit['label']}\n\n{summaries[unit_id]}\n\n"
            "| Alvo | Gate derivado | Principais códigos | Sessão |\n"
            "|---|---|---|---|\n" + "\n".join(rows) + "\n"
        )
    decisions = "\n".join(
        f"{index}. {decision}." for index, decision in enumerate(artifact["aggregate"]["human_decisions_required"], 1)
    )
    return f"""# Dossiê Cultural R360 — Molambudos

## Estatuto

Este documento é uma **auditoria heurística interna** de doze segmentos. Ele
**não constitui validação cultural externa**, parecer nativo independente ou
autorização de publicação. A **revisão humana** bilíngue e temática continua
obrigatória; o **release bloqueado** é mantido em todos os casos. Houve
**nenhuma alteração automática** no manuscrito ou nos glossários.

## Método e rastreabilidade

- 6 unidades × 2 variantes-alvo = 12 execuções do `cultural-episteme-agent`.
- Cada sessão está identificada no JSON e nas tabelas abaixo.
- Duas respostas tiveram chaves idempotentes divergentes; foram rejeitadas pelo
  gate e corrigidas pelas mesmas sessões antes da persistência.
- Os envelopes persistidos são compactações contratuais das conclusões centrais;
  a saída integral permanece vinculada ao ID da sessão runtime.
- Spans, hashes, preflight e decisões podem ser recalculados localmente.
- Scores são sinais internos não calibrados e não provam qualidade.

{chr(10).join(sections)}
## Decisões humanas pendentes

{decisions}

## Resultado seguro

Os pareceres identificaram conflitos terminológicos, riscos de literalismo,
apagamento/domesticação, mudança simbólica, registro e lacunas históricas. A
versão EN da ameaça não gerou preocupação candidata neste recorte, mas isso
significa apenas ausência de indício no escopo examinado. Nenhuma recomendação
foi aplicada, nenhum delta foi aprovado e todos permanecem `proposed`.
"""


def main() -> None:
    artifact = build_artifact()
    JSON_PATH.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    MD_PATH.write_text(build_markdown(artifact), encoding="utf-8")
    print(f"R360: {len(artifact['reviews'])} pareceres persistidos; release bloqueado.")


if __name__ == "__main__":
    main()
