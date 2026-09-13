---
spec_id: SPEC-935-R471
title: Resiliência científica integrada — capacidades externas (open-swe, OpenShell, NemoClaw, PAIR, DeepSeekGUI, minimind, SciHubEVA)
component: research_factory
test_file: tests/test_r471_research_factory.py
status: green
estoque: rc
data: 2026-09-12
---

# SPEC-935-R471 — Resiliência científica integrada: capacidades externas (open-swe, OpenShell, NemoClaw, PAIR, DeepSeekGUI, minimind, SciHubEVA)

## Objetivo
Transformar o OpenCode Ecosystem Core em ambiente mais resiliente para construção de pesquisas científicas, integrando — de forma auditável e respeitando as políticas vigentes — as capacidades dos repositórios `open-swe`, `OpenShell`, `NemoClaw`, `Personal-AI-Router`, `DeepSeekGUI`, `minimind` e `SciHubEVA`, de modo a superar a abrangência de pipeline do SciHubEVA isolado (que resolve apenas o subproblema pontual de download de PDF) com um fluxo completo: descoberta federada → curadoria → evidência → experimento → redação → revisão → publicação.

## Contexto e justificativa (análise de gap contra SciHubEVA)
O SciHubEVA (leovan/SciHubEVA; upstream 1.1k estrelas) é uma GUI Qt/PySide6 cross-platform de download de artigos via Sci-Hub: aceita DOI, PMID, URL, string de busca, padrões de intervalo e listas; suporta proxy, captcha, temas e i18n. O fork `MarceloClaro/SciHubEVA` (criado em 2023, sem diffs próprios evidentes, 0 estrelas) adiciona nada além do upstream no momento da análise. Limitações estruturais do SciHubEVA que este Core já endereça e passará a endereçar com resiliência:

| Dimensão | SciHubEVA isolado | Core atual (R120, R468–R470) | Integração R471 |
|---|---|---|---|
| Fontes descoberta | Sci-Hub apenas | 11+ fontes federadas (openalex, crossref, europepmc, arxiv, pubmed, biorxiv, core, …) | mantém e adiciona capacidade de GUI sobre o pipeline |
| Pipeline | download PDF | busca→curadoria→evidência→fichamento→redação→revisão (MASWOS, pesquisador universal) | adiciona fábrica de pesquisa (open-swe) |
| Isolamento de execução | processo local único | limites locais + sandbox de processo (evolução R451) | sandbox declarativo multi-camada (OpenShell/NemoClaw) |
| Inferência | não se aplica | Ollama local → OpenAI | roteamento local multi-máquina (PAIR) |
| Trabalho desktop | GUI download | CLI/OpenCode | workbench desktop opcional (DeepSeekGUI sobre harness já presente) |
| Modelos pequenos | não se aplica | LiteRT-LM, Colibri OLMoE | treinamento didático/reprodutível (minimind) |
| Política de acesso | contorna paywall por omissão | `open_science_only` + resolvedores restritos opt-in auditáveis (R468, R469, R470) | GUI não altera política; herda gates fail-closed |

## Não-objetivos
- Não tornar sci-hub, `scihub-cli`, SciHubEVA ou qualquer resolvedor restrito padrão, dependência padrão ou fallback automático (conserva invariante 8 da R468 e rejeição de default da R469).
- Não automatizar, facilitar ou orientar violação de controles de acesso, paywalls ou termos contratuais; a GUI SciHubEVA, se integrada, herda integralmente o modelo de autorização opt-in da R470.
- Não declarar "superação" de SciHubEVA como mérito absoluto ou validação externa; o termo é delimitado a abrangência de pipeline e resiliência operacional, mensurável por critérios de aceitação.
- Não redistribuir código proprietário; DeepSeekGUI (camada de produto) é PolyForm Perimeter 1.0.1 — uso local de pesquisa permitido, redistribuição competitiva vedada sem licença.
- Não replicar sharding de GPU nem pooling de memória; PAIR roteia requisições independentes entre nós da LAN.
- Não prometer disponibilidade, integridade ou autenticidade de cópias obtidas por resolvedores restritos.

## Mapa de capacidades externas e papel na resiliência

