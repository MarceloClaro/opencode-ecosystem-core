"""
MiroFish Social — Perfis editoriais de periódicos de referência (SPEC-976 R-976.14).

Baseado nas normas/exigências editoriais PÚBLICAS de periódicos Qualis A1 (Educação)
e Q1 internacionais de tecnologia educacional, pesquisadas em 2026-09-23.

ANTI-OVERCLAIM (R110): estes são RÓTULOS DE SIMULAÇÃO para calibração de perfis
de banca. Os perfis traduzem critérios públicos em pesos de avaliação; NÃO
representam parecer real, afiliação, promessa editorial nem reproduzem conteúdo
protegido das revistas. Uso permitido: ensaio de submissão orientado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ─────────────────────────────────────────────────────────────
# Perfis editoriais (R-976.14)
# Cada perfil: escopo, prioridade de tipo de estudo, estilo de referência,
# prazos/limites, critérios de avaliação e pesos sobre os 12 critérios da banca.
# ─────────────────────────────────────────────────────────────
@dataclass
class EditorialProfile:
    journal: str
    scope: str
    priority: str                    # perfil do melhor artigo
    reference_style: str
    length_limit: str
    review_flow: str
    special_gates: List[str]         # gates editoriais adicionais (ex.: anti-IA)
    weights: Dict[str, float]        # pesos dos 12 critérios (null → default 1.0)
    source: str                      # URL de referência pública


EDITORIAL_PROFILES: Dict[str, EditorialProfile] = {
    "Revista Brasileira de Educação": EditorialProfile(
        journal="Revista Brasileira de Educação (ANPEd)",
        scope=(
            "Artigos inéditos de educação resultantes prioritariamente de pesquisas; "
            "estudos teóricos que contribuam para o avanço do conhecimento e "
            "fomentem novos estudos."
        ),
        priority=(
            "Pesquisa empírica com contribuição clara à educação/linha editorial, "
            "originalidade do tema ou do tratamento, consistência e rigor da "
            "abordagem teórico-metodológica."
        ),
        reference_style="ABNT (ordem alfabética; citação (Autor, data[, p.]))",
        length_limit="40.000 a 70.000 caracteres com espaços (com refs.)",
        review_flow="Editorial + pareceristas ad hoc; duplo-cego; referências incorretas → não consideradas",
        special_gates=[],
        weights={
            "metodologia": 1.5, "ética": 1.3, "evidências": 1.5,
            "originalidade": 1.4, "teoria": 1.3, "clareza": 1.0,
            "redação": 1.0, "coerência": 1.1, "estatística": 1.0,
            "relevância": 1.2, "reprodutibilidade": 1.0, "impacto": 1.0,
        },
        source="https://educa.fcc.org.br/revistas/rbedu/pinstruc.htm",
    ),
    "Educação & Sociedade": EditorialProfile(
        journal="Educação & Sociedade (CEDES/Unicamp)",
        scope=(
            "Relação educação e sociedade com base em teorias sociais; ensaios "
            "originais; dossiês. Rejeita relatos de projetos, relatórios de "
            "pesquisa, capítulos de teses/TCCs."
        ),
        priority=(
            "Contribuição teórico-social consistente; análise crítica da relação "
            "educação-sociedade; diálogo com teorias sociais e conceitos; "
            "atualidade e relevância do tema."
        ),
        reference_style="ABNT (citação (Autor, data))",
        length_limit="~50.000 caracteres (artigos); conforme instruções",
        review_flow="Comitê + pareceristas; duplo-cego; Similarity Check (plágio, autoplágio, republicação, falsificação)",
        special_gates=[
            "NÃO aceita textos criados por IA generativa (ChatGPT/DeepSeek como autor ou coautor)",
            "Declaração de integridade científica obrigatória",
            "Conflito de interesses declarado",
        ],
        weights={
            "teoria": 1.8, "originalidade": 1.5, "impacto": 1.5,
            "ética": 1.5, "metodologia": 1.1, "coerência": 1.2,
            "clareza": 1.0, "redação": 1.0, "evidências": 1.0,
            "estatística": 0.8, "relevância": 1.4, "reprodutibilidade": 0.8,
        },
        source="https://scielo.br/journal/es/about + cedes.unicamp.br/autores-educacao-sociedade",
    ),
    "Cadernos de Pesquisa": EditorialProfile(
        journal="Cadernos de Pesquisa (FCC)",
        scope=(
            "Trabalhos inéditos com perspectivas teóricas diversas; prioridade "
            "para pesquisas de caráter empírico, histórico ou documental; atenção "
            "a desigualdades sociais, gênero, raça, infância, juventude, escola, "
            "trabalho, família e políticas públicas."
        ),
        priority=(
            "Pesquisa empírica/histórica/documental com relevância social; "
            "interdisciplinaridade; contribuição à equidade e políticas públicas."
        ),
        reference_style="APA 7ª edição (CRediT recomendado)",
        length_limit="Conforme template/normas de apresentação",
        review_flow="Duplo-anônimo; análise antiplágio e autoplágio antes da avaliação",
        special_gates=["Check antiplágio obrigatório", "Contribuição de cada autor declarada (CRediT)"],
        weights={
            "evidências": 1.6, "metodologia": 1.5, "ética": 1.4,
            "impacto": 1.4, "relevância": 1.4, "teoria": 1.0,
            "coerência": 1.0, "originalidade": 1.0, "estatística": 1.1,
            "clareza": 1.0, "redação": 1.0, "reprodutibilidade": 0.9,
        },
        source="https://publicacoes.fcc.org.br/cp/about/submissions + fcc.org.br/difusao/cadernos",
    ),
    "Práxis Educacional": EditorialProfile(
        journal="Práxis Educacional (UESB)",
        scope=(
            "Pesquisas e estudos do campo da educação (Brasil e exterior); "
            "NÃO admite revisão de literatura ou congêneres; resenhas."
        ),
        priority=(
            "Pesquisa original com método claro, atualização bibliográfica e "
            "relevância; autores com titulação (≥1 doutor); H-index considerados."
        ),
        reference_style="ABNT (ou APA quando aplicável)",
        length_limit="Template da revista (artigos 12–20 páginas em revistas do gênero; ver instruções)",
        review_flow="Desk review (normalização, titulação, atualização bib., não duplicação) + double blind ≥2 pareceristas",
        special_gates=["Declaração de originalidade assinada", "Desk review rejeita submissões fora do formato"],
        weights={
            "metodologia": 1.6, "evidências": 1.4, "ética": 1.3,
            "originalidade": 1.3, "coerência": 1.2, "clareza": 1.1,
            "redação": 1.2, "estatística": 1.0, "teoria": 1.0,
            "relevância": 1.1, "reprodutibilidade": 0.9, "impacto": 0.9,
        },
        source="https://periodicos2.uesb.br/praxis/about/submissions",
    ),
    "Computers & Education": EditorialProfile(
        journal="Computers & Education (Elsevier)",
        scope=(
            "Como a tecnologia digital pode aprimorar a educação; pesquisa de alta "
            "qualidade que estende teoria e prática; foco amplo o suficiente para "
            "a comunidade educacional."
        ),
        priority=(
            "Estudo empírico robusto (RCT/quase-experimental/longitudinal) que "
            "estende teoria E prática; contribuição generalizável; ética e "
            "reprodutibilidade explícitas."
        ),
        reference_style="Elsevier (APA-style); CRediT; ORCID",
        length_limit="Conforme template Elsevier; abstract estruturado",
        review_flow="Editorial triage (desk reject se fora das guidelines) + double anonymized ≥2 revisores",
        special_gates=[
            "Declaração de uso de IA generativa obrigatória",
            "Dados acessíveis para revisão/publicação",
            "Conformidade com Elsevier Publishing Ethics",
        ],
        weights={
            "metodologia": 1.8, "estatística": 1.7, "evidências": 1.8,
            "reprodutibilidade": 1.7, "ética": 1.4, "originalidade": 1.3,
            "teoria": 1.5, "coerência": 1.2, "clareza": 1.0,
            "redação": 1.0, "impacto": 1.1, "relevância": 1.1,
        },
        source="https://sciencedirect.com/journal/computers-and-education/publish/guide-for-authors",
    ),
    "British Journal of Educational Technology": EditorialProfile(
        journal="British Journal of Educational Technology (BERA/Wiley)",
        scope=(
            "Tecnologia educacional e de treinamento; acolhe estudos multi-site/"
            "multi-perspectiva, longitudinais, relatos de falhas com lições e "
            "estudos que confirmam/contradizem contribuições anteriores."
        ),
        priority=(
            "Evidência empírica de benefícios (longitudinal/multi-site); transparência "
            "de dados; registro de pré-registro (Registered Reports) valorizado."
        ),
        reference_style="Wiley/APA; 6.000 palavras (aprox.); abstract padrão",
        length_limit="~6.000 palavras (excl. abstract e refs.)",
        review_flow="Double-blind; triagem editorial; Registered Reports (Stage 1→2)",
        special_gates=["Dados empíricos incentivados em repositório", "Sugestão de 4 revisores (RR)"],
        weights={
            "metodologia": 1.7, "evidências": 1.7, "estatística": 1.6,
            "reprodutibilidade": 1.6, "ética": 1.3, "originalidade": 1.3,
            "teoria": 1.3, "impacto": 1.1, "coerência": 1.1, "clareza": 1.0,
            "redação": 1.0, "relevância": 1.0,
        },
        source="https://bera-journals.onlinelibrary.wiley.com/hub/journal/14678535/forauthors.html",
    ),
    "Education and Information Technologies": EditorialProfile(
        journal="Education and Information Technologies (Springer/IFIP TC3)",
        scope=(
            "Relações complexas entre TIC e educação; da micro (aplicações em sala) "
            "à macro (políticas nacionais); todos os níveis, da infância ao superior."
        ),
        priority=(
            "Pesquisa original primária com disclosure; revisão de evidências; "
            "perspectivas micro-macro; imparcialidade e conflitos declarados."
        ),
        reference_style="Springer/APA; abstract estruturado; disclosure",
        length_limit="Conforme template Springer (revisão sist. 2.500–5.000 palavras)",
        review_flow="Double-anonymous; triagem técnica (anonymização estrita)",
        special_gates=[
            "LLMs (ChatGPT) NÃO satisfazem critérios de autoria",
            "Disclosure statement obrigatória (pesquisas primárias e revisões)",
            "Préprint pode comprometer anonimato — considerar antes",
        ],
        weights={
            "metodologia": 1.6, "evidências": 1.5, "ética": 1.5,
            "estatística": 1.4, "reprodutibilidade": 1.3, "teoria": 1.2,
            "originalidade": 1.1, "clareza": 1.0, "coerência": 1.0,
            "redação": 1.0, "impacto": 1.0, "relevância": 1.0,
        },
        source="https://link.springer.com/journal/10639/submission-guidelines",
    ),
    "International Review of Education": EditorialProfile(
        journal="International Review of Education (UNESCO UIL/Springer)",
        scope=(
            "Educação comparada e internacional; lifelong learning; prioridade a "
            "educação de adultos, educação não-formal, alfabetização, EaD e "
            "educação vocacional; artigos com relevância internacional."
        ),
        priority=(
            "Estudos internacionais/comparativos com implicações de política e "
            "prática; contribuição para lifelong learning; rigor e clareza global."
        ),
        reference_style="Springer/APA; EN ou FR; máx. 6.000 palavras (artigos)",
        length_limit="Artigo ≤6.000 palavras (excl. abstract e bibliografia)",
        review_flow="Double-blind (artigos e research notes); editor executivo solicita contribuições",
        special_gates=["Aceita pesquisa notes (≤3.000) e book reviews", "Relevância para audiência internacional"],
        weights={
            "impacto": 1.6, "relevância": 1.5, "teoria": 1.4,
            "evidências": 1.3, "metodologia": 1.2, "ética": 1.2,
            "coerência": 1.1, "clareza": 1.0, "redação": 1.0,
            "originalidade": 1.0, "estatística": 1.0, "reprodutibilidade": 0.9,
        },
        source="https://uil.unesco.org/en/journal-international-review-education/instruction-authors",
    ),
    "Práxis Educativa": EditorialProfile(
        journal="Práxis Educativa (UEPG)",
        scope=(
            "Educação (campo amplo); aceita artigos, traduções e resenhas; "
            "temas atuais como ética e integridade, IA, TICs e desinformação."
        ),
        priority=(
            "Pesquisa com consistência teórico-metodológica; atualidade e "
            "adequação ao escopo; contribuição original."
        ),
        reference_style="ABNT/APA conforme instruções",
        length_limit="Conforme instruções da revista",
        review_flow="Duplo-cego; pareceristas de estados diferentes/exterior; parecer de consolidação",
        special_gates=["Anonimato estrito (sem identificação no arquivo)", "Desk review prévio"],
        weights={
            "metodologia": 1.5, "ética": 1.4, "evidências": 1.4,
            "teoria": 1.2, "coerência": 1.1, "originalidade": 1.1,
            "clareza": 1.0, "redação": 1.1, "estatística": 1.0,
            "relevância": 1.0, "reprodutibilidade": 0.9, "impacto": 0.9,
        },
        source="https://revistas.uepg.br/index.php/praxiseducativa/about/submissions",
    ),
    "Estudos em Avaliação Educacional": EditorialProfile(
        journal="Estudos em Avaliação Educacional (FCC)",
        scope=(
            "Avaliação educacional e análise de políticas/programas que dialogam "
            "com avaliação; ciências humanas, perspectivas teórico-metodológicas "
            "diversas; fluxo contínuo."
        ),
        priority=(
            "Estudos avaliativos com solidez metodológica; subsídio a políticas "
            "e programas; interdisciplinaridade."
        ),
        reference_style="(ver instruções FCC/ABNT)",
        length_limit="Conforme instruções da revista",
        review_flow="Duplo-cego; antiplágio prévio",
        special_gates=["Escopo restrito a avaliação educacional e afins"],
        weights={
            "estatística": 1.7, "evidências": 1.6, "metodologia": 1.6,
            "ética": 1.3, "impacto": 1.4, "coerência": 1.1, "clareza": 1.0,
            "teoria": 1.0, "originalidade": 1.0, "redação": 1.0,
            "relevância": 1.1, "reprodutibilidade": 1.0,
        },
        source="https://fcc.org.br/fcc-noticia/eae-a1",
    ),
    "Journal of Dentistry": EditorialProfile(
        journal="Journal of Dentistry (Elsevier)",
        scope=(
            "Periódico internacional líder em Odontologia Restauradora; influenciar "
            "prática clínica, pesquisa, indústria e policy-maker. Pesquisa "
            "odontológica translacional e clínica; artigos de revisão com perguntas "
            "estruturadas (quadro PCC), síntese de evidências e implicações clínicas "
            "proporcionais; destaque para a criação e o uso responsável de "
            "ferramentas de IA em odontologia."
        ),
        priority=(
            "Revisão/scoping review com protocolo registrado, pergunta estruturada "
            "por população-conceito-contexto (PCC), critérios de elegibilidade "
            "explícitos, seleção dupla independente, extração padronizada, síntese "
            "descritiva (contagens/proporções) e 'Clinical significance' no resumo; "
            "anti-overclaim: novidade verificada na literatura e implicações "
            "proporcionais à evidência."
        ),
        reference_style="Numerado com DOI ([1] A.A. Surname, [Title], [Journal] [volume] ([year]) [pages]. [DOI])",
        length_limit=(
            "Review: máx. 10 páginas impressas ≈ 33 páginas processadas (incl. "
            "figuras/tabelas); Original Research 6 pp ≈ 20 pp; Short Comm 2 pp ≈ 7 pp; "
            "Digital Dentistry Section segue o mesmo padrão (6/10/2 pp)"
        ),
        review_flow=(
            "Editorial triage + double anonymized ≥2 revisores (Elsevier); "
            "checklist estrutural do template (abstract com Clinical significance, "
            "protocolo/registro, fluxo PRISMA, declarações obrigatórias); "
            "timeline oficial: 1ª decisão ~5 dias (desk), ~29 dias pós-review, "
            "~74 dias até aceite; apelação única (Elsevier Appeal Policy); "
            "mudança de autoria NÃO considerada após submissão"
        ),
        special_gates=[
            "Abstract estruturado com Background/Objective/Methods/Results/Conclusion/Clinical significance",
            "Protocolo registrado declarado SEM implicar registro inexistente (anti-overclaim)",
            "Declaração obrigatória de uso de IA generativa em seção própria ANTES das referências (ferramenta, propósito, revisão humana; revisores/editores proibidos de submeter manuscrito a IA)",
            "Declarações obrigatórias: CRediT, funding, conflito de interesses, ética (aprovação com data/número + ICMJE p/ ensaios), disponibilidade de dados",
            "Estratégia de busca completa disponibilizada em material suplementar (reprodutibilidade)",
            "NÃO aceita Case Reports (removidos do sistema se submetidos)",
            "CONSORT checklist + fluxograma para RCTs; resumo <500 palavras em registro de ensaio NÃO conta como publicação prévia",
        ],
        weights={
            "evidências": 1.8, "metodologia": 1.7, "reprodutibilidade": 1.7,
            "ética": 1.5, "estatística": 1.4, "clareza": 1.3,
            "coerência": 1.2, "relevância": 1.2, "impacto": 1.1,
            "originalidade": 1.1, "redação": 1.0, "teoria": 0.9,
        },
        source=(
            "https://www.sciencedirect.com/journal/journal-of-dentistry/publish/guide-for-authors "
            "+ https://www.sciencedirect.com/journal/journal-of-dentistry "
            "+ https://docs.google.com/document/d/1yKkypArCLZefsADlvxqvFWgRWONwGRVnw34gHlILInQ/edit "
            "(template oficial Review Article, compartilhado pelo autor) — ver EDITAL_JOD_RIGOR_EDITORIAL.md"
        ),
    ),
    "Educação (PUCRS)": EditorialProfile(
        journal="Educação (PUCRS)",
        scope=(
            "Trabalhos originais de educação (estudos teóricos, pesquisas, "
            "relatos de experiência, debates atuais); avaliação duplo-cega com "
            "dois pareceres; dados de pesquisa sugeridos em repositórios (Zenodo)."
        ),
        priority=(
            "Originalidade do tratamento; consistência e rigor da abordagem; "
            "contribuição e adequação à linha temática."
        ),
        reference_style="ABNT/APA conforme instruções",
        length_limit="Conforme instruções da revista",
        review_flow="Duplo-cega; dois pareceres especializados; editor tem decisão final",
        special_gates=["Ciência aberta incentivada (dados em repositórios)", "Preprint deve ser informado"],
        weights={
            "metodologia": 1.5, "ética": 1.4, "evidências": 1.3,
            "originalidade": 1.3, "teoria": 1.2, "coerência": 1.1,
            "reprodutibilidade": 1.2, "clareza": 1.0, "redação": 1.0,
            "estatística": 1.0, "relevância": 1.0, "impacto": 1.0,
        },
        source="https://revistaseletronicas.pucrs.br/faced/about",
    ),
}

# Nomes canônicos (rótulos de simulação) aceitos como target_institution
JOURNAL_KEYS: List[str] = list(EDITORIAL_PROFILES.keys())

# Aliases comuns/abreviações para facilitar target_institution
JOURNAL_ALIASES: Dict[str, str] = {
    "rbe": "Revista Brasileira de Educação",
    "cadernos": "Cadernos de Pesquisa",
    "cadernos de pesquisa": "Cadernos de Pesquisa",
    "ees": "Educação & Sociedade",
    "e&s": "Educação & Sociedade",
    "educacao e sociedade": "Educação & Sociedade",
    "ce": "Computers & Education",
    "computers and education": "Computers & Education",
    "bjet": "British Journal of Educational Technology",
    "eit": "Education and Information Technologies",
    "education and information technologies": "Education and Information Technologies",
    "ire": "International Review of Education",
    "práxis educacional": "Práxis Educacional",
    "praxis educacional": "Práxis Educacional",
    "práxis educativa": "Práxis Educativa",
    "praxis educativa": "Práxis Educativa",
    "educacao pucrs": "Educação (PUCRS)",
    "estudos em avaliacao": "Estudos em Avaliação Educacional",
    "estudos em avaliação": "Estudos em Avaliação Educacional",
    "jod": "Journal of Dentistry",
    "journal of dentistry": "Journal of Dentistry",
    "dentistry": "Journal of Dentistry",
}


def get_profile(journal_key: str) -> Optional[EditorialProfile]:
    """Recupera perfil editorial pelo nome; aceita aliases, parcial e caixa mista."""
    if not journal_key:
        return None
    exact = EDITORIAL_PROFILES.get(journal_key)
    if exact:
        return exact
    # alias explícito
    alias = JOURNAL_ALIASES.get(journal_key.strip().lower())
    if alias:
        return EDITORIAL_PROFILES.get(alias)
    lower = journal_key.lower()
    for key, profile in EDITORIAL_PROFILES.items():
        if lower in key.lower() or key.lower() in lower:
            return profile
    return None


def merge_weights(base_weights: Dict[str, float], profile_weights: Dict[str, float]) -> Dict[str, float]:
    """Pesos da banca ampliada ajustados pelos pesos editoriais do periódico."""
    merged = dict(base_weights)
    for crit, w in profile_weights.items():
        if crit in merged:
            merged[crit] = round(merged[crit] * w, 3)
    return merged


def profile_summary(journal_key: str) -> Dict[str, Any]:
    """Resumo público do perfil para relatórios (anti-overclaim incluso)."""
    profile = get_profile(journal_key)
    if not profile:
        return {"journal": journal_key, "found": False}
    return {
        "journal": profile.journal,
        "found": True,
        "scope": profile.scope,
        "priority": profile.priority,
        "reference_style": profile.reference_style,
        "length_limit": profile.length_limit,
        "review_flow": profile.review_flow,
        "special_gates": profile.special_gates,
        "source": profile.source,
        "disclaimer": (
            "Perfil editorial baseado em normas públicas (simulação R-976.14). "
            "Rótulo de calibração; não representa parecer real, afiliação nem "
            "promessa editorial da revista."
        ),
    }