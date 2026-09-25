"""
MiroFish Social — Perfis editoriais de periódicos de referência (SPEC-976 R-976.14).

Baseado nas normas/exigências editoriais PÚBLICAS de periódicos Qualis A1 (Educação)
e Q1 internacionais de tecnologia educacional, pesquisadas em 2026-09-23.

ANTI-OVERCLAIM (R110): estes são RÓTULOS DE SIMULAÇÃO para calibração de perfis
de banca. Os perfis traduzem critérios públicos em pesos de avaliação; NÃO
representam parecer real, afiliação, promessa editorial nem reproduzem conteúdo
protegido das revistas. Uso permitido: ensaio de submissão orientado.

R-976.22: get_profile() aceita variações de alias com barra/parênteses/acento/
hífen/caixa mista via normalização (normalize_institution_alias).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Regexes de normalização de aliases (R-976.22)
_re_sep = re.compile(r"[^a-z0-9]+")
_re_space = re.compile(r"\s+")

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
        reference_style="ABNT (ordem alfabética; citação (Autor, data[, p.])); falha nas referências → não considerada",
        length_limit=(
            "Artigos: 40.000 a 70.000 caracteres com espaços INCLUINDO referências, "
            "notas, título, resumo e palavras-chave nos 3 idiomas; Espaço Aberto "
            "30–50 mil; resenhas ≤10 mil caracteres"
        ),
        review_flow=(
            "Editorial + pareceristas (Conselho Editorial ou ad hoc); duplo-cego; "
            "verificação de quebra de anonimato (autocitação, projeto/grupo, "
            "dissertação/tese); referências incorretas → não consideradas"
        ),
        special_gates=[
            "Resumo/abstract/palavras-chave ≤1.000 caracteres cada, em PT/EN/ES "
            "(+FR se original em francês); título em 3 idiomas",
            "Texto em PT, EN, FR ou ES; Times New Roman 12, entrelinha simples",
            "Notas de rodapé exclusivamente explicativas (numeradas automaticamente)",
            "Referências ABNT atualizadas: matérias sem refs corretas não são "
            "consideradas para exame/publicação",
            "Cessão integral de direitos autorais ao enviar colaboração",
            "Anonimato: substituir autocitações por 'Autor, Ano' (quebra de "
            "anonimato = critério de rejeição)",
        ],
        weights={
            "metodologia": 1.5, "ética": 1.3, "evidências": 1.5,
            "originalidade": 1.4, "teoria": 1.3, "clareza": 1.0,
            "redação": 1.0, "coerência": 1.1, "estatística": 1.0,
            "relevância": 1.2, "reprodutibilidade": 1.0, "impacto": 1.0,
        },
        source="https://submission.scielo.br/index.php/rbedu/about/submissions",
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
        length_limit="~45.000 caracteres (referência de custo médio de produção por artigo; conferir instruções)",
        review_flow=(
            "Comitê + pareceristas; duplo-cego/avaliação aberta opcional (open "
            "evaluation: parecerista pode comunicar-se com autor); Similarity Check "
            "em fases (plágio, autoplágio, republicação, falsificação); rejeição se "
            "alta similaridade"
        ),
        special_gates=[
            "NÃO aceita textos criados por IA generativa (ChatGPT/DeepSeek como autor ou coautor)",
            "Declaração de integridade científica obrigatória",
            "Conflito de interesses declarado",
            "Open data: citação do repositório na seção metodológica + Data Availability",
            "CC BY 4.0; contribuição editorial pós-aceite (associação CEDES — ver "
            "cedes.unicamp.br/autores-educacao-sociedade)",
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
        length_limit="Conforme template/normas de apresentação (ver instruções FCC)",
        review_flow=(
            "Desk review (adequação ao escopo e normas) + duplo-anônimo com ≥2 "
            "pareceristas; fluxo em 8 etapas; scanner iThenticate 2.0 (antiplágio/"
            "autoplágio) antes da avaliação"
        ),
        special_gates=[
            "Scanner iThenticate 2.0 obrigatório (antiplágio e autoplágio)",
            "Open peer review experimental (em avaliação pelo periódico)",
            "Contribuição de cada autor declarada (CRediT)",
            "Desk review: fora de normas/escopo → devolvido sem avaliação de mérito",
        ],
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
        reference_style="ABNT (NBR 6022/6028/10520; ou APA quando aplicável)",
        length_limit="Template da revista (artigos 12–20 páginas em revistas do gênero; ver instruções)",
        review_flow=(
            "Desk review (normalização, titulação, atualização bib., não duplicação) "
            "+ double blind ≥2 pareceristas; divergência → 3º parecerista ad hoc ou "
            "parecer de consolidação da equipe editorial; 2 arquivos (template com e "
            "sem identificação)"
        ),
        special_gates=[
            "Declaração de originalidade assinada",
            "Desk review rejeita submissões fora do formato",
            "≥1 autor com doutorado; todos mestres/doutores/doutorandos; máx. 3 "
            "autores (4 excepcional justificado)",
            "Contribuições de cada autor informadas na submissão",
        ],
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
        length_limit="Artigos ≤8.000 palavras (excl. referências e apêndices); abstract estruturado",
        review_flow=(
            "Desk reject se fora das guidelines (devolvido SEM revisão) + double "
            "anonymized ≥2 revisores; title page e manuscrito anônimo em arquivos "
            "separados; arquivos editáveis (.doc/.docx/.tex) — PDF não é fonte aceitável"
        ),
        special_gates=[
            "Declaração de uso de IA generativa obrigatória na submissão (ferramenta, "
            "propósito, supervisão humana)",
            "Revisores/editores PROIBIDOS de submeter manuscrito não publicado a IA "
            "generativa (proteção de confidencialidade)",
            "Arquivos editáveis obrigatórios (.doc/.docx/.tex; PDF rejeitado como fonte)",
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
        reference_style="Wiley/APA; 5.000–6.000 palavras (excl. refs/abstracts/notas práticas/apêndices)",
        length_limit=(
            "Original/Review: 5.000–6.000 palavras excluindo referências, abstracts, "
            "practitioner notes, apêndices e suplementares; INCLUI tabelas & figuras "
            "e footnotes; leeway >6.000 mediante e-mail ao editor (bjeteditor@wiley.com)"
        ),
        review_flow=(
            "Double-anonymised; triagem editorial; Free Format submission (sem "
            "formatação rígida na 1ª submissão); Registered Reports (Stage 1→2)"
        ),
        special_gates=[
            "Decisão final sobre uso de IA generativa (AIGC/GenAI) pertence ao editor",
            "Dados empíricos incentivados em repositório; IRB/data statements conforme tipo",
            "Sugestão de 4 revisores (RR)",
        ],
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
            "à macro (políticas nacionais); todos os níveis, da infância ao superior; "
            "jornal oficial do IFIP Technical Committee on Education."
        ),
        priority=(
            "Pesquisa original primária (artigos originais; NÃO aceita mais review "
            "papers — literature/systematic/bibliometric reviews); disclosure; "
            "perspectivas micro-macro; imparcialidade e conflitos declarados."
        ),
        reference_style="Springer/APA; abstract estruturado; disclosure",
        length_limit=(
            "Sem limite rígido de palavras declarado no guia; fontes editáveis "
            "obrigatórias (.docx/LaTeX) em toda submissão/revisão — falha → não "
            "considerado para revisão"
        ),
        review_flow=(
            "Double-anonymous; triagem técnica (anonymização estrita); NÃO permite "
            "mudança de autoria após submissão; 1ª decisão mediana ~29 dias (típico "
            "~40 dias); IF 7.2 / 5-yr 7.3"
        ),
        special_gates=[
            "Sem mudança de autoria após a submissão do manuscrito",
            "Arquivos editáveis obrigatórios em toda submissão/revisão (senão → "
            "não considerado)",
            "LLMs (ChatGPT) NÃO satisfazem critérios de autoria",
            "Disclosure statement obrigatória (pesquisas primárias)",
            "NÃO aceita review papers: literature reviews, systematic reviews e "
            "bibliometric reviews",
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
        reference_style="Springer/APA; EN ou FR; abstract 150–250 palavras sem abreviações/refs",
        length_limit=(
            "Articles ≤6.000 palavras (excl. abstract e bibliografia); Research "
            "notes ≤3.000; Book reviews ≤1.000 (EN ou FR)"
        ),
        review_flow=(
            "Double-blind para artigos e research notes (book reviews excluídas); "
            "editor executivo solicita contribuições; 1ª decisão mediana ~97 dias; "
            "IF 1.9 / 5-yr 2.7"
        ),
        special_gates=[
            "Aceita: articles, research notes (≤3.000) e book reviews (≤1.000)",
            "Abstract 150–250 palavras, sem abreviações/acrônimos indefinidos e sem referências",
            "4–6 keywords para indexação",
            "Manuscrito em .docx, Times New Roman 12; outros idiomas com resumo em EN ou FR + tradução",
            "Relevância para audiência internacional (educação comparada e lifelong learning)",
        ],
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
        reference_style="APA (referências); resumo ≤10 linhas (150 palavras) com 3 palavras-chave em PT/EN/ES",
        length_limit=(
            "Artigos: 20–28 páginas (A4, espaço 1,5, margens 2,0 cm sup/inf e "
            "2,5 cm lat); resenhas 4–7 páginas (obras dos últimos 5 anos)"
        ),
        review_flow=(
            "Duplo-cego; 2 pareceristas; opiniões contraditórias → outros "
            "pareceristas consultados; controle de plágio/autoplágio antes do envio "
            "aos pareceristas; atualmente NÃO aceita submissões (portal OJS)"
        ),
        special_gates=[
            "Sem identificação de autoria no arquivo (anonimato estrito)",
            "Ética: Res. CNS 466/2012 e 510/2016; CNPq Ética e Integridade na prática científica",
            "Plágio e autoplágio controlados por programa antes dos pareceristas",
            "Papel oriundo de dissertação/tese: indicar orientador nos comentários ao editor",
            "Atualmente não aceita submissões (verificar status no portal)",
        ],
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
        length_limit="Conforme instruções da revista (fluxo contínuo)",
        review_flow=(
            "Duplo anônimo com ≥2 pareceristas ad hoc; parecer consolidado emitido "
            "pelo Comitê Editorial; se 1ª versão publicada como preprint → avaliação "
            "simples anônimo (revisor conhece autoria, autor não)"
        ),
        special_gates=[
            "Escopo restrito a avaliação educacional e afins",
            "Preprint da 1ª versão deve ser informado nos metadados (muda o regime "
            "de anonimato)",
            "Licença CC BY 4.0",
        ],
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
    "Journal of Dental Research": EditorialProfile(
        journal="Journal of Dental Research (IADR/Sage)",
        scope=(
            "Periódico revisado por pares dedicado à ciência relevante para a "
            "odontologia, cavidade oral e estruturas associadas em saúde e doença; "
            "leitoria de pesquisadores orais/dentais/craniofaciais, cientistas "
            "clínicos, dentistas, educadores e policy-makers; órgão oficial da "
            "IADR/AADOCR."
        ),
        priority=(
            "Original Research Report (≤3.200 palavras, 5 fig./tab., 40-50 refs, "
            "abstract 300 palavras) ou Critical Review (≤4.000 palavras, 6 fig./tab., "
            "~60-80 refs, abstract 300 palavras) com avaliação crítica e "
            "ilustrações/diagramas; Clinical Reviews (antigas Concise Reviews) de "
            "alta relevância clínica com síntese de evidência; meta-análises só com "
            "nº suficiente de estudos; áreas pouco estudadas com qualidade limitada "
            "tipicamente não são aceitas como clinical review."
        ),
        reference_style="CSE 9ª edição (estilo Council of Science Editors)",
        length_limit=(
            "Original Research Report: 3.200 palavras (excl. abstract/acks/figure "
            "legends/refs) + 5 fig./tab. + 40-50 refs + abstract 300 palavras; "
            "Critical Review: 4.000 palavras + 6 fig./tab. + ~60-80 refs + abstract "
            "300 palavras; Discovery! 2.500 palavras + 2 fig./tab. (por convite); "
            "Letter 250 palavras (sem fig./tab.)"
        ),
        review_flow=(
            "Editorial triage (SAGETrack) + revisão por pares; média ~17-18 dias "
            "submissão→1ª decisão; COPE; ICMJE Uniform Requirements; title page "
            "separada + cover letter + lista de revisores sugeridos; OnlineFirst"
        ),
        special_gates=[
            "Estilo CSE 9ª edição obrigatório",
            "Abstract de 300 palavras exigido para originais e Critical Reviews",
            "ICMJE Uniform Requirements (registro de ensaios clínicos)",
            "CONSORT checklist+fluxograma para RCTs; STROBE/GATHER/CHEERS para "
            "desenhos observacionais conforme tipo (JDR CTR)",
            "Discovery! apenas por convite do Editor",
            "Meta-análises só com nº suficiente de estudos; áreas pouco estudadas "
            "com qualidade limitada rejeitadas como clinical review",
        ],
        weights={
            "evidências": 1.8, "metodologia": 1.7, "ética": 1.5,
            "reprodutibilidade": 1.6, "estatística": 1.6, "originalidade": 1.3,
            "clareza": 1.2, "coerência": 1.2, "relevância": 1.4,
            "impacto": 1.3, "redação": 1.1, "teoria": 1.0,
        },
        source=(
            "https://journals.sagepub.com/author-instructions/jdr "
            "+ https://www.iadr.org/media/4191 (JDR Instructions to Authors, PDF)"
        ),
    ),
    "Clinical Oral Investigations": EditorialProfile(
        journal="Clinical Oral Investigations (Springer)",
        scope=(
            "Fórum multidisciplinar internacional para publicações de todas as "
            "áreas da medicina oral; conecta ciências básicas e clínicas para o "
            "avanço da medicina oral em benefício do paciente; tópicos: cirurgia "
            "maxilofacial e oral, prótese e odontologia restauradora, dentística "
            "operatória, endodontia, periodontia, ortodontia, materiais dentários, "
            "ensaios clínicos, epidemiologia, implantodontia oral, patologia oral."
        ),
        priority=(
            "Original scientific articles e invited reviews que informem leitura "
            "internacional com resultados atualizados de estudos básicos e clínicos "
            " e esclareçam a relevância para a prática moderna; abstract estruturado "
            "150-250 palavras (Objectives/Materials and Methods/Results/Conclusions/"
            "Clinical Relevance); Case Reports geralmente desencorajados."
        ),
        reference_style="Springer (estilo específico do periódico; referências numeradas/alfabéticas conforme template)",
        length_limit=(
            "Original Research: corpo 4.000 palavras (excl. abstract, tab/fig, "
            "refs) + 6 tab/fig + 60 refs; Review: abstract estruturado 150-250; "
            "Opinion/Comment: 1.500-3.000 palavras + 4 tab/fig + 60 refs, abstract "
            "não estruturado 200 palavras"
        ),
        review_flow=(
            "single-blind (revisores conhecem autores; relatórios anônimos); "
            "editorial desk + ≥2 revisores; 1ª decisão mediana ~6 dias; COPE; "
            "se fora do escopo, Editor devolve sem enviar para revisão"
        ),
        special_gates=[
            "Abstract estruturado 150-250 palavras com Objectives/Materials and "
            "Methods/Results/Conclusions/Clinical Relevance (obrigatório)",
            "Clinical Relevance no resumo (implicação clínica explícita)",
            "Case Reports geralmente desencorajados",
            "COPE (má conduta, autoria, conflitos, retratação)",
            "Arquivos editáveis obrigatórios (.docx/LaTeX); sem fonte editável → "
            "não considerado para revisão",
        ],
        weights={
            "evidências": 1.8, "metodologia": 1.6, "ética": 1.5,
            "reprodutibilidade": 1.5, "estatística": 1.5, "relevância": 1.4,
            "originalidade": 1.2, "clareza": 1.2, "coerência": 1.2,
            "impacto": 1.2, "redação": 1.0, "teoria": 0.9,
        },
        source="https://link.springer.com/journal/784/submission-guidelines + https://link.springer.com/journal/784/aims-and-scope",
    ),
    "Medical Image Analysis": EditorialProfile(
        journal="Medical Image Analysis (Elsevier/MICCAI Society)",
        scope=(
            "Fórum para disseminação de novos resultados de pesquisa em análise "
            "de imagens médicas e biológicas, com ênfase em aplicações de visão "
            "computacional, realidade virtual e robótica a problemas de imagem "
            "biomédica; conjuntos de dados em todas as escalas espaciais "
            "(molecular/celular a tecido/órgão); periódico oficial da MICCAI "
            "Society."
        ),
        priority=(
            "Papers originais de altíssima qualidade com contribuição à ciência "
            "básica do processamento/análise/uso de imagens médicas e biológicas; "
            "algoritmos e estratégias baseadas em modelos (geométricos, "
            "estatísticos, físicos, funcionais) para representação, visualização, "
            "extração de features, segmentação, registro, estudos longitudinais/"
            "temporais, cirurgia guiada, textura/forma/movimento, atlas anatômicos, "
            "anatomia computacional, fisiologia computacional, VR/AR para terapia, "
            "telemedicina/telerobótica."
        ),
        reference_style="Elsevier (estilo da revista; referências autor-data ou numérica conforme template)",
        length_limit=(
            "Sem limite rígido declarado no guia (formato padrão do periódico); "
            "word single-column ou LaTeX double-column; gráficos/suplementos são "
            "encorajados"
        ),
        review_flow=(
            "single anonymized review (autores ocultos dos revisores); triagem "
            "editorial + mínimo de 2 revisores independentes; MICCAI Society journal"
        ),
        special_gates=[
            "Contribuição metodológica/algorítmica frente ao estado da arte "
            "(não apenas aplicação)",
            "Validação experimental em conjuntos de dados biomédicos",
            "≥2 revisores independentes para avaliação de qualidade científica",
            "Formato: Word single-column; LaTeX double-column permitido; PDF não é "
            "fonte aceitável",
            "Graṕhical abstract recomendado (resumo pictórico do conteúdo)",
        ],
        weights={
            "metodologia": 1.9, "originalidade": 1.8, "teoria": 1.5,
            "reprodutibilidade": 1.6, "estatística": 1.5, "evidências": 1.4,
            "clareza": 1.3, "coerência": 1.3, "impacto": 1.3,
            "relevância": 1.2, "redação": 1.0, "ética": 0.9,
        },
        source="https://www.sciencedirect.com/journal/medical-image-analysis/publish/guide-for-authors",
    ),
    "Artificial Intelligence in Medicine": EditorialProfile(
        journal="Artificial Intelligence in Medicine (Elsevier)",
        scope=(
            "Artigos originais interdisciplinares sobre teoria e prática de IA em "
            "medicina, biologia orientada à medicina e saúde; áreas: decisão "
            "clínica baseada em IA, engenharia do conhecimento médico, sistemas "
            "baseados em conhecimento e agentes, inteligência computacional em "
            "bio/clínica, sistemas inteligentes e process-aware em saúde, NLP em "
            "medicina, questões metodológicas/filosóficas/éticas/sociais da IA "
            "em saúde."
        ),
        priority=(
            "Novidade metodológica e/ou teórica em IA e Ciência da Computação "
            "claramente demonstrada; alto impacto potencial em domínio médico ou "
            "de saúde; aplicação de algoritmos já publicados a dados médicos NÃO é "
            "considerada pesquisa original de interesse; inglês claro e revisado "
            "(exposição fraca → rejeição)."
        ),
        reference_style="Elsevier (estilo da revista; referências numeradas com DOI)",
        length_limit=(
            "Sem limite rígido de palavras declarado; tipos: artigos originais, "
            "revisões, cartas ao editor, book reviews, in memoriam; special issues"
        ),
        review_flow=(
            "Editorial triage + revisão por pares (Elsevier); declaração de IA "
            "generativa obrigatória na submissão; revisores/editores proibidos de "
            "submeter manuscrito a ferramentas de IA"
        ),
        special_gates=[
            "Novidade metodológica/teórica em IA e CS OBRIGATÓRIA (mera aplicação "
            "de algoritmos conhecidos rejeitada)",
            "Declaração de uso de IA generativa obrigatória na submissão "
            "(ferramenta, propósito, revisão humana)",
            "Revisores/editores proibidos de submeter manuscrito a IA (proteção à "
            "confidencialidade)",
            "Inglês de alta qualidade exigido (revisão por falantes fluentes ou "
            "serviços de edição)",
            "Alto impacto em domínio médico/saúde demonstrado",
        ],
        weights={
            "originalidade": 1.9, "metodologia": 1.8, "teoria": 1.7,
            "reprodutibilidade": 1.5, "impacto": 1.5, "estatística": 1.4,
            "ética": 1.4, "evidências": 1.4, "clareza": 1.3,
            "coerência": 1.2, "relevância": 1.2, "redação": 1.1,
        },
        source="https://www.sciencedirect.com/journal/artificial-intelligence-in-medicine/publish/guide-for-authors",
    ),
    "Journal of Biomedical Informatics": EditorialProfile(
        journal="Journal of Biomedical Informatics (Elsevier/AMIA)",
        scope=(
            "Periódico de metodologia da informática biomédica; novas metodologias "
            "e técnicas de aplicação geral que formam a base da ciência da "
            "informática biomédica; endossado pela AMIA; foco em decisão clínica, "
            "segurança do paciente, NLP, IA/ML, representação de conhecimento, "
            "bioinformática translacional, informática clínica."
        ),
        priority=(
            "Método/tecnica novo com aplicação geral (não apenas aplicação ou "
            "avaliação); problema biomédico/clínico real + abordagem inovadora + "
            "avaliação frente ao estado da arte (SoA); envolvimento de profissionais "
            "de saúde na motivação e avaliação esperado; Special Communication para "
            "lições generalizáveis de projetos de métodos existentes."
        ),
        reference_style="Elsevier (estilo da revista; referências numeradas com DOI)",
        length_limit=(
            "Sem limite rígido de palavras declarado; tipos: research papers, "
            "methodological reviews, special communications, commentaries, letters, "
            "book reviews, editorials"
        ),
        review_flow=(
            "single anonymized review (autores ocultos; revisores visíveis ao "
            "editor); triagem editorial + mínimo de 2 revisores independentes; "
            "timeline: ~2 dias 1ª decisão, ~49 dias pós-review, ~142 dias até "
            "aceite, ~8 dias aceite→online; APC OA USD 3.550"
        ),
        special_gates=[
            "Metodologia NOVA com aplicação geral obrigatória (não apenas "
            "aplicação de método existente)",
            "Problema clínico/healthcare real + comparação com estado da arte (SoA)",
            "Envolvimento de profissionais de saúde na motivação/avaliação esperado",
            "Special Communication para lições generalizáveis de métodos existentes",
            "APC Open Access USD 3.550 (opcional; via assinatura sem taxa)",
        ],
        weights={
            "metodologia": 1.9, "originalidade": 1.7, "teoria": 1.6,
            "reprodutibilidade": 1.7, "evidências": 1.5, "estatística": 1.4,
            "ética": 1.3, "clareza": 1.3, "coerência": 1.2,
            "relevância": 1.4, "impacto": 1.3, "redação": 1.0,
        },
        source="https://www.sciencedirect.com/journal/journal-of-biomedical-informatics/publish/guide-for-authors",
    ),
    "npj Digital Medicine": EditorialProfile(
        journal="npj Digital Medicine (Nature Portfolio)",
        scope=(
            "Interseção de tecnologia digital e saúde: IA, aprendizado de máquina, "
            "intervenções digitais de saúde para melhorar desfechos de pacientes e "
            "sistemas de saúde; biomarcadores digitais, wearables e monitoramento "
            "remoto, NLP generativo, privacidade e ética em saúde digital, "
            "regulação/política; ponte tecnologia ↔ prática clínica."
        ),
        priority=(
            "Article (pesquisa primária substancial; sistemáticas/escopo/"
            "meta-análises submetidos como Article, não como Review); título ≤15 "
            "palavras; abstract ≤150 palavras sem subheadings; introdução sem "
            "subheadings; métodos com subheadings; CONSORT para RCTs; Data "
            "Availability Statement obrigatório; sem limites estritos de palavras "
            "(online only)."
        ),
        reference_style="Nature Portfolio (referências numeradas com DOI)",
        length_limit=(
            "Sem limites estritos de palavras/páginas (online only, fully Open "
            "Access); recomenda-se concisão; refs ~60 (guideline, não estrito); "
            "figure legends ≤350 palavras"
        ),
        review_flow=(
            "Editorial triage + revisão por pares (Nature Portfolio); 1ª decisão "
            "~5 dias; formatos só na aceitação (1ª submissão sem formatação "
            "estrita); cover letter + arquivo editável + checklists obrigatórios"
        ),
        special_gates=[
            "Abstract ≤150 palavras, sem subheadings (Article)",
            "CONSORT + extensões para RCTs (checklist no Supplementary)",
            "Data Availability Statement obrigatório",
            "Competing Interests obrigatório para todos os autores",
            "Sistemáticas/escopo/meta-análises como Article (não como Review)",
            "Cover letter obrigatório na submissão",
        ],
        weights={
            "evidências": 1.8, "impacto": 1.7, "relevância": 1.7,
            "reprodutibilidade": 1.7, "ética": 1.6, "metodologia": 1.6,
            "originalidade": 1.5, "estatística": 1.5, "clareza": 1.2,
            "coerência": 1.1, "redação": 1.0, "teoria": 1.0,
        },
        source="https://www.nature.com/npjdigitalmed/for-authors-and-referees/submission-guidelines + https://www.nature.com/npjdigitalmed/content-types",
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
        reference_style="APA (normas American Psychological Association; www.apa.org)",
        length_limit="Máx. 20 páginas (entrevistas, outros temas, resenhas, traduções); até 4 autores (3 em resenhas/traduções)",
        review_flow=(
            "Análise de forma com 8 critérios de rejeição (revisão bibliográfica "
            "isolada, recorte de tese, projeto/relatório, sem consistência teórica, "
            "meramente descritivo, sem eixo Educação, fora das normas, sem avanços) "
            "+ duplo-cega com ≥2 pareceristas; reformulações em 30 dias; Turnitin; "
            "editor tem decisão final"
        ),
        special_gates=[
            "Folha de rosto separada obrigatória na submissão",
            "Declaração de IA obrigatória: informar uso em qualquer etapa da pesquisa "
            "(ferramenta e uso; OMISSÃO = infração ética)",
            "Turnitin para identificação de plágio",
            "Ciência aberta incentivada (dados em repositórios)",
            "Preprint deve ser informado",
            "Titulação mínima: doutorado em andamento (a depender da seção)",
            "CC BY 4.0; sem APCs",
        ],
        weights={
            "metodologia": 1.5, "ética": 1.4, "evidências": 1.3,
            "originalidade": 1.3, "teoria": 1.2, "coerência": 1.1,
            "reprodutibilidade": 1.2, "clareza": 1.0, "redação": 1.0,
            "estatística": 1.0, "relevância": 1.0, "impacto": 1.0,
        },
        source="https://revistaseletronicas.pucrs.br/faced/about",
    ),
    # ── Computação Quântica (R-976.19, pesquisado 2026-09-24) ─────
    "npj Quantum Information": EditorialProfile(
        journal="npj Quantum Information (Nature Portfolio)",
        scope=(
            "Pesquisa em ciência da informação quântica: computação quântica, "
            "comunicação quântica, teoria da informação quântica, metrologia, "
            "sensoriamento e criptografia quântica; importantes avanços em "
            "informação quântica e teoria, incluindo computação e comunicação "
            "quânticas."
        ),
        priority=(
            "Research article (pesquisa primária substancial de impacto claro à "
            "área); Reviews & Analysis; News & Comment; deduplicação contra arXiv "
            "(política de pré-print no Nature Portfolio); título conciso; "
            "abstract estruturado; contribuições de autores definidas."
        ),
        reference_style="Nature Portfolio (referências numeradas com DOI; citações com superscript)",
        length_limit=(
            "Sem limites estritos de palavras (online only; OA); recomenda-se "
            "concisão; figure legends e tabelas conforme guia; ~50–70 referências "
            "em artigos de pesquisa (orientativo, não estrito)"
        ),
        review_flow=(
            "Editorial triage + revisão por pares (Nature Portfolio); 1ª decisão "
            "mediana ~5 dias; formatos apenas na aceitação; cover letter + "
            "checklists/reporting summary obrigatórios na submissão; políticas "
            "editoriais do Nature Portfolio (deduplicação, preprint, IA generativa)"
        ),
        special_gates=[
            "Open access: CC BY; APC aplicável",
            "Cover letter obrigatório na submissão",
            "Reporting summary / checklists editoriais na submissão",
            "Deduplicação: manuscritos já publicados em arXiv devem ser informados "
            "na submissão",
            "Política de IA generativa do Nature Portfolio declarada na submissão",
            "Contribuições de autores (CRediT) verificadas",
        ],
        weights={
            "originalidade": 1.8, "evidências": 1.7, "metodologia": 1.7,
            "impacto": 1.7, "relevância": 1.6, "reprodutibilidade": 1.6,
            "teoria": 1.5, "estatística": 1.4, "ética": 1.3,
            "clareza": 1.2, "coerência": 1.1, "redação": 1.0,
        },
        source="https://www.nature.com/npjqi/for-authors-and-referees + https://www.nature.com/npjqi/content-types",
    ),
    "Quantum": EditorialProfile(
        journal="Quantum — The open journal for quantum science",
        scope=(
            "Resultados de destaque em ciência quântica: computação, informação, "
            "tecnologia e fundamentos; periódico overlay publicado sobre arXiv "
            "(quant-ph), revisão por pares rigorosa e transparente."
        ),
        priority=(
            "Submissão via arXiv (quant-ph) seguida de pedido de avaliação; "
            "altamente seletiva — apenas trabalhos tecnicamente corretos, "
            "significativos, claros e reprodutíveis com reivindicações honestas "
            "e dentro do escopo; contributions obrigatórias; disclosure de uso "
            "de LLM na submissão."
        ),
        reference_style="Estilo livre (sem formato obrigatório; referências claras e completas)",
        length_limit=(
            "SEM limite de formato nem de comprimento (explicitamente declarado); "
            "qualquer estilo de escrita permitido"
        ),
        review_flow=(
            "Submissão via arXiv (quant-ph) + pedido de avaliação; revisão por "
            "pares aberta com pareceristas nomeados (transparência); sem taxas de "
            "publicação (APC zero); decisão editorial após consulta aos pareceristas"
        ),
        special_gates=[
            "Submissão obrigatoriamente via arXiv (quant-ph)",
            "Sem taxas: APC zero",
            "Sem limite de formato/comprimento (explícito)",
            "Critérios de avaliação: correção técnica, significância, clareza e "
            "reprodutibilidade, reivindicações honestas e escopo",
            "Contributions obrigatórias; disclosura de uso de LLM na submissão",
            "Revisão por pares com pareceristas nomeados (open peer review)",
        ],
        weights={
            "originalidade": 1.8, "teoria": 1.7, "metodologia": 1.7,
            "evidências": 1.6, "reprodutibilidade": 1.6, "impacto": 1.6,
            "relevância": 1.5, "clareza": 1.4, "estatística": 1.4,
            "ética": 1.3, "coerência": 1.2, "redação": 1.0,
        },
        source="https://quantum-journal.org/authors/",
    ),
    "Quantum Science and Technology": EditorialProfile(
        journal="Quantum Science and Technology (IOP Publishing)",
        scope=(
            "Resultados e perspectivas em ciência e tecnologia quânticas, teóricos "
            "e experimentais; criptografia, simulação, metrologia, engenharia, "
            "sensoriamento, comunicação, computação, biologia, materiais, "
            "controle, sistemas híbridos, termodinâmica, machine learning e "
            "software quânticos."
        ),
        priority=(
            "Altamente seletivo: submissões devem ser 'essential reading' para "
            "um subcampo e de interesse da comunidade quântica mais ampla, com "
            "expectativa de impacto científico e tecnológico duradouro; Letters "
            "excepcionalmente concisas (justification statement exigido); Papers "
            "de pesquisa original com avanço significativo; Topical reviews "
            "convidadas; Roadmaps (perspectivas de 2–3 páginas por seção)."
        ),
        reference_style="IOP (estilo da revista; referências numeradas; templates IOP)",
        length_limit=(
            "Letters: concisas ('outstanding concise articles'); Papers: sem "
            "limite rígido declarado, mas comprimento deve ser justificado pelo "
            "conteúdo; Topical reviews convidadas; Roadmaps: 2–3 páginas por seção"
        ),
        review_flow=(
            "Peer review single anonymous (autores ocultos; revisores visíveis ao "
            "editor); triagem editorial rigorosa; Letters com tratamento "
            "prioritário; Roadmaps por convite do Conselho Editorial"
        ),
        special_gates=[
            "Exigência de 'essential reading' + interesse da comunidade ampla + "
            "impacto duradouro (alto limiar de seletividade)",
            "Letters exigem justification statement na submissão",
            "Topical reviews tipicamente convidadas pelo Conselho Editorial",
            "Artigos longos aceitos somente se o comprimento for justificado "
            "pelo conteúdo científico",
            "Preprint policy IOP: pré-prints permitidos (arquivamento em repositórios)",
        ],
        weights={
            "originalidade": 1.8, "impacto": 1.7, "teoria": 1.6,
            "metodologia": 1.6, "evidências": 1.6, "relevância": 1.6,
            "reprodutibilidade": 1.5, "estatística": 1.4, "ética": 1.2,
            "clareza": 1.2, "coerência": 1.1, "redação": 1.0,
        },
        source="https://publishingsupport.iopscience.iop.org/journals/quantum-science-technology/about-quantum-science-technology",
    ),
    "IEEE Transactions on Quantum Engineering": EditorialProfile(
        journal="IEEE Transactions on Quantum Engineering (TQE)",
        scope=(
            "Engenharia de aplicações de fenômenos quânticos: computação quântica, "
            "informação, comunicação, software, hardware, dispositivos e metrologia; "
            "inclui supercondutividade, magnética, micro-ondas, fotônica e "
            "processamento de sinais; artigos regulares, de revisão e tutoriais."
        ),
        priority=(
            "Regular papers (contribuição de engenharia original), review papers "
            "e tutorial papers; foco em engenharia de aplicações quânticas — "
            "não apenas física fundamental; rigor técnico e reprodutibilidade."
        ),
        reference_style="IEEE (templates IEEE; referências numeradas [1]; formato dupla coluna na versão final)",
        length_limit=(
            "SEM page limit (all-electronic, contínuo); recomenda-se concisão; "
            "apêndices e suplementos aceitos"
        ),
        review_flow=(
            "Peer review duplo-cego (IEEE); gold open access; publicação "
            "contínua (online first); APC USD 1.995 (efetivo 01/01/2024; desconto "
            "IEEE members 5%, Society members 20%, não combináveis); submissão "
            "via IEEE Author Portal"
        ),
        special_gates=[
            "Gold open access; APC USD 1.995 (descontos IEEE 5% / Society 20%, "
            "não combináveis)",
            "Sem page limit declarado (all-electronic)",
            "Tipos: regular, review e tutorial papers",
            "Escopo de engenharia (supercondutividade, magnética, micro-ondas, "
            "fotônica, processamento de sinais)",
            "Templates IEEE obrigatórios na submissão",
        ],
        weights={
            "metodologia": 1.7, "originalidade": 1.7, "evidências": 1.6,
            "impacto": 1.6, "reprodutibilidade": 1.6, "teoria": 1.5,
            "estatística": 1.4, "ética": 1.3, "relevância": 1.4,
            "clareza": 1.2, "coerência": 1.1, "redação": 1.0,
        },
        source="https://tqe.ieee.org/submission-process",
    ),
    "ACM Transactions on Quantum Computing": EditorialProfile(
        journal="ACM Transactions on Quantum Computing (ACM TQC)",
        scope=(
            "Computação quântica e informações quânticas: algoritmos, arquiteturas, "
            "software, hardware, correção de erros, teoria da complexidade e "
            "aplicações; publicação da ACM com transição 100% Open Access em "
            "01/01/2026."
        ),
        priority=(
            "Pesquisa original substancial com avanço claro; conferências "
            "estendidas: manuscritos estendidos de conferências devem declarar "
            "substancial novidade; regular papers e revisões; revisores seniores "
            "por seção (Senior Associate Editors)."
        ),
        reference_style="ACM (templates ACM; referências numeradas; ORCID obrigatório)",
        length_limit=(
            "Sem limite rígido de páginas declarado; comprimento conforme "
            "necessidade do conteúdo; revisões extensas aceitas"
        ),
        review_flow=(
            "Submissões via Manuscript Central (desde 01/01/2026); revisão: Editor-"
            "in-Chief → seção da revista → Senior Associate Editors → pareceristas; "
            "revised manuscripts esperados em 30 dias para minor revisions; "
            "transição 100% Open Access (APC com waivers/discounts conforme "
            "políticas ACM)"
        ),
        special_gates=[
            "Transição 100% Open Access (01/01/2026); APC com waivers/discounts",
            "ORCID obrigatório para autores",
            "Manuscritos estendidos de conferências devem declarar substancial "
            "novidade",
            "Revisão hierárquica: EIC → seção → Senior Associate Editors",
            "Revised manuscripts em 30 dias para minor revisions",
            "Templates ACM obrigatórios",
        ],
        weights={
            "originalidade": 1.8, "teoria": 1.7, "metodologia": 1.6,
            "evidências": 1.6, "impacto": 1.6, "reprodutibilidade": 1.6,
            "relevância": 1.5, "estatística": 1.4, "ética": 1.4,
            "clareza": 1.2, "coerência": 1.1, "redação": 1.0,
        },
        source="https://dl.acm.org/journal/tqc/author-guidelines",
    ),
    "Quantum Information Processing": EditorialProfile(
        journal="Quantum Information Processing (Springer)",
        scope=(
            "Processamento e transmissão de informação quântica: computação "
            "quântica, comunicação, criptografia, simulação, algoritmos, "
            "hardware/software quânticos e temas correlatos."
        ),
        priority=(
            "Artigo original com contribuição clara; revisões solicitadas; "
            "abstract 150–250 palavras; fonte editável + PDF obrigatórios; "
            "recomenda-se template LaTeX; linguagem: inglês."
        ),
        reference_style="Springer (estilo da revista; referências numeradas com DOI; template LaTeX recomendado)",
        length_limit=(
            "Abstract 150–250 palavras; sem limite rígido de comprimento do "
            "corpo; concisão recomendada"
        ),
        review_flow=(
            "Peer review single-blind (autores anônimos para revisores? não — "
            "single-blind: autores identificados, revisores anônimos); triagem "
            "editorial (desk review); avaliação por pareceristas externos; "
            "Springer Nature policies (similarity check)"
        ),
        special_gates=[
            "Single-blind peer review",
            "Abstract 150–250 palavras",
            "Fonte editável (.tex/.docx) + PDF obrigatórios na submissão",
            "Template LaTeX recomendado (Springer)",
            "Língua inglesa",
        ],
        weights={
            "metodologia": 1.6, "originalidade": 1.6, "teoria": 1.5,
            "evidências": 1.5, "reprodutibilidade": 1.5, "impacto": 1.4,
            "relevância": 1.4, "estatística": 1.3, "ética": 1.2,
            "clareza": 1.2, "coerência": 1.1, "redação": 1.0,
        },
        source="https://link.springer.com/journal/11128/submission-guidelines",
    ),
    # ── Direito (R-976.19, pesquisado 2026-09-24) ────────────────
    "Revista Direito GV": EditorialProfile(
        journal="Revista Direito GV (FGV Direito SP)",
        scope=(
            "Pesquisa jurídica de qualidade em perspectiva crítica e reflexiva: "
            "direito, instituições, regulação e sociedade; recebe artigos "
            "inéditos de autores nacionais e estrangeiros; adota ciência aberta "
            "com duplo-cego (simples-cego quando há preprint)."
        ),
        priority=(
            "Artigos inéditos de pesquisa jurídica; desidentificação obrigatória; "
            "resenhas ≤2.000 palavras (incluindo referências); 5 palavras-chave "
            "em PT/EN/ES; adequação temático-metodológica e atendimento a "
            "requisitos formais avaliados no desk review."
        ),
        reference_style="ABNT (com adaptações editoriais da revista; notas de rodapé para citações)",
        length_limit=(
            "Resenhas: máximo 2.000 palavras (INCLUINDO referências); artigos: "
            "extensão conforme gênero acadêmico, com limite superior orientativo; "
            "resumo com 5 palavras-chave em português, inglês e espanhol"
        ),
        review_flow=(
            "Desk review preliminar (ineditismo, adequação temático-metodológica, "
            "requisitos formais); duplo-cego; preprint declarado → avaliação "
            "simples-cego (revisor conhece autoria); submissão via ScholarOne; "
            "sem taxas de submissão/publicação; software de similaridade"
        ),
        special_gates=[
            "Desidentificação obrigatória (sem nome/afiliação no corpo do texto)",
            "5 palavras-chave em português, inglês e espanhol",
            "Preprint declarado → duplo-cego muda para simples-cego",
            "Sem submissão simultânea em outro periódico",
            "Sem taxas (APC zero)",
            "Software de similaridade na triagem",
            "Resenha ≤2.000 palavras incluindo referências",
        ],
        weights={
            "originalidade": 1.6, "teoria": 1.5, "clareza": 1.4,
            "evidências": 1.4, "relevância": 1.4, "metodologia": 1.4,
            "ética": 1.3, "coerência": 1.3, "redação": 1.3,
            "impacto": 1.2, "estatística": 1.0, "reprodutibilidade": 1.0,
        },
        source="https://periodicos.fgv.br/revdireitogv/politicaeditorial",
    ),
    "Revista Direito e Práxis": EditorialProfile(
        journal="Revista Direito e Práxis (UERJ)",
        scope=(
            "Crítica do direito, teoria e filosofia do direito, sociologia e "
            "história do direito; trilíngue (português, inglês, espanhol); "
            "dossiês temáticos e fluxo contínuo."
        ),
        priority=(
            "Artigos inéditos com contribuição crítica e original; adequação ao "
            "escopo; dupla avaliação por pares ad hoc (avaliadores de programas "
            "de pós-graduação stricto sensu); 3º avaliador se divergência; "
            "declaração rigorosa de conflito de interesses."
        ),
        reference_style="ABNT (citações e referências conforme normas; adaptações editoriais da revista)",
        length_limit=(
            "Sem limite rígido de palavras publicado; extensão compatível com o "
            "gênero acadêmico; resumo + palavras-chave em 3 idiomas"
        ),
        review_flow=(
            "Desk review editorial em duas etapas: triagem inicial sem "
            "identificação (autores informados em até 30 dias se não adequado) + "
            "avaliação duplo-cega com 2 avaliadores ad hoc (professores/"
            "pesquisadores de stricto sensu); 3º avaliador em caso de divergência; "
            "preprints permitidos (SciELO/arXiv/bioRxiv/medRxiv); sem APC"
        ),
        special_gates=[
            "Desk review com resposta em até 30 dias quando fora do escopo",
            "Duplo-cega com 2 avaliadores ad hoc",
            "3º avaliador em caso de divergência",
            "Declaração de conflito de interesses (vínculos, honorários, "
            "financiamento, patentes, conselhos editoriais)",
            "Preprints permitidos (SciELO/arXiv/bioRxiv/medRxiv)",
            "Sem APC; trilíngue PT/EN/ES",
        ],
        weights={
            "originalidade": 1.6, "teoria": 1.6, "metodologia": 1.4,
            "clareza": 1.4, "redação": 1.3, "coerência": 1.3,
            "evidências": 1.3, "ética": 1.4, "relevância": 1.3,
            "impacto": 1.2, "estatística": 1.0, "reprodutibilidade": 1.0,
        },
        source="https://www.e-publicacoes.uerj.br/revistaceaju/about/submissions",
    ),
    "Revista de Direito Administrativo": EditorialProfile(
        journal="Revista de Direito Administrativo (RDA, FGV Direito Rio)",
        scope=(
            "Direito administrativo e áreas afins; publicação mais antiga do "
            "direito administrativo brasileiro (desde 1945); doutrina, "
            "jurisprudência comentada e atualidades."
        ),
        priority=(
            "Artigos doutrinários de autores com titulação mínima de doutor; "
            "máximo 2 autores (pelo menos 1 doutor); sem inclusão de coautor "
            "após submissão; pareceristas doutores na área."
        ),
        reference_style="ABNT (referências conforme NBR 6023; citações no padrão da revista)",
        length_limit=(
            "Extensão conforme gênero doutrinário; sem limite rígido publicado; "
            "resumo e palavras-chave (PT/EN)"
        ),
        review_flow=(
            "Desk review com resposta em até 15 dias; avaliação por 2–3 "
            "pareceristas doutores por área (duplo-cega); autores mantêm direitos "
            "autorais; primeira publicação (não exclusiva) cedida à FGV Direito "
            "Rio; restrições de preprint"
        ),
        special_gates=[
            "Desk review com resposta em até 15 dias",
            "Titulação mínima: doutor (autores e pareceristas)",
            "Máximo 2 autores (pelo menos 1 doutor)",
            "Sem inclusão de autor após submissão",
            "2–3 pareceristas doutores por área",
            "Licença CC BY-NC-ND 4.0",
            "ABNT obrigatória",
        ],
        weights={
            "teoria": 1.7, "originalidade": 1.6, "clareza": 1.5,
            "redação": 1.4, "coerência": 1.4, "ética": 1.4,
            "evidências": 1.3, "relevância": 1.3, "metodologia": 1.3,
            "impacto": 1.2, "estatística": 1.0, "reprodutibilidade": 1.0,
        },
        source="https://periodicos.fgv.br/rda/about/submissions",
    ),
    "Seqüência (UFSC)": EditorialProfile(
        journal="Seqüência — Estudos Jurídicos e Políticos (UFSC)",
        scope=(
            "Estudos jurídicos e políticos com pluralismo teórico-metodológico; "
            "direito, política, constitucionalismo, teoria do direito, "
            "hermenêutica e áreas afins; periódico do Programa de Pós-Graduação "
            "em Direito da UFSC."
        ),
        priority=(
            "Artigos inéditos com consistência teórica e metodológica; adequação "
            "ao escopo; avaliação duplo-cega; verificação antiplágio via "
            "iThenticate; fluxo contínuo."
        ),
        reference_style="ABNT (NBR 6023: referências; citações conforme norma vigente)",
        length_limit=(
            "Extensão conforme gênero acadêmico; resumo e palavras-chave em "
            "português e inglês (e espanhol quando aplicável)"
        ),
        review_flow=(
            "Avaliação duplo-cega (pareceristas externos); desk review inicial; "
            "iThenticate para verificação de plágio; CC BY 4.0; sem taxas de "
            "submissão/publicação; fluxo contínuo"
        ),
        special_gates=[
            "Avaliação duplo-cega",
            "iThenticate para verificação de plágio",
            "CC BY 4.0; sem taxas",
            "ABNT obrigatória",
            "Fluxo contínuo",
        ],
        weights={
            "teoria": 1.6, "originalidade": 1.5, "metodologia": 1.4,
            "clareza": 1.4, "coerência": 1.3, "redação": 1.3,
            "ética": 1.3, "evidências": 1.2, "relevância": 1.3,
            "impacto": 1.1, "estatística": 1.0, "reprodutibilidade": 1.0,
        },
        source="https://periodicos.ufsc.br/index.php/sequencia/about/submissions",
    ),
    "Revista de Estudos Empíricos em Direito": EditorialProfile(
        journal="Revista de Estudos Empíricos em Direito (REED)",
        scope=(
            "Pesquisa empírica em direito: estudos quantitativos e qualitativos "
            "que usam dados e evidências para compreender o fenômeno jurídico; "
            "editorial com ciência aberta (avaliadores nomeados publicamente)."
        ),
        priority=(
            "Artigos com pesquisa empírica explícita (dados, métodos e "
            "evidências); avaliação duplo-cega com exogenia de pareceristas ≥75%; "
            "parecerista tem ~1 mês; avaliação média ~6 meses; ORCID obrigatório."
        ),
        reference_style="ABNT (com seção explícita de métodos; dados em apêndice)",
        length_limit=(
            "Extensão conforme pesquisa empírica; sem limite rígido publicado; "
            "resumo + palavras-chave"
        ),
        review_flow=(
            "Duplo-cega; pareceristas com exogenia ≥75% em relação aos autores; "
            "parecerista tem ~1 mês para avaliação; avaliação média de ~6 meses; "
            "nomes de avaliadores publicados (ciência aberta); formatos aceitos: "
            ".doc/.docx/.odt"
        ),
        special_gates=[
            "Foco em pesquisa empírica em direito (dados e evidências)",
            "Exogenia de pareceristas ≥75%",
            "Nomes de avaliadores publicados (ciência aberta)",
            "ORCID obrigatório",
            "Formatos .doc/.docx/.odt",
            "Avaliação média ~6 meses; parecerista ~1 mês",
        ],
        weights={
            "metodologia": 1.8, "evidências": 1.8, "estatística": 1.6,
            "reprodutibilidade": 1.6, "originalidade": 1.5, "ética": 1.5,
            "teoria": 1.3, "clareza": 1.3, "coerência": 1.2,
            "relevância": 1.3, "impacto": 1.2, "redação": 1.0,
        },
        source="https://revistareas.unifesp.br/index.php/reed/about",
    ),
    "Suprema (STF)": EditorialProfile(
        journal="Suprema — Revista de Estudos Constitucionais (STF)",
        scope=(
            "Estudos constitucionais: direito constitucional, teoria da "
            "constituição, jurisdição constitucional, direitos fundamentais; "
            "periodicidade semestral; aceita textos em português, inglês, espanhol, "
            "francês e italiano."
        ),
        priority=(
            "Artigos inéditos com contribuição original; até 3 coautores (titulação "
            "de doutor primordial); avaliação duplo-cega com ≥2 pareceristas "
            "externos; 3º parecerista em caso de impasse; fluxo contínuo."
        ),
        reference_style="ABNT (referências conforme NBR 6023; citações normatizadas)",
        length_limit=(
            "Extensão conforme gênero acadêmico; resumo e palavras-chave em "
            "português e em idioma estrangeiro"
        ),
        review_flow=(
            "Duplo-cega com ≥2 pareceristas externos; 3º parecerista em caso de "
            "impasse; desk review inicial; fluxo contínuo; sem taxas"
        ),
        special_gates=[
            "Duplo-cega com ≥2 pareceristas externos",
            "3º parecerista em caso de impasse",
            "Até 3 coautores (titulação de doutor primordial)",
            "Idiomas: PT/EN/ES/FR/IT",
            "Fluxo contínuo; sem taxas",
        ],
        weights={
            "teoria": 1.7, "originalidade": 1.6, "clareza": 1.4,
            "redação": 1.3, "coerência": 1.3, "ética": 1.3,
            "evidências": 1.2, "relevância": 1.3, "metodologia": 1.3,
            "impacto": 1.2, "estatística": 1.0, "reprodutibilidade": 1.0,
        },
        source="https://suprema.stf.jus.br/index.php/suprema/about/submissions",
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
    "jdr": "Journal of Dental Research",
    "journal of dental research": "Journal of Dental Research",
    "dental research": "Journal of Dental Research",
    "coi": "Clinical Oral Investigations",
    "clinical oral investigations": "Clinical Oral Investigations",
    "clinical oral investigations (springer)": "Clinical Oral Investigations",
    "mia": "Medical Image Analysis",
    "medical image analysis": "Medical Image Analysis",
    "aiim": "Artificial Intelligence in Medicine",
    "artificial intelligence in medicine": "Artificial Intelligence in Medicine",
    "jbi": "Journal of Biomedical Informatics",
    "journal of biomedical informatics": "Journal of Biomedical Informatics",
    "npj": "npj Digital Medicine",
    "npj digital medicine": "npj Digital Medicine",
    "npj digital medicine (nature portfolio)": "npj Digital Medicine",
    # ── Computação Quântica (R-976.19)
    "npjqi": "npj Quantum Information",
    "npj qi": "npj Quantum Information",
    "npj quantum information": "npj Quantum Information",
    "npj quantum information (nature portfolio)": "npj Quantum Information",
    "quantum": "Quantum",
    "quantum journal": "Quantum",
    "qst": "Quantum Science and Technology",
    "quantum science and technology": "Quantum Science and Technology",
    "quantum science and technology (iop)": "Quantum Science and Technology",
    "ieee tqe": "IEEE Transactions on Quantum Engineering",
    "tqe": "IEEE Transactions on Quantum Engineering",
    "transactions on quantum engineering": "IEEE Transactions on Quantum Engineering",
    "acm tqc": "ACM Transactions on Quantum Computing",
    "tqc": "ACM Transactions on Quantum Computing",
    "transactions on quantum computing": "ACM Transactions on Quantum Computing",
    "qip": "Quantum Information Processing",
    "quantum information processing": "Quantum Information Processing",
    # ── Direito (R-976.19)
    "direito gv": "Revista Direito GV",
    "revista direito gv": "Revista Direito GV",
    "direitogv": "Revista Direito GV",
    "direito e práxis": "Revista Direito e Práxis",
    "direito e praxis": "Revista Direito e Práxis",
    "revista direito e práxis": "Revista Direito e Práxis",
    "rda": "Revista de Direito Administrativo",
    "revista de direito administrativo": "Revista de Direito Administrativo",
    "sequencia": "Seqüência (UFSC)",
    "seqüência": "Seqüência (UFSC)",
    "sequencia ufsc": "Seqüência (UFSC)",
    "seqüência ufsc": "Seqüência (UFSC)",
    "reed": "Revista de Estudos Empíricos em Direito",
    "revista de estudos empíricos em direito": "Revista de Estudos Empíricos em Direito",
    "revista de estudos empiricos em direito": "Revista de Estudos Empíricos em Direito",
    "suprema": "Suprema (STF)",
    "suprema stf": "Suprema (STF)",
    "suprema revista de estudos constitucionais": "Suprema (STF)",
}


def _normalize_key(value: Optional[str]) -> str:
    """Normaliza texto para comparação de aliases (R-976.22):
    minúsculas, sem acentos, separadores não alfanuméricos viram espaço."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFD", value.lower())
    no_accents = "".join(
        c for c in decomposed if unicodedata.category(c) != "Mn"
    )
    return _re_space.sub(" ", _re_sep.sub(" ", no_accents)).strip()