| Repositório (origem) | Licença | Capacidade incorporada | Papel na resiliência científica |
|---|---|---|---|
| `open-swe` (langchain-ai/open-swe) | MIT | Fábrica de software sobre Deep Agents + LangGraph: loops Plan→Implement→Validate→Deliver, subagentes, revisão, CI, scheduler | **Fábrica de pesquisa**: ciclo reproduzível de investigação→experimento→validação→manuscrito; revisão automática grounded no diff; automação recorrente |
| `OpenShell` (NVIDIA) | Apache-2.0 | Sandboxes isolados (Docker/Podman/MicroVM/K8s) com políticas YAML em 4 camadas (filesystem, rede, processo, providers) | **Resiliência operacional**: contenção de coleta/scraping/parse; credenciais endpoint-bound; falha segura |
| `NemoClaw` (NVIDIA) | Apache-2.0 | Reference stack de agentes (OpenClaw, Hermes, Deep Agents) dentro do OpenShell; CLI de ciclo de vida, snapshots, hardening | **Operação padronizada** de agentes em sandbox; hardening e políticas de rede por padrão |
| `Personal-AI-Router` (NVIDIA) | Apache-2.0 | Roteador local de inferência multi-máquina (Ollama/LM Studio); endpoints Ollama-compatible e OpenAI-compatible; descoberta na LAN | **Resiliência de compute**: pool local de inferência para os agentes; independência de provedor externo quando desejado |
| `DeepSeekGUI` (See-Sol-Lab) | Camada produto PolyForm Perimeter 1.0.1; upstream DeepSeek Harness MIT | Workbench desktop sobre DeepSeek Harness: Git/PR tools, memória global e de projeto, worktrees, browser, terminal, notificações | **Produtividade de supervisão humana**: estado de projeto visível, revisão de mudanças e memória de decisões com aprovação Harness |
| `minimind` (jingyaogong/minimind) | Apache-2.0 | Currículo de treinamento de LLM 64M do zero (tokenizer→pretrain→SFT→RLHF→DPO→MoE→distill/quant) | **Educação e reprodutibilidade**: pipelines didáticos auditáveis; geração de modelos pequenos especializados em domínios científicos |
| `SciHubEVA` (leovan/SciHubEVA) | MIT | GUI Qt/QML de download com DOI/PMID/URL/string, intervalos e listas | **Frontend opcional** sobre o resolvedor restrito opt-in da R470; nunca padrão; herda gates fail-closed |
| `tig` (rsrohan99/tig) | **sem licença declarada** (`license: null`) | Agente de codificação IA em terminal, multi-LLM (Gemini, OpenAI, Claude, OpenRouter, DeepSeek, Groq, Ollama); modos Architect (design→markdown) e Code; stack LlamaIndex/Tree-sitter/Ripgrep | **Executor alternativo multi-provedor** (M7): resiliência de execução da fábrica — se um provedor falha, outro executa; modo Architect espelha o ethos SDD |
| `openclaw-qa` (ythx-101) | Conteúdo **CC BY-SA 4.0** (share-alike); repositório sem licença na API | Comunidade "Agent Waystation": check-in de agentes, Field Reports (falhas reais, padrões úteis), Tool Workshop (x-tweet-fetcher, ask-search, grok-bridge, antigravity-bridge, lan-control), memória/autonomia (six6), Task Board | **Observatório de campo e padrões comunitários** (M8): aporte de lições verificáveis ao MetaBus com atribuição CC BY-SA; relatórios de campo como insumo de reflexão; Task Board como banco de desafios de verificação; participação opcional em check-in pelo orquestrador — **nenhuma incorporação de conteúdo** (share-alike exige derivados sob mesma licença) |

Conexões já presentes no repositório local: `deepseek-harness/` (zip + diretório + `_reversa_docs` + `_reversa_sdd`) está no raiz; `ollama` é provedor preferido do doctor; `scihub-cli` já é CLI externa registrada (R120) e coberta pela política fail-closed.

