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

## Perfis editoriais por periódico (R-976.14 + R-976.15 + R-976.16)

`mirofish/social/editorial_profiles.py::EDITORIAL_PROFILES` registra perfis
baseados em **normas públicas** de 12 revistas Qualis A1/Q1 e internacionais
(RBE/ANPEd, Educação & Sociedade/CEDES, Cadernos de Pesquisa/FCC, Práxis
Educacional/UESB, Práxis Educativa/UEPG, Estudos em Avaliação
Educacional/FCC, Educação/PUCRS, Computers & Education/Elsevier, BJET/Wiley,
Education and Information Technologies/Springer, International Review of
Education/UNESCO UIL, **Journal of Dentistry/Elsevier**): escopo,
prioridade (perfil do melhor artigo), estilo de referência, limite de tamanho,
fluxo de revisão, gates especiais (ex.: Educação & Sociedade e Computers &
Education **não aceitam IA generativa como autora**; disclosure obrigatória na
Springer; Journal of Dentistry exige **abstract com Clinical significance** +
protocolo registrado + declaração de IA generativa + estratégia de busca em
suplemento) e pesos por critério.

O perfil **Journal of Dentistry (JOD)** baseia-se no template oficial Review
Article da Elsevier (fonte: Google Docs compartilhado pelo autor) **reforçado
pelo guide-for-authors oficial** (ScienceDirect, acesso 24/09/2026 — ver
`mirofish/social/EDITAL_JOD_RIGOR_EDITORIAL.md`): escopo líder em Odontologia
Restauradora; limites por tipo (**Review máx. 10 pp impressas ≈ 33 pp
processadas**; Original 6 pp; Short Comm 2 pp); **NÃO aceita Case Reports**;
timeline 1ª decisão ~5 dias (desk) / ~29 dias pós-review / ~74 dias até
aceite; apelação única; mudança de autoria proibida pós-submissão; declaração
de IA generativa em seção própria ANTES das referências (revisores/editores
proibidos de usar IA com manuscrito); ICMJE/CONSORT para ensaios; resumo <500
palavras em registro de ensaio não conta como pré-publicação. Útil para
ensaiar **scoping reviews** com pergunta PCC, seleção dupla, síntese descritiva
e referências numeradas com DOI (weights: evidências 1.8, metodologia 1.7,
reprodutibilidade 1.7, ética 1.5, estatística 1.4, clareza 1.3, teoria 0.9).

Escolha o periódico-alvo para recalibrar a banca (aliases aceitos: `RBE`,
`E&S`, `C&E`, `BJET`, `EIT`, `IRE`, `Cadernos`, `JOD`, `journal of
dentistry`...):

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

## Serviço externo (AGPL-3.0)

Para capacidades completas do MiroFish-Offline original (Neo4j, Ollama, focus
group com LLM, frontend), use o repo AGPL separado por composição:

```bash
export MIROFISH_OFFLINE_DIR=/caminho/para/MiroFish-Offline
python3 - <<'PY'
from integrations.mirofish_offline import MiroFishOfflineDriver
d = MiroFishOfflineDriver()
print(d.check())   # fail-closed: available=True só com serviço real
PY
```

Nenhum código do projeto AGPL é copiado para o Core (SPEC-976, gate de licença).

## Verificação

- Testes: `python3 -m pytest tests/test_r583_mirofish_offline.py -q`
- Determinismo: mesma `seed` → mesmas ações e opiniões (INV-976.2).