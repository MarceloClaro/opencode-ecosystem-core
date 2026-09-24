# SPEC-976 — Integração MiroFish-Offline (Simulação Social OASIS + Knowledge Graph + ReportAgent)

```yaml
spec_id: SPEC-976
title: Integração MiroFish-Offline — motor de simulação social determinístico no Core
status: in_progress
component: mirofish/social/ + integrations/mirofish_offline.py
inspiration: github.com/MarceloClaro/MiroFish-Offline (fork AGPL-3.0 do MiroFish OASIS)
license_note: Nenhum código do MiroFish-Offline é copiado; apenas contratos de dados e
              comportamento são reimplementados em stdlib (MIT-compatível). O serviço
              externo original permanece no repo próprio e é acionado por composição.
cycle: R583
```

## Contexto e gap

O Core já possui `mirofish/` (SPEC-015): **enxame preditivo** (wisdom of crowds + Delphi +
Nash) 100% stdlib. O MiroFish-Offline agrega três capacidades que **não existem** no Core:

1. **Simulação social OASIS** — agentes com perfis (persona, viés de opinião, velocidade de
   reação, influência, memória) interagem em plataformas simuladas (twitter/reddit):
   postar, curtir, repostar, argumentar, mudar de opinião; rastreio de evolução de sentimento.
2. **Knowledge graph** — entidades/relações extraídas do documento (people, companies,
   events) com memória individual e de grupo; busca híbrida 0.7×vetor + 0.3×BM25.
3. **ReportAgent** — análise estruturada pós-simulação: entrevista focus group, busca de
   evidências no grafo, relatório markdown com outline e seções.

### Restrições de integração

- **Licença**: MiroFish-Offline é **AGPL-3.0**; o Core é **MIT**. Nenhum código-fonte é
  copiado. A integração reimplementa contratos (dataclasses, fluxos) em stdlib própria
  (MIT) e, opcionalmente, **aciona por composição** o serviço original quando o usuário
  o disponibiliza (padrão R473: runner injetável + fail-closed + recibo, sem acoplamento).
- **Dependências**: o Core não ganha dependências pesadas (neo4j/openai/camel-oasis).
  O motor local é 100% stdlib; persistência em `.mci_state/` (JSON) — não Neo4j.
