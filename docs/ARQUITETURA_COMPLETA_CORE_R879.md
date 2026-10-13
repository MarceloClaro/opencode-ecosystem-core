# Arquitetura completa do OpenCode Ecosystem Core — R879

Este documento acompanha o mapa navegável e os fluxogramas operacionais do Core. A referência de implementação é o commit `6380cfa`: o código rastreado nessa revisão, a configuração compilada e as fontes indicadas em cada fluxo. A documentação R879 amplia a representação da arquitetura; não constitui uma nova execução de todos os componentes nem certificação de completude funcional.

As alterações RX R874–R878 existentes em paralelo no diretório de trabalho não pertencem a esta fotografia. Os mapas históricos R433–R438 são conservados como documentos de sua época. Quando houver divergência, consulte o inventário R879, a fonte de código vinculada e o histórico Git.

## Como consultar o mapa

Abra [architecture_map.html](architecture_map.html) em um navegador. O arquivo foi preparado para consulta local; a versão entregue não depende de uma CDN para recuperar o inventário. A visão geral serve para localizar as camadas. As visões por fluxo explicam as decisões, os estados de falha e as fronteiras entre os componentes.

Os fluxogramas editáveis estão em [architecture/flows/](architecture/flows/) e seu catálogo está em [flows.json](architecture/flows.json). Cada entrada do catálogo contém título, descrição, arquivo Mermaid, fontes, símbolos, linhas e limitações. As âncoras foram conferidas contra o código da revisão de referência. Linhas podem mudar nas revisões posteriores; o símbolo e o histórico Git continuam sendo a referência de resolução.

| Visão | Finalidade |
|---|---|
| [01 — Panorama](architecture/flows/01-panorama.mmd) | Localizar interfaces, primário, execução, governança, dados e pesquisa. |
| [02 — Orquestração](architecture/flows/02-orquestracao.mmd) | Seguir a tarefa da especificação textual ao executor e ao aceite. |
| [03 — Workflow DAG](architecture/flows/03-workflow-dag.mmd) | Entender dependências, checkpoints, orçamento e retomada. |
| [04 — SDD/TDD](architecture/flows/04-sdd-tdd.mmd) | Examinar os contratos, o histórico autenticado e os gates. |
| [05 — Provedores REA](architecture/flows/05-rea-provedores.mmd) | Localizar camadas, engines e superfícies de ferramentas. |
| [06 — REA local direto](architecture/flows/06-rea-local.mmd) | Conferir o isolamento do worker, os digests e os recibos. |
| [07 — REA com agente](architecture/flows/07-rea-agente.mmd) | Separar configuração do cliente, chamada MCP e análise aceita. |
| [08 — Conhecimento e RAG](architecture/flows/08-conhecimento-rag.mmd) | Entender recuperação, abstenção, referências e grafos. |
| [09 — Memória observável](architecture/flows/09-memoria-observavel.mmd) | Identificar a origem dos nós, arestas e animações. |
| [10 — Raciocínio](architecture/flows/10-raciocinio.mmd) | Acompanhar a entrada real, a gramática restrita e os fallbacks. |
| [11 — Diagnóstico e governança](architecture/flows/11-diagnostico-governanca.mmd) | Distinguir cobertura lexical, políticas, confiança e evolução. |
| [12 — Ciência e publicação](architecture/flows/12-ciencia-publicacao.mmd) | Separar análise reproduzível, runtime, descoberta e entrega editorial. |
| [13 — Validação e entrega](architecture/flows/13-validacao-entrega.mmd) | Entender testes, JUnit, exportação limpa, commit e CI remota. |

## O que cada relação significa

Há duas formas de representar o sistema, com propósitos distintos. O inventário extraído de fontes mostra relações estáticas: importações explícitas, módulos, símbolos e configuração. Os fluxogramas curados descrevem percursos que o código permite executar, incluindo suas condições. Nenhuma dessas representações, isoladamente, comprova que o percurso foi executado com sucesso nesta máquina.

Nos fluxogramas, caixas identificam componentes ou etapas; losangos representam decisões; setas contínuas indicam composição ou passagem possível de dados e controle; setas pontilhadas registram uma condição opcional, uma fronteira ou uma limitação. Uma seta em uma visão geral não deve ser interpretada como uma chamada direta de função. Para a ordem operacional e a condição de passagem, use o fluxograma específico e a fonte vinculada.

