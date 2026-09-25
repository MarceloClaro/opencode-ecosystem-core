---
name: mirofish-offline
description: >-
  Simulação de opinião pública multi-agente no Core (SPEC-976). Use para
  prever reações a comunicados, políticas, notícias ou relatórios: gera perfis
  determinísticos de agentes, roda a simulação social em rounds (postar,
  curtir, repostar, argumentar), mede evolução de sentimento e produz relatório
  markdown estruturado. Use também para integrar o serviço externo
  MiroFish-Offline (AGPL-3.0) por composição via
  integrations.mirofish_offline. NÃO use para pesquisa empírica com humanos
  reais nem para decisões sem revisão humana.
disable-model-invocation: true
---

# MiroFish Social Simulation (SPEC-976)

## Quando usar

- Avaliar **reação pública** a um documento (press release, política, relatório financeiro).
- Testar **cenários de sentimento** (crise de PR, impacto de política, tendência de mercado).
- Gerar **insight determinístico** — sem LLM, sem Neo4j, 100% stdlib e com seed reprodutível.

## Pipeline (orquestrador)

1. **Preparar documento**: texto simples (extraia de PDF/MD/TXT antes).
2. **Gerar perfis**: `SimulationProfileGenerator(doc, n_agents, seed).generate()`
   — extrai tópicos por frequência de termos e cria N agentes heterogêneos
   (supportive/opposing/neutral/observer) com viés, influência e atividade.
3. **Simular**: `SocialSimulationEngine(profiles, params, seed).run(rounds)`
   — agentes ativos por faixa horária, ações (CREATE_POST/LIKE_POST/REPOST/
   QUOTE_POST/DO_NOTHING), sentimento médio por round, opinião final.
4. **Relatar**: `SocialReportGenerator(result).generate()` — markdown com
   Objetivo, Metodologia, Agentes, Linha do Tempo, Sentimento, Conclusão.
5. **Persistir**: estado em `.mci_state/mirofish_social_<id>.json`.

## Uso via orquestrador (recomendado)

```bash
python3 - <<'PY'
from marceloclaro.orchestrator import MarceloClaroOrchestrator
orch = MarceloClaroOrchestrator()
resumo = orch.mirofish_simulate(
    doc_text="Prefeitura anuncia faixas exclusivas para ônibus elétricos...",
    n_agents=20, rounds=24, seed=42,
    requirement="Avaliar reação pública ao plano de mobilidade",
)
print(resumo["final_sentiment"], resumo["post_count"])
print(resumo["report_md"][:500])
PY
```

## Banca editorial (R-976.11)

Simular a **opinião de uma banca de publicação** (PhDs por critério:
metodologia, estatística, ética, originalidade, clareza, relevância) sobre um
manuscrito de pesquisa:

```bash
python3 - <<'PY'
from mirofish.social.banca import BancaProfileGenerator, summarize_banca
from mirofish.social.contracts import (
    EventConfig, PlatformConfig, SimulationParameters, TimeSimulationConfig,
)
from mirofish.social.engine import SocialSimulationEngine

manuscrito = "SEU TEXTO DE PESQUISA AQUI..."
g = BancaProfileGenerator(manuscrito, n_members=6, seed=42)
members = g.generate()
params = SimulationParameters(
    simulation_id="banca_x",
    simulation_requirement="avaliar manuscrito",
    event_config=EventConfig(hot_topics=["metodologia", "estatística", "ética"]),
    twitter_config=PlatformConfig(platform="twitter", echo_chamber_strength=0.4),
    time_config=TimeSimulationConfig(total_simulation_hours=12, minutes_per_round=60),
)
result = SocialSimulationEngine([m.profile for m in members], params, seed=42).run(rounds=12)
resumo = summarize_banca(members, result.final_opinions)
print(resumo["verdict"], resumo["final_sentiment"])
print(resumo["by_criterion"])
PY
```

