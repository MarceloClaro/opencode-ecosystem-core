# Arquitetura completa do Core — R916

> **Apresentação R1056:** [todos os fluxos em GIF/PNG/SVG](architecture/ANIMATED.md).
> A animação complementa este retrato histórico; não recalcula seus módulos,
> fontes ou hashes. [Manifesto](architecture/animated/manifest.json).

Este atlas parte das fontes e percorre interfaces, coordenação, execução,
conhecimento e entrega. Os diagramas estruturais e operacionais se completam:
um import mostra dependência declarada; um fluxo curado explica um caminho e
seus gates. Nenhum dos dois comprova que todos os caminhos foram executados.

## Origem, abrangência e formatos

Base Git `d02817ca460ee6411761a8a3f0b82d17dafd2740`; identidade das fontes locais `d53ac4511f757431da55589db0e6a0fcde2daebdb2b20303611d45882b7ab6b5`.

**707 módulos Python**, **1000 pares internos**, **1131 declarações de importação**, **6779 símbolos**, **45 pacotes**, **18 camadas** e **22 fluxogramas**.

O inventário inclui 10267 arquivos rastreados presentes e
8 superfícies não Python. Há 0 erros
de AST na extração, 6 imports dinâmicos e
4119 registros de imports externos. Parsing sem erro não
comprova importação executável ou instalação das dependências.

