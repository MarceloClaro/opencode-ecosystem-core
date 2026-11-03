# Arquitetura do OpenCode Ecosystem Core

Este documento descreve a organização técnica observável no checkout. Não é um
relatório de desempenho, cobertura ou validação externa. Para ressalvas sobre
alegações históricas, consulte [CORRIGENDUM.md](CORRIGENDUM.md).

> Hashes, testes e diagnósticos são controles internos de artefatos e
> configurações específicas; não constituem certificação externa de segurança,
> qualidade ou adequação para um domínio de uso.

## Configuração estrutural

A revisão R916 usa a configuração local atual e a coleta de fontes documentada
no atlas. Os comandos abaixo repetem a conferência, sem interpretar inventário
como prontidão funcional:

```bash
python3 -m marceloclaro.cli doctor
python3 -c "import json; c=json.load(open('opencode.json', encoding='utf-8')); print({'mcps': len(c.get('mcp', {})), 'agentes': len(c.get('agent', {}))})"
```

<!-- core-state:start -->
**329 agentes** · **25 MCPs** · **35 comandos** · **22 checks**

Inventário derivado de [opencode.json](opencode.json) e do [diagnóstico estrutural](marceloclaro/doctor.py). Contagens de configuração e checks não comprovam disponibilidade, autenticação, inferência ou validação externa.

Para conferir estes blocos, execute na raiz `.venv/bin/python scripts/reconcile_operational_docs.py --check`; para sincronizá-los, execute o mesmo comando sem `--check`.
<!-- core-state:end -->

A configuração inclui `ecosystem-network` e `polymath-labs-mcp`.
As contagens de edições anteriores permanecem em seus recibos históricos.

Specs, ciclos, testes e cobertura mudam com o checkout. Consulte,
respectivamente, `specs/`, `evolution/cycles.json`, `tests/` e a configuração
de CI em vez de tratar números de documentos antigos como estado atual.

## Atlas atual R916 e fluxos conectados

A [página offline](docs/architecture_map.html) e o
[guia minucioso R916](docs/ARQUITETURA_COMPLETA_CORE_R916.md) reúnem o grafo
estrutural integral, as camadas, símbolos, origens e todos os fluxogramas do
[catálogo](docs/architecture/flows.json), também publicados por inteiro no README.

O grafo atual amostra fontes de produção rastreadas e `opencode.json` do
diretório de trabalho. `git.commit` identifica a base 84ef082; `worktree_sha256`
identifica os bytes analisados. Removidos são omitidos, symlinks/submódulos não
são seguidos, não rastreados e privados ficam fora. O índice não produtivo usa
metadados da base Git, identificados por `content_source=git_base`.

Essa distinção é necessária porque o checkout contém remoções e modificações
posteriores ao último commit. A fachada acadêmica e o serviço estão presentes
novamente, mas R914 permanece parcial: os 34 cartões antigos, a CLI dedicada,
`profiles.py`, `scoring.py` e a spec anterior estão removidos. Regras locais,
atribuição A2A e inferência do especialista têm estados próprios.
[Estado e pendências](docs/ESTADO_ATUAL_CORE_R916.md).

| Vista | Fonte e significado |
|---|---|
| [JSON](docs/architecture/architecture-inventory.json) | Manifesto, hashes, AST, classes, funções, imports e exclusões |
| [DOT/SVG](docs/architecture/dependencies.svg) | Todos os módulos, inclusive isolados; pares de imports declarados |
| [Mermaid](docs/architecture/dependencies.mmd) | Mesmos IDs, módulos e pares, sem corte para caber no GitHub |
| [Manifesto Mermaid](docs/architecture/mermaid-correspondence.json) | Correspondência entre formatos e declarações AST |
| [Fluxos curados](docs/architecture/flows.json) | Controle/composição com fontes, decisões, falhas e limites |

Cada fluxo preserva as fronteiras de licença, conta, rede, execução e revisão
humana. O extrator estático não prova conexão funcional, prontidão ou segurança.
R879, R900 e R911 permanecem históricos, sem reescrever suas evidências.

## Visão das camadas

```mermaid
graph TD
    Usuario[Usuário ou automação] --> CLI[marceloclaro CLI]
    CLI --> Orquestrador[MarceloClaroOrchestrator]
    Orquestrador --> SDD[SpecRegistry e SpecVerifier]
    Orquestrador --> MCI[MetaBus e Blackboard]
    Orquestrador --> MCP[MCPs configurados]
    Orquestrador --> Agentes[Agentes configurados]
    Orquestrador --> MIRA[mira-presenter]
```

## Diagrama operacional atual

O diagrama abaixo resume o runtime observável sem tentar listar todos os
arquivos, classes auxiliares ou serviços opcionais do ecossistema.

