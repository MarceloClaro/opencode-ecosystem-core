#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Triagem título/resumo da revisão de escopo — decisões de inclusão/exclusão (1 revisor, regras PRISMA-ScR).
Revisor: marceloclaro (documentar: 2º revisor pendente).
Cria: 06_triagem_corpus.tsv (incluídos) e 06_triagem_excluidos.tsv (amostra de exclusões com motivo).
"""
import csv

rows = list(csv.DictReader(open('scripts/05_busca_registros_triagem.tsv', encoding='utf-8'), delimiter='\t'))

# Índices incluídos (baseado em título + resumo):
include_idx = {
    9, 21, 53, 55, 69, 70, 86, 92, 93, 94, 98, 102, 104, 105, 106, 107, 110, 114,
    124, 135, 136, 141, 142, 143, 144, 145, 151, 156, 157, 158, 161, 170, 174, 182,
    183, 184, 189, 191, 194, 197, 205, 208, 210, 216, 221, 224,
}
# 219 é duplicata de 216; excluir como duplicata.

exclusion_reasons = {
    # amostra de exclusões ilustrativas para o fluxograma (motivos)
    0: ("conceito", "Enfermagem (fora do Direito)"),
    1: ("contexto", "Educação superior geral (Rússia) — não jurídica"),
    3: ("contexto", "Indústrias criativas — não jurídica"),
    8: ("conceito", "Educação médica — fora do Direito"),
    12: ("contexto", "Saúde — AI Act para hospitais"),
    14: ("conceito", "Educação médica — fora do Direito"),
    16: ("conceito", "Responsabilidade civil por IA — sem dimensão formativa"),
    18: ("conceito", "Formação de masters of laws sem IA"),
    20: ("idioma", "Texto em russo/cazaque — fora PT/EN/ES"),
    22: ("conceito", "Competência tele-comunicativa — geral"),
    23: ("conceito", "Componente prático em mestrados — sem IA"),
    24: ("idioma", "Texto em cazaque/russo — fora PT/EN/ES"),
    25: ("conceito", "Teoria do Direito no currículo — sem IA"),
    26: ("contexto", "Educação médica (integração legal) — população errada"),
    27: ("conceito", "Graduados tailandeses — IA no trabalho, não formação jurídica"),
    29: ("conceito", "Educação infantil — fora do Direito"),
    30: ("conceito", "Educação em saúde — fora do Direito"),
    37: ("conceito", "Ensino médio/educação geral"),
    39: ("conceito", "Remoção de artigo (engineering)"),
    42: ("conceito", "Ensino médio — educação estética"),
    53: ("conceito", "Ensino médio/fundamental — fora do Direito"),
    57: ("conceito", "IA na tomada de decisão judicial — sem formação"),
    58: ("conceito", "IA em operações judiciais — sem formação"),
    59: ("conceito", "Alucinações em LLMs judiciais — sem formação"),
    60: ("conceito", "IA no judiciário do Vietnã — sem formação"),
    61: ("conceito", "IA, Direito e bibliotecas jurídicas — sem formação"),
    62: ("conceito", "Gestão de registros legais — sem formação"),
    63: ("conceito", "Contratações públicas — sem formação"),
    64: ("conceito", "Responsabilidade civil — sem formação"),
    65: ("conceito", "Matemática — fora do Direito"),
    66: ("conceito", "EAD geral — fora do Direito"),
    72: ("conceito", "Prática jurídica com GenAI — sem dimensão formativa"),
    81: ("conceito", "Consentimento em saúde — sem formação jurídica"),
    84: ("conceito", "Inglês como língua estrangeira — fora do Direito"),
    88: ("contexto", "Percepções globais de ChatGPT — educação superior geral"),
    98: ("conceito", "Preparação da educação marítima chinesa — CONFERIR (incluída)"),
}

# Ajuste: 98 foi marcada para conferir — mantemos incluída (preparação da educação jurídica marítima).
exclusion_reasons.pop(98, None)

included, excluded = [], []
for i, r in enumerate(rows):
    if i in include_idx:
        included.append(r)
    else:
        reason = exclusion_reasons.get(i, ("triagem", "Não atende critérios de inclusão (ver protocolo)"))
        excluded.append({**r, "motivo": reason[1]})

def dump(path, recs):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=["fonte","doi","ano","periodico","titulo","resumo","autores","motivo"])
        w.writeheader()
        for r in recs:
            w.writerow(r)
    print(f"{len(recs)} registros em {path}")

dump('scripts/06_triagem_corpus.tsv', included)
dump('scripts/06_triagem_excluidos.tsv', excluded)

# Resumo do fluxo
from collections import Counter
print("\n=== Fluxo de triagem ===")
print("Identificados (após dedup):", len(rows))
print("Excluídos na triagem:", len(excluded))
print("Incluídos para extração:", len(included))
print("Motivos de exclusão:", dict(Counter(x["motivo"] for x in excluded)))
print("\n=== Corpus (por ano/idioma) ===")
for r in sorted(included, key=lambda x: -(int(x["ano"] or 0))):
    print(f"[{r['ano']}] ({r['fonte']}) {r['periodico'][:45]:47} | {r['titulo'][:105]}")