O mapa estático de importações não consegue resolver com certeza todos os carregamentos tardios, importações dinâmicas, plugins, serviços externos ou efeitos produzidos por subprocessos. O catálogo de fluxos complementa essas relações com leituras dirigidas do código. O universo de arquivos considerado, as exclusões e as contagens pertencem ao manifesto do gerador, e não a uma estimativa de qualidade.

Relação estática, componente configurado, ferramenta instalada, autenticação disponível, inferência concluída, análise de alvo aceita e validação externa são estados diferentes. A leitura dos mapas deve conservar essa distinção.

## Interfaces e fronteiras do Core

O operador pode chegar ao primário pela CLI, pelo OpenCode, pelo MCP `ecosystem-network` ou pela interface Streamlit. A configuração do OpenCode é gerada por `integrations/opencode_cli.py`; mudanças nessa configuração devem ser feitas pelo gerador e reproduzidas no arquivo compilado. O MCP expõe ferramentas e contratos. A colaboração e a seleção dos agentes pertencem ao primário e ao Blackboard.

O site local REA explica configuração e exemplos. Servir a página de instruções não comprova que um engine esteja configurado nem que um alvo tenha sido analisado. Os demais sites, os plugins científicos e as integrações de publicação têm contratos próprios. A garantia de execução local do worker REA não deve ser estendida automaticamente a esses serviços.

Os executores de programação Codex, Claude e Antigravity são adaptadores de CLI. Cada executor depende de seu ambiente, da autenticação e, quando aplicável, do saldo. O OpenCode hospeda a coordenação; a execução recursiva do mesmo MCP por um executor OpenCode é bloqueada na ponte autônoma. Configurar um modelo local não comprova que ele consiga cumprir uma tarefa completa com chamadas de ferramentas.

## Primário, Blackboard e MetaBus

O ponto de entrada é `MarceloClaroOrchestrator`. No servidor `ecosystem-network`, `get_library_orchestrator()` cria uma instância mínima; `get_coordinator()` reutiliza essa mesma instância e chama `ensure_agents_loaded()`. Um lock impede que o catálogo seja registrado várias vezes nesse primário. A leitura da biblioteca e a execução coordenada, portanto, não criam primários concorrentes nesse percurso.

O primário consulta contexto e lições, publica tarefas no Blackboard, pondera capacidades e confiança e recebe a conclusão. O Blackboard contém cartões de agentes e estados de tarefas. O MetaBus transporta eventos e persiste memória episódica, conteúdo semântico, observações e o ledger de confiança. Os estados persistidos são dados operacionais locais; sua existência não certifica a exatidão de uma resposta.

O roteamento inspirado em atenção combina sinais de semântica, capacidade, confiança e carga. Gates de elegibilidade antecedem a seleção. A arquitetura também inclui `LLMReductionLayer`, `TransformerPipeline`, `GradingHead` e `HierarchicalMemory`. Esses nomes descrevem mecanismos de roteamento, contexto e revisão; não indicam treinamento de uma rede Transformer no Core.

`TaskRuntime` oferece o percurso nanogranular com DAGs, leases e recuperação. `WorkflowCoordinator` oferece outro nível de composição: etapas coordenadas com checkpoints duráveis. Os dois contratos devem ser examinados separadamente, pois um workflow não é apenas um alias do runtime de leases.

## Execução autônoma e retomada

Antes de uma análise textual coordenada, `ecosystem_text_spec` cria uma especificação de sessão com critérios. Ela é identificada como `criteria_only` e `software_delivery=false`. O `spec_id` acompanha a execução. Esse contrato ajuda a verificar a forma da entrega textual, mas não substitui especificação de software, testes nem histórico RED–GREEN.

`AutonomousCoordinator` cruza o inventário federado com a disponibilidade dos executores, verifica instruções e publica a tarefa por meio do primário. O executor recebe instruções, contexto e orçamento. `HarnessRuntime._run_cli` fornece `stdin=PIPE` quando existe entrada a comunicar, preservando o transporte do prompt para CLIs que o recebem pela entrada padrão. A saída real e os estados da CLI são examinados antes de considerar o passo concluído.

Falhas são classificadas; uma alternativa só pode ser usada quando elegível e dentro do orçamento. O resultado do executor não é o aceite final. `report_completion` aplica o gate do primário, e o estado autoritativo da tarefa é publicado ao Blackboard. Trust, economia e reflexão participam desse fechamento.

