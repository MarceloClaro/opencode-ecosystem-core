# Avaliação de code-intelligence local via MCP — preparação R887

**Data da consulta: 14 de outubro de 2026. Escopo: avaliação estática; integração ainda não realizada.**

**Recomendação: testar somente `context-link-mcp/context-link` em um piloto R887 separado**, com revisão fixada, corpus materializado e filtrado, índice fora do checkout, consultas limitadas por whitelist e controle de rede pelo ambiente. O binário Linux publicado evita acoplar outro conjunto de extensões ao Python 3.14 do Core. CodeSight permanece alternativa caso os contratos de confinamento e abrangência necessários não sejam atendidos pelo piloto; MCP Context Graph permanece referência de uma implementação pequena e de benchmark.

Esta recomendação complementa [CURADORIA_CODIFICACAO_EFICIENTE.md](CURADORIA_CODIFICACAO_EFICIENTE.md) sem modificá-lo. A fase R886 de metacognição continua distinta: o provedor de contexto de código não recebe memória canônica, confiança ou autoridade de coordenação. Este documento não cria ciclo, spec, configuração MCP ou instalação.

## Método e fotografia das fontes

Foram lidos metadados, HEADs, licenças, manifests, interfaces e implementação dos caminhos críticos por GitHub/API. A avaliação de CodeSight incluiu revisão estática paralela. Nenhum candidato foi instalado, clonado ou executado; nenhum benchmark dos projetos foi reproduzido.

| Candidato | Branch e HEAD fixado | Data do commit, UTC | Licença lida | Interface e requisitos declarados |
| --- | --- | --- | --- | --- |
| [context-link](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/README.md) | `master` — `e5af49c11c5b2228c6b611dd3594d93014997306` | 2026-04-26T16:55:13Z | [Apache-2.0](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/LICENSE) | CLI `index`/`serve`, MCP stdio; Go **1.24.2** no manifest e CGo/GCC no build; binário Linux publicado |
| [CodeSight MCP](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/README.md) | `main` — `816d523a1126b210afffa8a422760bbfce42f5f6` | 2026-08-30T06:41:29Z | [MIT](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/LICENSE) | Python >=3.10; MCP stdio e CLI; parsers nativos, cliente Anthropic e semântica opcional |
| [MCP Context Graph](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/README.md) | `main` — `d88e7367f2e8600ac64c8413bf15aca190da57ba` | 2026-07-08T14:57:49Z | [MIT](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/LICENSE) | Python >=3.12; MCP stdio; CLI `serve`/`index`/`benchmark`; NetworkX, Tree-sitter e tiktoken |

Os SHAs são fotografias da consulta, não garantias de manutenção futura. A configuração local do Core lida nesta fase contém **16 entradas MCP**; isso é contagem de configuração, não comprovação de que as 16 respondem. O inventário AST e os mapas já existentes continuam úteis, mas o inventário publicado fixa o snapshot `6380cfaff4aac0dd940d42011826bb21126e5635`; não deve servir como manifesto atual sem atualização e comparação dos arquivos.

### Compatibilidade com esta máquina

Sonda somente de executáveis já presentes no WSL: Linux x86_64, kernel `6.18.33.2-microsoft-standard-WSL2`, Node **22.23.1**, Python de sistema **3.14.4** e GCC **15.2.0**. `go` não foi encontrado no PATH dessa sonda. Nenhum código dos candidatos participou dela.