## Invariantes
1. O padrão de acesso permanece `open_science_only`; nenhuma integração externa altera `DEFAULT_SOURCES=[openalex,crossref,europepmc,arxiv]` nem a ordem de escolha de PDF aberto.
2. Toda execução externa (open-swe, OpenShell, NemoClaw, PAIR, DeepSeekGUI) é opt-in, configurável por flag/ambiente e auditável; ausência de configuração equivale a inatividade.
3. O resolvedor restrito (SciHubEVA/scihub-cli) permanece sob o modelo R470: desabilitado por omissão, allowlist versionada, autorização humana explícita, base legal + evidência registradas, recibos auditáveis; GUI não contorna gates.
4. Nenhum despacho de ferramenta externa utiliza `shell=True`; argumentos passados como lista, sem interpolação de shell.
5. Credenciais (API keys, tokens PAIR, providers OpenShell) nunca são persistidas em sandbox nem em recibo; injeção ocorre por variável de ambiente no runtime, sob política.
6. O orquestrador `marceloclaro` permanece o único coordenador autorizado a avaliar gates e ordenar despachos; é vedada delegação direta que contorne o orquestrador.
7. Nenhuma alteração desta spec viola `SECURITY.md`, `THIRD_PARTY_NOTICES`, R468, R469 ou R470; integrações externas entram como componentes registrados e versionados.
8. Anti-overclaim: nenhum relatório declara "superioridade", "Qualis A1", "verificado" ou "superação" sem validação externa explícita e sem métricas objetivas dos critérios de aceitação.
9. Licenças são respeitadas por componente: MIT (open-swe), Apache-2.0 (OpenShell/NemoClaw/PAIR/minimind), MIT upstream + PolyForm Perimeter produto (DeepSeekGUI), MIT (SciHubEVA); redistribuição exige análise de licença prévia e registro em `THIRD_PARTY_NOTICES`. O componente `tig` **não possui licença declarada** no upstream: uso local como ferramenta invocada é tolerado sob responsabilidade do operador, mas é vedada a redistribuição, inclusão em bundle ou venda de código derivado sem autorização do autor — integração limitada a invocação externa opcional, nunca incorporação de código-fonte. O conteúdo de `openclaw-qa` é **CC BY-SA 4.0** (share-alike): citações exigem atribuição e derivados sob mesma licença; o Core não incorpora trechos, apenas registra lições/insumos com autoria explícita; ferramentas do Tool Workshop seguem suas próprias licenças e exigem auditoria individual antes de qualquer adoção.
10. Todo componente integrado dispara fallback seguro: indisponibilidade do componente externo degrada para o fluxo nativo vigente (pesquisador universal, MASWOS, LiteRT-LM/Colibri) sem perda de dados do MetaBus.

## Arquitetura de integração proposta (módulos, em ordem de baixo risco para alto)
1. **M1 — Research Factory (open-swe)**: adaptar o loop Agent/Reviewer/Analyzer/Scheduler do open-swe como entrypoints científicos (investigar literatura → planejar estudo → executar experimento/simulação em sandbox → validar evidência → entregar manuscrito + PR/relatório). Reuso de subagentes paralelos para curadoria e revisão.
2. **M2 — Sandbox científico declarativo (OpenShell + NemoClaw)**: template de política YAML para tarefas de pesquisa (coleta de dados, scraping, execução de código estatístico), com allowlist de endpoints bibliográficos e negação padrão de egresso; credentials endpoint-bound.
3. **M3 — Roteador local de inferência (PAIR)**: conector que expõe endpoints PAIR (Ollama-compatible/OpenAI-compatible) como provedor adicional do doctor e roteador para agentes; prioridade local → PAIR → Ollama → OpenAI.
4. **M4 — Workbench de supervisão (DeepSeekGUI)**: apontar o workbench para projetos do Core (ex.: `pesquisa/`, `academic/`, `publications/`) usando o harness já presente; documentar licença e limitação de produto.
5. **M5 — Modelos pequenos reprodutíveis (minimind)**: material didático e benchmark de treinamento de LLM 64M para pipelines científicos; avaliação de hardware local (LiteRT-LM/Colibri como alvos de distill).
6. **M6 — Frontend de download opt-in (SciHubEVA)**: empacotar a GUI como frontend do resolvedor restrito R470 (allowlist `scihubeva`), com recibos e autorização idênticos; GUI nunca altera política.
7. **M7 — Executor alternativo multi-provedor (tig)**: registrar `tig` como CLI externa opcional no doctor e como executor da fábrica (M1) com fallback entre provedores (Ollama local → DeepSeek → Groq → Gemini → OpenAI), espelhando o duo Architect/Code no ethos SDD; integração limitada a invocação externa (upstream sem licença declarada), nunca incorporação de código.
8. **M8 — Observatório de campo comunitário (openclaw-qa)**: coletar periodicamente lições verificáveis e padrões de Field Reports/relatórios do Agent Waystation como insumo de reflexão do MetaBus (com autoria e atribuição CC BY-SA), usar o Task Board como banco de desafios de verificação da fábrica e registrar veredito técnico de adoção/rejeição por ferramenta do Tool Workshop (ex.: `ask-search` em auditoria; `x-tweet-fetcher` e `lan-control` **não-adotar** por ToS de scraping X e risco de segurança LAN, salvo exceção explícita do operador); nenhuma incorporação de conteúdo.