def _alias_substring_match(norm: str, norm_alias: str) -> bool:
    """Substring segura entre termo normalizado e alias normalizado.

    Alias curtos (≤4 chars, ex.: 'eit', 'ire') só casam como PALAVRA
    delimitada — evita falso positivo "'eit' dentro de 'dir-eit-o'".
    Aliases longos casam por substring livre (ex.: 'direito e praxis'
    dentro de 'direito e praxis uerj').
    """
    if norm in norm_alias:
        return True
    if len(norm_alias) <= 4:
        return re.search(rf"\b{re.escape(norm_alias)}\b", norm) is not None
    return norm_alias in norm


def normalize_institution_alias(value: Optional[str]) -> str:
    """Normalização pública tolerante de alias de periódico (R-976.22).

    Ex.: "Educação / PUCRS" -> "educacao pucrs"
         "npj/quantum/information" -> "npj quantum information"
    """
    return _normalize_key(value)


# Índices normalizados (R-976.22) — canônicos e aliases resolvem variações
# de barra, parênteses, acento, hífen e caixa mista no get_profile().
_NORMALIZED_CANONICAL: Dict[str, str] = {
    _normalize_key(_k): _k for _k in EDITORIAL_PROFILES
}
_NORMALIZED_ALIASES: Dict[str, str] = {
    _normalize_key(_a): _c for _a, _c in JOURNAL_ALIASES.items()
}