| Artefato | Como usar |
|---|---|
| [Página offline](architecture_map.html) | Busca por módulos, filtro de camada, zoom e todos os fluxos |
| [Visão operacional](architecture/curated-overview.svg) | Interfaces e fronteiras principais; composição explicada |
| [Grafo integral SVG](architecture/dependencies.svg) | Todos os módulos Python, inclusive isolados, e pares internos |
| [Grafo integral Mermaid — raw 2,4 MB](https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/docs/architecture/dependencies.mmd) | Mesmos IDs, módulos, pares e metadados, sem truncar para o GitHub |
| [Render Mermaid](architecture/dependencies-mermaid.svg) | Layout alternativo do mesmo grafo |
| [Por pacote](architecture/overview.svg) | Agrupamento das dependências entre pacotes |
| [Inventário JSON](architecture/architecture-inventory.json) | Hashes, símbolos qualificados, linhas, imports e classificação |
| [Manifesto Mermaid](architecture/mermaid-correspondence.json) | Correspondência independente entre os formatos |
| [Catálogo dos fluxos](architecture/flows.json) | Fontes ancoradas, legendas e limites de cada fluxo |
| [README completo](../README.md#fluxogramas-operacionais-completos) | Todos os fluxogramas Mermaid no documento principal |

> O Mermaid integral tem **2,4 MB** e excede o limite do renderizador do GitHub.
> O link abre o arquivo **raw** para renderização local; use o SVG Graphviz, o
> SVG Mermaid ou a página offline para leitura imediata.

### Identidade das fontes

O modo `worktree` lê somente fontes de produção rastreadas e `opencode.json`.
O commit em `git.commit` é a base, não a identidade dos bytes modificados.
`git.source_manifest`, `changed_paths`, `deleted_paths` e `worktree_sha256`
explicitam a diferença. Removidos são omitidos; symlinks e submódulos não são
seguidos. Fontes não rastreadas, pastas privadas e dados locais novos ficam fora.
As demais categorias usam `content_source=git_base`: seus metadados não são
uma auditoria dos conteúdos locais. Isso evita a circularidade de hashear o
README e os mapas gerados como parte da própria identidade de produção.

A extração repete hashes ao terminar e recusa mudança concorrente. O modo Git
continua determinístico e ignora alterações locais. Na página, uma fonte
modificada localmente mostra caminho/linha e condição local, sem atribuir esses
bytes a um permalink do commit-base. Fontes inalteradas podem apontar à base.

## Sequência operacional

1. **Entrada e contrato.** CLI, OpenCode, MCP e Streamlit chegam ao primário
   `MarceloClaroOrchestrator`. O contrato valida operação, campos, orçamento,
   prazo e efeito. Perfis têm capacidades, origem, spec/teste, permissões e
   saída esperada; nomes no catálogo não significam agentes executados.
2. **Preparação e atribuição.** O ciclo metacognitivo recupera memória com fonte
   e versão. O primário cria a tarefa no Blackboard A2A e seleciona executor.
   Memória recuperada é contexto, não instrução com autoridade sobre o usuário.
   Workflows possuem definição e checkpoints; a retomada exige compatibilidade
   e repetição de falha explicitamente autorizada pelo parâmetro próprio.
3. **Execução e aceite.** O executor produz artefatos e recibos. `report_completion`
   aplica critérios e histórico TDD quando exigido. Trust/economia e reflexão
   têm efeitos distintos. Um processo concluído pode falhar no conteúdo; uma
   tarefa atribuída pode continuar pendente de executor.
4. **Conhecimento e raciocínio.** RAG mantém fontes e abstenção, os dois modelos
   EvidenceGraph têm papéis diferentes, e o contexto de código extrai estrutura.
   Os motores restritos declaram indisponibilidade/fallback. Resultados Lean
   dependem da rota: compilação local e verificação lexical são estados distintos.
5. **Inspeção e ciência.** REA estático produz recibos por hash sob limites
   declarados. Análise reproduzível, runtime sintético, descoberta, composição
   de manuscrito e revisão acadêmica são percursos diferentes. Um cenário de
   agentes sintéticos não é experimento validado sobre população real.
6. **Memória e entrega.** MetaBus registra episódios, erros e próximas ações.
   Observação local não promove confiança calibrada nem valida fontes externas.
   A entrega inclui limitações, proveniência e revisão humana. Publicação ou
   envio a serviços externos depende da configuração e autorização pertinentes.

## Integrações e fronteiras

**Plugins locais.** Core, REA, MiroFish e Lean usam entradas MCP próprias e o
mesmo primário. O host hospeda a conversa; executar a ferramenta localmente
não torna o conteúdo devolvido ao chat offline. REA diferencia worker sem rede
do cliente que acessa modelo loopback. MiroFish requer endpoint já ativo.
Lean atual verifica apenas o primeiro teorema reportado; não há certificado
integral do livro nesta revisão. [Contratos dos plugins](PLUGINS_LOCAIS_CORE.md).

**NotebookLM.** Fachada `gemini_notebook_action` → política por efeito → schema
instalado → conector comunitário → serviço Google. Descobrir 53 ferramentas
não autoriza as quatro novas sem política. Leituras, mutações, operações
compostas e downloads têm gates diferentes. Login e sessão privados ficam no
cliente upstream. [Guia operacional](GEMINI_NOTEBOOK_CORE.md).

**Rigor acadêmico.** A fachada e o serviço estão presentes novamente. Regras
locais são o padrão; `managed_profiles` depende de perfis válidos e resultados
reais. Os 34 cartões e outras superfícies permanecem removidos. O preflight
não é chamado automaticamente, e a rota `banca_rate` aponta a um método ausente.
O [estado atual](ESTADO_ATUAL_CORE_R916.md) separa esses defeitos das evidências
operacionais; o atlas não os corrige ou promove à prontidão científica.

**Modelos e contexto.** O fluxo 20 orienta comparação por custo/tarefa aceita;
não muda o padrão. O modelo da sessão `openai/gpt-6-luna` aparece na documentação
de API, mas não no catálogo local `opencode.json` observado (que lista GPT-6 Astra
e GPT-5.6 Luna). Gemini Flash e suas cotas também dependem do provider/conta.
O default local permanece `ollama-local/llama3.2`. A inspeção read-only
`ollama show --modelfile llama3.2` não encontrou `PARAMETER num_ctx`, enquanto
Ollama documenta default 2048; portanto a janela 32768 declarada pelo cliente
não prova janela ativa do daemon. SDK R918 detecta num_ctx por `/api/show` e
recusa estimativas excedidas sem truncar; não intercepta o OpenCode interno.
Consulte [modelos e custo](architecture/MODELOS_E_ECONOMIA_DE_TOKENS_R916.md),
[quantização no GitHub](architecture/QUANTIZACAO_LOCAL_GITHUB_R916.md) e
[recibos da revisão](verification-documentation-r916-ollama-quantizacao.json).

**CI.** O perfil local científico é fechado e verificável por recibos. Ele não
cria check GitHub ou substitui a revisão externa. O problema de cobrança da CI
remota é separado de testes locais aprovados.

## Todos os fluxogramas

| Nº | Fonte Mermaid | Leitura |
|---|---|---|
| 01 | [Panorama completo por camadas](architecture/flows/01-panorama.mmd) | Interfaces, primário, execução, governança, conhecimento e fronteiras externas. |
| 02 | [Orquestração primária e execução CLI](architecture/flows/02-orquestracao.mmd) | Primário compartilhado, especificação textual, roteamento, Blackboard, executor e aceite autoritativo. |
| 03 | [Workflow DAG e retomada](architecture/flows/03-workflow-dag.mmd) | Definição normalizada, checkpoint durável, orçamento global e repetição explícita de falhas. |
| 04 | [SDD e histórico RED–GREEN](architecture/flows/04-sdd-tdd.mmd) | Especificação, contratos por critério, execução pytest real e recibos autenticados no escopo local. |
| 05 | [REA e camadas de provedores](architecture/flows/05-rea-provedores.mmd) | Registro informativo das 18 camadas, sondas estruturais e percursos efetivamente implementados: analyze JavaScript, analyze_binary Ghidra e layer com inspeção definida. |
| 06 | [REA local direto e evidência](architecture/flows/06-rea-local.mmd) | Inspeção estática com rede/PID privados, digest antes/depois, recibo por hash e explicação derivada. |
| 07 | [REA com agente local e gate de recibos](architecture/flows/07-rea-agente.mmd) | Setup próprio, configuração efetiva, quatro ferramentas, timeout e validação do resultado do cliente. |
| 08 | [Conhecimento, RAG e grafos de evidência](architecture/flows/08-conhecimento-rag.mmd) | Recuperação de fontes, abstenção, referências e dois modelos de grafo com responsabilidades distintas. |
| 09 | [Rede de memória observável](architecture/flows/09-memoria-observavel.mmd) | Eventos reais, memória persistida, claims, cartões e visualização em terminal/Streamlit. |
| 10 | [Raciocínio restrito e fallbacks](architecture/flows/10-raciocinio.mmd) | AST permitida, tradução SMT integral, cálculo simbólico da entrada e falha sem conclusão inventada. |
| 11 | [Diagnóstico, confiança, federação e evolução](architecture/flows/11-diagnostico-governanca.mmd) | Autodescoberta e corpus retido, categorias canônicas, remediação, políticas e ledger de evolução. |
| 12 | [Ciência, proveniência e publicação](architecture/flows/12-ciencia-publicacao.mmd) | Execução científica e descoberta com gates, revisão interna, composição e entrega editorial humana. |
| 13 | [Validação e entrega](architecture/flows/13-validacao-entrega.mmd) | Suíte/JUnit, contagens físicas, exportação limpa, manifesto, commit e resultado remoto independente. |
| 14 | [Plugins locais, Lean 4 e MiroFish](architecture/flows/14-plugins-locais.mmd) | Pacotes privados reutilizam o mesmo primário; status e execução possuem contratos distintos. |
| 15 | [NotebookLM coordenado e política R915](architecture/flows/15-notebooklm.mmd) | CLI, MCP, catálogo e skill compartilham validação, política de efeitos e recibos pelo MarceloClaro. |
| 16 | [Autenticações de ChatGPT, Gemini e NotebookLM](architecture/flows/16-autenticacoes.mmd) | Três clientes e sessões independentes; resposta observada e login são evidências diferentes. |
| 17 | [Ciclo metacognitivo e memória de outcomes](architecture/flows/17-metacognicao.mmd) | Recuperação de lições antes da tarefa e observação posterior, sem transformar heurística em validação externa. |
| 18 | [Lifecycle permanente de agentes e subagentes](architecture/flows/18-lifecycle.mmd) | Definição validada, contrato, permissões e correlação da tarefa antes da execução efetiva. |
| 19 | [CI local e validação delimitada](architecture/flows/19-ci-local.mmd) | Alternativa local ao bloqueio da CI remota, com seleção fechada e recibos próprios. |
| 20 | [Seleção econômica de modelos e contexto](architecture/flows/20-economia-modelos.mmd) | Política recomendada para comparar custo por tarefa aceita; não é um roteador automático novo. |
| 21 | [Contexto de código e consultas de grafo](architecture/flows/21-contexto-codigo.mmd) | Busca e estrutura local reduzem leituras desnecessárias; ganhos precisam de medição comparável. |
| 22 | [Contexto e erros de Ollama local](architecture/flows/22-ollama-contexto-erros.mmd) | Num_ctx observado, preflight estimado, erro quota/contexto e uso com origem declarada; sem truncamento/retry/fallback automático. |

Cada fonte possui um SVG correspondente. O catálogo conserva âncoras de código
com caminho, símbolo, linha e SHA-256. Os testes exigem correspondência real;
existência de arquivo ou substring de saída não vale como prova funcional.

## Legenda e níveis de evidência

| Elemento/estado | Interpretação |
|---|---|
| Nó do grafo integral | Um módulo de produção classificado, mesmo sem imports internos |
| Seta do grafo integral | Import interno declarado/resolvido estaticamente; não execução |
| Grupo e cor | Pacote/camada; não implica isolamento de processo nem de rede |
| Retângulo de fluxo | Operação/estado curado a partir de código, sujeito aos limites do catálogo |
| Losango | Gate que pode bloquear; os ramos negativos fazem parte do contrato |
| Seta pontilhada/nota | Condição, limite ou relação de evidência; não chamada observada |
| `installation_only` | Arquivo/ferramenta instalado; inferência não demonstrada |
| `awaiting_executor` | Tarefa criada, sem resultado real observado |
| `syntax_verified` | Checagem lexical legada, sem comprovação de compilação Lean |
| `machine_checked` | Enunciado submetido aceito pelo compilador, sob pressupostos explícitos |
| `completed` | Operação satisfez seu contrato; não equivale a correção científica |
| `blocked`/`failed`/`partial` | Preservar causa, artefatos e limites; não normalizar como sucesso |
| Validação externa | Exige fonte/avaliador e escopo explícitos; não foi realizada por R916 |

## Camadas e símbolos

As categorias são de organização do código; não medem cobertura funcional.
Métodos e funções assíncronas entram nos símbolos, conservando nomes qualificados.

| Camada | Módulos | Símbolos AST |
|---|---:|---:|
| `agentes` | 10 | 80 |
| `diagnostico` | 31 | 477 |
| `engenharia_reversa` | 10 | 69 |
| `evolucao` | 10 | 84 |
| `ferramentas` | 66 | 439 |
| `governanca` | 26 | 304 |
| `infraestrutura` | 6 | 5 |
| `integracoes` | 130 | 1516 |
| `interfaces` | 10 | 126 |
| `memoria_e_evidencias` | 44 | 234 |
| `modulos_adicionais` | 122 | 1092 |
| `orquestracao` | 39 | 476 |
| `pesquisa_e_rag` | 124 | 1201 |
| `plugins` | 5 | 15 |
| `protocolos` | 9 | 8 |
| `publicacao` | 3 | 32 |
| `raciocinio` | 16 | 152 |
| `skills` | 46 | 469 |

## Reprodução

Use as dependências já instaladas para reprodução offline. A coleta abaixo
representa o diretório de trabalho no momento da execução, e não recupera
automaticamente os bytes locais históricos a partir do hash. Para preservar
outro estado, faça um snapshot autorizado das fontes antes de alterá-las.

```bash
.venv/bin/python scripts/build_architecture_maps.py --source worktree \
  --ref HEAD --output docs/architecture
.venv/bin/python scripts/build_mermaid_architecture.py \
  --inventory docs/architecture/architecture-inventory.json \
  --output docs/architecture/dependencies.mmd \
  --correspondence docs/architecture/mermaid-correspondence.json
dot -Tsvg docs/architecture/curated-overview.dot \
  -o docs/architecture/curated-overview.svg
```

Renderize cada `flows/*.mmd` no SVG correspondente e o grafo integral com
Mermaid CLI 12.0.0, Chromium e a configuração
`docs/architecture/mermaid-render-config.json` (`strict`, sem rótulos HTML).
O [manual Mermaid](architecture/MERMAID_INTEGRAL.md) detalha o renderer.
Depois execute:

```bash
.venv/bin/python scripts/sync_readme_flowcharts.py --refresh-sources
.venv/bin/python scripts/render_architecture_page.py
.venv/bin/python scripts/reconcile_operational_docs.py --check
.venv/bin/python scripts/build_architecture_maps.py --source worktree \
  --ref 84ef0820a71f52756203854ea83d5a1211d8c254 --output docs/architecture --check
.venv/bin/python scripts/build_mermaid_architecture.py \
  --inventory docs/architecture/architecture-inventory.json \
  --output docs/architecture/dependencies.mmd \
  --correspondence docs/architecture/mermaid-correspondence.json --check
.venv/bin/python scripts/sync_readme_flowcharts.py --check
```

Não editar manualmente blocos gerados no README. Atualize fontes/catalogo e
regenere. O verificador compara bytes e recusa deriva. A página é autocontida,
sem CDN; pode ser servida por HTTP local, com raiz `docs`, como no endereço
`http://127.0.0.1:8771/architecture_map.html` usado pelo operador.

Os [testes e a inspeção visual R916](verification-documentation-r916.json)
têm escopo documental/estrutural. R879, R881, R900 e R911 permanecem históricos,
sem reescrever recibos. Leia o [estado atual](ESTADO_ATUAL_CORE_R916.md) antes
de usar qualquer mapa como orientação de operação científica.