- **Determinismo**: com `seed`, a simulação local é reprodutível (INV-976.3).

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-976.1 | Contratos de dados | Módulo `mirofish/social/profiles.py` expõe `OasisAgentProfile` com campos `user_id`, `user_name`, `name`, `bio`, `persona`, `karma`, `friend_count`, `follower_count`, `statuses_count`, `age`, `gender`, `mbti`, `country`, `profession`, `interested_topics`; métodos `to_reddit_format()`, `to_twitter_format()`, `to_dict()` |
| R-976.2 | Configuração de simulação | `SimulationParameters` com `time_config` (total_simulation_hours, minutes_per_round, faixa de agentes/hora, multiplicadores pico/fora-pico), `agent_configs` (activity_level, posts_per_hour, comments_per_hour, active_hours, response_delay, sentiment_bias, stance, influence_weight), `event_config` (initial_posts, scheduled_events, hot_topics), `platform_config` (recency/popularity/relevance weights, viral_threshold, echo_chamber_strength) |
| R-976.3 | Geração determinística de perfis | `SimulationProfileGenerator(doc_text, n_agents, seed)` gera N perfis heterogêneos (biases: supportive/opposing/neutral/observer) sem chamada LLM; com seed fixa, saída idêntica |
| R-976.4 | Motor de simulação | `SocialSimulationEngine.run(rounds)` executa rounds: agentes ativos por hora (pico = multiplicador), ações `CREATE_POST`, `LIKE_POST`, `REPOST`, `QUOTE_POST`, `DO_NOTHING`; sentimento médio por round ∈ [−1, 1]; conteúdo de posts derivado de `hot_topics` + `sentiment_bias`; moral da simulação persistida |
| R-976.5 | Evolução de opinião | Opinião de agente muda em direção à média do grupo ponderada por `influence_weight` + `echo_chamber_strength`; com `echo_chamber=0.5` e grupos separados, polarização esperada (desvio da média cresce) |
| R-976.6 | Persistência | Estado da simulação (perfis, ações, sentimento por round, opinião final) sobrevive a reinicialização via `.mci_state/mirofish_social_<id>.json` |
| R-976.7 | ReportAgent | `SocialReportGenerator` produz markdown com seções `# Objetivo`, `# Metodologia`, `# Agentes`, `# Linha do Tempo`, `# Sentimento`, `# Conclusão` a partir do estado salvo |
| R-976.8 | Integração orquestrador | `orch.mirofish_simulate(doc_text, n_agents, rounds, seed)` executa o pipeline (perfis → simulação → relatório → reflexão no MetaBus) e retorna resumo |
| R-976.9 | Driver externo fail-closed | `integrations/mirofish_offline.py::MiroFishOfflineDriver` detecta serviço externo ($MIROFISH_OFFLINE_DIR); se ausente, `status=unavailable` e chamadas falham com mensagem clara — nunca silenciosamente degrada para "sucesso" |
| R-976.10 | Skill | Skill `mirofish-offline` apresenta o fluxo: preparar documento → gerar perfis → simular → reportar → interagir; `policy.allow_implicit_invocation: false` |
| R-976.11 | **Banca editorial** | `mirofish/social/banca.py::BancaProfileGenerator` gera perfis de revisores especialistas (PhD por critério: metodologia, estatística, ética, originalidade, clareza, relevância) com instituição, postura (rigoroso/equilibrado/entusiasta/cético) e viés; `banca_verdict()` converte sentimento final em decisão editorial (aceitar, revisões menores, revisões maiores, rejeitar) |
| R-976.12 | **Peso do texto (sinais textuais)** | `text_signals(texto) → {critério: 0..1}` detecta solidez textual por critério via regex (PRISMA, JBI, κ, n=, OSF, DOI, ABNT, etc.); `adjust_bias_by_signal()` modula o bias de cada revisor: texto forte suaviza postura rigorosa, texto fraco endurece; determinístico e stdlib-only |
| R-976.13 | **Banca ampliada** | 12 critérios (metodologia, estatística, ética, originalidade, clareza, relevância, teoria, reprodutibilidade, evidências, redação, coerência, impacto); default `n_members=12` (1 PhD por critério, cíclico acima); instituições de publicação de referência como RÓTULOS de simulação (Qualis A1 citado só como calibração, nunca como parecer real); veredito ponderado `banca_weighted_score()` (0..100) + `recommendation_from_score()`; `summarize_banca()` inclui `text_signals`, `strengths`, `weaknesses` e disclaimer anti-overclaim |
| R-976.14 | **Perfis editoriais por periódico** | `mirofish/social/editorial_profiles.py::EDITORIAL_PROFILES` registra perfis baseados em normas PÚBLICAS de 11 periódicos Qualis A1/Q1 (RBE/ANPEd, Educação & Sociedade/CEDES, Cadernos de Pesquisa/FCC, Práxis Educacional/UESB, Práxis Educativa/UEPG, Estudos em Avaliação Educacional/FCC, Educação/PUCRS, Computers & Education/Elsevier, BJET/Wiley, EIT/Springer, IRE/UNESCO UIL): escopo, prioridade (perfil do melhor artigo), estilo de referência, limite de tamanho, fluxo de revisão, gates especiais (ex.: E&S/C&E não aceitam IA generativa como autora; disclosure obrigatória) e pesos por critério; `get_profile()` resolve nome/alias (BJET, RBE, C&E, E&T...); `BancaProfileGenerator(target_institution=...)` afilia toda a banca ao rótulo do periódico e usa `merge_weights()` para calibrar a nota ponderada; `summarize_banca()` expõe `editorial_profile` (com fonte e aviso anti-overclaim); `orch.banca_simulate(target_institution=...)` enriquece o pipeline |
| R-976.15 | **Perfil Journal of Dentistry (JOD)** | `EDITORIAL_PROFILES["Journal of Dentistry"]` (Elsevier) baseado no **template oficial Review Article** compartilhado pelo autor (Google Docs `1yKkypArCLZefsADlvxqvFWgRWONwGRVnw34gHlILInQ`, 24/09/2026): escopo odontológico translacional/clínico com foco em síntese de evidências e IA odontológica; prioridade para revisões com protocolo registrado, pergunta estruturada PCC, seleção dupla, extração padronizada, síntese descritiva e "Clinical significance" no resumo; estilo de referência **numerado com DOI** ([1] Surname, [Title], [Journal] [volume] ([year]) [pages]. [DOI]); 5 special_gates (abstract estruturado, protocolo sem implicar registro inexistente, declaração de IA generativa, declarações CRediT/funding/conflito/ética/dados, estratégia de busca completa em suplemento); pesos reforçados (evidências 1.8, metodologia 1.7, reprodutibilidade 1.7, ética 1.5, estatística 1.4, clareza 1.3, teoria 0.9); aliases `jod`, `journal of dentistry`, `dentistry`; `JOURNAL_ALIASES` exportado publicamente; `tests/test_r586_banca_journal_dentistry.py` (11 testes: registro, campos, fonte, gates, estilo, alias, pesos, afiliação, summarize, anti-overclaim, determinismo); anti-overclaim R110 mantido (rótulo de simulação, não parecer real) |
| R-976.16 | **Rigor do edital JOD + similares** | Análise do **guide-for-authors oficial** (ScienceDirect, acesso 24/09/2026) e periódicos odontológicos semelhantes (JDR/IADR-Sage, Clinical Oral Investigations/Springer, JCP/Wiley, J Periodontol/Wiley) consolidada em `mirofish/social/EDITAL_JOD_RIGOR_EDITORIAL.md`: escopo JOD (líder em Odontologia Restauradora; influenciar clínica/pesquisa/indústria/policy), métricas (IF 5.8, CiteScore 7.8, APC USD 3.920), limites por tipo (**Review 10 pp impressas ≈ 33 processadas**; Original 6 pp; Short Comm 2 pp; Digital Dentistry 6/10/2 pp), **NÃO aceita Case Reports**, timeline (1ª decisão 5d desk / 29d pós-review / 74d aceite), apelação única, mudança de autoria proibida pós-submissão, declaração de IA generativa em seção própria ANTES das referências (revisores/editores proibidos de usar IA com manuscrito), ICMJE/CONSORT para ensaios, resumo <500 palavras em registro não conta como pré-publicação; perfil JOD atualizado com esses dados (`length_limit`, `review_flow` com timeline, `special_gates` +2 = 7 gates, `source` com guia oficial); `tests/test_r586_banca_journal_dentistry.py` estendido para **14 testes** (+3: gates do edital oficial, limites por tipo, timeline/flow); regressão R583+R584+R585+R586 = 59 passed + 12 subtests |