> **Importante**: `banca_verdict()` converte sentimento em ACEITAR /
> REVISÕES MENORES / REVISÕES MAIORES / REJEITAR. Isto é **SIMULAÇÃO** — não
> substitui revisão por pares real, nem constitui validação externa (R110
> anti-overclaim). Use como ensaio de submissão, não como decisor.

## Banca editorial ampliada (R-976.12/13)

Banca de **12 revisores** por 12 critérios com **peso do texto nas decisões**:
`text_signals()` detecta solidez textual por critério (PRISMA, JBI, κ, n=,
OSF, DOI, ABNT...) e modula os biases dos revisores — manuscrito forte em
um critério suaviza a postura rigorosa; fraco endurece. Veredito ponderado
0–100 + recomendação:

```bash
python3 - <<'PY'
from marceloclaro.orchestrator import MarceloClaroOrchestrator
orch = MarceloClaroOrchestrator()
r = orch.banca_simulate(DOC, n_members=12, rounds=12, seed=42,
                        requirement="avaliar revisão de escopo")
print(r["verdict"], r["weighted_score"], r["recommendation"])
print(r["text_signals"])   # sinais textuais por critério
print(r["strengths"], r["weaknesses"])
PY
```

- Instituições citadas são **rótulos de simulação** (Qualis A1 usado apenas
  para calibrar perfil; nunca parecer real) — ver `disclaimer` no resumo.
- `n_members>12` repete critérios com posturas distintas (mais granularidade).

## Perfis editoriais por periódico (R-976.14 a R-976.19)

`mirofish/social/editorial_profiles.py::EDITORIAL_PROFILES` registra **30
perfis** baseados em **normas públicas** de revistas Qualis A1/Q1 e
internacionais (RBE/ANPEd, Educação & Sociedade/CEDES, Cadernos de Pesquisa/FCC,
Práxis Educacional/UESB, Práxis Educativa/UEPG, Estudos em Avaliação
Educacional/FCC, Educação/PUCRS, Computers & Education/Elsevier, BJET/Wiley,
Education and Information Technologies/Springer, International Review of
Education/UNESCO UIL, **Journal of Dentistry/Elsevier**, **Journal of Dental
Research/IADR-Sage**, **Clinical Oral Investigations/Springer**, **Medical
Image Analysis/Elsevier-MICCAI**, **Artificial Intelligence in Medicine/
Elsevier**, **Journal of Biomedical Informatics/Elsevier-AMIA**, **npj Digital
Medicine/Nature Portfolio**, **6 de computação quântica** — npj Quantum
Information/Nature, Quantum/overlay arXiv, Quantum Science and Technology/IOP,
IEEE TQE, ACM TQC, Quantum Information Processing/Springer — e **6 de
direito** — Revista Direito GV/FGV, Revista Direito e Práxis/UERJ,
RDA/FGV, Seqüência/UFSC, REED, Suprema/STF): escopo, prioridade (perfil do
melhor artigo), estilo de referência, limite de tamanho, fluxo de revisão,
gates especiais (ex.: Educação & Sociedade e Computers & Education **não
aceitam IA generativa como autora**; disclosure obrigatória na Springer; JOD
exige **abstract com Clinical significance**; JDR exige **CSE 9ª ed.**; AIIM
exige **novidade metodológica em IA/CS**; npj exige **Data Availability
Statement**; Quantum é **overlay via arXiv com APC zero e sem limite de
formato**; Direito GV faz **duplo-cego → simples-cego se preprint**; RDA exige
**titulação mínima de doutor e máx. 2 autores**; REED publica **nomes de
avaliadores** — ciência aberta) e pesos por critério.