```mermaid
flowchart TB
    Usuario2[Usuário ou automação] --> CLI2[CLI marceloclaro]
    CLI2 --> Orq2[MarceloClaroOrchestrator]
    Orq2 --> Router[AttentionRouter]
    Orq2 --> SpecRegistry2[SpecRegistry]
    Orq2 --> SpecVerifier2[SpecVerifier]
    Orq2 --> TDDRunner2[TDDRunner]
    Orq2 --> MetaBus2[MetaBus]
    Orq2 --> Blackboard2[Blackboard]
    Orq2 --> MCP2[MCPs configurados]
    Orq2 --> Agents2[Agentes configurados]
    Orq2 --> Mira2[mira-presenter]
    Mira2 --> Deck2[MiraDeckPipeline]
    Deck2 --> Engine2[MiraEngine]
```

| Camada | Responsabilidade | Referências principais |
|---|---|---|
| Entrada | CLI interativo e comandos diretos. | `marceloclaro/cli.py`, `MANUAL.md` |
| Orquestração | Coordenação de tarefas e roteamento. | `marceloclaro/orchestrator.py` |
| SDD/TDD | Registro de specs, critérios e evidência por teste. | `sdd/spec_engine.py`, `specs/`, `tests/` |
| Memória | Eventos, tarefas e reflexões compartilhadas. | `mci/` |
| Integrações | Servidores MCP e definição de agentes. | `opencode.json`, `integrations/` |
| Apresentação | Geração de deck a partir de pasta de produção. | `illustrations/mira_deck.py` |
| Integridade | Cálculo local de raiz de arquivos selecionados. | `benchmarks/merkle_integrity_guard.py` |

## Servidores MCP Interoperáveis

As entradas abaixo são derivadas das chaves `mcp` de `opencode.json`:

<!-- core-mcp:start -->
1. `antigravity-bridge`;
2. `artigo-academico-mcp`;
3. `arxiv-mcp`;
4. `caed-spaece-data`;
5. `chroma`;
6. `colibri-mcp`;
7. `context7`;
8. `ecosystem-network`;
9. `educacao-legislacao`;
10. `fetch`;
11. `filesystem`;
12. `latexmk-mcp`;
13. `litert-lm`;
14. `mcp-memory`;
15. `mcp-time`;
16. `metacognitive-interconnect`;
17. `oa-resolver`;
18. `playwright`;
19. `polymath-labs-mcp`;
20. `pypi-search`;
21. `qdrant`;
22. `rea`;
23. `scanners-mcp`;
24. `sequential-thinking`;
25. `web-deploy-mcp`;
<!-- core-mcp:end -->

O MCP `ecosystem-network` conecta o `MarceloClaroOrchestrator`, o roteamento
Transformer inspirado em atenção e a memória MetaBus/Blackboard aos executores
de análise e leitura Claude, Antigravity e Codex disponíveis no ambiente. A
coordenação tem limites de passos e tempo, não executa hooks importados e
exige a conclusão para reportar sucesso. O identificador `chatgpt` não controla
o aplicativo ChatGPT; o uso da CLI Codex requer selecionar `codex`
explicitamente. Disponibilidade e autenticação são verificações locais.

Na R644, `ecosystem_workflow` executa um DAG validado de até oito nós sobre
`AutonomousCoordinator`, sob um orçamento global de passos e prazo por
invocação. A execução é sequencial para preservar o Blackboard compartilhado.
`WorkflowStore` publica checkpoints atômicos e aplica exclusão entre processos
por ID; retomada confere a definição e conserva os nós concluídos. Resultado
incerto de execução interrompida exige repetição explícita. A saúde dos CLIs
usa metadados sanitizados em SQLite e pausa automática de 120 segundos.
`ecosystem_workflow_status` consulta o registro sem repetir execuções.

A presença dessas entradas de configuração não implica disponibilidade de toda
dependência externa em cada máquina. O `doctor` expõe a situação encontrada
localmente nos checks do inventário estrutural acima.

## Agentes e orquestração

O arquivo `opencode.json` é a fonte da contagem corrente de agentes configurados
para a integração OpenCode, reproduzida no inventário acima. O Blackboard pode apresentar registros em momentos
diferentes do processo de inicialização; por isso, não se deve misturar uma
contagem de runtime com a contagem declarada no arquivo de configuração.

O fluxo básico é:

1. uma tarefa chega pelo CLI ou por integração;
2. o orquestrador recupera contexto e publica ou encaminha a tarefa;
3. um agente produz um resultado e o estado é registrado;
4. a entrega é avaliada contra os critérios disponíveis para aquela tarefa.

Esse fluxo descreve mecanismos de software, não mérito externo do resultado.

