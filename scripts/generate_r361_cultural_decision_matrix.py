#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a matriz decisória cultural da SPEC-935-R361.

Fontes foram lidas em 2026-08-01. O dossiê distingue evidência externa de
inferência editorial e nunca abre o release nem aplica decisões culturais.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "validacao_externa" / "cultural_episteme"
MATRIX_PATH = BASE / "molambudos_r361_decision_matrix.json"
DOSSIER_PATH = BASE / "molambudos_r361_decision_matrix.md"
SOURCES_PATH = BASE / "molambudos_r361_sources.json"
DRIFT_PATH = BASE / "molambudos_r361_provenance_drift.json"
VERIFICATION_PATH = BASE / "molambudos_r361_verification.json"
PROJECT = "projetos/molambudos/Molambudos_VictoriaRegia"


SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "S01-fapesp-seca-pt",
        "concept_ids": ["curral_do_governo", "retirantes"],
        "url": "https://revistapesquisa.fapesp.br/memorias-da-seca/",
        "title": "Memórias da seca",
        "author_or_institution": "Christina Queiroz / Pesquisa FAPESP",
        "published_at": "2020-03-20",
        "accessed_at": "2026-08-01",
        "source_type": "academic_outreach",
        "read_status": "full_page",
        "retrieval_method": "webfetch",
        "claim_supported": "Alagadiço, próximo a Fortaleza, foi criado na seca de 1915; Patu, em Senador Pompeu, funcionou em 1932–1933. Os casarões do Patu foram construídos a partir de 1919 e cedidos em 1932. A página também registra tombamento, Caminhada da Seca e práticas comunitárias de memória.",
        "limitations": "Reportagem de jornalismo científico baseada em especialistas e acervos; não é documento administrativo primário.",
    },
    {
        "source_id": "S02-ufmg-patu",
        "concept_ids": ["curral_do_governo"],
        "url": "https://periodicos.ufmg.br/index.php/vestigios/article/view/48169",
        "title": "O Campo de Concentração da Seca do Patu: memórias e percepções arqueológicas",
        "author_or_institution": "Danyel Douglas Miranda de Almeida; Maria do Amparo Alves de Carvalho / UFMG",
        "published_at": "2025-07-06",
        "accessed_at": "2026-08-01",
        "source_type": "peer_reviewed",
        "read_status": "abstract_page",
        "retrieval_method": "webfetch",
        "claim_supported": "O resumo situa o Campo do Patu em Senador Pompeu no ano de 1932 e o caracteriza por vigilância, controle e prisão dos sertanejos.",
        "limitations": "A página informa volume 18(1), de 2024, e publicação em 2025; o claim usado deriva do resumo, não de leitura integral do PDF.",
    },
    {
        "source_id": "S03-fapesp-seca-en",
        "concept_ids": ["curral_do_governo", "retirantes"],
        "url": "https://revistapesquisa.fapesp.br/en/memories-of-drought/",
        "title": "Memories of drought",
        "author_or_institution": "Christina Queiroz / Pesquisa FAPESP, edição inglesa",
        "published_at": "2020-01",
        "accessed_at": "2026-08-01",
        "source_type": "academic_outreach",
        "read_status": "full_page",
        "retrieval_method": "webfetch",
        "claim_supported": "A edição inglesa usa “concentration camp” e apresenta a primeira ocorrência como “retirantes (drought refugees)”; também distingue Alagadiço/1915 de Patu/1932–1933.",
        "limitations": "É tradução editorial de reportagem, não terminologia oficial universal nem prescrição literária.",
    },
    {
        "source_id": "S04-michaelis-retirante",
        "concept_ids": ["retirantes"],
        "url": "https://michaelis.uol.com.br/moderno-portugues/busca/portugues-brasileiro/retirante/",
        "title": "Retirante",
        "author_or_institution": "Dicionário Brasileiro da Língua Portuguesa Michaelis / Melhoramentos",
        "published_at": None,
        "accessed_at": "2026-08-01",
        "source_type": "dictionary",
        "read_status": "dictionary_entry",
        "retrieval_method": "webfetch",
        "claim_supported": "Define retirante, em uma acepção, como quem migra durante as grandes secas, acossado pela penúria, isoladamente ou em grupo.",
        "limitations": "Definição lexical; não detalha a história social nem prescreve equivalentes EN-US/ZH-CN.",
    },
    {
        "source_id": "S05-ufpr-retirantes",
        "concept_ids": ["retirantes"],
        "url": "https://revistas.ufpr.br/made/article/view/73031",
        "title": "Representações dos retirantes das secas do Semiárido nordestino",
        "author_or_institution": "José Gomes Ferreira; Anna Lidiane Oliveira Paiva; Anastácia Brandão de Mélo / UFPR",
        "published_at": "2020-12-17",
        "accessed_at": "2026-08-01",
        "source_type": "peer_reviewed",
        "read_status": "abstract_page",
        "retrieval_method": "webfetch",
        "claim_supported": "O resumo caracteriza retirante/flagelado da seca como emigrante sertanejo fragilizado, afetado pela estiagem e compelido a buscar sobrevivência nas cidades litorâneas.",
        "limitations": "Analisa representações sociais contemporaneamente; não estabelece equivalência jurídica nem tradução única.",
    },
    {
        "source_id": "S06-ufersa-suinadara",
        "concept_ids": ["rasga_mortalha"],
        "url": "https://ccbs.ufersa.edu.br/conhecendo-a-coruja-suindara/",
        "title": "Conhecendo as corujas suindara e buraqueira",
        "author_or_institution": "Centro de Ciências Biológicas e da Saúde / UFERSA",
        "published_at": "2022-05-09",
        "accessed_at": "2026-08-01",
        "source_type": "institutional",
        "read_status": "full_page",
        "retrieval_method": "webfetch",
        "claim_supported": "Tyto furcata também é chamada rasga-mortalha porque uma vocalização lembra tecido grosso sendo rasgado; a presença é associada por algumas pessoas a mau agouro e morte.",
        "limitations": "Divulgação institucional de zoologia; não é monografia folclórica e não sustenta a narrativa do bico libertando a alma.",
    },
    {
        "source_id": "S07-etnobiologia-rasga",
        "concept_ids": ["rasga_mortalha"],
        "url": "https://revistaetnobiologia.mx/index.php/etno/article/view/132",
        "title": "Aversão a espécies de aves por moradores da zona urbana e rural do município de Itabaiana, Sergipe, Brasil",
        "author_or_institution": "Cleverton da Silva; Tainara Lima da Silva; Benjamim Leonardo Alves White / Etnobiología",
        "published_at": "2017-09-04",
        "accessed_at": "2026-08-01",
        "source_type": "peer_reviewed",
        "read_status": "abstract_page",
        "retrieval_method": "webfetch",
        "claim_supported": "O resumo identifica rasga-mortalha como Tyto furcata e registra, entre entrevistados de Itabaiana, aversão justificada por aparência e prenúncio de morte.",
        "limitations": "Pesquisa regional de Sergipe; não generaliza toda a tradição brasileira nem confirma a etiologia do bico e da alma.",
    },
    {
        "source_id": "S08-aulete-molambudo",
        "concept_ids": ["molambudos"],
        "url": "https://www.aulete.com.br/molambudo",
        "title": "molambudo",
        "author_or_institution": "Dicionário Caldas Aulete / Lexikon",
        "published_at": None,
        "accessed_at": "2026-08-01",
        "source_type": "dictionary",
        "read_status": "dictionary_entry",
        "retrieval_method": "webfetch",
        "claim_supported": "Registra molambudo como brasileirismo adjetival: esfarrapado, equivalente a molambento, derivado de molambo.",
        "limitations": "Não comprova uso por soldados em 1915 nem a função ficcional específica da obra.",
    },
    {
        "source_id": "S09-michaelis-molambudo",
        "concept_ids": ["molambudos"],
        "url": "https://michaelis.uol.com.br/moderno-portugues/busca/portugues-brasileiro/molambudo/",
        "title": "Molambudo",
        "author_or_institution": "Dicionário Brasileiro da Língua Portuguesa Michaelis / Melhoramentos",
        "published_at": None,
        "accessed_at": "2026-08-01",
        "source_type": "dictionary",
        "read_status": "dictionary_entry",
        "retrieval_method": "webfetch",
        "claim_supported": "Registra molambudo, variante mulambudo, como derivado de molambo e remete a molambento.",
        "limitations": "Atesta o vocábulo, mas não data sua primeira ocorrência nem prescreve sua tradução literária.",
    },
    {
        "source_id": "S10-aulete-molambo",
        "concept_ids": ["molambudos"],
        "url": "https://www.aulete.com.br/molambo",
        "title": "molambo",
        "author_or_institution": "Dicionário Caldas Aulete / Lexikon",
        "published_at": None,
        "accessed_at": "2026-08-01",
        "source_type": "dictionary",
        "read_status": "dictionary_entry",
        "retrieval_method": "webfetch",
        "claim_supported": "Define molambo como pano/roupa velha, suja e rasgada e registra uso figurado para pessoa; indica origem no quimbundo mu'lambu.",
        "limitations": "Etimologia e acepções lexicais não determinam a carga pragmática de molambudos no romance.",
    },
    {
        "source_id": "S11-fhemig-chpb",
        "concept_ids": ["hospital_colonia"],
        "url": "https://fhemig.mg.gov.br/atendimento/complexo-hospitalar-de-barbacena/centro-hospitalar-psiquiatrico-de-barbacena/",
        "title": "Centro Hospitalar Psiquiátrico de Barbacena",
        "author_or_institution": "Fundação Hospitalar do Estado de Minas Gerais — FHEMIG",
        "published_at": None,
        "accessed_at": "2026-08-01",
        "source_type": "institutional",
        "read_status": "full_page",
        "retrieval_method": "webfetch",
        "claim_supported": "A instituição foi inaugurada em 1903, tornou-se “hospital colônia” em 1911, integrou a FHEMIG em 1977, foi reestruturada nos anos 1980 e continua como CHPB.",
        "limitations": "Autonarrativa institucional atual, potencialmente seletiva; não resolve sozinha abusos, estimativas de vítimas ou nomes de todos os períodos.",
    },
    {
        "source_id": "S12-puc-hospital-colonia",
        "concept_ids": ["hospital_colonia"],
        "url": "https://doi.org/10.5752/p.1678-9563.2017v23n3p952-974",
        "title": "Depois do Holocausto: efeitos colaterais do Hospital Colônia em Barbacena",
        "author_or_institution": "Fuad Kyrillos Neto; Christian Ingo Lenz Dunker / Psicologia em Revista",
        "published_at": "2017",
        "accessed_at": "2026-08-01",
        "source_type": "peer_reviewed",
        "read_status": "metadata_only",
        "retrieval_method": "webfetch",
        "claim_supported": "Os metadados confirmam uso acadêmico do nome Hospital Colônia em Barbacena e a existência de estudo sobre seus efeitos históricos.",
        "limitations": "A leitura direta retornou apenas metadados; nenhum detalhe factual do artigo é usado como evidência nesta matriz.",
    },
    {
        "source_id": "S13-tribuna-corpos-negociados",
        "concept_ids": ["hospital_colonia"],
        "url": "https://tribunademinas.com.br/noticias/cidade/22-11-2011/comercio-da-morte-so-parou-na-decada-de-80.html",
        "title": "Comércio da morte só parou na década de 80",
        "author_or_institution": "Daniela Arbex / Tribuna de Minas",
        "published_at": "2011-11-22",
        "accessed_at": "2026-08-01",
        "source_type": "journalistic_investigation",
        "read_status": "full_page",
        "retrieval_method": "webfetch",
        "claim_supported": "A reportagem afirma que 1.853 corpos foram negociados com faculdades em uma década; não os identifica como 1.853 corpos exumados. Também informa desativação da última cela em 1993.",
        "limitations": "Reportagem, não documento arquivístico primário; dados institucionais citados não vêm acompanhados de cotas ou metodologia integral.",
    },
    {
        "source_id": "S14-who-mental-disorders-stigma",
        "concept_ids": ["hospital_colonia"],
        "url": "https://www.who.int/news-room/fact-sheets/detail/mental-disorders",
        "title": "Mental disorders",
        "author_or_institution": "World Health Organization",
        "published_at": "2025-09-30",
        "accessed_at": "2026-08-01",
        "source_type": "institutional",
        "read_status": "full_page",
        "retrieval_method": "webfetch",
        "claim_supported": "A OMS registra que pessoas com transtornos mentais enfrentam estigma, discriminação e violações de direitos humanos.",
        "limitations": "Fonte geral de saúde mental; não avalia esta obra nem demonstra que uma passagem específica produza estigma em leitores.",
    },
]


