# Avaliação dirigida de repositórios — R888, lote A

Revisão local de 14 de outubro de 2026. Foram consultados os forks indicados por Marcelo Claro, fixados os commits e lidos arquivos selecionados. Nenhum instalador, servidor, modelo ou script desses repositórios foi executado. A análise utiliza dados públicos baixados do GitHub e inspeções estáticas do REA através do primário `MarceloClaroOrchestrator`; não constitui validação externa ou auditoria integral.

O manifesto [repo-reviews-r888-a.json](repo-reviews-r888-a.json) contém os commits completos, hashes dos arquivos amostrados, licenças declaradas e recibos locais. O conjunto não foi incorporado como dependência do Core.

| Repositório | Commit consultado | Decisão para o Core |
|---|---|---|
| mira-animator | `3e72a6533cf4642e3bfd9128b69e7cf3431fcf7c` | Referência de apresentação; restrição não comercial exige escopo próprio. Não importar automaticamente. |
| RAGnaRock | `45637fea5e97ae4dec6ce1da697abf5575dbe008` | Adaptar contrato compacto de recuperação e proveniência; não adicionar outro daemon de memória. |
| superhuman | `ddd68dc9191022a0c8bbb7c5a417e7ce2e90f2f7` | Corrigir o harness existente antes de ampliar benchmarks; datasets/prompts não fornecem o agente completo. |
| opentwins | `2511ffebb245c47098f6809e8dd632387de7ee2f` | Referência de gêmeos digitais para domínio específico; sobreposição e infraestrutura excessivas para o núcleo. |
| transformers | `3a3b59cb1a7c0238c8d1072e35d3879c5faff48e` | Backend opcional isolado, com modelo local fixado; não substituir o orquestrador. |

## Evidência de execução do REA

As chamadas passaram por `MarceloClaroOrchestrator(auto_load_agents=False).rea_assistant_action(...)`, com operação `inspect`. O primário persistiu observações no MetaBus sem promover confiança.

| Alvo amostrado | Operação observada | Resultado e alcance |
|---|---|---|
| mira-animator, `bin/mira.js` | Parser JavaScript do REA por MCP, 27,415 s | 1 arquivo, 2.394 bytes, 201 nós AST declarados pelo provider; relações/imports estáticos. |
| RAGnaRock, `ragd/src/dashboard.html` | Parser HTML local do assistente, 9,117 s | 90.597 bytes; título, 1 formulário e 1 script declarados. Não analisou nem executou o daemon Rust. |
| opentwins, `docs/babel.config.js` | Parser JavaScript do REA por MCP, 26,807 s | 89 bytes, 16 nós AST; somente configuração documental, sem concluir sobre os serviços externos. |
| transformers, `utils/hub.py` | Solicitação `kind=python` rejeitada | Tipo não suportado; nenhum parser REA executado. A leitura Python descrita abaixo é revisão estática separada. |
| superhuman, `README.md` | Solicitação `kind=markdown` rejeitada | Tipo não suportado; nenhum parser REA executado. Os dados e documentos foram lidos separadamente. |

Os três recibos de sucesso registraram `target_unchanged=true`, namespace de rede contendo apenas `lo`, `external_route_available=false` e `host_probe_connected=false`. Essa observação cobre o worker analítico e seus descendentes, não o download inicial pelo GitHub nem um cliente de inferência em nuvem. As duas rejeições não contam como análises bem-sucedidas.

O provider JavaScript instalado identificou REA 6.4.0, commit `4daea941bfeeb426886f2d048aed7f3cb2dbf97b`. Os recibos estão em `outputs/core-r888/a-rea-{mira-animator,RAGnaRock,opentwins,transformers,superhuman}.json`; seus identificadores e hashes constam do manifesto. Arquivos JavaScript avulsos foram copiados sem alteração para diretório temporário; dependências vizinhas não foram incluídas. Achados estáticos não demonstram execução da aplicação.

## mira-animator

Contribui para apresentações e explicações visuais. O conceito de fontes vinculadas, lidas separadamente dos artefatos produzidos, pode orientar a exportação de evidências e mapas do Core. A criação de slides não resolve o controle metacognitivo nem fornece outro coordenador necessário.

