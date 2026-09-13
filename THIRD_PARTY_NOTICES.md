# THIRD_PARTY_NOTICES

Registro de componentes de terceiros integrados ao OpenCode Ecosystem Core
(SPEC-935-R471 e subspecs). A redistribuição de qualquer componente exige
análise de licença prévia; este arquivo é o registro canônico.

## Componentes da R471 (Fase 1–6)

| Componente | Origem | Licença | Uso no Core | Restrição |
|---|---|---|---|---|
| open-swe | langchain-ai/open-swe | MIT | Fábrica de pesquisa (M1) | Nenhuma além das exigências MIT |
| OpenShell | NVIDIA | Apache-2.0 | Sandbox declarativo (M2) | Redistribuição exige avisos Apache-2.0 |
| NemoClaw | NVIDIA | Apache-2.0 | Operação padronizada de agentes (M2) | Redistribuição exige avisos Apache-2.0 |
| Personal-AI-Router (PAIR) | NVIDIA | Apache-2.0 | Roteador local de inferência (M3) | Sem sharding de GPU; roteia requisições independentes |
| DeepSeekGUI | See-Sol-Lab | camada de produto **PolyForm Perimeter 1.0.1**; upstream DeepSeek Harness **MIT** | Workbench de supervisão desktop (M4) | Uso interno de pesquisa/estudo permitido; **redistribuição competitiva vedada** sem licença |
| minimind | jingyaogong/minimind | Apache-2.0 | Currículo didático 64M (M5) | Treinamento real exige GPU; sem GPU documenta-se limitação |
| SciHubEVA | leovan/SciHubEVA | MIT | Frontend opt-in do resolvedor restrito (M6) | Nunca padrão; herda gates fail-closed da R470 |
| tig | rsrohan99/tig | **sem licença declarada** (license: null) | Executor alternativo multi-provedor (M7) | Invocação externa opcional; **vedada redistribuição**, inclusão em bundle ou venda de código derivado sem autorização |
| openclaw-qa | ythx-101 | conteúdo **CC BY-SA 4.0** (share-alike) | Observatório de campo (M8) | **Nenhuma incorporação de conteúdo**; citar com atribuição; derivados sob mesma licença |
| 500-AI-Agents-Projects | MarceloClaro (fork); ashishpatel26/500-AI-Agents-Projects | MIT | **Referência de paisagem** (R482): manifest curado com 20 agentes auto-contidos e LANDSCAPE_REPORT; **espelhos arquiteturais** (item 2B): `examples/agents/` 00+20 | **Nenhum código-fonte copiado**; apenas metadados curados (metadados não são obra derivada) e documentação de padrões; sem promessa de integração |

## Referências epistemológicas da R483 (Scanner Reverso)

Componentes citados no **design** do `scanners/reverse_scanner.py` (inspiração
de métricas; nenhum código copiado, nenhuma dependência):

| Componente | Origem | Licença | Papel no design |
|---|---|---|---|
| feynman-skill | MarceloClaro (fork); alchaincyf/feynman-skill | MIT (Huashu/花叔) | Termo **ritual(g)** — teste anti-cargo-cult: distinguir lacuna genuína de lacuna ritual |
| feynman | MarceloClaro (fork); advaitpaliwal/feynman | MIT (Companion, Inc.) | Executor futuro das trajetórias de pesquisa (planejado, fora do escopo R483) |
| bernstein | MarceloClaro (fork); sipyourdrink-ltd/bernstein | Apache-2.0 | Executor futuro do roadmap via orquestração determinística (planejado, fora do escopo R483) |

## Análise de paisagem — repos inspecionados (R487)

Inspeção local com `git clone --depth 1` em `/tmp/opencode/`; nenhum código
incorporado ao Core nesta revisão.

| Componente | Origem | Licença | Papel/lição para o Core |
|---|---|---|---|
| science-skills | google-deepmind/science-skills | Apache-2.0 | 37 skills científicas (UniProt, ClinVar, gnomAD, PubMed, OpenAlex, AlphaFold, Foldseek…). Lição: **vocabulário de convergência** — as skills de literature search (arXiv/bioRxiv/EuropePMC/OpenAlex/PubMed) e bancos de dados preenchem parte das lacunas metodológicas que o `ReverseScanner`/`PolymathicConvergence` (R483/R486) sinalizam; candidatas a enriquecer o landscape/manifest com domínio **academic** |
| ruflo (ex Claude Flow) | ruvnet/ruflo | MIT | "Sistema nervoso" de agente: CLI/MCP → Router → Swarm → Memory com Learning Loop. Lição: o Core já cobre o equivalente via Blackboard (A2A) + Trust Engine + MetaBus; o **Learning Loop** (retroalimentação de padrões bem-sucedidos) confirma o desenho do ciclo **Reflexion** R472+; arquitetura em TypeScript não é copiada |

## Paisagem acadêmica — fontes DeepMind (R489)

Fontes curadas em `landscape/manifest.json` (chave `academic`) e cruzadas pelo
`PolymathicConvergence` (R486 ampliado). Metadados apenas; nenhum código de
terceiros incorporado.

| Componente | Origem | Licença | Uso no Core |
|---|---|---|---|
| deepmind-superhuman | google-deepmind/superhuman | Apache-2.0 | Fonte de paisagem p/ **raciocínio formal** (AlphaGeometry, AlphaGeometry2, IMO Bench, Aletheia). Curadoria anti-overclaim: o rótulo do repo não é adotado como veredicto no Core |
| deepmind-alphageometry | google-deepmind/alphageometry | Apache-2.0 | Fonte de paisagem p/ **prova geométrica / dedução simbólica** |
| deepmind-alphageometry2 | google-deepmind/alphageometry2 | Apache-2.0 | Fonte de paisagem p/ **prova geométrica / busca orientada** |
| deepmind-science-skills | google-deepmind/science-skills | Apache-2.0 | Fonte de paisagem p/ **literature search e bancos de dados biológicos** (37 skills) |
| deepmind-acme | google-deepmind/acme | Apache-2.0 | Fonte de paisagem p/ **reinforcement learning e loops agente-ambiente** (R497). Analogia estrutural: `environment_loop` ↔ ciclo Perceber→…→Refletir do orquestrador; `adders`/replay ↔ MetaBus; `specs` ↔ SDD. Metadados apenas; stack TF/JAX/Reverb não incorporada (princípio hermético/stdlib) |
| feynman-tutor | koukekoukej-glitch/feynman-tutor | MIT | Inspiração conceptual para o Successor Generator (R491): método Feynman aplicado a tutoria |

## Fonte de espelhos (item 2B)

`examples/agents/` referencia 21 espelhos (00 fundação + 20 pilotos) do
500-AI-Agents-Projects (MIT). Licenças individuais dos agentes-fonte: MIT.
Os espelhos são **documentação de padrões**, não redistribuição de código.

## Política geral

- Credenciais nunca são persistidas em sandbox, recibo ou configuração.
- Falha de componente externo degrada para o fluxo nativo sem perda de dados
  (invariante 10 da SPEC-935-R471).
- Este registro não constitui parecer jurídico; consulte a licença de cada
  componente antes de redistribuir.