## Critérios de aceitação
- CA1: Sem configuração de integração, o ecossistema opera idêntico ao vigente: `open_science_only`, `DEFAULT_SOURCES` inalterados, doctor pass, suíte de pesquisa nativa verde.
- CA2: M1 entrega um manuscrito-demonstração completo (espec + testes + resultado) a partir de um tópico dado, com relatório de auditoria registrando cada etapa; critério: arquivos e recibos presentes e legíveis.
- CA3: M2 aplica política OpenShell a uma tarefa de scraping/coleta de exemplo; egresso não autorizado é bloqueado com recibo de negação; egresso bibliográfico autorizado funciona.
- CA4: M3 adiciona o provedor PAIR ao doctor e ao roteador de inferência; com PAIR ausente, fallback para Ollama/OpenAI é transparente e testado.
- CA5: M4 inicia o workbench DeepSeekGUI apontando para um workspace do Core e documenta o fluxo; licenças (PolyForm Perimeter vs MIT upstream) registradas em `THIRD_PARTY_NOTICES`.
- CA6: M5 reproduz, com seeds fixos, um treinamento 64M curto em hardware local disponível ou documenta limitação de hardware explicitamente; produto inclui relatório de reprodutibilidade.
- CA7: M6 não altera o padrão: sem habilitação R470, nenhum caminho de GUI aciona SciHubEVA; com habilitação completa, o despacho gera `CLIExecutionReceipt` com todos os campos obrigatórios.
- CA8: Suíte de testes cobre os 6 módulos com mocks; nenhum teste realiza download real sob paywall, contém credenciais ou usa rede restrita.
- CA9: `python3 -m marceloclaro.cli doctor` permanece pass (com avisos apenas das CLIs opcionais conhecidas) após integrações; `core-check` verde.
- CA10: Nenhum relatório de integração contém alegação de Qualis A1, "verificado" ou "superação" sem validação externa explícita (gate anti-overclaim R142 aplicado).

## Riscos e limites honestos
- A "superação do SciHubEVA" é delimitada a abrangência de pipeline e resiliência; o SciHubEVA resolve bem o subproblema de download e permanece uma ferramenta útil, não um inimigo a ser desmerecido.
- PAIR não faz sharding de GPU nem pooling de memória; roteia requisições independentes; resultados dependem de hardware local.
- minimind requer GPU para treinamento viável em horas; sem GPU documenta-se limitação sem overclaim.
- DeepSeekGUI tem licença de produto restritiva; uso interno de pesquisa e estudo é permitido, redistribuição competitiva não — sem parecer jurídico desta spec.
- Sandboxes e políticas reduzem superfície de risco, não substituem curadoria humana nem eliminam risco residual (TOCTOU, dependências transitivas, E2E não elevado).
- Nenhuma integração externa é validação editorial de qualidade científica; qualidade permanece no gate SDD/TDD, MASWOS e revisão humana.

## Plano TDD
RED: redigir testes por módulo cobrindo CA1–CA8 antes de implementar cada M: inatividade sem configuração (CA1/CA7), bloqueio de egresso não autorizado (CA3), fallback sem PAIR (CA4), ausência de rede real e de credenciais (CA8), invariantes de shell (4) e de política (1, 3, 5). GREEN: implementar módulos M1→M6 na ordem de risco, cada um com gate individual; M6 herda e reutiliza fachada R470. VERIFY: executar `pytest` das suítes dedicadas + `core-check` + `doctor` após cada módulo; considerar concluído somente com todos os CA verificados e reflexão registrada no MetaBus.

## Roadmap de execução
- Fase 0 (planejamento, esta spec): aprovada e arquivada.
- Fase 1: M1 (fábrica de pesquisa) — maior ganho de abrangência; delegar ao agente `bernstein-orchestrator`/`ws-coder` sob supervisão.
- Fase 2: M2 + M3 (sandbox e roteamento) — resiliência operacional e de compute.
- Fase 3: M4 + M5 (supervisão desktop e modelos didáticos) — produtividade e educação.
- Fase 4: M6 (frontend SciHubEVA opt-in) — integração mais sensível; exige revisão de licença e política; último a executar.
- Fase 5: M7 (executor tig multi-provedor) — resiliência de execução da fábrica; exige revisão de licença (upstream sem licença declarada); integração por invocação externa opcional.
- Fase 6: M8 (observatório openclaw-qa) — participação comunitária e aporte de lições; exige atribuição CC BY-SA; nenhuma incorporação de conteúdo; veredito de adoção por ferramenta do Tool Workshop.
- Cada fase em ciclo evolutivo registrado no EvolutionRegistry (R47x+) com score e lições; cada falha gera reflexão no MetaBus e slashing proporcional conforme Token Economy.