# Avaliação de repositórios para metacognição e orquestração — R886

Avaliação em **14 de outubro de 2026**. **Knowl é o candidato prioritário para uma futura integração opcional de memória tipada.** Laya pode auxiliar decisões limitadas; Awesome LLM Apps fornece referências seletivas; OpenShell pode oferecer contenção de execução; Feynman pode atuar como especialista de pesquisa. Nenhum deles, isoladamente, resolve a coerência do Core.

O escopo desta fase prioriza conexões internas entre memória canônica, reflexão, raciocínio e delegação pelo `MarceloClaroOrchestrator`. **Nenhum runtime externo é instalado ou executado por este levantamento.** As propostas abaixo são contratos de integração e critérios de adoção, não capacidades entregues.

## Método e limites da leitura

Foram consultados pelo conector GitHub os metadados dos cinco repositórios, a branch padrão, o HEAD, árvores recursivas sem truncamento, arquivos de licença e os arquivos de interface citados abaixo. Os READMEs também foram relidos nos SHAs fixados. Todos os cinco repositórios estavam públicos, acessíveis, não arquivados e eram forks no momento da consulta.

Não foram executados instaladores, modelos, servidores, testes ou workflows desses projetos. Código consultado não equivale a integração funcional, inferência concluída, calibração ou validação externa. Alegações de desempenho nos READMEs pertencem aos projetos e não foram reproduzidas aqui.

A busca nominal por clones em `/home/marceloclaro`, até profundidade quatro e excluindo caches, ambientes e dependências, não encontrou diretórios com os cinco nomes. Isso não comprova ausência de instalações ou de clones renomeados, mais profundos ou em outros locais.

Os dados estruturados, caminhos e fontes permanentes estão em [metacognition-candidates-r886.json](metacognition-candidates-r886.json).

## Fotografia dos candidatos