Os workflows executam as etapas sequencialmente. A definição é normalizada, ordenada topologicamente e vinculada a um hash. O checkpoint registra a reserva de orçamento antes de iniciar o executor. Ao retomar, é preciso fornecer a mesma definição. Etapas aceitas são reaproveitadas. Uma etapa encontrada como `running` é tratada como execução interrompida, com resultado incerto; repeti-la exige `retry_failed=true`. Consultar o status de um workflow não inicia uma etapa.

## SDD, TDD e histórico autenticado

`SpecRegistry` carrega especificações e critérios; `TDDRunner` executa os testes registrados; `SpecVerifier` decide o aceite. Os contratos executáveis podem vincular evidência a targets específicos por critério. Evidência declarada pelo agente não substitui o objeto de runtime emitido pelo runner.

`TDDHistory` registra execuções reais de pytest. Um RED elegível precisa apresentar falha funcional de asserção nos testes coletados, sem erro de coleta, setup ou teardown. Uma falha de infraestrutura não é aceita como RED funcional. Um GREEN precisa concluir os testes correspondentes com sucesso. As fases produzem recibos locais autenticados por HMAC e vinculados à especificação, à configuração, aos testes e às fontes.

O par exige ordem temporal e de ledger correta, os mesmos nodeids coletados e correspondência com as fontes atuais. Mudanças posteriores nos testes, na especificação, na configuração ou no código podem invalidar a ligação do recibo à entrega. A reexecução de um baseline pode criar nova evidência, identificada com sua data real; não recria um RED histórico que nunca ocorreu.

O gate de software é fechado quando falta evidência confiável ou quando um contrato falha. O aceite significa que os critérios locais registrados foram satisfeitos. Qualidade editorial, segurança universal e validação externa exigem verificações próprias.

## REA: registro de camadas e engines

`rea_layers.py` é o registro canônico que traduz as camadas do REA em sondas de ambiente e operações suportadas. Ele distingue motores embarcados de engines externos. `layers_status()` e `probe_layer()` verificam diretórios, comandos e configuração; essas sondas não abrem um alvo, não iniciam o REA e não aumentam confiança.

`ReaBridge` valida o pedido, prepara o ambiente por `_child_environment`, incorpora `engine_environment`, inicia a troca stdio com o REA e interpreta a resposta estruturada. A allowlist do worker é aplicada no modo local isolado; não representa uma restrição universal de ambiente sobre toda invocação da ponte. `status` examina arquivos e dependências por `ReaBridge.status`; `layers` consulta `layers_status` e as sondas de cada camada. Nenhuma dessas duas operações equivale a uma análise de alvo.

O registro declara 18 camadas, mas a operação Core `layer` aceita somente aquelas com `layer_inspection` definido. No commit de referência, são `javascript`, `apple`, `android_jadx`, `android_apktool`, `firmware`, `native_offline_elf`, `native_core_crash`, `managed_dotnet`, `pe_resources`, `evm` e `artifact`. A ponte rejeita uma camada cuja inspeção seja nula. O caminho `analyze` executa a análise JavaScript, e `analyze_binary` exige o provedor Ghidra, com vínculo de sessão e fechamento dos recursos. Esse último percurso não alterna automaticamente para IDA ou Hopper.

As camadas `native_ida`, `native_hopper`, `android_adb`, `browser`, `jeb` e `reference` são registros informativos sem uma operação `layer` executável nesta ponte. `native_ghidra` também tem inspeção de camada nula, mas possui o percurso separado `analyze_binary`. As demais ferramentas anunciadas nesses registros dependem de seus runtimes MCP próprios, configuração, dispositivos e licenças; seu nome no catálogo não autoriza desenhar um resultado de análise Core como consequência direta. Quando uma operação analítica implementada é concluída, sua Evidence contém identidade, operação, sujeito, resultado e limitações. O primário registra a observação com proveniência, sem converter sucesso estrutural em confiança adicional.