SOURCE_META = {
    "S01-fapesp-seca-pt": ("G01-fapesp-memorias-seca", "source_fact", "abertura e seções sobre Alagadiço/1915, Patu/1932–1933, casarões de 1919, tombamento e Devoção popular/Caminhada da Seca", None, None),
    "S02-ufmg-patu": ("G02-ufmg-patu", "source_fact", "resumo: Campo do Patu em 1932, Senador Pompeu", None, None),
    "S03-fapesp-seca-en": ("G01-fapesp-memorias-seca", "target_usage", "primeiras ocorrências de concentration camp e retirantes (drought refugees)", "en-US", "retirantes (drought refugees); concentration camp"),
    "S04-michaelis-retirante": ("G03-michaelis-dictionary", "source_fact", "verbete retirante, acepção 2", None, None),
    "S05-ufpr-retirantes": ("G04-ufpr-retirantes", "source_fact", "resumo e palavras-chave", None, None),
    "S06-ufersa-suinadara": ("G05-ufersa-suindara", "source_fact", "parágrafos sobre rasga-mortalha, vocalização e mau agouro", None, None),
    "S07-etnobiologia-rasga": ("G06-etnobiologia-rasga", "source_fact", "resumo: Tyto furcata, aversão e prenúncio de morte", None, None),
    "S08-aulete-molambudo": ("G07-aulete-dictionary", "source_fact", "verbete molambudo", None, None),
    "S09-michaelis-molambudo": ("G03-michaelis-dictionary", "source_fact", "verbete molambudo", None, None),
    "S10-aulete-molambo": ("G07-aulete-dictionary", "source_fact", "verbete molambo, acepções 1–2 e etimologia", None, None),
    "S11-fhemig-chpb": ("G08-fhemig-chpb", "source_fact", "seção Histórico: 1903, 1911, 1977, anos 1980 e continuidade", None, None),
    "S12-puc-hospital-colonia": ("G09-puc-hospital-colonia", "metadata", "metadados DOI: título, autoria, periódico e ano", None, None),
    "S13-tribuna-corpos-negociados": ("G10-tribuna-daniela-arbex", "source_fact", "parágrafo: “Em uma década, 1.853 corpos foram negociados”; última cela em 1993", None, None),
    "S14-who-mental-disorders-stigma": ("G11-who-mental-health", "source_fact", "Key facts e parágrafo sobre estigma, discriminação e direitos humanos", None, None),
}