| Repositório | HEAD examinado | Data do commit HEAD, UTC | Licença do código | Papel recomendado |
| --- | --- | --- | --- | --- |
| [laya](https://github.com/MarceloClaro/laya/tree/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d) | `c73908d96ff73c0062c340a11bf7c54ec7d8bc4d` | 2026-10-12T09:29:59Z | [Apache-2.0](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/LICENSE) | Conselho auxiliar, sem autoridade de confiança |
| [knowl](https://github.com/MarceloClaro/knowl/tree/b90ca83c82c284a4f58f43934ea1de7dd03bcab3) | `b90ca83c82c284a4f58f43934ea1de7dd03bcab3` | 2026-09-10T06:12:55Z | [Apache-2.0](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/LICENSE) | Memória tipada opcional, primeira prioridade |
| [awesome-llm-apps](https://github.com/MarceloClaro/awesome-llm-apps/tree/6272f8bd1fdeb75153d1a95d7fc761e26e477116) | `6272f8bd1fdeb75153d1a95d7fc761e26e477116` | 2026-09-13T03:46:11Z | [Apache-2.0](https://github.com/MarceloClaro/awesome-llm-apps/blob/6272f8bd1fdeb75153d1a95d7fc761e26e477116/LICENSE) | Referência seletiva |
| [OpenShell](https://github.com/MarceloClaro/OpenShell/tree/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0) | `5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0` | 2026-09-12T00:17:15Z | [Apache-2.0](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/LICENSE) | Sandbox opcional de execução |
| [feynman](https://github.com/MarceloClaro/feynman/tree/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c) | `dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c` | 2026-09-06T18:51:09Z | [MIT](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/LICENSE) | Especialista opcional de pesquisa |

Os upstreams informados pela API eram `NandhaKishorM/laya`, `dat999zx/knowl`, `Shubhamsaboo/awesome-llm-apps`, `NVIDIA/OpenShell` e `Companion-Inc/feynman`. Suas datas de último push eram posteriores às dos forks consultados. Esse dado indica necessidade de revisar sincronização; não informa quantos commits divergem, nem prova que atualizar melhoraria a qualidade. A comparação de históricos não foi executada. Os SHAs acima permanecem a referência desta avaliação.

## Knowl: memória tipada e substituição auditável

O pacote examinado é `@dat999zx/knowl` **5.23.0**, para Node.js >=22. O schema SQLite contém itens de conhecimento, asserções, evidências, histórico de commits, `source_commit`, `provenance` e `superseded_by_id`. O store por projeto está documentado em `.knowl/knowl.db`; também existe estado por máquina em `~/.knowl/`. [Schema](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/src/store/schema.ts#L1-L108), [requisitos e dados locais](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/README.md#L842-L858).

A interface útil é `knowl serve`, por MCP stdio. Entre os contratos reais estão `knowl_store`, `knowl_ingest_atoms`, `knowl_decide`, `knowl_query`, `knowl_timeline`, `knowl_conflicts` e `knowl_evidence_list`. As operações de armazenamento estruturado não exigem configuração de IA do Knowl. A ingestão de texto bruto por IA é outra operação, e a própria descrição exige solicitação explícita. [Transporte](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/src/mcp/server.ts#L144-L163), [ferramentas de armazenamento](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/src/mcp/tool-definitions.ts#L403-L543), [consulta e conflitos](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/src/mcp/tool-definitions.ts#L640-L740).

**Integração proposta:** um adaptador opcional, acionado pelo orquestrador, projeta átomos canônicos do MetaBus com IDs estáveis, fonte, commit, caminhos afetados, estado epistêmico e vínculo de substituição. A consulta pode trazer candidatos, mas a promoção a evidência observada continua sob os contratos do Core. Inicialmente, uma projeção em uma direção torna explícita a autoridade; uma sincronização bidirecional sem regra de conflitos criaria outra ilha.

**Custos e restrições:** Node e dependências nativas, disco e migrações SQLite; embeddings são opcionais. Recursos de nuvem e provedores de IA devem permanecer separados do modo local. `knowl init` registra hosts e altera configuração, portanto não foi executado como simples sonda. A documentação afirma que worktrees compartilham o store principal; concorrência, isolamento e restauração exigem teste antes da adoção. A palavra `confidence` do store não constitui confiança calibrada de agente. [Pacote](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/package.json#L1-L27), [conexão de agentes](https://github.com/MarceloClaro/knowl/blob/b90ca83c82c284a4f58f43934ea1de7dd03bcab3/README.md#L172-L189).

## Laya: decisão tipada com abstenção, sem substituir julgamento

O pacote Python examinado é **0.4.6**, com PyTorch/Transformers, SDK e extras opcionais. O MCP stdio `laya-mcp-server` expõe `laya_status`, `laya_route`, `laya_predict`, `laya_decide`, shortlist e operações batch. O HTTP opcional usa `POST /v1/systemone` e `/v1/systemone/batch`. A interface produz decisões `choice`, `score` e `noul`; não é uma interface de explicação aberta. [Pacote](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/pyproject.toml#L5-L50), [contratos MCP](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/docs/cli-mcp.md#L156-L231), [HTTP](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/laya/serve.py#L1-L26).

**Integração proposta:** classificar uma lista curta de intenções ou sugerir seleção de ferramenta, em modo consultivo, com abstenção e fallback explícito. A saída não altera `TrustEngine`, não autoriza efeitos externos e não transforma uma hipótese em fato. O próprio guia separa confiança de autorização.

**Custos e restrições:** a primeira inferência obtém pesos do Hugging Face; o cache permite usos posteriores locais. Os checkpoints descritos têm centenas de milhões de parâmetros. O preload por sessão MCP pode multiplicar consumo de memória; um servidor local compartilhado é alternativa a avaliar. RAM, latência, precisão em português e licenças específicas dos pesos não foram verificadas nesta máquina. `LAYA_BASE_URL` permite serviço remoto, e o HTTP declara host padrão `0.0.0.0`; localização do processo e exposição da interface precisam ser configuradas. [Lifecycle MCP](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/laya/mcp/server.py#L132-L187), [requisitos de carga](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/docs/cli-mcp.md#L48-L69).

O README do snapshot reconhece sobreconfiança, necessidade de calibração e falhas em exemplos de negação, inclusive com rótulos semânticos. Isso impede usar seus escores como gate de confiança sem ensaio local com casos positivos, negativos, negados e dados retidos da tarefa real. A qualidade de uma explicação do Core não pode ser deduzida da confiança desse classificador. [Limitações declaradas](https://github.com/MarceloClaro/laya/blob/c73908d96ff73c0062c340a11bf7c54ec7d8bc4d/README.md#L1551-L1580).

## Awesome LLM Apps: aproveitar contratos, não instalar uma coleção

O repositório é um catálogo de aplicações com dependências e provedores diferentes. A leitura dirigida encontrou três referências pertinentes:

- O RAG tipado define `Citation`, `Answer`, `RetrievalEvidence` e recusa sem evidência suficiente. O validador liga citação a um chunk conhecido e verifica trecho textual. É útil para o contrato de saída do Core; verificar substring não demonstra, por si, apoio semântico à conclusão. [Modelos e validação](https://github.com/MarceloClaro/awesome-llm-apps/blob/6272f8bd1fdeb75153d1a95d7fc761e26e477116/rag_tutorials/agentic_typed_rag_pydanticai/agent.py#L26-L63), [checagem das citações](https://github.com/MarceloClaro/awesome-llm-apps/blob/6272f8bd1fdeb75153d1a95d7fc761e26e477116/rag_tutorials/agentic_typed_rag_pydanticai/agent.py#L174-L217), [testes disponíveis, não executados](https://github.com/MarceloClaro/awesome-llm-apps/blob/6272f8bd1fdeb75153d1a95d7fc761e26e477116/rag_tutorials/agentic_typed_rag_pydanticai/test_typed_rag.py).
- O Multi-MCP Agent Forge conecta `ClientSession` via stdio e distribui ferramentas por especialista. Serve de referência para escopo de capacidades, mas já há um orquestrador no Core. A implementação consultada usa Anthropic e inicia servidores `npx -y`; adoção exigiria fixação de versões e política de execução. [Conexão e chamadas](https://github.com/MarceloClaro/awesome-llm-apps/blob/6272f8bd1fdeb75153d1a95d7fc761e26e477116/mcp_ai_agents/multi_mcp_agent_router/agent_forge.py#L150-L227).
- O Corrective RAG exemplifica reavaliação da recuperação e fallback de busca. A aplicação usa LangGraph, OpenAI, Qdrant e ferramentas de busca, acrescentando dependências e possível tráfego/custo. O padrão de reavaliar a evidência pode ser incorporado aos módulos existentes sem importar a aplicação. [Implementação](https://github.com/MarceloClaro/awesome-llm-apps/blob/6272f8bd1fdeb75153d1a95d7fc761e26e477116/rag_tutorials/corrective_rag/corrective_rag.py).

**Recomendação:** referência seletiva com atribuição de origem e testes próprios do Core. Não há conclusão única de privacidade, compatibilidade ou custo para toda a coleção.

## OpenShell: fronteira de execução opcional

OpenShell é um runtime de sandbox, não um motor de raciocínio. O snapshot descreve CLI, políticas YAML, gateway e drivers de execução. Os contratos incluem `sandbox create/connect/list`, `policy set`, providers e logs. A política descreve restrições de sistema de arquivos, processos e saída de rede. O código MCP examinado trata revisões/opções para políticas; sua presença não equivale a um servidor de raciocínio MCP. [CLI](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/README.md#L169-L180), [política](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/architecture/security-policy.md#L11-L50), [módulo MCP](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/crates/openshell-core/src/mcp.rs#L1-L24).

**Integração proposta:** backend opcional de execução do Core/REA, conservando a tarefa, o orçamento, a política, os recibos e os artefatos sob o orquestrador. Antes de selecioná-lo, comprovar criação, bloqueio e permissão de rede, limites de arquivos, término e coleta dos resultados.

**Custos e restrições:** requer Docker, Podman ou virtualização; Windows com WSL 2 é experimental no README consultado. O pacote Python fornece somente SDK, não o CLI. O build declara Rust >=1.94; GPU exige componentes adicionais. Instalar um SDK não permite declarar o isolamento de uma análise. [Pré-requisitos](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/README.md#L21-L50), [toolchain](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/Cargo.toml#L8-L13).

**Telemetria:** há coleta padrão documentada. O gateway aceita `OPENSHELL_TELEMETRY_ENABLED=false`; Helm usa `server.telemetryEnabled=false`; o projeto também documenta build sem o recurso. O opt-out não governa terceiros, provedores ou agentes. Uma promessa de execução sem saída da máquina requer política e medição de tráfego, ainda não realizadas. [Configuração e limites](https://github.com/MarceloClaro/OpenShell/blob/5b9daab9351b1e053f9a5e0ce4c899f5d3f674b0/README.md#L261-L294).

## Feynman: especialista de pesquisa com fronteira explícita

O pacote examinado é `@advaitpaliwal/feynman` **0.3.49**, Node >=22.22.0 e <26, com CLI baseado em Pi/alphaXiv. Há workflows de pesquisa e interfaces `deepresearch`, `lit`, `rank`, `paper`, `audit` e execução pontual. Skills podem ser instaladas separadamente para OpenCode/Codex; isso não instala o runtime. O README descreve configuração de modelos locais e conectores que podem utilizar rede. [Pacote](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/package.json#L1-L12), [modelos e skills](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/README.md#L53-L119), [workflows](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/README.md#L123-L223).

**Integração proposta:** especialista delimitado, chamado pelo orquestrador com timeout, orçamento e política de rede. Importar artefatos e fontes para o EvidenceGraph do Core, preservando a execução e a origem. A instrução do agente verificador exige apoio específico para cada afirmação e distinção de certeza; é uma referência de contrato, não comprovação de execução ou correção. [Verificador](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/.feynman/agents/verifier.md#L1-L20), [workflow de pesquisa](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/prompts/deepresearch.md#L1-L19).

**Distinção necessária:** o módulo [`reversa_feynman/`](../reversa_feynman/) já presente no Core deriva de `MarceloClaro/reversa`, conforme [SPEC-935-R504](../specs/SPEC-935-R504-feynman-governance.md). Ele é um port Python independente de contratos/gates; não comprova integração com este CLI. Manter nomes e recibos diferentes evita confundir a camada de governança existente com o agente de pesquisa externo.

**Custos, telemetria e limites:** provedores hospedados e conectores podem exigir credenciais e cobranças; modelos locais consomem recursos da máquina e não tornam busca online local. O código resolve telemetria PostHog habilitada por padrão; `FEYNMAN_TELEMETRY=false` ou `DO_NOT_TRACK=1` desativa essa configuração. Extensões, OTLP e provedores precisam de revisão própria. A interface publicada examinada é CLI; não se presume servidor MCP cognitivo a partir dos ledgers de MCP do workbench. [Telemetria](https://github.com/MarceloClaro/feynman/blob/dfdcb7cf2c73183cff7b10aa8ea8ce370c8b152c/src/telemetry/posthog.ts#L249-L302).

## Critérios para uma integração sem ilhas

As seguintes condições orientam qualquer adoção posterior:

1. **Uma coordenação:** toda chamada de provedor deve carregar `task_id`, objetivo e limites definidos pelo `MarceloClaroOrchestrator`. Nenhum segundo coordenador recebe autoridade implícita.
2. **Uma memória canônica:** MetaBus conserva os registros do Core. Adaptadores carregam IDs e versões, registram substituições e distinguem memória ativa, obsoleta e contestada.
3. **Raciocínio vinculado à evidência:** a reflexão registra o que foi recuperado, decisão, incerteza, contradições e próximo teste. Uma nova explicação não vale como nova observação.
4. **Falhas visíveis:** ausência, timeout, resposta inválida ou bloqueio de rede vira resultado explícito. Fallback tem nome e origem; não simula execução do provedor.
5. **Confiança condicionada a resultados:** escores de memória/classificador permanecem separados do histórico de desempenho e da evidência do gate do Core.
6. **Aceite por execução:** provar o caminho tarefa → recuperação → decisão → ferramenta → resultado → reflexão → memória e as falhas correspondentes com testes tipados. Validar novamente após reiniciar; uma chamada isolada não prova continuidade.
7. **Instalação posterior e controlada:** fixar revisão/artefato, preservar licenças e procedência, revisar privilégios, tráfego e configuração. Esta avaliação não executou essa etapa.

A prioridade prática é consolidar o ciclo interno do Core e medir esse caminho antes de acrescentar runtimes. Os candidatos podem completar funções específicas mediante contratos; não justificam declarar que o ecossistema inteiro está livre de falhas.