**Editais originais de educação confirmados (R-976.18,** sintetizados em
`mirofish/social/EDITAL_PERFIS_ORIGINAIS.md`):** RBE/ANPEd — 40–70 mil
caracteres c/ espaços **incluindo** refs/notas/título/resumo nos 3 idiomas,
ABNT obrigatória (senão não considerada), quebra de anonimato = rejeição;
E&S/CEDES — ~45.000 caracteres, Similarity Check, open evaluation opcional;
Cadernos de Pesquisa/FCC — iThenticate 2.0, fluxo em 8 etapas, CRediT;
Práxis Educacional/UESB — ABNT 6022/6028/10520, 3º parecerista em divergência,
≥1 doutor, máx. 3 autores; Computers & Education — ≤8.000 palavras (excl.
refs/apêndices), revisores proibidos de usar IA, arquivos editáveis (PDF não é
fonte); BJET — 5.000–6.000 palavras (excl. refs/abstracts/notas práticas/
apêndices), leeway via e-mail; EIT/Springer-IFIP — sem mudança de autoria,
fontes editáveis obrigatórias, **NÃO aceita review papers**; IRE/UNESCO —
artigos ≤6.000, research notes ≤3.000, book reviews ≤1.000, abstract 150–250,
4–6 keywords; Práxis Educativa/UEPG — 20–28 pp, APA, resumo ≤10 linhas + 3
keywords PT/EN/ES, **atualmente não aceita submissões**; EAE/FCC — 2 ad hoc +
parecer consolidado, preprint → simples anônimo; Educação/PUCRS — APA, folha de
rosto separada, declaração de IA obrigatória (omissão = infração ética),
Turnitin, ≤20 pp, ≤4 autores.

Perfis odontológicos: **JOD (Elsevier)** — Review máx. 10 pp impressas ≈ 33
processadas, NÃO aceita Case Reports, declaração IA antes das refs (ver
`mirofish/social/EDITAL_JOD_RIGOR_EDITORIAL.md`); **JDR (IADR/Sage)** —
Original Research 3.200 palavras + abstract 300 + CSE 9ª + ICMJE/CONSORT +
~17-18 dias 1ª decisão; **Clinical Oral Investigations (Springer)** —
single-blind, 4.000 palavras + abstract estruturado 150-250 com **Clinical
Relevance**, Case Reports desencorajados, ~6 dias 1ª decisão.

Perfis de outras áreas (método/IA/saúde): **Medical Image Analysis
(Elsevier/MICCAI)** — single anonymized + ≥2 revisores, contribuição
metodológica frente ao SoA, validação experimental em datasets biomédicos;
**Artificial Intelligence in Medicine (Elsevier)** — **novidade metodológica/
teórica em IA e CS obrigatória** (mera aplicação rejeitada), declaração de IA
generativa obrigatória, revisores proibidos de usar IA; **Journal of Biomedical
Informatics (Elsevier/AMIA)** — metodologia com aplicação geral, problema
clínico real + SoA, single anonymized, timeline 2/49/142 dias;
**npj Digital Medicine (Nature Portfolio)** — abstract ≤150 palavras sem
subheadings, **Data Availability obrigatório**, CONSORT p/ RCTs, sistemáticas
como Article, sem limites estritos, cover letter obrigatório, ~5 dias 1ª
decisão.