A [licença do commit consultado](https://github.com/MarceloClaro/mira-animator/blob/3e72a6533cf4642e3bfd9128b69e7cf3431fcf7c/LICENSE) e `package.json` declaram PolyForm Noncommercial 1.0.0; o indicador genérico da API GitHub foi `NOASSERTION`. Não se deve reclassificar esse conteúdo como MIT ou Apache. Esta revisão não importou código, templates ou skills e não emite parecer jurídico sobre usos futuros.

Há uma diferença material entre apresentação offline e instalação sem rede: [`lib/runtime/version-notice.js`](https://github.com/MarceloClaro/mira-animator/blob/3e72a6533cf4642e3bfd9128b69e7cf3431fcf7c/lib/runtime/version-notice.js) consulta o registro npm por processo destacado; [`writer.js`](https://github.com/MarceloClaro/mira-animator/blob/3e72a6533cf4642e3bfd9128b69e7cf3431fcf7c/lib/installer/writer.js) instala esse runtime e hook. O servidor de edição `mira-serve.js` escuta loopback, mas permite CORS amplo e gravação de HTML. Templates/recursos descritos incluem CDNs e serviços externos; o modo offline depende de preparação específica. Nenhum desses caminhos foi executado.

Adaptação indicada: contrato próprio para fonte identificada por hash e saída isolada, usando a infraestrutura já presente em `webapp/`, `mci/evidence_graph.py` e `docs/architecture/`. Qualquer animação deve distinguir visualmente dado observado de metáfora. Não portar automaticamente o instalador nem tratar a licença como permissiva para redistribuição irrestrita.

## RAGnaRock

Oferece recuperação léxica e fonética em CPU, com histograma silábico, ponderação TF-IDF e reranqueamento por proximidade. O ganho de relevância para o Core ainda não foi medido; sílabas portuguesas também não substituem um grafo de símbolos de código. A [implementação de referência vetorial](https://github.com/MarceloClaro/RAGnaRock/blob/45637fea5e97ae4dec6ce1da697abf5575dbe008/python_concept/sylkit/vector.py) permite examinar as operações sem modelo neural. O código é MIT, mas o README separa licenças dos dicionários/thesauri de terceiros.

O [MCP de referência](https://github.com/MarceloClaro/RAGnaRock/blob/45637fea5e97ae4dec6ce1da697abf5575dbe008/examples/mcp/mcp_ragnarock_server.py) compacta a busca para hits e pequena quantidade de metadados; o resultado pode preservar coleção, base, corpus, caminho e posição de chunk. Essa é uma contribuição concreta para o piloto de code-intelligence R887: limites de saída com proveniência e indicação explícita de truncagem, sem despejar diagnósticos volumosos no contexto do agente.

A instalação original não atende automaticamente ao modo exclusivamente local do Core. [`ragd/src/main.rs`](https://github.com/MarceloClaro/RAGnaRock/blob/45637fea5e97ae4dec6ce1da697abf5575dbe008/ragd/src/main.rs#L651) vincula painel e API a `0.0.0.0`; o dispatch principal não usa a sessão de autenticação do painel. Há ingestão/leitura de caminhos e exclusão de bases. A expansão opcional envia a consulta a provedores externos via `wget` nas linhas 907–950. O MCP aceita endereço `RAGD_URL` configurável e expõe ingestão. Portanto, consultas compactas e um endereço aparentemente local não garantem isolamento.

Adaptação proposta, sem executar o daemon: manter o primário e MetaBus como autoridades; limitar consultas a corpus previamente materializado; separar indexação autorizada de leitura; deduplicar por identidade de origem; transportar `repository`, `commit`, `relative_path`, `source_sha256`, posição e truncagem junto ao snippet. Rejeitar resultados cuja origem não seja rastreável. Avaliar contra o baseline existente por acerto de localização, bytes e chamadas, sem converter similaridade em confiança ou estimativa de bytes em tokens efetivamente economizados.

## superhuman

O fork reúne benchmarks, documentos matemáticos e prompts/respostas; a [árvore consultada](https://github.com/MarceloClaro/superhuman/tree/ddd68dc9191022a0c8bbb7c5a417e7ce2e90f2f7) não oferece um runtime completo do Aletheia para instalar no Core. O nome do repositório não é uma classificação de capacidade do ecossistema. O README diferencia software Apache 2.0 de outros materiais CC-BY 4.0.

O [README de IMO Bench](https://github.com/MarceloClaro/superhuman/blob/ddd68dc9191022a0c8bbb7c5a417e7ce2e90f2f7/imobench/README.md) identifica versões corrigidas `answerbench_v2.csv` e `proofbench_v2.csv`. Usar versões anteriores sem registrar a diferença comprometeria comparabilidade. Uma avaliação futura deve fixar arquivo/hash, retirar o gabarito da entrada do solver e reservar o conjunto de avaliação, registrando exposição prévia e limites de contaminação.

Já há sobreposição direta em `integrations/deepmind/imobench_harness.py`, `aletheia_scaffold.py` e `benchmarks/scientific_reasoning/`. A inspeção encontrou uma falha local mais urgente que nova instalação: o harness padrão injeta `short_answer` na resposta gerada quando não recebe solver; uma nota textual heurística de 7 também marca `formal_verified=true`.

A reprodução executada em `outputs/core-r888/a-core-imobench-reproducer.json`, anterior à correção, observou 1/1 acerto e `formal_verified=true` sem solver; o texto adversarial contendo resposta **13**, palavra “lema” e sinal de igualdade recebeu nota 7 para gabarito **3**. Esse resultado prova a falha do harness nessa entrada, não competência matemática. O hash do arquivo anterior está no recibo. Não foi executado nenhum código do fork.

Adaptação imediata indicada: corrigir o harness existente sob especificação e testes R888; ausência de solver deve produzir `not_executed` e acurácia ausente, a entrada do solver deve excluir gabarito/solução, comparação de resposta deve usar igualdade normalizada explícita e a nota textual não pode atestar prova formal. Eventual validação formal precisa de evidência de verificador associada à afirmação e à execução. O restante do pacote é referência de avaliação, não um segundo orquestrador.

## opentwins

É uma plataforma de gêmeos digitais com serviços de mensageria, armazenamento, monitoramento e simulação. O [README do fork fixado](https://github.com/MarceloClaro/opentwins/blob/2511ffebb245c47098f6809e8dd632387de7ee2f/README.md) declara desenvolvimento em curso e desaconselha uso em produção naquele estado. Os manifestos e documentos referenciam Kafka, Eclipse Ditto/Hono, MongoDB, RabbitMQ, InfluxDB e Grafana. Instalar essa plataforma para melhorar o raciocínio do Core criaria um conjunto de serviços que o objetivo atual não exige.

O arquivo [`.gitmodules`](https://github.com/MarceloClaro/opentwins/blob/2511ffebb245c47098f6809e8dd632387de7ee2f/.gitmodules) referencia cinco repositórios componentes; a árvore consultada não trouxe entradas gitlink nem o código desses componentes. Seus contratos e licenças não foram auditados por transitividade. Os manifestos amostrados também expõem portas de serviços e dependem de imagens externas. Não foi implantado Kubernetes ou iniciado container.

A contribuição adaptável é o padrão abstrato de identidade estável, composição e separação entre estado desejado e observado. Aplicá-lo ao status do Core significa preservar as distinções já existentes entre instalação, prontidão, autenticação, execução e verificação, sem atribuir uma inferência a um componente apenas instalado. Pontos de integração: `mci/blackboard.py`, `mci/metabus.py` e `integrations/harness_health.py`; para um futuro domínio industrial, um adapter específico poderia consumir eventos autorizados.

## transformers

O fork é a biblioteca Hugging Face Transformers, não o pacote local `transformer/` do Core. O [setup fixado](https://github.com/MarceloClaro/transformers/blob/3a3b59cb1a7c0238c8d1072e35d3879c5faff48e/setup.py) declara `5.3.0.dev0`, Python 3.10+ e dependências como Hugging Face Hub, tokenizers e safetensors, com PyTorch 2.4+ no extra correspondente. Esta análise não instalou dependências, baixou pesos nem verificou wheels para o Python 3.14 do ambiente.

[`utils/hub.py`](https://github.com/MarceloClaro/transformers/blob/3a3b59cb1a7c0238c8d1072e35d3879c5faff48e/src/transformers/utils/hub.py) usa `local_files_only=False` como padrão de carregamento e prevê download/cache. O user-agent considera `HF_HUB_DISABLE_TELEMETRY`. [`dynamic_module_utils.py`](https://github.com/MarceloClaro/transformers/blob/3a3b59cb1a7c0238c8d1072e35d3879c5faff48e/src/transformers/dynamic_module_utils.py) explica que código de módulos customizados pode ser executado quando `trust_remote_code` autoriza. Isso exige um contrato explícito, não apenas chamar o backend de local.

Um adapter opcional deveria aceitar apenas modelo previamente presente em diretório autorizado, com hashes e revisão fixados, `local_files_only=True`, `trust_remote_code=False`, modo offline do Hub e telemetria desativada; um bloqueio de rede precisa ser observado no processo real para sustentar a alegação de isolamento. Cada checkpoint conserva a própria licença. O Core já tem roteador de modelos, LiteRT-LM e harnesses; instalar a biblioteca não demonstraria ganho sobre eles. Prioridade menor que corrigir o harness e concluir a recuperação de código R887.

## Ordem de implementação e limites

1. Corrigir a avaliação IMO do próprio Core com teste adversarial e separação de gabarito, sem incorporar código de terceiros.
2. Usar o contrato compacto e citado de recuperação no único provider de code-intelligence R887, mantendo consultas e memória no caminho do primário.
3. Conservar MIRA, OpenTwins e Transformers como referências ou adapters opcionais de escopo específico; não iniciar runtimes adicionais por mera disponibilidade de um repositório.

As recomendações são inferências de engenharia baseadas na amostra. Não foram medidos ganho de tokens, qualidade semântica do retrieval, precisão matemática do modelo, segurança integral de dependências ou funcionamento dos sistemas externos. As inspeções REA são estáticas, locais e limitadas aos alvos identificados. O manifesto e os recibos permitem reexaminar cada afirmação observada.

## Adaptação realizada no mesmo ciclo

A recomendação do lote foi aplicada ao caminho existente, sob a especificação
R888. O harness agora transmite `IMOSolverInput` imutável e sem `short_answer`,
aceita resposta curta explícita separada de `reasoning`, recusa acerto por
substring e devolve `not_executed` quando nenhum solver foi executado. A
normalização não apaga distinções entre `13` e `3`, conjuntos e tuplas, caixa
ou expoentes; não resolve equivalência algébrica. A nota textual permanece
não calibrada e não emite prova formal.

`RealIMOSolver.submit` calcula a resposta pelas funções já existentes, sem ler
um gabarito do problema; fórmulas candidatas conservam essa marca. Na execução
local após a correção, as nove respostas curtas da amostra interna coincidiram
com os valores esperados e **nenhuma** foi marcada como formalmente verificada.
Essa amostra conhecida/adaptada não demonstra generalização, desempenho no
IMO Bench completo nem calibração.

O consumidor Deep Think também foi ajustado: nota textual não é gate; o
candidato deve apontar para o mesmo enunciado e a identidade original é
reexecutada no verificador restrito com SymPy disponível. Candidato falso,
alegação trocada, linguagem natural e fallback sem backend não recebem sucesso.
Um recibo vincula entrada, hash, backend e resultado local. A confiança
probabilística permanece `None` e `calibrated=false`, inclusive quando uma
identidade é confirmada nesse fragmento. As tentativas são sequenciais sobre
o mesmo prover e não demonstram diversidade independente de raciocínio.

Os métodos correspondentes do primário registram observações no MetaBus sem
EMA de confiança derivada do próprio resultado. Testes negativos reproduziram
os contratos anteriores antes da correção; o fechamento dirigido teve **71
testes aprovados**, incluindo consumidores R442/R443/R499/R503, invariantes
formais e novos testes R888. Ruff aprovou os quatro arquivos de implementação/
testes novos verificados. Recibos: `outputs/core-r888/a-release-final.xml`,
`a-ruff.txt` e `a-core-after-fix.json`; hashes atuais e limites constam do manifesto.
Esta verificação dirigida não representa execução aprovada de toda a suíte do Core.