- **context-link:** independe de Node/Python depois de disponibilizado como binário. O [`go.mod`](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/go.mod#L1-L13) exige Go 1.24.2, embora a tabela do README diga 1.22+. A [CI](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/.github/workflows/ci.yml#L5-L16) usa Go 1.24/GCC. A release [v1.1.0](https://github.com/context-link-mcp/context-link/releases/tag/v1.1.0) aponta para o mesmo commit examinado e publica `context-link_1.1.0_linux_amd64.tar.gz` (20.852.723 bytes). A API informa digest `sha256:cb61fe2618d1aa27724520c5c9205440d57802fc4e1bee9a0690c2c652927b1a`; o arquivo não foi baixado nem seu conteúdo ou suas dependências dinâmicas verificados. A existência do asset não prova execução no WSL.
- **CodeSight:** a faixa Python >=3.10 inclui 3.14 formalmente, mas a [CI examinada](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/.github/workflows/ci.yml#L55-L85) configura Python 3.12/Ubuntu 24.04. O projeto [exige POSIX](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/core/platform_check.py#L11-L23); WSL Linux é candidato plausível, Windows nativo é recusado. Parsers e dependências nativas precisam de sonda isolada. O motor não exige Node; o wrapper TypeScript citado no README é outro projeto, com Bun, fora desta avaliação.
- **MCP Context Graph:** o [manifest](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/pyproject.toml#L1-L34) permite Python >=3.12, mas os classificadores citam 3.12/3.13; [`.python-version`](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/.python-version) fixa 3.12. Não há demonstração específica de Python 3.14 nas configurações lidas. O lock fixa Tree-sitter 0.25.2, parsers e tiktoken 0.12.0, sujeitos à disponibilidade de wheels compatíveis. Nenhum dos três candidatos necessita de Node 22 como motor principal.

## 1. Context-link: por que é o único piloto recomendado

A implementação publica MCP stdio e separa indexação de serviço. Oferece busca semântica, recuperação por símbolo, esqueleto de arquivo, usos, árvore de chamadas, impacto, busca em blocos de símbolos e outras ferramentas. A lista exposta é configurável por `--tools`; vazia significa **todas habilitadas**. [Entrada e flags](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/cmd/context-link/main.go#L64-L118), [registro e filtragem](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/server/server.go#L66-L126).

O embedding padrão é **Model2Vec embutido**: os pesos, tokenizer e configuração usam `go:embed`. ONNX é uma alternativa configurada por caminhos locais. A criação real do embedder usa Model2Vec quando não há configuração ONNX; o comentário antigo de configuração “deixar vazio desativa semântica” não descreve esse comportamento do entrypoint. [Pesos embutidos](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/vectorstore/model2vec_data.go#L1-L12), [seleção no serviço](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/cmd/context-link/main.go#L342-L355).

### Escopo de leitura e ruído do Core

O walker ignora `vendor`, `node_modules`, `.git`, builds e alguns caches; limita arquivos a 1 MiB. A implementação de `.gitignore` é **simplificada**, lê o arquivo da raiz e não implementa negações `!`. Não há campo de configuração próprio para todas as classes históricas/templates do Core. Não basta apontá-lo para todo o checkout. [Exclusões e tamanho](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/indexer/walker.go#L20-L34), [descoberta](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/indexer/walker.go#L82-L135), [limites do ignore](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/indexer/walker.go#L215-L263).

Para o piloto, o Core deve construir uma **visão materializada** a partir de um manifesto atual de arquivos autorizados, mantendo caminhos relativos e hashes. Excluir dependências vendorizadas, snapshots históricos, templates, outputs, caches e artefatos de domínio; testes podem formar uma partição explícita para perguntas sobre contratos. Usar cópias, sem links simbólicos ou hardlinks para o checkout. Isso é um requisito futuro do adaptador; não foi implementado aqui.

A leitura dos caminhos críticos não mostrou uma barreira geral por `realpath`/`O_NOFOLLOW` no walker. Uma entrada com extensão de código pode chegar ao hash/leitura por caminho; logo a política de corpus e o confinamento do processo continuam necessários. O índice também guarda código: tem conteúdo sensível e deve ser tratado como dado local privado.

### Leitura do código não significa zero escrita

O SQLite é criado/aberto, migra e recebe permissões 0600. A indexação e os sidecars pertencem ao diretório privado do provedor, fora do checkout. Não há um modo geral de “não escrever nada” no serviço examinado. [Abertura e permissões](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/store/db.go#L20-L44), [configuração do DB](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/config/config.go#L37-L49).

O grupo `memory` publica armazenamento e remoção de notas; habilitar até o nome `get_symbol_memories` seleciona o **grupo inteiro**, não só a leitura. O prompt `explore_codebase` também instrui salvar memória e contém alegação própria de redução de tokens. Esses comportamentos não devem ser adotados pelo Core: memória continua no MetaBus, e instruções de uma ferramenta são dados subordinados à política local. [Grupo e prompt](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/server/server.go#L110-L165).

Whitelist inicial proposta para o futuro serviço:

`ping,semantic_search_symbols,get_code_by_symbol,get_file_skeleton,get_symbol_usages,get_call_tree,get_blast_radius`

Deixar fora `memory`, `reindex_project`, `get_modified_symbols` e operações adicionais até revisão específica. `--watch` permanece desligado. O wrapper controlado pelo Core faz a indexação quando o manifesto muda, verifica hashes e promove a nova geração do índice; o agente recebe apenas consultas. `get_modified_symbols` usa subprocessos Git e parâmetro de referência, uma superfície desnecessária para esta primeira etapa. [Git invocado](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/git.go#L38-L116), [watch opt-in](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/cmd/context-link/main.go#L381-L388).

### Limitações semânticas

O próprio README explica que blocos sem símbolo — imports, configurações, alguns decoradores e código de topo — podem não aparecer em `search_code_patterns`. Um resultado vazio exige fallback explícito para busca e leitura de trechos; não permite concluir ausência do comportamento. Grafo estático não é execução nem prova de dependência dinâmica. [Limitações documentadas](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/README.md#L842-L871).

## 2. CodeSight: alternativa mais ampla, com mais controles e superfícies

O snapshot é **0.6.0**, possui 34 operações MCP/CLI e oferece contexto de símbolo, callers/callees, impacto, hierarquia, Mermaid e análises estáticas. Seu confinamento de indexação local é mais explícito: exige `CODESIGHT_ALLOWED_ROOTS` no MCP, resolve caminhos e usa controles de links/leitura; recebe `extra_ignore_patterns`. Há limites de 5.000 arquivos, 500 KiB por arquivo, profundidade dez e vinte padrões extras. Esses limites podem truncar o corpus e os avisos devem acompanhar o resultado. [Manifest](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/pyproject.toml#L1-L56), [operações](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/contract/operations.json), [allowlist](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/tools/index_folder.py#L173-L205), [descoberta](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/discovery.py#L167-L359), [limites](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/core/limits.py#L6-L25).

Três condições impedem tratá-lo como instalação local segura por padrão:

1. `index_folder` usa `use_ai_summaries=True`. Se houver chave Anthropic, o sumarizador pode enviar assinaturas à API. A alternativa local requer `False`; semântica opcional pode baixar modelos na primeira carga e aceita `CODESIGHT_NO_SEMANTIC=1`. [Padrão](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/tools/index_folder.py#L140-L168), [API](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/summarizer/batch_summarize.py#L341-L415), [conteúdo enviado](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/summarizer/batch_summarize.py#L469-L480), [embeddings](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/embeddings/providers.py#L1-L107).
2. `CODESIGHT_READ_ONLY` no IndexStore não bloqueia universalmente `save_index`; há gravação do rate limiter e logs opcionais. O CLI abre exceção à política default-deny: `index` autoriza o próprio alvo se não houver allowlist. `CODESIGHT_AUTOINDEX` é opt-in, mas, ativado, permite reconstrução por consultas. [Read-only limitado](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/storage/index_store.py#L284-L315), [rate limiter](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/core/rate_limiting.py#L87-L104), [atalho CLI](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/server.py#L666-L678), [autoindex](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/tools/_common.py#L47-L65).
3. O índice conserva conteúdo completo em disco; “zero-DB” não significa ausência de persistência ou de dados sensíveis. O diretório padrão é `~/.code-index`, configurável por `CODE_INDEX_PATH`. A invalidação tenta remover índices e conteúdo, mas locks, logs e caches de modelos podem permanecer. [Persistência](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/storage/index_store.py#L461-L570), [invalidação](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/tools/invalidate_cache.py#L12-L66).

O grafo também tem limite de interpretação: a resolução usada é heurística por nome, e duas funções do módulo de resolução sensível a importações ainda lançam `NotImplementedError`. Assim, riqueza de ferramentas não comprova resolução de aliases, escopos ou coordenação real. [Heurística](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/parser/graph.py#L215-L246), [funções pendentes](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/parser/resolution.py#L10-L17).

A revisão do logger de uso encontrou registro local, em memória por padrão e JSONL opcional; isso não constitui auditoria completa de tráfego de todas as dependências. [Logger](https://github.com/cmillstead/codesight-mcp/blob/816d523a1126b210afffa8a422760bbfce42f5f6/src/codesight_mcp/core/usage_logging.py#L21-L115). Por amplitude e dependências, é alternativa posterior, não um segundo servidor instalado junto do piloto.

## 3. MCP Context Graph: menor superfície, mas sem vantagem comprovada no Core

O snapshot **0.2.0**, classificado Alpha no manifest, mantém grafo e mapas de origem em memória. Suporta Python, TypeScript e JavaScript e publica seis ferramentas: `index_project`, `find_symbol`, `find_callers`, `get_context`, `expand_source` e `debug_dump_graph`. O servidor usa stdio; o CLI possui subcomandos de índice e benchmark. [Ferramentas](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/mcp/server.py#L71-L137), [CLI](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/cli.py#L104-L174).

`index_project` recusa trocar a raiz do servidor. O ingestor respeita `.gitignore` raiz via pathspec e exclui ambientes/caches, mas não inclui `vendor` ou todas as classes históricas na lista fixa. O walker e `read_text` não demonstram barreira geral a links de arquivos; “raiz fixada” não basta como isolamento de leitura. O graph dump pode retornar contexto excessivo se exposto sem orçamento. [Raiz vinculada](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/mcp/tools.py#L227-L240), [exclusões](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/ingest/ingestor.py#L70-L104), [ignore e caminhada](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/ingest/ingestor.py#L338-L445), [leitura](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/ingest/ingestor.py#L463-L488).

É uma referência útil para oráculos pequenos e métricas, mas não demonstra cobertura completa do ecossistema, compatibilidade Python 3.14 ou ausência literal de rede. Não instalar em paralelo a context-link.

## “Offline”, local e “sem rede” são contratos diferentes

- **Local:** processo e índice residem na máquina. O cliente LLM ainda pode ser remoto.
- **Offline após preparação:** binário, pacotes e dados já estão em cache; nenhuma API de inferência é exigida por essa operação. A preparação pode ter usado rede.
- **Sem rede durante a execução:** exige bloqueio de egress pelo ambiente e teste de tentativa de conexão, além de recibo do processo. Stdio não é um bloqueador de rede.

Nos 58 arquivos Go próprios de produção de context-link lidos, uma busca dirigida não encontrou imports `net/http`/`net`, clientes HTTP explícitos ou marcadores de telemetria. O padrão de embedding está embutido. Isso sustenta a possibilidade de operação local; não audita bibliotecas transitivas nem prova comportamento do binário publicado. A recomendação mantém bloqueio de rede externo ao provedor.

O benchmark de MCP Context Graph tenta `tiktoken.get_encoding("o200k_base")` e, em falha, muda para heurística chars/4. No tiktoken **0.12.0** fixado em seu lock, o carregador pode buscar a tabela de codificação por HTTPS se ela não estiver em cache. Portanto, “benchmark offline” não assegura “não tentou acessar rede”. Pré-disponibilizar e verificar o cache, bloquear rede e registrar se o resultado usou tokenizer ou heurística. [Chamada/fallback](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/benchmark.py#L60-L85), [codificação com URL](https://github.com/openai/tiktoken/blob/97e49cbadd500b5cc9dbb51a486f0b42e6701bee/tiktoken_ext/openai_public.py#L95-L104), [cache e download](https://github.com/openai/tiktoken/blob/97e49cbadd500b5cc9dbb51a486f0b42e6701bee/tiktoken/load.py#L8-L81).

## Instalação futura reversível e sem nova ilha

Somente após concluir R886 e abrir a spec própria R887:

1. Fixar SHA, release e digest; preservar licença/procedência. Usar diretório privado exclusivo do provedor, sem instalar pacotes no ambiente Python do Core nem alterar o PATH global.
2. Criar corpus de cópias filtradas, sem links, e manifesto de caminhos/hashes. O mapa de origem deve apontar cada resultado ao arquivo real e ao snapshot; corpo de código não vira evidência de execução.
3. Indexar em diretório externo dedicado por snapshot. Guardar stdout/stderr, contagens, exclusões e falhas. Validar referências conhecidas e ausência de arquivos proibidos antes de publicar a geração.
4. Iniciar só o processo MCP autorizado, com root de leitura restrito, cache gravável separado, rede bloqueada e whitelist definida acima. Consultas ficam subordinadas ao orquestrador; nenhum armazenamento de memória do provedor recebe autoridade do MetaBus.
5. Registrar configuração pelo gerador do Core, em vez de edição manual que será perdida na regeneração. Expor disponibilidade separada de instalação e de chamada concluída.
6. Para reverter, remover a entrada gerada, parar o processo identificado e retirar somente o diretório privado desse provedor após verificar seu caminho absoluto. Manter recibos de avaliação. Não apagar o checkout ou caches compartilhados.

São critérios de aceitação propostos. Nenhuma dessas etapas foi executada por este levantamento.

## Medir eficiência sem fabricar ganho

O contador de context-link calcula tokens por **bytes/4**, acumula apenas economias positivas e projeta custo com preço fixo. Seus valores `tokens_saved_est` e custos não são medição de consumo ou fatura do Core. [Contador](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/tokens.go#L8-L15), [cálculo e clamp](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/tokens.go#L41-L76).

O benchmark de MCP Context Graph compara corpus e workflows selecionados, conta respostas serializadas e escolhe símbolos mais chamados. É útil para medir tamanho de contexto, mas não executa o ciclo completo de um agente nem contabiliza toda a negociação/schema MCP. [Seleção e baseline](https://github.com/padobrik/mcp-context-graph/blob/d88e7367f2e8600ac64c8413bf15aca190da57ba/src/mcp_context_graph/benchmark.py#L252-L335).

A medição própria do Core deve:

- Congelar commit, corpus, modelo, configurações, permissões, task-set e oráculos. Incluir localização de símbolo, callers, impacto, teste associado, configuração fora de símbolo, caso negativo e ambiguidade.
- Comparar **A: ferramentas atuais, incluindo rg e leitura de trechos**, com **B: as mesmas ferramentas mais um único MCP**. Evitar baseline artificial que obrigue ler arquivos completos.
- Registrar chamadas de ferramentas, retries, erros, duração de indexação/consulta, bytes e tokens de todos os contextos relevantes, incluindo schemas MCP, respostas, fallback e expansões de código. Separar primeira carga de cache aquecido.
- Usar consumo reportado pelo provedor quando disponível, mantendo input/output/cache distintos. Se houver somente tokenizer local, identificá-lo e rotular o número como estimativa de serialização; não afirmar que é a cobrança do executor.
- Exigir os mesmos resultados corretos por oráculo e verificar path traversal, symlinks, exclusões, limite de resposta, índices obsoletos e falha do provedor. Menos tokens com resposta errada não passa.
- Publicar por tarefa diferenças e resultados absolutos, inclusive regressões e economias negativas; incluir custo de preparação amortizado e não extrapolar uma amostra para todo o Core.

**Resultado desta avaliação:** há justificativa técnica para um piloto único de context-link, condicionado aos controles e à execução dos testes acima. Não há ganho de tokens, compatibilidade operacional, ausência de rede ou completude já demonstrados no Core.

## Apêndice de implementação futura: flags e argumentos consultados

Exemplos de invocação **não executados**, derivados da CLI desse SHA. `BIN`, `CORPUS`, `DB` e `CONFIG` representam caminhos absolutos privados preparados pelo futuro adaptador. A configuração explícita deve ser controlada pelo Core, sem ONNX externo, e o ambiente do processo deve ser saneado; não carregar configuração do checkout por acidente.

```bash
"$BIN" index --project-root "$CORPUS" --db-path "$DB" --config "$CONFIG" --workers 4
"$BIN" serve --project-root "$CORPUS" --db-path "$DB" --config "$CONFIG" --tools ping,semantic_search_symbols,get_code_by_symbol,get_file_skeleton,get_symbol_usages,get_call_tree,get_blast_radius
```

O primeiro comando grava o índice. O segundo serve stdio e também abre/migra o DB; não equivale a modo global sem escrita. Não passar `--watch`, não adicionar `--repo-name` divergente da base do `project_root`, não expor ferramentas de mutação. A indexação incremental é padrão; `--force` existe, mas deve ser uma decisão do wrapper ao criar/reconstruir geração, não argumento arbitrário recebido do agente. [Flags reais](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/cmd/context-link/main.go#L95-L118), [namespace na indexação](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/cmd/context-link/main.go#L140-L155), [namespace no serviço](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/server/server.go#L69-L79).

### Propriedades de entrada declaradas das sete consultas

Esta tabela deriva de `mcp.NewTool`/`mcp.WithString`/`mcp.WithNumber`; não é captura de `tools/list` em processo executado. Os tipos são os do schema publicado no código. Defaults e limites abaixo, quando existentes, pertencem ao handler/descrição; não se presume que sejam constraints JSON Schema.

| Ferramenta | Obrigatórios | Opcionais declarados | Tratamento observado no código |
| --- | --- | --- | --- |
| `ping` | Nenhum | Nenhum | Retorna status, versão, uptime e runtime |
| `semantic_search_symbols` | `query: string` | `top_k: number`, `kind: string`, `file_path_prefix: string`, `min_similarity: number` | top_k default 10; <=0 ou >50 volta a 10. Similaridade default 0,3; fora de [0,1] volta a 0,3 |
| `get_code_by_symbol` | `symbol_name: string` | `depth: number` | depth default 1 e limitado a 0..3 |
| `get_file_skeleton` | `file_path: string` | Nenhum | Caminho relativo; consulta símbolos do índice |
| `get_symbol_usages` | `symbol_name: string` | Nenhum | Nome não vazio; resolve símbolo e dependências reversas |
| `get_call_tree` | `symbol_name: string` | `direction: string`, `depth: number` | direction default callees; só callees/callers. depth default 1 e limitado a 0..3 |
| `get_blast_radius` | `symbol_name: string` | `depth: number` | depth default 2 e limitado a 1..3 |

Fontes: [ping](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/ping.go#L14-L24), [busca semântica](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/semantic_search.go#L46-L74), [símbolo](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/get_code.go#L14-L40), [esqueleto](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/skeleton.go#L18-L39), [usos](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/usages.go#L16-L29), [árvore](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/calltree.go#L16-L36), [impacto](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/blastradius.go#L16-L33).

Os handlers de símbolo/esqueleto também aceitam arrays de strings (até 50), mas o registro declara **string**, com comentário de ausência de `oneOf`. Para o primeiro adaptador, usar só strings e testar o schema real recebido em `tools/list`; não ampliar a superfície por assumir que descrição de batch modifica o schema. O wrapper deve validar propriedades permitidas, tipos, finitude dos números, caminhos e tamanho de resposta por conta própria.

Recuperação por símbolo consulta também notas já armazenadas na base, mesmo quando o grupo de memória não foi exposto. Criar um DB dedicado novo, não importar notas de outra base e preservar MetaBus como autoridade. [Memórias na resposta](https://github.com/context-link-mcp/context-link/blob/e5af49c11c5b2228c6b611dd3594d93014997306/internal/tools/get_code.go#L113-L162).

### Asset identificado, sem download

- Release: [v1.1.0](https://github.com/context-link-mcp/context-link/releases/tag/v1.1.0).
- Fonte: commit `e5af49c11c5b2228c6b611dd3594d93014997306`, também alvo direto do tag.
- Asset Linux x86_64: [context-link_1.1.0_linux_amd64.tar.gz](https://github.com/context-link-mcp/context-link/releases/download/v1.1.0/context-link_1.1.0_linux_amd64.tar.gz).
- Digest publicado pela API: `sha256:cb61fe2618d1aa27724520c5c9205440d57802fc4e1bee9a0690c2c652927b1a`.
- Tamanho publicado: 20.852.723 bytes.
- [checksums.txt](https://github.com/context-link-mcp/context-link/releases/download/v1.1.0/checksums.txt) também consta na release; seu conteúdo não foi baixado nesta avaliação.

O piloto ainda precisa comprovar digest do arquivo obtido, extração confinada, dependências do executável, handshake MCP, equivalência de respostas aos oráculos, ausência de alterações nas fontes e bloqueio de rede. O hash publicado não foi convertido em afirmação de verificação local.