for _source in SOURCES:
    _group, _scope, _locator, _target_language, _target_form = SOURCE_META[_source["source_id"]]
    _source.update(
        {
            "independent_group_id": _group,
            "evidence_scope": _scope,
            "locator": _locator,
            "target_language": _target_language,
            "target_form": _target_form,
            "supports_target_equivalence": False,
            "independence_note": "Grupo usado para impedir dupla contagem de versões linguísticas ou verbetes da mesma obra editorial.",
        }
    )


def option(
    option_id: str,
    text: str,
    gains: list[str],
    losses: list[str],
    risks: list[str],
    evidence: list[str],
    claim_type: str = "translation_hypothesis",
) -> dict[str, Any]:
    return {
        "option_id": option_id,
        "text": text,
        "claim_type": claim_type,
        "assessment_claim_type": "editorial_inference",
        "gains": gains,
        "losses": losses,
        "risks": risks,
        "evidence_source_ids": evidence,
        "evidence_refs": [
            {
                "source_id": source_id,
                "support_scope": (
                    "target_usage_only"
                    if source_id == "S03-fapesp-seca-en"
                    else "referent_or_lexical_context_only"
                ),
            }
            for source_id in evidence
        ],
    }


DECISIONS: list[dict[str, Any]] = [
    {
        "decision_id": "D01-curral-en",
        "concept_id": "curral_do_governo",
        "target_language": "en-US",
        "current_form": "Government Pen",
        "status": "pending_human",
        "options": [
            option("A", "Government Pen, with one contextual classification as a concentration camp", ["preserva curral–gado e a voz infantil"], ["instituição segue parcialmente opaca"], ["maiúsculas podem simular nome oficial"], ["S01-fapesp-seca-pt", "S02-ufmg-patu", "S03-fapesp-seca-en"]),
            option("B", "Alagadiço/Patu concentration camp", ["espera-se explicitar a categoria histórica"], ["apaga a repetição animalizante"], ["exige resolver primeiro 1915 versus 1932"], ["S01-fapesp-seca-pt", "S02-ufmg-patu", "S03-fapesp-seca-en"]),
            option("C", "curral do governo, with a first-use gloss", ["espera-se favorecer a rastreabilidade cultural"], ["maior carga explicativa"], ["estrangeirização e excesso de paratexto"], ["S01-fapesp-seca-pt", "S03-fapesp-seca-en"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["resolver o bloqueio Patu/1915", "revisão histórica do Ceará", "revisão literária EN-US"]},
        "human_question": "Escolher A, B ou C após decidir a cronologia e a geografia do campo.",
    },
    {
        "decision_id": "D02-curral-zh",
        "concept_id": "curral_do_governo",
        "target_language": "zh-CN",
        "current_form": "政府牲畜圈",
        "status": "pending_human",
        "options": [
            option("A", "“政府牲畜圈”，首现附“旱灾集中营”说明", ["conserva metáfora pecuária"], ["expressão longa e marcada"], ["pode parecer nome oficial literal"], ["S01-fapesp-seca-pt", "S02-ufmg-patu"]),
            option("B", "阿拉加迪索集中营或帕图集中营；牲畜圈仅保留在隐喻中", ["separa instituição e animalização"], ["reduz repetição lexical"], ["depende da escolha 1915/1932 e de revisor nativo"], ["S01-fapesp-seca-pt", "S02-ufmg-patu"]),
        ],
        "conditional_preference": {"option_id": "B", "status": "conditional", "conditions": ["resolver Patu/1915", "confirmar transliterações", "revisão ZH-CN"]},
        "human_question": "Escolher A (repetição literal) ou B (separação entre nome institucional e metáfora).",
    },
    {
        "decision_id": "D03-retirantes-en",
        "concept_id": "retirantes",
        "target_language": "en-US",
        "current_form": "retirante(s)",
        "status": "pending_human",
        "options": [
            option("A", "retirantes (drought refugees), once; retirantes thereafter", ["preserva categoria regional e segue uso editorial publicado"], ["opacidade inicial"], ["refugees não deve ser lido como estatuto jurídico automático"], ["S03-fapesp-seca-en", "S04-michaelis-retirante", "S05-ufpr-retirantes"]),
            option("B", "drought-displaced people/families", ["espera-se facilitar a compreensão sem pressupor fronteira"], ["apaga a categoria histórica"], ["registro humanitário contemporâneo"], ["S04-michaelis-retirante", "S05-ufpr-retirantes"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["glosa acessível em todas as rotas", "sem itálico reiterado", "revisão EN-US"]},
        "human_question": "Escolher A (reter o brasileirismo) ou B (descrição integral em inglês).",
    },
    {
        "decision_id": "D04-retirantes-zh",
        "concept_id": "retirantes",
        "target_language": "zh-CN",
        "current_form": "逃荒者",
        "status": "pending_human",
        "options": [
            option("A", "逃荒者，首现说明为塞阿拉旱灾中的被迫迁徙者", ["conciso e ligado a fome/escassez"], ["não lexicaliza Ceará"], ["domesticação por repertório histórico chinês"], ["S04-michaelis-retirante", "S05-ufpr-retirantes"]),
            option("B", "因旱灾流离失所者", ["explicita causa e deslocamento"], ["perde nominalidade regional e oralidade"], ["tom burocrático contemporâneo"], ["S04-michaelis-retirante", "S05-ufpr-retirantes"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["glosa única", "revisão de falante ZH-CN", "não converter em categoria jurídica"]},
        "human_question": "Escolher A (manter 逃荒者) ou B (explicitar sempre deslocamento pela seca).",
    },
    {
        "decision_id": "D05-rasga-en",
        "concept_id": "rasga_mortalha",
        "target_language": "en-US",
        "current_form": "Shroud-Ripper",
        "status": "pending_human",
        "options": [
            option("A", "Rasga-Mortalha", ["preserva o nome popular brasileiro e a recorrência"], ["significado inicialmente opaco"], ["estrangeirização sem mediação"], ["S06-ufersa-suinadara", "S07-etnobiologia-rasga"]),
            option("B", "Shroud-Ripper / the shroud-ripper owl", ["espera-se tornar a etimologia mais legível"], ["apaga a forma cultural"], ["pode parecer criatura gótica inventada"], ["S06-ufersa-suinadara", "S07-etnobiologia-rasga"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["a cena continua explicando coruja e agouro", "cotejo de todas as recorrências", "revisão EN-US"]},
        "human_question": "Escolher A (Rasga-Mortalha) ou B (Shroud-Ripper).",
    },
    {
        "decision_id": "D06-rasga-zh",
        "concept_id": "rasga_mortalha",
        "target_language": "zh-CN",
        "current_form": "裹尸布撕裂者",
        "status": "pending_human",
        "options": [
            option("A", "裹尸布撕裂者（报丧猫头鹰），仅首现加注", ["conserva etimologia e esclarece ave/agouro"], ["primeira ocorrência pesada"], ["pode soar como entidade fantástica"], ["S06-ufersa-suinadara", "S07-etnobiologia-rasga"]),
            option("B", "Rasga-Mortalha 的音译并加释义", ["preserva identidade brasileira"], ["baixa transparência e extensão"], ["transliteração ainda não validada"], ["S06-ufersa-suinadara", "S07-etnobiologia-rasga"]),
            option("C", "报丧猫头鹰", ["espera-se explicitar a função de agouro"], ["elimina a mortalha rasgada"], ["domesticação excessiva"], ["S06-ufersa-suinadara", "S07-etnobiologia-rasga"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["glosa uma única vez", "repetição consistente", "revisão ZH-CN e folclórica"]},
        "human_question": "Escolher A (calque com glosa), B (retenção/transliteração) ou C (nome funcional).",
    },
    {
        "decision_id": "D07-molambudos-en",
        "concept_id": "molambudos",
        "target_language": "en-US",
        "current_form": "molambudo(s)",
        "status": "pending_human",
        "options": [
            option("A", "molambudos—rag-clad people, once; molambudos thereafter", ["mantém título, insulto e recorrência"], ["glosa não reproduz toda a carga"], ["pode parecer equivalência total"], ["S08-aulete-molambudo", "S09-michaelis-molambudo", "S10-aulete-molambo"]),
            option("B", "the ragged ones", ["espera-se facilitar a compreensão e o tom depreciativo"], ["perde raiz e elo com o título"], ["reduz categoria imposta a descrição visual"], ["S08-aulete-molambudo", "S10-aulete-molambo"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["não alegar invenção absoluta do vocábulo", "glosa única", "revisão EN-US"]},
        "human_question": "Escolher A (preservar molambudos) ou B (traduzir todas as ocorrências).",
    },
    {
        "decision_id": "D08-molambudos-zh",
        "concept_id": "molambudos",
        "target_language": "zh-CN",
        "current_form": "莫兰布多斯 / 破衣人",
        "status": "pending_human",
        "options": [
            option("A", "莫兰布多斯 nas recorrências centrais; 破衣人 somente como glosa", ["mantém cadeia insulto–praga–categoria–título"], ["transliteração opaca"], ["pode parecer etnônimo"], ["S08-aulete-molambudo", "S09-michaelis-molambudo", "S10-aulete-molambo"]),
            option("B", "破衣人 em todas as ocorrências", ["insulto visual transparente"], ["perde neologização e identidade do título"], ["redução a roupa rasgada"], ["S08-aulete-molambudo", "S10-aulete-molambo"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["revisor ZH-CN confirma força pragmática", "glosa acessível", "cotejo de rotas"]},
        "human_question": "Escolher A (莫兰布多斯 central) ou B (破衣人 em todas as ocorrências).",
    },
    {
        "decision_id": "D09-hospital-en",
        "concept_id": "hospital_colonia",
        "target_language": "en-US",
        "current_form": "Hospital-Colony of Barbacena / the Colony",
        "status": "pending_human",
        "options": [
            option("A", "Hospital Colônia de Barbacena; historical psychiatric institution on first use", ["preserva nome e rastreabilidade"], ["exige mediação inicial"], ["maior presença do português"], ["S11-fhemig-chpb", "S12-puc-hospital-colonia"]),
            option("B", "Barbacena psychiatric hospital (Hospital Colônia de Barbacena)", ["espera-se explicitar a natureza institucional"], ["nome próprio perde primeiro plano"], ["pode confundir instituição histórica e CHPB atual"], ["S11-fhemig-chpb", "S12-puc-hospital-colonia"]),
            option("C", "Hospital-Colony of Barbacena", ["reproduz componentes do nome"], ["soa como calque"], ["sugere hospital de colônia territorial; uso oficial não localizado"], ["S11-fhemig-chpb", "S12-puc-hospital-colonia"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["resolver o claim de fechamento em 1980", "distinguir período histórico do CHPB atual", "revisão EN-US"]},
        "human_question": "Escolher A (nome português), B (descrição inglesa) ou C (calque atual).",
    },
    {
        "decision_id": "D10-hospital-zh",
        "concept_id": "hospital_colonia",
        "target_language": "zh-CN",
        "current_form": "巴尔巴塞纳收容医院 / 收容院",
        "status": "pending_human",
        "options": [
            option("A", "巴尔巴塞纳科洛尼亚医院〔Hospital Colônia de Barbacena〕", ["preserva identidade e rastreabilidade"], ["expressão longa"], ["科洛尼亚 é proposta, não nome oficial chinês comprovado"], ["S11-fhemig-chpb", "S12-puc-hospital-colonia"]),
            option("B", "巴尔巴塞纳精神病院（历史上的 Hospital Colônia de Barbacena）", ["espera-se explicitar a função psiquiátrica"], ["reduz especificidade de Colônia"], ["pode confundir períodos institucionais"], ["S11-fhemig-chpb", "S12-puc-hospital-colonia"]),
            option("C", "收容院", ["conciso"], ["transforma nome próprio em categoria genérica"], ["conotações de abrigo/asilo não equivalentes"], ["S11-fhemig-chpb", "S12-puc-hospital-colonia"]),
        ],
        "conditional_preference": {"option_id": "A", "status": "conditional", "conditions": ["revisor ZH-CN valida transliteração", "resolver fechamento/continuidade", "distinguir referência histórica e atual"]},
        "human_question": "Escolher A (nome rastreável), B (descrição funcional) ou C (forma genérica atual).",
    },
]

for _decision in DECISIONS:
    _decision["target_equivalence_evidence"] = "none"
    _decision["conditional_preference"]["claim_type"] = "editorial_inference"


BLOCKERS = [
    {
        "blocker_id": "patu_1915_chronology",
        "status": "blocked_author_decision",
        "claim_type": "documented_fact_conflict",
        "documented_conflict": "Fontes lidas situam Alagadiço/Fortaleza em 1915 e Patu/Senador Pompeu em 1932–1933; o corpus situa Senador Pompeu/Patu em 1915–1917.",
        "source_ids": ["S01-fapesp-seca-pt", "S02-ufmg-patu", "S03-fapesp-seca-en"],
        "evidence_basis": ["external_source_fact", "internal_corpus_comparison"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/luc/LUC-10.tex:27",
            f"{PROJECT}/fragmentos/doc/DOC-02.tex:21",
            f"{PROJECT}/fragmentos/doc/DOC-05.tex:28",
            f"{PROJECT}/fragmentos/doc/DOC-08.tex:33",
            f"{PROJECT}/fragmentos/doc/DOC-18.tex:8-44",
            f"{PROJECT}/fragmentos/mem/MEM-02.tex:8-10",
            f"{PROJECT}/fragmentos/mem/MEM-06.tex:100",
            f"{PROJECT}/zh/frontmatter/glossario_historico.tex:22",
            "homólogos EN-US/ZH-CN dos fragmentos acima",
        ],
        "author_options": [
            "Manter 1915 e transferir o campo para Alagadiço/Fortaleza, revisando geografia e números.",
            "Manter Senador Pompeu/Patu e deslocar a cronologia para 1932–1933, recalculando toda a linha de vida de Joaquim.",
            "Assumir história alternativa explicitamente e retirar alegações de corroboração factual específica.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "hospital_closed_1980",
        "status": "blocked_author_decision",
        "claim_type": "documented_fact_conflict",
        "documented_conflict": "O corpus afirma fechamento em 1980; a FHEMIG registra reestruturação nos anos 1980, desospitalização posterior e continuidade como CHPB.",
        "source_ids": ["S11-fhemig-chpb", "S13-tribuna-corpos-negociados"],
        "evidence_basis": ["external_source_fact", "internal_corpus_comparison"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/luc/LUC-03.tex:14",
            f"{PROJECT}/fragmentos/doc/DOC-25.tex:68",
            f"{PROJECT}/en/fragmentos/luc/LUC-03.tex:14",
            f"{PROJECT}/en/fragmentos/doc/DOC-25.tex:67",
            f"{PROJECT}/zh/fragmentos/luc/LUC-03.tex:14",
            f"{PROJECT}/zh/fragmentos/doc/DOC-25.tex:70",
        ],
        "author_options": [
            "Substituir fechamento por reestruturação/desospitalização historicamente delimitada após pesquisa adicional.",
            "Remover a data e manter apenas que o modelo manicomial foi transformado.",
            "Assumir fechamento ficcional e marcar explicitamente a divergência da instituição histórica.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "rasga_mortalha_beak_etiology",
        "status": "blocked_author_decision",
        "claim_type": "limited_source_support_gap",
        "documented_conflict": "Fontes sustentam nome, som semelhante a tecido rasgado e prenúncio de morte; não sustentam, no material lido, a narrativa do bico rasgando a mortalha para libertar a alma.",
        "source_ids": ["S06-ufersa-suinadara", "S07-etnobiologia-rasga"],
        "evidence_basis": ["limited_external_source_set", "internal_corpus_comparison"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/mem/MEM-12.tex:50",
            f"{PROJECT}/en/fragmentos/mem/MEM-12.tex:50",
            f"{PROJECT}/zh/fragmentos/mem/MEM-12.tex:50",
        ],
        "author_options": [
            "Manter como crença específica de Seu Nonô ou variante ficcional, sem alegar etimologia externa comprovada.",
            "Pesquisar documentação folclórica regional adicional antes de apresentar como tradição.",
            "Reduzir a explicação ao som de tecido rasgado e ao agouro, mediante decisão autoral.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "molambudo_absolute_neologism",
        "status": "blocked_author_decision",
        "claim_type": "lexical_attestation_scope_uncertainty",
        "documented_conflict": "Dicionários atuais atestam molambudo/mulambudo como derivado de molambo; isso torna a invenção absoluta não demonstrada, mas não data a primeira ocorrência nem comprova o uso por soldados em 1915.",
        "source_ids": ["S08-aulete-molambudo", "S09-michaelis-molambudo", "S10-aulete-molambo"],
        "evidence_basis": ["current_lexicographic_attestation", "internal_corpus_comparison"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/doc/DOC-07.tex:20",
            f"{PROJECT}/en/fragmentos/doc/DOC-07.tex:20",
            f"{PROJECT}/zh/fragmentos/doc/DOC-07.tex:20",
            f"{PROJECT}/en/TRADUTOR_NOTES.md:9",
            f"{PROJECT}/fragmentos/mem/MEM-06.tex:22",
            f"{PROJECT}/frontmatter/glossario_historico.tex:23",
        ],
        "author_options": [
            "Manter neologismo como diagnóstico ficcional do uso existencial idiossincrático.",
            "Trocar a descrição paratextual por ressignificação lexical ou uso idiossincrático, após decisão autoral.",
            "Explicitar que o vocábulo é atestado e que a obra inova na função narrativa.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "victim_count_category_drift",
        "status": "blocked_author_decision",
        "claim_type": "documented_category_conflict_and_source_gap",
        "documented_conflict": "O corpus alterna 60 mil mortos, internados, corpos enterrados, desaparecidos e 1.853 exumados. A fonte S13 sustenta 1.853 corpos negociados com faculdades, não 1.853 exumações.",
        "source_ids": ["S11-fhemig-chpb", "S13-tribuna-corpos-negociados"],
        "evidence_basis": ["external_source_fact", "internal_claim_inventory"],
        "affected_occurrences": [
            f"{PROJECT}/frontmatter/nota_arquivista.tex:41",
            f"{PROJECT}/frontmatter/nota_ao_leitor.tex:12",
            f"{PROJECT}/fragmentos/luc/LUC-01.tex:29",
            f"{PROJECT}/fragmentos/luc/LUC-04.tex:87",
            f"{PROJECT}/fragmentos/doc/DOC-19.tex:8-25",
            f"{PROJECT}/fragmentos/doc/DOC-18.tex:8,22-32",
            "homólogos EN-US/ZH-CN e paratextos TRI",
        ],
        "author_options": [
            "Auditar cada número por categoria, período, fonte e grau de incerteza antes de qualquer reescrita.",
            "Atribuir estimativas à fonte e remover conversões entre mortos, corpos, exumados e vendidos.",
            "Suspender todos os números não sustentados até revisão histórica e arquivística independente.",
        ],
        "automatic_change_applied": False,
        "publication_reach_audit_required": True,
    },
    {
        "blocker_id": "pseudoarchive_authenticity",
        "status": "blocked_author_decision",
        "claim_type": "ethical_authenticity_risk",
        "documented_conflict": "Documentos ficcionais se apresentam como peças do Arquivo Público do Ceará, Arquivo Nacional, Arquivo Público Mineiro e transcrição autorizada, sem proveniência ou permissão demonstrada no pacote R361.",
        "source_ids": [],
        "evidence_basis": ["internal_corpus_and_paratext_analysis"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/doc/DOC-17.tex:8-27",
            f"{PROJECT}/fragmentos/doc/DOC-18.tex:8-44",
            f"{PROJECT}/fragmentos/doc/DOC-19.tex:8-25",
            "homólogos EN-US/ZH-CN e referências ao Arquivo Público Mineiro",
        ],
        "author_options": [
            "Marcar cada pseudoarquivo inequivocamente como construção ficcional.",
            "Comprovar citações, permissões, proveniência e estatuto de reprodução antes de manter nomes reais.",
            "Substituir instituições reais por arquivo ficcional claramente declarado.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "fictional_victim_insertion",
        "status": "blocked_author_decision",
        "claim_type": "ethical_memory_boundary_risk",
        "documented_conflict": "Joaquim é declarado personagem ficcional, mas DOC-19 o chama de um dos 60 mil e notas tratam seu testemunho como corroboração de fatos históricos.",
        "source_ids": ["S13-tribuna-corpos-negociados"],
        "evidence_basis": ["internal_fiction_reality_boundary_analysis"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/doc/DOC-19.tex:19-25",
            f"{PROJECT}/fragmentos/mem/MEM-06.tex:96",
            f"{PROJECT}/fragmentos/mem/MEM-07.tex:80",
            "homólogos EN-US/ZH-CN",
        ],
        "author_options": [
            "Separar explicitamente o personagem de qualquer contagem de vítimas reais.",
            "Remover linguagem de corroboração testemunhal atribuída ao personagem ficcional.",
            "Submeter a estratégia memorial a revisão de sobreviventes, familiares e especialistas em ética do testemunho.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "living_memory_erasure",
        "status": "blocked_author_decision",
        "claim_type": "documented_fact_conflict_and_memory_risk",
        "documented_conflict": "O corpus descreve Patu como desaparecido/esquecido e o Hospital como ruína fechada; S01 registra ruínas tombadas, romaria e memória comunitária, enquanto S11/S13 registram continuidade, museu, reforma e última cela até 1993.",
        "source_ids": ["S01-fapesp-seca-pt", "S11-fhemig-chpb", "S13-tribuna-corpos-negociados"],
        "evidence_basis": ["external_source_fact", "internal_corpus_comparison"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/doc/DOC-15.tex:19-31",
            f"{PROJECT}/fragmentos/luc/LUC-03.tex:14-16",
            "homólogos EN-US/ZH-CN e paratextos históricos",
        ],
        "author_options": [
            "Reconhecer práticas vivas de memória e distinguir abandono parcial de apagamento total.",
            "Reescrever apenas após consulta a comunidades de memória de Patu e Barbacena.",
            "Assumir cenário alternativo ficcional sem reivindicar descrição factual contemporânea.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "psychiatric_stigma_horror",
        "status": "blocked_author_decision",
        "claim_type": "ethical_representation_risk",
        "documented_conflict": "A combinação entre diagnóstico, violência, possessão e contágio pode reforçar estigma; S14 documenta a existência geral de estigma e violações, mas não mede o efeito desta obra.",
        "source_ids": ["S14-who-mental-disorders-stigma"],
        "evidence_basis": ["external_general_context", "internal_representation_analysis"],
        "affected_occurrences": [
            f"{PROJECT}/fragmentos/doc/DOC-07.tex:18-51",
            f"{PROJECT}/fragmentos/doc/DOC-08.tex:26-113",
            "arquitetura paciente–criatura–contaminação em PT/EN/ZH",
        ],
        "author_options": [
            "Submeter a obra a leitura de sensibilidade em saúde mental e movimento antimanicomial.",
            "Separar explicitamente transtorno psíquico, violência e mecanismo sobrenatural.",
            "Reavaliar a arquitetura de contágio sem instrumentalizar pacientes reais ou ficcionais.",
        ],
        "automatic_change_applied": False,
    },
    {
        "blocker_id": "reader_consent_visual_provenance",
        "status": "blocked_author_decision",
        "claim_type": "ethical_consent_and_provenance_gap",
        "documented_conflict": "O pacote R361 não demonstra cobertura integral dos avisos para violência sexual, consumo de cadáveres e ameaça, nem proveniência, direitos e marcação ficcional inequívoca de todas as imagens pseudoarquivísticas.",
        "source_ids": [],
        "evidence_basis": ["internal_content_warning_and_visual_asset_audit_gap"],
        "affected_occurrences": [
            f"{PROJECT}/frontmatter/aviso_ao_leitor.tex",
            f"{PROJECT}/frontmatter/copyrightpage.tex:28-39",
            f"{PROJECT}/figures/",
            "homólogos EN-US/ZH-CN/TRI",
        ],
        "author_options": [
            "Auditar avisos de conteúdo por idioma e por rota antes de publicação.",
            "Criar ledger visual com origem, licença, consentimento e estatuto ficcional de cada imagem.",
            "Remover ativos e chamadas promocionais sem proveniência ou adequação ética demonstrada.",
        ],
        "automatic_change_applied": False,
    },
]


MECHANICAL_CHANGES = [
    {
        "change_class": "restore_metric_unit",
        "path": f"{PROJECT}/en/fragmentos/mem/MEM-06.tex",
        "before": "about two hundred yards wide and perhaps three hundred long",
        "after": "about two hundred meters wide and perhaps three hundred meters long",
        "rationale": "A fonte usa metros; os mesmos números não podiam ser rotulados como jardas.",
        "risk_level": "low",
        "applied": True,
    },
    {
        "change_class": "repair_english_duration_grammar",
        "path": f"{PROJECT}/en/fragmentos/doc/DOC-17.tex",
        "before": "People who walked days without food or water",
        "after": "People who walked for days without food or water",
        "rationale": "Correção gramatical sem alteração cultural ou factual.",
        "risk_level": "low",
        "applied": True,
    },
    {
        "change_class": "restore_barbed_wire_semantics",
        "path": f"{PROJECT}/zh/fragmentos/mem/MEM-06.tex",
        "before": "用铁丝网围起来的区域",
        "after": "用带刺铁丝网围起来的区域",
        "rationale": "带刺 restaura o traço material explícito de arame farpado.",
        "risk_level": "low",
        "applied": True,
    },
]


PROTECTED = [
    {"term": "Government Pen", "language": "en-US", "changed": False},
    {"term": "政府牲畜圈", "language": "zh-CN", "changed": False},
    {"term": "retirantes", "language": "en-US", "changed": False},
    {"term": "逃荒者", "language": "zh-CN", "changed": False},
    {"term": "Shroud-Ripper", "language": "en-US", "changed": False},
    {"term": "裹尸布撕裂者", "language": "zh-CN", "changed": False},
    {"term": "molambudos", "language": "en-US", "changed": False},
    {"term": "莫兰布多斯 / 破衣人", "language": "zh-CN", "changed": False},
    {"term": "Hospital-Colony / the Colony", "language": "en-US", "changed": False},
    {"term": "收容医院 / 收容院", "language": "zh-CN", "changed": False},
]


DRIFT_RECORDS: list[dict[str, Any]] = [
    {
        "path": f"{PROJECT}/en/fragmentos/mem/MEM-06.tex",
        "change_class": "restore_metric_unit",
        "old_sha256": "722edb54755e119d4325e3cdb46a5ffd6598ab5a66328875f6f7b804f7d93fba",
        "new_sha256": "84eaa695aad062b6ab03e1511a2fb1cd5afa50f5eef63993dafa35fc363069a2",
        "before": "two hundred yards wide and perhaps three hundred long",
        "after": "two hundred meters wide and perhaps three hundred meters long",
        "cultural_terms_changed": False,
        "snapshot_preserved": True,
        "affected_reviews": [
            {
                "review_id": "r360-curral_do_governo-en-us",
                "locator_role": "target",
                "reviewed_segment_changed": True,
                "status": "mechanical_segment_rechecked",
                "recheck_scope": "unidade métrica apenas; parecer cultural permanece snapshot R360",
            },
            {
                "review_id": "r360-molambudos-en-us",
                "locator_role": "target",
                "reviewed_segment_changed": False,
                "status": "snapshot_segment_unchanged",
                "recheck_scope": "hash integral mudou em linha anterior; trecho molambudos não mudou",
            },
        ],
    },
    {
        "path": f"{PROJECT}/zh/fragmentos/mem/MEM-06.tex",
        "change_class": "restore_barbed_wire_semantics",
        "old_sha256": "13f42d7e0e4aa6c48545281bb5fa3706bdc24e25a1247b16db8ad55acfdb0948",
        "new_sha256": "3d1e65f5dd335e8d4379df2fc2fc99c2ef0f2fbac2f2de8dc018f2d7cec0db86",
        "before": "用铁丝网围起来的区域",
        "after": "用带刺铁丝网围起来的区域",
        "cultural_terms_changed": False,
        "snapshot_preserved": True,
        "affected_reviews": [
            {
                "review_id": "r360-curral_do_governo-zh-cn",
                "locator_role": "target",
                "reviewed_segment_changed": True,
                "status": "mechanical_segment_rechecked",
                "recheck_scope": "materialidade da farpa apenas; termo 政府牲畜圈 preservado",
            },
            {
                "review_id": "r360-molambudos-zh-cn",
                "locator_role": "target",
                "reviewed_segment_changed": False,
                "status": "snapshot_segment_unchanged",
                "recheck_scope": "hash integral mudou em linha anterior; trecho molambudos não mudou",
            },
        ],
    },
    {
        "path": f"{PROJECT}/en/fragmentos/doc/DOC-17.tex",
        "change_class": "repair_english_duration_grammar",
        "old_sha256": "c5d59f538dcda2f08790e62be215980d56eff5e34b83673ab191dffe115d6f33",
        "new_sha256": "bf8bb62773bb2f6b373def9fce74fe9bd502992cbe5ed75acf511598c427bf0f",
        "before": "People who walked days without food or water",
        "after": "People who walked for days without food or water",
        "cultural_terms_changed": False,
        "snapshot_preserved": True,
        "affected_reviews": [
            {
                "review_id": "r360-retirantes-en-us",
                "locator_role": "target",
                "reviewed_segment_changed": True,
                "status": "mechanical_segment_rechecked",
                "recheck_scope": "gramática de duração apenas; retirantes preservado",
            },
        ],
    },
]


def default_verification() -> dict[str, Any]:
    return {
        "quote_normalizer_pending": -1,
        "routes": {"valid": 0, "total": 540, "missing": -1, "divergent": -1},
        "builds": {
            key: {"passed": False, "pages": 0, "fatal_errors": -1, "undefined_references": -1, "missing_characters": -1}
            for key in ("pt", "en", "zh", "tri", "kdp_tri")
        },
        "regression": {"passed": 0, "failed": -1, "total": 0},
    }


def load_verification() -> dict[str, Any]:
    if not VERIFICATION_PATH.exists():
        return default_verification()
    payload = json.loads(VERIFICATION_PATH.read_text(encoding="utf-8"))
    return payload["verification"]


def source_evidence_summary() -> dict[str, Any]:
    concepts = ["curral_do_governo", "retirantes", "rasga_mortalha", "molambudos", "hospital_colonia"]
    substantive_groups = {
        concept: sorted(
            {
                source["independent_group_id"]
                for source in SOURCES
                if concept in source["concept_ids"] and source["read_status"] != "metadata_only"
            }
        )
        for concept in concepts
    }
    return {
        "record_count": len(SOURCES),
        "independent_group_count": len({source["independent_group_id"] for source in SOURCES}),
        "substantive_independent_groups_by_concept": substantive_groups,
        "target_usage_count": sum(source["evidence_scope"] == "target_usage" for source in SOURCES),
        "target_equivalence_count": sum(source["supports_target_equivalence"] for source in SOURCES),
        "zh_cn_target_evidence_count": sum(
            source["target_language"] == "zh-CN" for source in SOURCES
        ),
        "records_coverage_passed": all(len(groups) >= 2 for groups in substantive_groups.values()),
        "target_equivalence_gate_passed": False,
        "release_allowed": False,
        "status": "sufficient_for_triage_only_insufficient_for_target_equivalence",
    }


def build_matrix() -> dict[str, Any]:
    return {
        "spec_id": "SPEC-935-R361",
        "generated_at": "2026-08-01",
        "external_validation": False,
        "human_review_required": True,
        "release_gate": "blocked",
        "quality_verdict_allowed": False,
        "decision_status": "pending_human",
        "manuscript_cultural_edits_applied": False,
        "concepts": ["curral_do_governo", "retirantes", "rasga_mortalha", "molambudos", "hospital_colonia"],
        "decisions": DECISIONS,
        "historical_blockers": BLOCKERS,
        "mechanical_changes": MECHANICAL_CHANGES,
        "protected_cultural_terms": PROTECTED,
        "provenance_drift_manifest": str(DRIFT_PATH.relative_to(ROOT)),
        "source_evidence_summary": source_evidence_summary(),
        "verification": load_verification(),
        "claim_classes": {
            "documented_fact": "afirmação delimitada pelas fontes lidas",
            "editorial_inference": "síntese do efeito provável; exige decisão humana",
            "translation_hypothesis": "opção candidata; não é equivalência comprovada",
        },
        "safe_claim": "A R361 organiza internamente dez decisões tradutórias provisórias e registra duas divergências factuais preliminares, lacunas documentais e riscos ético-memoriais ainda não resolvidos. As fontes servem para triagem e perguntas, não para equivalência cultural, aceitabilidade EN-US/ZH-CN, consenso histórico, qualidade literária ou validação externa. O release permanece bloqueado.",
    }


def build_markdown(matrix: dict[str, Any]) -> str:
    source_by_id = {source["source_id"]: source for source in SOURCES}
    labels = {
        "curral_do_governo": "Curral do Governo",
        "retirantes": "Retirantes",
        "rasga_mortalha": "Rasga Mortalha",
        "molambudos": "Molambudos",
        "hospital_colonia": "Hospital Colônia",
    }
    sections: list[str] = []
    for concept in matrix["concepts"]:
        decisions = [item for item in matrix["decisions"] if item["concept_id"] == concept]
        body = [f"## {labels[concept]}"]
        for decision in decisions:
            body.append(f"\n### {decision['target_language']} — forma atual: `{decision['current_form']}`")
            for item in decision["options"]:
                body.append(
                    f"\n- **Hipótese tradutória {item['option_id']} — `{item['text']}`**\n"
                    f"  - Fatos-fonte/referente: {', '.join(item['evidence_source_ids'])}; "
                    "essas fontes não provam a equivalência-alvo.\n"
                    f"  - **Inferência editorial — ganhos esperados:** {'; '.join(item['gains'])}.\n"
                    f"  - **Inferência editorial — perdas esperadas:** {'; '.join(item['losses'])}.\n"
                    f"  - **Inferência editorial — riscos:** {'; '.join(item['risks'])}."
                )
            pref = decision["conditional_preference"]
            body.append(
                f"\n**Preferência condicionada:** opção {pref['option_id']}; "
                f"condições: {'; '.join(pref['conditions'])}.\n\n"
                f"**Decisão humana:** {decision['human_question']}"
            )
        sections.append("\n".join(body))

    blocker_rows = []
    blocker_labels = {
        "documented_fact_conflict": "Fato documentado em conflito",
        "limited_source_support_gap": "Lacuna de suporte folclórico",
        "lexical_attestation_scope_uncertainty": "Incerteza lexical e de datação",
        "documented_category_conflict_and_source_gap": "Deriva categorial e lacuna documental",
        "ethical_authenticity_risk": "Risco ético de autenticidade pseudoarquivística",
        "ethical_memory_boundary_risk": "Risco ético na fronteira ficção–memória",
        "documented_fact_conflict_and_memory_risk": "Conflito factual e risco de apagamento memorial",
        "ethical_representation_risk": "Risco ético de representação e estigma",
        "ethical_consent_and_provenance_gap": "Lacuna de consentimento e proveniência visual",
    }
    for blocker in matrix["historical_blockers"]:
        blocker_rows.append(
            f"### `{blocker['blocker_id']}`\n\n"
            f"**{blocker_labels[blocker['claim_type']]}:** {blocker['documented_conflict']}\n\n"
            f"**Base de evidência:** {', '.join(blocker['evidence_basis'])}.\n\n"
            f"**Ocorrências afetadas:** {len(blocker['affected_occurrences'])}.\n\n"
            "**Opções autorais:**\n" + "\n".join(
                f"{idx}. {value}" for idx, value in enumerate(blocker["author_options"], 1)
            )
        )

    sources_rows = []
    for source in SOURCES:
        sources_rows.append(
            f"| {source['source_id']} | {source['independent_group_id']} | "
            f"[{source['title']}]({source['url']}) | {source['read_status']} | "
            f"{source['evidence_scope']} | não |"
        )

    _ = source_by_id  # mantém validação local explícita das referências
    return f"""---
spec_id: SPEC-935-R361
external_validation: false
human_review_required: true
release_gate: blocked
quality_verdict_allowed: false
---

# Matriz editorial cultural R361 — Molambudos

## Estatuto epistemológico

Esta síntese é **pesquisa interna; não constitui validação cultural externa**.
O **release bloqueado** permanece vigente e toda escolha de alto risco exige
**decisão humana**. Nenhuma preferência é aprovação.

### Classes de afirmação

- **Fato documentado:** limitado ao que as fontes lidas sustentam.
- **Inferência editorial:** avaliação de ganho/perda feita a partir do corpus.
- **Hipótese tradutória:** opção a testar com revisores EN-US/ZH-CN.

{chr(10).join(sections)}

# Bloqueios históricos e ético-memoriais

{chr(10).join(blocker_rows)}

# Correções mecânicas aplicadas

Foram aplicadas somente três mudanças de baixo risco: metros, `walked for days`
e `带刺铁丝网`. Nenhum nome histórico, regionalismo, símbolo, neologismo,
cronologia ou forma institucional foi alterado.

# Fontes lidas

| ID | Grupo independente | Fonte | Leitura | Escopo | Equivalência-alvo? |
|---|---|---|---|---|---|
{chr(10).join(sources_rows)}

# Limites

- A ausência de fonte chinesa institucional não torna uma transliteração correta.
- Há zero evidências de equivalência-alvo; o uso publicado em inglês informa
  prática editorial, não cria equivalência oficial.
- Metadados isolados sustentam somente existência, título e autoria do estudo.
- Contagem de registros não equivale a independência, profundidade ou suficiência.
- Revisão histórica cearense, revisão sobre Barbacena e revisão nativa continuam
  obrigatórias antes de qualquer alteração de alto risco.
"""


def main() -> None:
    sources_payload = {
        "spec_id": "SPEC-935-R361",
        "generated_at": "2026-08-01",
        "external_validation": False,
        "human_review_required": True,
        "release_gate": "blocked",
        "quality_verdict_allowed": False,
        "sources": SOURCES,
        "evidence_summary": source_evidence_summary(),
        "retrieval_notes": [
            "Antigravity aceitou tarefas, mas não retornou conclusões; nenhuma foi contada como evidência.",
            "Um acesso DOI UFPR retornou 429; a página OJS foi lida diretamente e substituiu o acesso falho.",
            "Uma URL presumida da PUC retornou 404; somente os metadados DOI efetivamente lidos foram usados.",
        ],
    }
    matrix = build_matrix()
    for record in DRIFT_RECORDS:
        current = hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()
        if current != record["new_sha256"]:
            raise RuntimeError(
                f"deriva não autorizada em {record['path']}: {current} != {record['new_sha256']}"
            )
    drift_payload = {
        "spec_id": "SPEC-935-R361",
        "predecessor_spec_id": "SPEC-935-R360",
        "generated_at": "2026-08-01",
        "predecessor_artifact_mutated": False,
        "external_validation": False,
        "human_review_required": True,
        "release_gate": "blocked",
        "quality_verdict_allowed": False,
        "records": DRIFT_RECORDS,
        "safe_claim": "Os hashes R360 continuam representando o snapshot revisado; R361 registra três derivações mecânicas sem reatribuir os pareceres antigos ao corpus novo.",
    }
    SOURCES_PATH.write_text(json.dumps(sources_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DRIFT_PATH.write_text(json.dumps(drift_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MATRIX_PATH.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOSSIER_PATH.write_text(build_markdown(matrix), encoding="utf-8")
    print("R361: 5 conceitos, 10 decisões, 10 bloqueios; release bloqueado.")


if __name__ == "__main__":
    main()