## Invariantes

- INV-976.1: Ações e sentimento por round sempre ∈ [−1, 1]; sentimento agregado é média aritmética das opiniões dos agentes ativos.
- INV-976.2: Com seed fixa, motor e geração de perfis são determinísticos (mesmos dados de entrada → mesmas ações na mesma ordem).
- INV-976.3: Nenhuma dependência externa em runtime do motor local (stdlib only); `openai/neo4j` nunca importados.
- INV-976.4: Driver externo nunca declara "sucesso" sem prova de serviço real (anti-overclaim R110).
- INV-976.5: Nenhum arquivo do MiroFish-Offline AGPL é copiado para o Core (gate de licença no recibo).

## Fora de escopo (v1)

- Frontend web do MiroFish-Offline (Vue) e API Flask — o Core integra o motor, não a UI.
- Neo4j/híbrido BM25 real — storage JSON local; busca vetorial fica para futura frente.
- Entrevista focus group com LLM — ReportAgent local gera análise determinística dos dados da simulação; entrevista LLM fica no driver externo opcional.

## Referências

- MarceloClaro/MiroFish-Offline (fork AGPL-3.0 do 666ghj/MiroFish, engine OASIS CAMEL-AI).
- SPEC-015 (enxame preditivo já existente no Core) — complementar, sem sobreposição.
- Padrão R473 (runner injetável + fail-closed + recibo) — lições R549/R550.