## Domínios multiárea observáveis

| Área | Principais referências observáveis |
|---|---|
| Pipeline acadêmico agentivo | `agentic_science_v2/orchestrator.py`, `deep_research.py`, `review_agent.py`, `revision_agent.py`, `paper_composer.py` |
| Prova, formalização e raciocínio | `integrations/deepmind/formal_verifier.py`, `alphaproof_engine.py`, `aletheia_scaffold.py`, `deep_think_engine.py`, `autoformalizer.py`, `geometry_engine.py`, `lean4_verifier.py`, `egraph_rewriter.py`, `erdos_hirzebruch_solver.py` |
| Jurídico | `legal/integration.py`, `specializations.py`, `knowledge_base.py`, `precedents.py`, `datajud_client.py`, `benchmarks.py` |
| Clínico | `integrations/medical/clinical_game_theory.py`, `clinical_verifier.py`, `evidence_grounding.py`, `clinical_orchestrator_bridge.py` |
| Scientific RAG | `rag/scientific.py`, `rag/evolved.py`, `rag/enhanced_search_rag.py` |
| Universidade Sintética | `synthetic_university/core.py`, `combinatorial_engine.py`, `evolutionary_memory.py`, `mcp_server.py`, `api_gateway.py` |
| Runtime local | `integrations/litert_lm.py`, `litert_lm_provider.py`, `litert_lm_supervisor.py`, `integrations/colibri_provider.py` |
| Conselho científico, autoria e sandbox | `scientific_lab/council.py` (13 cientistas), `academic/author_editor.py` (IMRaD/estilo/raciocínios), `scanners/scientific_evolution.py` (calibração dev/holdout), `integrations/openshell_pilot.py` (sandbox), `integrations/gemini_client/` (executor Gemini portátil) |
| Integridade e quality gates | `installer/`, `benchmarks/merkle_integrity_guard.py`, `scripts/quality_report.py`, `benchmarks/scientific_reasoning/` |

## SDD e TDD

Uma spec formal pode declarar objetivo, critérios de aceitação, invariantes e
arquivo de teste. O `SpecVerifier` avalia a evidência estruturada disponível
para esses critérios. A ausência de evidência deve permanecer identificável,
em vez de ser apresentada como êxito.

O ciclo de desenvolvimento recomendado é:

1. definir ou ler a spec aplicável;
2. escrever o teste dirigido;
3. implementar a menor mudança que atende ao contrato;
4. executar os testes relevantes;
5. registrar limitações e resultados observados.

O resultado de um teste é restrito ao ambiente, versão e dados utilizados na
execução. Não transforme uma passagem local em certificação externa.

## MIRA e documentação em dupla leitura

O subsistema de apresentações inclui:

| Elemento | Papel |
|---|---|
| `MiraEngine` | Produz componentes visuais de apresentação. |
| `MiraDeckPipeline` | Executa os estágios `extract`, `plan`, `copywrite`, `build`, `animate` e `validate`. |
| `mira-presenter` | Agente usado na execução delegada da apresentação. |

`SPEC-935-R126` registra o agente delegável e `SPEC-935-R127` registra a
documentação em dupla leitura. A interface de uso é documentada no manual;
a arquitetura aponta os arquivos e as responsabilidades.

## Biblioteca técnica local e dados para fine-tuning (R657/R658)

`rag/book_library.py::LocalBookLibrary` extrai PDFs por página física e mantém
fontes, páginas, trechos e termos em SQLite local. Indexação explícita usa
transação; leitura verifica os hashes atuais e bloqueia fontes alteradas.
Os métodos `library_*` do `MarceloClaroOrchestrator` centralizam a interface.
`integrations/ecosystem_mcp.py` publica catálogo e páginas como resources,
busca como tool somente leitura e um prompt de revisão com referências.

`integrations/finetuning_data.py` valida pares, deduplica e conecta fontes
que compartilham conteúdo antes de dividir grupos inteiros entre conjuntos.
Seu gate de avaliação confere identidade do conjunto, protocolo e limiar de
melhora sobre números informados; não executa modelos. A CLI está em
`marceloclaro/library_cli.py`, com saída de dados limitada ao manifesto.

Os contratos, limites e provas locais estão em
[docs/BIBLIOTECA_AI_R657.md](docs/BIBLIOTECA_AI_R657.md).

## Vídeo, dublagem e animação R1035–R1046

O editor universal vive em `integrations/video_editor.py`: projeto com fontes
hashadas, fps racional, clipes frame-exatos, faixas e operações declarativas.
FFmpeg é o backend padrão; Remotion é um backend de composição com licença e
aprovação de render; `register_backend` permite outros motores. O MCP
`editor-local` expõe projeto/plano/render sem shell arbitrário.