| Grupo | Superfícies registradas | Condições principais |
|---|---|---|
| JavaScript e Electron | Bundles, ASAR, sourcemaps e semântica declarada | Analisador embarcado; recuperação depende dos artefatos presentes. |
| Nativo | Ghidra, IDA MCP e Hopper | Core `analyze_binary` é Ghidra; IDA/Hopper são registros para runtimes próprios, sujeitos a configuração/licença. |
| Apple | Mach-O, plist, Objective-C e Swift | Leitores e operações específicas do provedor. |
| Android | JADX, apktool, adb e JEB | Core `layer` contempla JADX/apktool; adb/JEB exigem seu runtime próprio e dispositivo/serviço quando aplicável. |
| Firmware | unblob e binwalk | Comandos externos e formatos suportados pelo engine. |
| ELF e crash gravado | pwntools, pyelftools, Unicorn, gdb e pwndbg | Engines e arquivos locais; não presumir debug de processo vivo. |
| .NET | Metadados gerenciados e ILSpy opcional | Metadados não equivalem a decompilação completa. |
| PE e EVM | Recursos PE e interface de bytecode | Codificação EVM e limites de entrada declarados. |
| Navegador | Cenário, screenshot e observação web | Registro sem inspeção `layer` Core; runtime coordenado próprio, separado do worker estático. |
| Artefatos e referências | Archives e bundles Evidence | Core `layer` contempla `artifact`; `reference` é registro sem inspeção, com ferramentas do runtime próprio. |

Um engine constar no registro não comprova que esteja instalado ou licenciado nesta máquina. O catálogo MCP real e a sonda atual resolvem essa condição.

## REA local: duas fronteiras de isolamento

O percurso direto é `inspect → recibo → explain`. `LocalReaAssistant` resolve o alvo, detecta seu tipo e inicia `run_isolated_worker`. No Linux/WSL, o worker recebe namespaces privados de usuário, rede e PID. Ele confirma PID 1, uma rede distinta da rede do host, somente a interface `lo` e ausência de rota externa. Se esse isolamento não estiver disponível, a análise é bloqueada.

O worker calcula o digest antes e depois. HTML é lido estaticamente; scripts e links são enumerados sem execução ou acesso aos destinos. Os demais tipos suportados passam pelo primário mínimo e pelo provedor REA correspondente. O resultado é recusado se os bytes do alvo mudarem. O recibo JSON é identificado pelo SHA-256 de seu conteúdo e gravado no diretório privado do assistente. `explain` exige contenção do caminho, limite de tamanho e correspondência do hash.

Uma URL admitida nesse percurso precisa ser literal loopback. O snapshot exige HTTP 200, rejeita redirects e limita o tamanho. Ele não representa navegação de um site completo, carregamento de recursos externos ou execução de JavaScript. A garantia de privacidade cobre o worker analítico e seus descendentes; a origem do alvo e o cliente que fornece o pedido continuam sendo responsabilidades do operador.

O percurso com agente tem outra fronteira. `setup` grava um perfil próprio, sem modificar a configuração global. O cliente OpenCode roda fora do projeto, com HOME/XDG próprios, provider local e quatro ferramentas MCP `core_rea_*`. A configuração efetiva é conferida antes de iniciar a conversa. O cliente é contido em namespace de PID, mas preserva a rede do host para acessar o modelo loopback. Essa rede não recebe a mesma garantia de isolamento do worker analítico.

Com `--prompt`, `validate_agent_trace` exige evento `tool_use` concluído da ferramenta esperada, sucesso e um recibo local que passe pela revalidação. Texto livre do modelo não vira achado observado. Um pedido que só executa a ferramenta de prontidão é marcado como prontidão; o alvo continua sem análise comprovada. Uma TUI que fecha com código zero recebe `client_exit_only`. Prazo, cancelamento e interrupção encerram o processo contido e seus descendentes.

A [prontidão R868/R869](PRONTIDAO_LOCAL_CORE_R868.md) registra uma análise local direta demonstrada e os limites das tentativas com modelo. A análise REA autônoma de alvo pelo LLM local permanece sem comprovação aceita nessa referência. O mapa não transforma os ramos condicionais do código em resultados executados.

## Conhecimento, memória e grafos

`UnifiedSearchRAG` reúne busca, recuperação enriquecida e auditoria de referências. A consulta pode expandir termos, aplicar sinal temporal e deduplicar resultados. O contexto recuperado contém dados e fontes, sem autoridade para modificar as instruções do agente. Uma resposta sem apoio suficiente deve declarar abstenção ou limitação. Provedores científicos e web externos têm sua própria fronteira de rede.

Há dois modelos de EvidenceGraph. O grafo em `mci/evidence_graph.py` persiste claims, versões, evidências, replicações e contradições. O grafo em `agentic_science_v2/evidence_graph.py` representa entidades, relações e evidências com consultas de caminhos e subgrafos. Ter entidades e relações no segundo grafo não comprova uma replicação experimental no primeiro.

