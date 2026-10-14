# Avaliação dirigida R888 — ciência, tutoria e simulação

Data: 14 de outubro de 2026. Escopo B: quatro repositórios solicitados pelo usuário.
Resultado: há contribuições úteis, sobretudo em governança científica e memória pedagógica. A recomendação é adaptar contratos e padrões ao primário e à memória existentes, preservando as diferenças entre evidência observada, interpretação e cenário simulado. Nenhum runtime destes quatro projetos foi instalado ou executado.

## Fontes fixadas e alcance

As referências foram consultadas no GitHub e os arquivos selecionados foram baixados do commit atual de cada branch padrão. A avaliação inclui leitura de entrypoints, dependências, configuração de rede, persistência, licença e integração. O manifesto [repo-reviews-r888-b.json](repo-reviews-r888-b.json) registra SHA-256, tamanho e URL fixa de cada arquivo. Foi aplicada seleção dirigida: cada arquivo tem menos de 1 MB, sem checkout executável, submódulos, modelos ou instalação de dependências.

| Projeto | Commit consultado | Arquivos / bytes lidos | Contribuição e decisão |
|---|---|---:|---|
| science-skills | `48df32bf95d3ee512e4962f1a6b67831b19e3549` | 15 / 130.866 | Priorizar governança de evidências e carregamento seletivo de skills. |
| feynman-tutor | `9e9ec6fa08bd2242b7aea1cf3419e28ea2e70664` | 9 / 143.098 | Adaptar memória de compreensão e perguntas de tutoria; sem novo sistema de memória. |
| MiroFish | `fa0f6519b10c4a25b78f1bcc1f00dfcd8bf1ab41` | 20 / 471.957 | Padrões de cenário e orçamento; não incorporar o runtime remoto. |
| MiroFish-Offline | `313fe642853ff9fff05e3ecae2e439886c2d29f4` | 25 / 460.731 | Referência para armazenamento desacoplado e execução local futura; sem instalar o stack neste ciclo. |

A amostra não representa auditoria integral do código ou de todas as dependências. Não foram medidos ganhos de tokens, qualidade científica, aprendizagem humana ou precisão preditiva.

## REA usado pelo primário: resultados reais

As chamadas passaram por `MarceloClaroOrchestrator(auto_load_agents=False)`, sem delegação direta a agentes do catálogo. Para JavaScript, o primário chamou `rea_action` e o servidor REA MCP instalado, versão 6.4.0, commit `4daea941bfeeb426886f2d048aed7f3cb2dbf97b`. Foi usada a operação `analyze_javascript_application`, com fontes como texto inerte.

| Alvo | Operação e resultado | Limite |
|---|---|---|
| science-skills, `http_client.py` | `rea_assistant_action(inspect)`: tipo não reconhecido. | O assistente atual não oferece parser Python para esse alvo; análise complementar foi leitura estática direta. |
| feynman-tutor, `extract_content.py` | `rea_assistant_action(inspect)`: tipo não reconhecido. | Markdown e Python não foram analisados semanticamente pelo REA. |
| MiroFish, frontend selecionado | MCP concluído: 3 arquivos relevantes, 2 JavaScript, 7.689 bytes, 44 nós e 46 arestas. | Subconjunto de frontend; não inclui execução do backend, Vue completo ou comportamento de agentes. |
| MiroFish-Offline, frontend selecionado | MCP concluído: 3 arquivos relevantes, 2 JavaScript, 7.739 bytes, 42 nós e 44 arestas. | Mesmo limite: grafo estático do subconjunto, sem simulação real. |

As primeiras chamadas JavaScript usaram arquivo individual e foram rejeitadas: o analisador exige diretório ou ASAR. Foram repetidas com o diretório de frontend selecionado, sem alterar arquivos de origem. Os erros e os resultados posteriores foram preservados em `outputs/core-r888/b-*-rea*.json`; seus hashes constam no manifesto público. As duas análises concluídas possuem observação persistida no MetaBus e `confidence_promoted: false`.

REA encontrou zero falhas de parsing nesses dois subconjuntos. As próprias respostas esclarecem que imports, endpoints e relações estáticas não comprovam invocação em tempo de execução; resolução dinâmica continua limitada. A ausência de contradições de integridade nesses artefatos não certifica segurança ou correção do aplicativo.

## science-skills: contribuição de maior prioridade