**Perfis de computação quântica (R-976.19,** sintetizados em
`mirofish/social/EDITAL_QUANTUM_DIREITO.md`):** **npj Quantum Information
(Nature Portfolio)** — OA CC BY, 1ª decisão ~5 dias, cover letter + reporting
summary/checklists na submissão, deduplicação vs arXiv; **Quantum (overlay
journal)** — submissão via **arXiv (quant-ph)**, **APC zero**, **sem limite de
formato/comprimento**, pareceristas nomeados, critérios: correção técnica/
significância/clareza/reprodutibilidade/reivindicações honestas/escopo,
contributions + disclosure LLM; **QST (IOP)** — altamente seletivo ("essential
reading" + interesse amplo + impacto duradouro), Letters com justification
statement, Papers com avanço significativo, Topical reviews convidadas,
Roadmaps 2–3 pp/seção, **single anonymous**; **IEEE TQE** — gold OA, **sem
page limit**, APC **USD 1.995**, escopo engenharia (supercondutividade,
magnética, micro-ondas, fotônica, processamento de sinais); **ACM TQC** —
Manuscript Central, transição 100% OA, revised minor em **30 dias**, ORCID
obrigatório; **QIP (Springer)** — single-blind, abstract 150–250, fonte
editável + PDF obrigatórios, template LaTeX recomendado.

**Perfis de direito (R-976.19):** **Revista Direito GV (FGV)** — desk review
(ine ditismo + adequação temático-metodológica + requisitos formais),
**duplo-cego → simples-cego se preprint**, 5 palavras-chave PT/EN/ES,
desidentificação, resenhas ≤2.000 palavras incl. referências, sem taxas;
**Revista Direito e Práxis (UERJ)** — trilíngue PT/EN/ES, desk review com
resposta em até 30 dias, duplo-cega com 2 ad hoc de stricto sensu, 3º avaliador
se divergência, declaração rigorosa de conflito de interesses, preprints
permitidos, sem APC; **RDA (FGV)** — desde 1945, desk review ≤15 dias, 2–3
pareceristas doutores por área, titulação mínima doutor, máx. 2 autores (≥1
doutor), sem inclusão de autor após submissão, ABNT, **CC BY-NC-ND 4.0**;
**Seqüência (UFSC)** — duplo-cega, iThenticate, CC BY 4.0, sem taxas, ABNT;
**REED** — foco em pesquisa empírica jurídica, exogenia de pareceristas ≥75%,
nomes de avaliadores publicados, ORCID, avaliação ~6 meses; **Suprema (STF)** —
semestral, duplo-cega com ≥2 pareceristas externos, 3º parecerista se impasse,
até 3 coautores, PT/EN/ES/FR/IT, fluxo contínuo.

Escolha o periódico-alvo para recalibrar a banca (aliases aceitos: `RBE`,
`E&S`, `C&E`, `BJET`, `EIT`, `IRE`, `Cadernos`, `JOD`, `JDR`, `COI`, `MIA`,
`AIIM`, `JBI`, `NPJ`, `journal of dentistry`, `npj digital medicine`...).
Desde R-976.22 a resolução de aliases é **tolerante a barra, parênteses,
acento, hífen e caixa mista** — `educação/pucrs`, `rbe/anped`,
`seqüência (ufsc)`, `npj/quantum/information`, `Suprema / STF` resolvem
normalmente (`normalize_institution_alias()`; sem falsos positivos em códigos
curtos como `EIT`/`IRE`):

```bash
python3 - <<'PY'
from marceloclaro.orchestrator import MarceloClaroOrchestrator
orch = MarceloClaroOrchestrator()
r = orch.banca_simulate(
    DOC, n_members=12, seed=42,
    target_institution="Computers & Education",   # ou "BJET", "RBE"...
    requirement="ensaiar submissão a periódico de tecnologia educacional")
print(r["verdict"], r["weighted_score"], r["recommendation"])
print(r["editorial_profile"]["journal"])   # perfil do periódico
print(r["editorial_profile"]["special_gates"])  # gates editoriais
PY
```

- A nota ponderada muda conforme o **peso editorial** do periódico (C&E
  reforça metodologia/estatística/evidências; E&S reforça teoria/impacto);
  o sentimento individual dos revisores permanece estável — a diferenciação
  entre periódicos vem dos pesos, não do humor.
- `resumo["target_profile"]` traz escopo, prioridade e fonte com aviso
  anti-overclaim (ensaio de submissão orientado; nunca parecer real).

## Uso direto (biblioteca)

```bash
python3 - <<'PY'
from mirofish.social import (
    EventConfig, PlatformConfig, SimulationParameters,
    SimulationProfileGenerator, SocialReportGenerator, SocialSimulationEngine,
)
from mirofish.social.contracts import TimeSimulationConfig

doc = "Plano municipal de mobilidade com ônibus elétricos..."
g = SimulationProfileGenerator(doc, n_agents=10, seed=42)
profiles = g.generate()
params = SimulationParameters(
    simulation_id="sim_manual_1",
    event_config=EventConfig(hot_topics=g.extract_topics()),
    twitter_config=PlatformConfig(platform="twitter", echo_chamber_strength=0.5),
    time_config=TimeSimulationConfig(total_simulation_hours=12, minutes_per_round=60),
)
result = SocialSimulationEngine(profiles, params, seed=42).run(rounds=12)
print(SocialReportGenerator(result).generate())
PY
```

## Interpretação (anti-overclaim)

- Resultado é **simulação determinística de modelo simplificado** — NÃO é
  pesquisa empírica, NÃO prediz eleições/reais mercados com precisão.
- Use o valor de `final_sentiment` como **sinal qualitativo** (apoio/oposição/polarização),
  nunca como previsão exata.
- `echo_chamber_strength` controla polarização: > 0.5 referencia grupos de mesma
  postura (câmaras de eco), ≤ 0.5 mistura o grupo todo.

## Serviço externo (AGPL-3.0) — integração por HTTP (R-976.20/21)

O backend Flask real do MiroFish-Offline (**repo canônico:
`MarceloClaro/MiroFish-Offline`** — fork English offline de `nikmcfly/
MiroFish-Offline`, AGPL-3.0, Neo4j + Ollama local stack; clone em
`~/projetos/MiroFish-Offline-AGPL`) pode ser detectado, iniciado e
consultado pelo Core **por composição HTTP** — nenhum código AGPL é
copiado (gate de licença). Um fork genérico (`MarceloClaro/MiroFish`)
também é aceito como fallback de detecção.

1. **Detectar + subir** (usa a venv própria do repo AGPL, sem tocar o Python do Core):

```bash
python3 - <<'PY'
from integrations.mirofish_offline import MiroFishOfflineDriver
d = MiroFishOfflineDriver()                 # detecta ~/projetos/MiroFish-Offline ou $MIROFISH_OFFLINE_DIR
print(d.start_backend(port=5001))           # sobe o Flask externo se a venv existir e não estiver de pé
print(d.health())                           # GET /health — nunca lança (R-976.9)
PY
```

2. **Consultar via orquestrador** (reflexão no MetaBus incluída):

```bash
python3 - <<'PY'
from marceloclaro.orchestrator import MarceloClaroOrchestrator
orch = MarceloClaroOrchestrator(auto_load_agents=False, pipeline_layers=1)
print(orch.mirofish_external_status())      # ok, http_ok, contagens reais observadas
PY
```

3. **Listagens determinísticas reais** do backend externo:

```bash
python3 - <<'PY'
from integrations.mirofish_offline import MiroFishOfflineDriver
d = MiroFishOfflineDriver()
print(d.list_simulations())   # GET /api/simulation/list
print(d.list_reports())       # GET /api/report/list
print(d.list_projects())      # GET /api/graph/project/list
PY
```

**Limite honesto (anti-overclaim R110)**: a simulação OASIS-full do backend
(`create`/`prepare`/`start`) depende de `LLM_API_KEY`/`ZEP_API_KEY` e de
`camel-oasis` (que exige Python <3.12). Neste ambiente o backend sobe com o
subconjunto core (Flask, openai, zep-cloud, pydantic, PyMuPDF). Para simulação
**determinística local** use `orch.mirofish_simulate(...)` /
`orch.banca_simulate(...)` — caminho principal do Core.

## Verificação

- Testes: `python3 -m pytest tests/test_r583_mirofish_offline.py -q`
- Determinismo: mesma `seed` → mesmas ações e opiniões (INV-976.2).