`CoreMemoryNetworkSource` lê memória compartilhada, eventos recentes, claims e um grafo científico opcional. A leitura tem limites de tamanho, janela de eventos, cache e avisos de fonte ausente. O grafo visual prioriza eventos e evidências antes de cartões ociosos do catálogo. Nós e arestas podem aparecer no terminal e no Streamlit; a pulsação é derivada de timestamps observados.

`memory_network_query` realiza busca lexical e publica eventos de consulta, recuperação e resposta. A operação declara `inference_executed=false` e `calibrated=false`. A visualização de rede não mostra pesos internos de um LLM nem demonstra treinamento. O simulador, quando usado, deve ser identificado como demonstração.

## Raciocínio formal e heurístico

A fachada `reasoning_engines.route` classifica a expressão por AST. Comparações e operações booleanas seguem para `z3_solver.check`, que valida atribuições e traduz a expressão integral pela gramática restrita canônica. O solver tem limites de tempo e recurso. Um backend que não conclui a fórmula produz fallback, sem inventar SAT ou UNSAT.

O ramo simbólico usa a expressão real da entrada, a AST matemática permitida e a construção SymPy validada. Entrada não parseável, chamada não permitida ou resultado indefinido não é substituído por uma conta fixa de demonstração. A gramática é restrita; o mecanismo não interpreta código Python arbitrário.

`MultiReasoningEngine` também contém motores heurísticos e motores opcionais. Seus passos e campos de confiança precisam ser lidos conforme o tipo de motor. Uma conclusão heurística, uma solução SMT em domínio declarado e uma prova formal Lean têm contratos diferentes. A existência de um adaptador não comprova competência geral nem validação externa.

## Diagnóstico, confiança, federação e evolução

`doctor` é uma verificação de sanidade estrutural. Ela examina especificações, evolução, memória, configuração e integrações. As sondas de provedores locais distinguem instalação de serviço acessível; inferência e execução de alvo continuam exigindo evidência própria.

O diagnóstico aceita `corpus_mode=autodiscovery` ou `corpus_mode=retained`. A autodescoberta enriquece o corpus com sinais do próprio repositório. A modalidade retida exige identidade e hash, sem esse enriquecimento. O scanner usa categorias canônicas para evitar dupla contagem. Em ambos os casos, cobertura lexical e density não são cobertura de comportamento executado.

O diagnóstico combina cobertura, gaps teleológicos e recomendações; o modo profundo inclui sucessores, inércia, ruído, compressão e engenharia reversa do escopo textual. Ele produz observações locais. Não se deve inferir completude funcional de um percentual elevado de autodescoberta ou segurança arquitetural de um indicador de ruído.

Há uma classe homônima em `scanners/diagnostic_pipeline.py` com responsabilidade diferente. Seu método `DiagnosticPipeline.varrer` audita a sincronia de artefatos declarados em um plano: arquivos, expressões regulares, nomes esperados/proibidos e cobertura entre arquivos. A operação é hermética, usa somente a biblioteca padrão e não acessa rede, subprocesso ou LLM. Seus achados são `candidato_a_inspecao`, com `exige_validacao_externa=true`; não substituem compilação, testes ou revisão externa. A função `run` desse mesmo módulo é uma fachada de compatibilidade para `scanners.pipeline.DiagnosticPipeline.run`, o diagnóstico lexical descrito acima. `varrer` não é uma sonda de inferência nem um alias de `doctor`.

A federação registra artefatos com política de invocação, fonte, integridade, suporte e licença. Um artefato pode estar degradado por licença não declarada. A declaração de licença é um dado de governança; sua ausência não é resolvida escrevendo uma licença presumida. O roteamento precisa considerar os motivos de bloqueio ou degradação relevantes.

O motor efetivamente criado pelo primário é `TrustEngine`, em `trust/trust_engine.py`, com scorer, gate, outcomes, memória e drift. A função menor `trust.behavioral_gate.allow` e a fachada `protocolos.behavioral_gate.check` formam outro contrato explícito. A fachada não representa um segundo algoritmo independente e não deve ser contada como duas capacidades. Também não deve ser confundida com uma chamada direta do primário ao gate de `TrustEngine`.

