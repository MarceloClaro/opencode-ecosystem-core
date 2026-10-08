#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guarda de força de alegação — triagem HEURÍSTICA de overclaim.

Implementa o Contrato de Força de Alegação (research/claim_strength/CONTRACT.md,
adaptado de Yila-AI/awesome-research-skills com crédito): detecta marcadores de
alegação forte (causação, efeito, eficácia, quantificadores absolutos) sem
mitigador próximo (citação, hedge, limitação declarada) e os sinaliza para
revisão humana.

NÃO é detector de plágio, NÃO é prova científica e NÃO aprova manuscritos.
Saída "sem achados" significa apenas: nenhum marcador forte sem mitigador
foi encontrado por regex — a decisão final é sempre humana (banca/revisor).

Uso: python3 guard.py < arquivo.txt   |  auditar(texto) via import.
"""
from __future__ import annotations

import json
import re
import sys

# (nível, rótulo, padrões) — ordem: mais forte primeiro
NIVEIS = [
    (6, "causação/demonstração", [
        r"\bprova(m)?(\s+que)?\b", r"\bdemonstra(m)?(\s+que)?\b", r"\bcomprova\w*\b",
        r"\bcausa(m|ram)?\b", r"\bprovoca(m|ram)?\b", r"\bcura(m|ram)?\b",
        r"\bgarante(m)?\b", r"\bproves?\b", r"\bdemonstrates?\b", r"\bcauses?\b",
        r"\bcures?\b", r"\bguarantees?\b",
    ]),
    (5, "efeito/eficácia", [
        r"\bleva(m)?\s+a\b", r"\bresulta(m)?\s+em\b", r"\bproduz(em|iu|iram)?\b",
        r"\bgera(m|ram|do|da)?\b", r"\breduz(em|iu|iram)?\b", r"\baumenta(m|ram|ram)?\b",
        r"\bmelhoram\b", r"\bmelhorou\b", r"\bmelhorar\b", r"\bmelhorando\b",
        r"\bpiora(m|ram)?\b", r"\beficaz(es)?\b",
        r"\beficácia\b", r"\befetiv[oa]s?\b", r"\bleads?\s+to\b", r"\bresults?\s+in\b",
        r"\breduc(es?|ed|ing)?\b", r"\bimprov(es?|ed|ing)?\b", r"\bincreas(es?|ed)?\b",
        r"\beffective\b", r"\befficacy\b",
    ]),
    (4, "predição/contribuição causal", [
        r"\bprevê\b", r"\bpreveem\b", r"\bprediz(em)?\b", r"\bcontribui\b",
        r"\bcontribuem\b", r"\bcontribuiu\b", r"\bpredicts?\b",
    ]),
]

ABSOLUTOS = [
    r"\bsempre\b", r"\bnunca\b", r"\bjamais\b", r"\btodos?\s+os\b",
    r"\btodas?\s+as\b", r"\bnenhum(a)?\b", r"\balways\b", r"\bnever\b",
]

MITIGADORES = [
    r"\([^)]*20\d\d[^)]*\)", r"\\cite", r"sem valor probat[óo]rio",
    r"\blimita", r"n[ãa]o conclui", r"n[ãa]o afirma", r"n[ãa]o [ée] o caso",
    r"\bquase\b", r"financiamento", r"conflito de interesses", r"n[ãa]o elimina",
    r"coer[êe]ncia",
    r"\bapenas\b", r"sugere(m)?\b", r"\bpode(m)?\b", r"hip[óo]tese",
    r"plaus[íi]vel", r"agenda", r"explorat[óo]ri", r"coerente com",
    r"compat[íi]vel", r"associad", r"vinheta", r"ilustrati", r"estudo de caso",
    r"sem escala", r"sem dado", r"n[ãa]o declarado", r"coerente\b",
]

# Frequências temporais não são alegações universais ("todos os dias")
TEMPO_EXCECAO = r"\b(todos?\s+os|todas?\s+as|tod[oa])\s+(dias?|semanas?|vezes|manh[ãa]s|noites?)\b"

LIMIAR_SINALIZAR = 5  # níveis >= 5 sem mitigador geram achado


def _divide_frases(texto: str) -> list[str]:
    texto = re.sub(r"\s+", " ", texto).strip()
    partes = re.split(r"(?<=[.!?;])\s+(?=[A-ZÀ-Ú0-9\"“\(\[])", texto)
    return [p.strip() for p in partes if len(p.strip()) > 20]


def auditar(texto: str) -> dict:
    achados: list[dict] = []
    frases = _divide_frases(texto)
    for frase in frases:
        baixo = frase.lower()
        tem_mitigador = any(re.search(p, baixo) for p in MITIGADORES)
        for nivel, rotulo, padroes in NIVEIS:
            marc = next((p for p in padroes if re.search(p, baixo)), "")
            if marc and nivel >= LIMIAR_SINALIZAR and not tem_mitigador:
                achados.append({
                    "nivel": nivel,
                    "rotulo": rotulo,
                    "marcador": marc,
                    "frase": frase[:220],
                    "acao": "rebaixar na escada ou ancorar em evidência/limitação declarada",
                })
                break
        for pat in ABSOLUTOS:
            m = re.search(pat, baixo)
            if m and not tem_mitigador and not re.search(TEMPO_EXCECAO, baixo):
                achados.append({
                    "nivel": 6,
                    "rotulo": "quantificador absoluto",
                    "marcador": pat.strip("\\b"),
                    "frase": frase[:220],
                    "acao": "quantificar com número/fonte ou remover o absoluto",
                })
                break
    return {
        "ok": True,
        "frases_analisadas": len(frases),
        "achados": achados,
        "total": len(achados),
        "status": "sem achados" if not achados else "revisar",
        "nota_metodo": "Triagem heurística por regex; não prova ausência de overclaim. Decisão final é humana.",
    }


def main() -> int:
    texto = sys.stdin.read()
    if not texto.strip():
        print(json.dumps({"ok": False, "error": "Texto vazio."}, ensure_ascii=False))
        return 1
    print(json.dumps(auditar(texto), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