def get_profile(journal_key: str) -> Optional[EditorialProfile]:
    """Recupera perfil editorial pelo nome; aceita aliases, parcial e caixa mista.

    R-976.22: além do match exato/alias histórico, normaliza o alvo
    (acentos, barras, parênteses, hífens, caixa mista) e procura em índices
    normalizados, preservando 100% de compatibilidade com os casos antigos.
    """
    if not journal_key:
        return None
    exact = EDITORIAL_PROFILES.get(journal_key)
    if exact:
        return exact
    # alias explícito (comportamento histórico, sem normalização)
    alias = JOURNAL_ALIASES.get(journal_key.strip().lower())
    if alias:
        return EDITORIAL_PROFILES.get(alias)
    # --- R-976.22: busca normalizada tolerante a acento/caixa/separadores ---
    norm = _normalize_key(journal_key)
    if norm:
        canonical_key = _NORMALIZED_CANONICAL.get(norm)
        if canonical_key:
            return EDITORIAL_PROFILES.get(canonical_key)
        canonical_key = _NORMALIZED_ALIASES.get(norm)
        if canonical_key:
            return EDITORIAL_PROFILES.get(canonical_key)
        # substring bidirecional sobre canônicos normalizados
        for norm_canon, canon_key in _NORMALIZED_CANONICAL.items():
            if norm in norm_canon or norm_canon in norm:
                return EDITORIAL_PROFILES.get(canon_key)
        # substring bidirecional sobre aliases normalizados
        for norm_alias, canon_key in _NORMALIZED_ALIASES.items():
            if _alias_substring_match(norm, norm_alias):
                return EDITORIAL_PROFILES.get(canon_key)
    # fallback substring histórica (preserva resultados antigos)
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