`TokenEconomy` administra stake, liberação, slashing e fees no ledger local. `EvolutionRegistry` deriva o próximo round do registro, preserva o histórico e oferece verificação de encadeamento e custódia. Registrar um ciclo e auditar um ciclo são operações distintas. Campos de auditoria ou validação externa só devem ser preenchidos quando existir evidência correspondente.

## Pesquisa, ciência e publicação

O percurso `scientific_reproducible_run` valida a configuração, utiliza `ScientificProvenancePipeline`, preserva um snapshot CSV e executa um método estatístico definido. Um subprocesso `reproduce.py` compara os mesmos bytes e o resultado. O pacote registra configuração, código de método, hashes, referências, revisão computacional e artefatos. A autenticidade da fonte pode continuar sendo uma declaração do usuário; reexecução não confirma sua origem de forma independente.

`scientific_runtime_run` é um ramo separado, apoiado por `LiveScientificRuntime`. Ele executa um processo externo configurado, acompanha chamadas ao modelo por proxy de auditoria e coleta recibos e artefatos. Esse resultado não equivale automaticamente à análise estatística do percurso reproduzível.

A descoberta científica compõe EvoSci, Deep Research, revisão, revisão de manuscrito e Paper Composer. No percurso estrito, Deep Research precisa declarar evidência elegível e experimento executado; sem isso, o fluxo é bloqueado antes de transformar a exploração em publicação. A revisão R103 tem seu gate de exportação. O composer organiza estrutura, seções e citações, e a auditoria de consistência e de movimentos científicos produz achados para revisão.

O pipeline OQS–MCI–VSEE–EGS tem outro contrato: trabalha com entradas reportadas e a saída do executor. A função de governança declara que não calcula um experimento sobre dados brutos e que a evidência não é elegível para esse fim. Os mapas mantêm essa limitação em vez de tratar um rótulo de sucesso como execução experimental.

O pacote final pode conter TeX, DOCX, referências, site e material didático. Autoria, declarações, adequação editorial e envio pertencem à revisão humana e ao processo de publicação autorizado. Revisão interna não substitui parecer externo; nenhum mapa confere validação clínica, Qualis ou certificação científica.

## Validação dos mapas e limites de entrega

A validação R879 deve conferir que o inventário corresponde à revisão declarada, que os caminhos e símbolos existem, que os arquivos Mermaid são parseáveis e que o HTML é utilizável localmente. As contagens do gerador descrevem somente o universo coberto por sua política de extração. Um módulo sem importação explícita ainda pode ser acessado por configuração ou carregamento dinâmico; uma aresta estática não prova que seja atingida em runtime.

Os recibos de testes da prontidão anterior são uma fotografia executada separada. O catálogo R879 inclui o fluxo de validação com pytest, JUnit e relatório de qualidade reutilizando o XML. Contagens físicas, skips e subtests permanecem separados. Exportação limpa e hashes antes/depois ajudam a vincular a verificação ao código entregue. A CI remota exige observação própria depois do push; seu estado não é derivado da suíte local.

Consulte também [ARCHITECTURE.md](../ARCHITECTURE.md), [MANUAL.md](../MANUAL.md), [CORRIGENDUM.md](../CORRIGENDUM.md) e [prontidão local R868/R869](PRONTIDAO_LOCAL_CORE_R868.md). As fontes detalhadas de cada percurso estão no catálogo de fluxos; o inventário e o histórico Git permitem localizar implementações que não cabem na visão panorâmica.

A visão operacional inicial usa [DOT curado](architecture/curated-overview.dot)
e [SVG](architecture/curated-overview.svg), com composição por responsabilidade.
O panorama minucioso continua no primeiro fluxograma. Arestas pontilhadas
representam operações específicas e fronteiras condicionadas, não execução
automática de todas as superfícies. Para regenerar o resumo: `dot -Tsvg
docs/architecture/curated-overview.dot -o docs/architecture/curated-overview.svg`.

## Resultado local registrado

O [recibo de validação R879](architecture/verification-local-r879.json) registra
57 testes específicos/regressões aprovados, os 13 fluxos renderizados, 78
âncoras conferidas e navegação em viewport desktop/móvel sem requisições HTTP
externas observadas na página. O gate SDD/TDD foi aceito pelo primário em cópia
isolada, com contraprova RED e GREEN atuais. Não se preencheu histórico retroativo.
Essa bateria não repete nem substitui a suíte integral anterior R869.