A R1046 acrescenta, em `video_editor_advanced.py`, composição multifaixa com
posição/tamanho/opacidade/raio de canto, áudio explícito e lacunas
preto/silêncio; conformidade de fps com arredondamento explícito; transições
`xfade`/`acrossfade`; preset x264 allowlisted; e cor SDR paramétrica com
`eq`/`colorbalance`. O plano é revalidado por digest e hash de fontes; probes
restringem protocolos/formatos. Isso não é paridade com Premiere/DaVinci: não
há UI NLE, keyframes, LUT/ACES/HDR, tracking, multicam ou aprovação estética
automática.

A dublagem é uma cadeia separada: `dubbing_batch` prepara as partes,
`dubbing_evidence` coleta OCR, `video_diarization_nemotron` identifica locutores,
`video_speaker_cluster` agrupa e extrai referências, `dubbing_translate_batch`
traduz, e `dubbing_xtts`/`dubbing_synth` sintetizam com cache e limite estrito.
Cada etapa tem recibo e pode bloquear; nenhuma etapa autoriza publicação.

Ver [pipeline](docs/DUBBING_PIPELINE_R1041_R1045.md),
[editor](docs/EDITOR_VIDEO_UNIVERSAL_R1042.md),
[catálogo](docs/VIDEO_EDITOR_TOOLCHAIN_R1043.md) e
[estado atual](docs/ESTADO_ATUAL_CORE_R1045.md).

## Integridade e procedência

### REA sob coordenação central (R808)

`integrations.rea_bridge.ReaBridge` conecta o runtime externo identificado ao
`MarceloClaroOrchestrator.rea_action`. CLI e MCP `ecosystem_rea` convergem
nesse método; resultado e proveniência alimentam observações MetaBus sem
promover confiança. O OpenCode registra também o servidor `rea`, lançado pelo
adaptador, e mantém o agente primário `marceloclaro`. Reversa Universal mantém
seu papel existente. Contratos e limites: [REA](docs/REA.md).

`MerkleIntegrityGuard` e os mecanismos SHA-256 permitem comparar os bytes de
artefatos definidos. Eles ajudam a detectar divergência do material conferido,
mas não são uma prova geral de comportamento, segurança ou correção.

A instalação deve começar por uma versão identificada, um commit Git completo
e uma soma SHA-256 publicada para o artefato que será conferido. O procedimento
reprodutível e as limitações por plataforma estão em
[installer/README.md](installer/README.md).


## Atualização de orquestração R894–R897

O [mapa dos novos percursos](docs/ORQUESTRACAO_AGENTES_PLUGINS_CI_R894_R897.md)
conecta o ciclo de vida de agentes ao mesmo primário, gerador, Blackboard e
MetaBus. Os perfis persistentes ficam no catálogo canônico. A compilação lê os
mesmos bytes validados e o registro mantém sua identidade e hash. Instruções de
plugins, conexão hospedada, grafo Python estático e CI local têm fronteiras e
recibos separados; nenhum deles promove automaticamente confiança científica.

O [parecer Wolfram](docs/AVALIACAO_WOLFRAM_CORE_R895.md) explica o encaixe no
contrato de plugins existente e as condições de uma futura engine local.

## Frente científica R985–R1001

- **Conselho R989** (`scientific_lab/council.py`): 13 perfis `scientist-*` no
  catálogo, sob MarceloClaro; orquestração sequencial com uma tentativa por
  papel, contrato de saída `status/findings/evidence/limitations/feynman` e
  validação de citação literal. `partial` não interrompe; `blocked` interrompe.
- **Autor/Editor R991** (`academic/author_editor.py`): `MANUSCRIPT_SECTIONS`
  (IMRaD expandido), `style_fingerprint` anti-plágio e `reasoning_registry`
  mapeando tradições aos motores de `reasoning/`.
- **Scanner evolutivo R990** (`scanners/scientific_evolution.py`): avaliação
  dev/holdout de candidatos fixos, sem código arbitrário nem autopromoção.
- **Piloto OpenShell R992** (`integrations/openshell_pilot.py`): preflight e
  plano de ensaios; a validação real de isolamento e a captura de pacotes estão
  em `docs/evidence/` e no [procedimento](docs/PROCEDIMENTO_OPENSHELL_GEMINI_CONSELHO.md).
- **Executor Gemini R1001** (`integrations/gemini_client/`): cliente Rust que
  chama a API Gemini com `GEMINI_API_KEY`, executável dentro do sandbox sem OAuth.

As fronteiras permanecem: instalação/inventário, execução observada e validação
externa são estados distintos; nenhuma pontuação interna vira Qualis/aceite.