O [README fixado](https://github.com/MarceloClaro/science-skills/blob/48df32bf95d3ee512e4962f1a6b67831b19e3549/README.md) descreve um catálogo de instruções, referências e scripts, e não um novo coordenador. O software tem licença Apache-2.0; os demais materiais são declarados CC-BY-4.0. O [mapa de licenças e termos de fontes](https://github.com/MarceloClaro/science-skills/blob/48df32bf95d3ee512e4962f1a6b67831b19e3549/SKILL_LICENSES.md) torna explícito que as bases consultadas têm termos próprios. O identificador Apache informado pela API GitHub, isoladamente, não cobre toda essa distinção.

O [skill PubMed](https://github.com/MarceloClaro/science-skills/blob/48df32bf95d3ee512e4962f1a6b67831b19e3549/skills/pubmed_database/SKILL.md#L131-L158) exige consulta à referência da operação, resultado estruturado, filtragem antes de carregar grandes respostas, interrupção de buscas sem correspondência após um orçamento definido e proibição de inventar identificadores. Esses padrões cabem em `integrations/scientific_plugins.py` e no pipeline de governança existente, sem duplicar conectores NCBI ou outras integrações já disponíveis.

A [interpretação de AlphaGenome](https://github.com/MarceloClaro/science-skills/blob/48df32bf95d3ee512e4962f1a6b67831b19e3549/skills/alphagenome_single_variant_analysis/docs/interpretation-guide.md#L157-L184) preserva resultados negativos e distingue localização, efeito previsto e limitação do modelo. Seu [checklist de relato](https://github.com/MarceloClaro/science-skills/blob/48df32bf95d3ee512e4962f1a6b67831b19e3549/skills/alphagenome_single_variant_analysis/docs/interpretation-guide.md#L284-L340) pede vínculo explícito a gráficos e escores. Adaptar a forma de rastrear suporte e refutação é útil; transportar limiares específicos de biologia para confiança genérica do Core seria inadequado.

O [cliente HTTP comum](https://github.com/MarceloClaro/science-skills/blob/48df32bf95d3ee512e4962f1a6b67831b19e3549/skills/science_skills_common/http_client.py) centraliza rate limit por API com lock entre processos, retry de 429/5xx, backoff, `Retry-After` e timeout. É um padrão útil para consultas autorizadas, porém seus defaults permitem sete retentativas e esperas longas; o Core deve impor orçamento global e cancelamento. Ele usa `fcntl`, portanto a portabilidade Windows nativa não é demonstrada pela leitura. Não foram feitas chamadas científicas externas nesta avaliação.

## feynman-tutor: memória pedagógica, sem segunda autoridade

O [SKILL corrente](https://github.com/MarceloClaro/feynman-tutor/blob/9e9ec6fa08bd2242b7aea1cf3419e28ea2e70664/SKILL.md) e as [regras de notas](https://github.com/MarceloClaro/feynman-tutor/blob/9e9ec6fa08bd2242b7aea1cf3419e28ea2e70664/references/note-management.md) são mais informativos que a descrição resumida do README. A proposta separa preferências expressas, padrões sustentados por múltiplas observações e situações ainda sem interpretação. A recuperação de tema/vizinhança possui orçamento aproximado de nove notas e não exige carregar toda a memória. O texto também pede revisão do aprendiz antes de registrar notas e inferências pessoais.

A adaptação adequada é uma modalidade de explicação e revisão no primário: recuperar memória contextual do MetaBus, formular perguntas sobre pontos sem suporte, preservar a resposta e suas referências como observação. Isso pode complementar `mci/metacognitive_loop.py` e `reversa_feynman/feynman_gates.py`, com teste de que uma resposta fluente não promove trust nem prova aprendizagem. Não criar um `notes/` paralelo como nova autoridade.

O projeto MIT é diferente de `MarceloClaro/feynman`, avaliado anteriormente como assistente de pesquisa, e do módulo `reversa_feynman` do Core. O [launcher](https://github.com/MarceloClaro/feynman-tutor/blob/9e9ec6fa08bd2242b7aea1cf3419e28ea2e70664/scripts/run.py#L54-L119) cria venv, instala dependências sem versões fixadas e baixa navegadores. O caminho normal faz essas preparações antes de chamar o extrator. Por isso ele não foi acionado: tutoria em Markdown não implica que seu pipeline de YouTube, páginas, cookies ou PDF seja offline.

## MiroFish e MiroFish-Offline: referência de cenário, não prova preditiva

O [MiroFish original](https://github.com/MarceloClaro/MiroFish/blob/fa0f6519b10c4a25b78f1bcc1f00dfcd8bf1ab41/backend/app/config.py#L30-L36) configura OpenAI remoto por default e requer Zep Cloud. Seu [pyproject](https://github.com/MarceloClaro/MiroFish/blob/fa0f6519b10c4a25b78f1bcc1f00dfcd8bf1ab41/backend/pyproject.toml) agrega Flask, OpenAI, CAMEL e OASIS. É uma aplicação com runtime próprio; incluí-la inteira criaria outra camada de coordenação e memória.

Há padrões concretos aproveitáveis: distinguir documentos de origem, perfis gerados, condições do cenário, rodadas e relatório; limitar chamadas de ferramentas e reflexão; manter o ciclo de vida da execução observável. O [report agent](https://github.com/MarceloClaro/MiroFish/blob/fa0f6519b10c4a25b78f1bcc1f00dfcd8bf1ab41/backend/app/services/report_agent.py#L875-L882) estabelece tetos próprios por seção e conversa. O Core pode reimplementar um contrato geral de orçamento sem copiar o runtime ou tratar a reflexão do modelo como validação.

O [Offline](https://github.com/MarceloClaro/MiroFish-Offline/blob/313fe642853ff9fff05e3ecae2e439886c2d29f4/backend/app/config.py#L30-L42) troca defaults por Ollama e Neo4j locais. Sua [interface GraphStorage](https://github.com/MarceloClaro/MiroFish-Offline/blob/313fe642853ff9fff05e3ecae2e439886c2d29f4/backend/app/storage/graph_storage.py) separa armazenamento e aplicação; embeddings em lote com cache também oferecem referência de implementação. O benefício seria um adaptador opcional com proveniência, subordinado ao MetaBus/EvidenceGraph, caso uma necessidade mensurável o justifique.

O nome Offline não é uma barreira técnica contra rede: os endpoints são configuráveis, o SDK aceita a URL configurada e a leitura não mostrou uma política de egress obrigatória. Os defaults de [Flask](https://github.com/MarceloClaro/MiroFish-Offline/blob/313fe642853ff9fff05e3ecae2e439886c2d29f4/backend/run.py#L40-L45), [CORS](https://github.com/MarceloClaro/MiroFish-Offline/blob/313fe642853ff9fff05e3ecae2e439886c2d29f4/backend/app/__init__.py#L42-L43) e [Docker Compose](https://github.com/MarceloClaro/MiroFish-Offline/blob/313fe642853ff9fff05e3ecae2e439886c2d29f4/docker-compose.yml) exigem ajuste antes de um eventual uso local isolado: host aberto, debug ativo por default, origem CORS ampla, senha de exemplo e portas publicadas sem endereço loopback. O modelo LLM default é `qwen2.5:32b`; o Compose reserva até 2 GB de heap para Neo4j. Esses recursos não foram iniciados.

Ambos declaram AGPL-3.0. Código não foi transplantado para o produto; uma eventual incorporação exige decisão explícita sobre compatibilidade e forma de distribuição. Padrões gerais podem ser reimplementados com contrato próprio. Nada nesta revisão demonstra que cenários de agentes predizem populações reais.

## Contrato proposto para adaptação no Core

1. Toda operação passa por `MarceloClaroOrchestrator`; plugins, tutoria e simulação não ganham um coordenador independente.
2. MetaBus continua como memória canônica. Uma projeção de busca ou interface gráfica carrega referências às observações de origem.
3. Cada resultado declara repositório/commit de origem, hash do artefato, método, tipo de fonte e limitações. Resultado de consulta não é automaticamente uma evidência verificada.
4. Separar `observed`, `inferred` e `simulated`. Cenários sintéticos não podem alimentar confirmação externa, promoção automática de confiança ou indicadores de qualidade epistêmica.
5. Orçamentos de itens, bytes, rodadas, chamadas e tempo são explícitos; esgotamento deve aparecer no resultado.
6. A implementação deve nascer de spec e testes negativos de entrada vazia, fonte ausente, simulação apresentada como evidência e provider indisponível. Ganho de tokens só pode ser declarado após comparação própria com baseline.

O relatório e seu manifesto são artefatos de avaliação. A presença de um padrão nesta lista não significa que sua adaptação esteja implementada. A integração e as medições subsequentes devem possuir recibo próprio.

Não foram encontrados identificadores explícitos de telemetry, PostHog, Sentry, Mixpanel, analytics ou Amplitude nos arquivos selecionados destes quatro projetos. A busca é limitada à amostra e não cobre dependências transitivas; não sustenta uma garantia de ausência de telemetria.
