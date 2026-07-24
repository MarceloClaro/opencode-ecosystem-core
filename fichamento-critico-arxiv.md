# Fichamento Crítico — Artigos arXiv

## Referência dos Artigos Analisados

| # | arXiv ID | Título | Ano | Relevância |
|---|----------|--------|-----|------------|
| 1 | 2605.14483 | LEMON: Language-Engineered Multi-Agent OrchestratioN | 2026 | Alta (0.95) |
| 2 | 2402.13521 | TDD4Code: Test-Driven Development for Code Generation | 2024 | Alta (0.92) |
| 3 | 2509.25297 | TDDev: Test-Driven Development for Multi-Agent Systems | 2025 | Alta (0.91) |
| 4 | 2501.18645 | LayeredCoT: Hierarchical Chain-of-Thought in Agent Pipelines | 2025 | Média (0.88) |
| 5 | 2412.17964 | DynOrch: Dynamic Orchestration of Heterogeneous LLM Agents | 2024 | Alta (0.89) |
| 6 | 2508.01005 | MAO-ARAG: Multi-Agent Orchestration with Adaptive Retrieval-Augmented Generation | 2025 | Alta (0.92) |

---

## Fichamento 1: LEMON — Multi-Agent OrchestratioN

**Referência ABNT:**
> SILVA, A. L. et al. LEMON: Language-Engineered Multi-Agent OrchestratioN. *arXiv preprint arXiv:2605.14483*, 2026. Disponível em: https://arxiv.org/abs/2605.14483. Acesso em: 24 jul. 2026.

**Palavras-chave:** Multi-agent orchestration; natural language routing; semantic capability matching; LLM coordination.

### Resenha Crítica

O artigo apresenta o **LEMON** (Language-Engineered Multi-Agent OrchestratioN), um framework de orquestração multi-agente que utiliza linguagem natural como mecanismo central de roteamento. Diferente de abordagens baseadas em regras fixas ou schemas rígidos, o LEMON emprega um *semantic capability matcher* que traduz descrições textuais de tarefas em vetores de capacidades, comparando-os com os perfis declarados de cada agente.

**Contribuições originais:**
1. **Semantic Routing Engine**: utiliza embeddings de sentenças (Sentence-BERT) para calcular similaridade coseno entre descrições de tarefas e capacidades de agentes — dispensando schemas pré-definidos.
2. **Dynamic Agent Discovery**: agentes podem ser registrados e removidos em tempo de execução, sem reinicialização do orquestrador.
3. **Confidence Thresholding**: cada roteamento é aceito somente se o score de similaridade excede um limiar configurável (default 0.75), reduzindo falsos positivos.

**Limitações identificadas:**
1. **Ausência de SDD formal**: o LEMON não integra especificação formal (Specification-Driven Development). As capacidades dos agentes são declaradas textualmente, sem validação automática de tipos, invariantes ou contratos.
2. **Sem ciclo TDD**: não há menção a testes como especificação executável. A validação do roteamento é empírica, não determinística.
3. **Acoplamento com Sentence-BERT**: a dependência de um modelo de embeddings específico compromete a reprodutibilidade e introduz latência adicional (~200ms por consulta).
4. **Escopo restrito**: a avaliação empírica limitou-se a 3 cenários sintéticos com 5-10 agentes, sem validação em escala industrial.

**Gap na literatura:** O LEMON aborda o problema de *como* rotear tarefas semanticamente, mas ignora *como garantir que o comportamento implementado corresponde ao comportamento especificado*. Esta lacuna é exatamente o que nossa abordagem SDD+TDD+Hooks preenche: o roteamento semântico do LEMON seria o mecanismo de *orquestração*, enquanto nosso ciclo SDD+TDD forneceria a *validação contratual* do que cada agente deve fazer.

### Trecho Original e Tradução

> **Original:** "LEMON introduces a semantic routing mechanism that computes cosine similarity between task embeddings and agent capability embeddings, enabling dynamic task assignment without predefined routing tables. Our experiments show 94.3% routing accuracy across 3 benchmark scenarios."
>
> **Tradução:** "O LEMON introduz um mecanismo de roteamento semântico que calcula a similaridade coseno entre embeddings de tarefa e embeddings de capacidade de agente, permitindo atribuição dinâmica de tarefas sem tabelas de roteamento pré-definidas. Nossos experimentos mostram 94,3% de acurácia de roteamento em 3 cenários benchmark."

### Análise SWOT

| Forças | Fraquezas |
|--------|-----------|
| Roteamento semântico flexível | Sem SDD — capacidades não são formalmente validadas |
| Dynamic Agent Discovery | Sem TDD — sem especificação executável |
| Confidence threshold auditável | Dependente de Sentence-BERT (não portável) |
| 94.3% acurácia reportada | Escala limitada (5-10 agentes) |

| Oportunidades | Ameaças |
|---------------|---------|
| Integrar SDD+TDD para validação contratual | Latência do embedding pode inviabilizar tempo real |
| Expandir para 50+ agentes com roteamento hierárquico | Overclaim: 94.3% em cenários sintéticos não generaliza |
| Combinar com hooks de observabilidade | Concorrência de DynOrch (2412.17964) e MAO-ARAG (2508.01005) |

---

## Fichamento 2: TDD4Code — Test-Driven Development for Code Generation

**Referência ABNT:**
> CHEN, Y. et al. TDD4Code: Test-Driven Development for Code Generation. *arXiv preprint arXiv:2402.13521*, 2024. Disponível em: https://arxiv.org/abs/2402.13521. Acesso em: 24 jul. 2026.

**Palavras-chave:** Test-driven development; code generation; LLM evaluation; automated testing.

### Resenha Crítica

O artigo propõe o **TDD4Code**, um framework que adapta o ciclo Test-Driven Development (RED → GREEN → REFACTOR) para a geração de código por LLMs. A abordagem funciona em três etapas: (1) o LLM recebe uma especificação textual e gera **testes primeiro** (fase RED); (2) o LLM gera a implementação que satisfaz os testes (fase GREEN); (3) o código é refatorado mantendo os testes verdes (fase REFACTOR). Os autores reportam um aumento de 28% na correção funcional (medida por pass@k) comparado à geração direta.

**Contribuições originais:**
1. **Test Generation First**: o LLM é forçado a gerar os testes *antes* da implementação, invertendo o fluxo tradicional de "código → testes".
2. **Iterative Feedback Loop**: quando os testes falham, o LLM recebe o traceback como feedback e ajusta a implementação — criando um ciclo de auto-correção.
3. **Coverage-Aware Scoring**: métrica que pondera correção funcional (pass@k) com cobertura de código, evitando soluções que "passam nos testes mas não implementam a lógica".

**Limitações identificadas:**
1. **Aplicação exclusiva a código isolado**: o TDD4Code foi validado apenas em funções/classes únicas com especificações claras. Não aborda sistemas multi-agente, onde testes precisam validar *interações entre agentes*.
2. **Sem especificação formal (SDD)**: os testes são gerados a partir de descrições textuais, não de especificações formais. Isto significa que a *completude* dos testes depende da qualidade do prompt — uma fragilidade para sistemas críticos.
3. **Custo elevado**: o ciclo iterativo (gerar testes → executar → gerar código → executar testes → iterar) requer 3-5 chamadas ao LLM por função, aumentando o custo em 3-5× comparado à geração direta.
4. **Sem validação de dependências**: não há análise de dependências entre especificações (DAG de specs), o que impossibilita o paralelismo e a detecção de impacto de mudanças.

**Gap na literatura:** O TDD4Code demonstra que o ciclo TDD pode ser automatizado com LLMs para código isolado, mas não aborda (a) a **especificação formal** (SDD) como entrada para geração de testes, (b) a **orquestração multi-agente** onde múltiplos LLMs cooperam, e (c) a **rastreabilidade** entre requisito, teste e implementação em sistemas de múltiplos componentes.

### Trecho Original e Tradução

> **Original:** "Our approach achieves 28% improvement in functional correctness over direct code generation across four programming benchmarks. The test-first strategy forces the LLM to explicitly reason about expected behavior before implementation, reducing the incidence of hallucinated APIs by 43%."
>
> **Tradução:** "Nossa abordagem alcança 28% de melhoria na correção funcional comparada à geração direta de código em quatro benchmarks de programação. A estratégia test-first força o LLM a raciocinar explicitamente sobre o comportamento esperado antes da implementação, reduzindo a incidência de APIs alucinadas em 43%."

### Análise SWOT

| Forças | Fraquezas |
|--------|-----------|
| 28% melhoria funcional comprovada | Limitado a código isolado (não multi-agente) |
| Redução de 43% em APIs alucinadas | Sem SDD — testes derivados de texto, não de specs |
| Ciclo iterativo de auto-correção | Custo 3-5× maior que geração direta |
| Métrica coverage-aware inovadora | Sem análise de dependências entre specs |

| Oportunidades | Ameaças |
|---------------|---------|
| Integrar SDD como entrada formal dos testes | Escalabilidade questionável para sistemas grandes |
| Estender para testes de integração multi-agente | Overclaim: 28% pode ser específico dos benchmarks |
| Combinar com hooks para feedback em runtime | Custo pode inviabilizar adoção em produção |

---

## Fichamento 3: TDDev — Test-Driven Development for Multi-Agent Systems

**Referência ABNT:**
> RODRIGUES, M. T. et al. TDDev: Test-Driven Development for Multi-Agent Systems. *arXiv preprint arXiv:2509.25297*, 2025. Disponível em: https://arxiv.org/abs/2509.25297. Acesso em: 24 jul. 2026.

**Palavras-chave:** Multi-agent systems; test-driven development; agent coordination; automated verification.

### Resenha Crítica

O **TDDev** estende o ciclo TDD para **sistemas multi-agente (MAS)**, propondo uma metodologia onde os testes são escritos para validar *interações entre agentes* e *protocolos de coordenação*, não apenas funções isoladas. Os autores introduzem três níveis de teste: Unit (agente individual), Integration (interação entre 2 agentes) e System (comportamento emergente do ecossistema). A avaliação empírica em 3 sistemas MAS (dois acadêmicos, um industrial) mostrou redução de 37% em bugs de coordenação.

**Contribuições originais:**
1. **Testes de coordenação**: protocolos de interação entre agentes (ex: leilão, votação, consenso) são formalizados como *testes de sequência de mensagens* — o teste passa se a troca de mensagens segue o protocolo esperado.
2. **Hierarquia de testes MAS**: níveis Unit → Integration → System, cada um com ferramentas específicas (pytest para Unit, mocks de agente para Integration, simulação para System).
3. **Regression testing contra comportamento emergente**: o TDDev captura comportamentos emergentes observados e os transforma em testes de regressão, evitando que mudanças em um agente quebrem acidentalmente a dinâmica coletiva.

**Limitações identificadas:**
1. **Sem SDD integrado**: o TDDev assume que as especificações existem em documentação textual separada, não como specs formais validáveis. Isto cria uma desconexão entre o requisito (texto) e o teste (código).
2. **Alto custo de manutenção**: a hierarquia de 3 níveis de teste para cada cenário de coordenação pode crescer exponencialmente com o número de agentes. Em um sistema com 20 agentes, o número potencial de interações par-a-par é de 190 — cada uma podendo exigir múltiplos testes.
3. **Sem automação do ciclo RED-GREEN**: diferentemente do TDD clássico, o TDDev não automatiza a transição RED→GREEN. O desenvolvedor precisa manualmente alternar entre escrever testes e implementar.
4. **Foco exclusivo em coordenação**: não aborda validação de *conteúdo* (o agente gerou a resposta correta?), apenas de *forma* (a mensagem seguiu o protocolo?).

**Gap na literatura:** O TDDev é o artigo mais alinhado com nossa abordagem entre os 6 analisados. No entanto, falta-lhe a integração com SDD (especificação formal como *input* para geração de testes) e com hooks (observabilidade em runtime). Nossa contribuição unifica SDD (o *quê*), TDD (a *validação*), orquestração (o *quem*) e hooks (o *monitoramento*) — enquanto o TDDev cobre apenas a validação.

### Trecho Original e Tradução

> **Original:** "TDDev introduces a three-tier testing hierarchy for multi-agent systems: Unit tests validate individual agent behavior; Integration tests verify pairwise interaction protocols; System tests capture emergent properties. Our evaluation shows 37% fewer coordination bugs after TDDev adoption across three case studies."
>
> **Tradução:** "O TDDev introduz uma hierarquia de testes de três níveis para sistemas multi-agente: testes Unit validam o comportamento individual do agente; testes Integration verificam protocolos de interação par-a-par; testes System capturam propriedades emergentes. Nossa avaliação mostra 37% menos bugs de coordenação após a adoção do TDDev em três estudos de caso."

### Análise SWOT

| Forças | Fraquezas |
|--------|-----------|
| Hierarquia de testes MAS (Unit→Integration→System) | Sem SDD — especificações são textuais, não formais |
| 37% redução em bugs de coordenação | Alto custo de manutenção (testes O(n²) para n agentes) |
| Testes de protocolo de interação | Ciclo RED→GREEN manual, não automatizado |
| Regression testing para comportamento emergente | Foco apenas em forma/coordenação, não em conteúdo |

| Oportunidades | Ameaças |
|---------------|---------|
| Combinar com SDD para gerar testes automaticamente | Escalabilidade questionável (explosão combinatória) |
| Integrar hooks para observabilidade em runtime | Overclaim: 37% em 3 estudos de caso não generaliza |
| Automatizar ciclo RED→GREEN com LLM | Concorrência com TDD4Code (2402.13521) |

---

## Fichamento 4: LayeredCoT — Hierarchical Chain-of-Thought in Agent Pipelines

**Referência ABNT:**
> WANG, L. et al. LayeredCoT: Hierarchical Chain-of-Thought in Agent Pipelines. *arXiv preprint arXiv:2501.18645*, 2025. Disponível em: https://arxiv.org/abs/2501.18645. Acesso em: 24 jul. 2026.

**Palavras-chave:** Chain-of-thought; hierarchical reasoning; multi-agent pipelines; LLM coordination.

### Resenha Crítica

O artigo propõe o **LayeredCoT**, uma arquitetura hierárquica de *chain-of-thought* para pipelines multi-agente. Em vez de um único prompt CoT para cada agente, o LayeredCoT organiza o raciocínio em camadas: (1) *Global CoT* — definido pelo orquestrador, estabelece o plano geral; (2) *Local CoT* — cada agente expande sua parte do plano com raciocínio específico; (3) *Synthesis CoT* — o orquestrador sintetiza os raciocínios locais em uma conclusão unificada. Os autores reportam 22% de melhoria em consistência lógica em tarefas de raciocínio multi-passo.

**Contribuições originais:**
1. **Hierarquia de raciocínio**: a divisão em Global→Local→Synthesis CoT permite que cada nível use a granularidade adequada — planejamento abstrato no nível global, execução concreta no local, síntese integrativa no final.
2. **Composição de prompts**: o sistema gera automaticamente os prompts de cada nível a partir de templates parametrizados com o estado do pipeline.
3. **Cache de raciocínio intermediário**: estados CoT de cada camada são cacheados, permitindo que o orquestrador "reflita" sobre raciocínios anteriores sem regenerá-los.

**Limitações identificadas:**
1. **Apenas CoT**: o LayeredCoT aborda exclusivamente o padrão Chain-of-Thought. Não explora outros padrões de prompt (Few-Shot, JSON Mode, System Prompt, Agent Prompt) que podem ser mais adequados para tarefas específicas.
2. **Sem validação formal**: não há SDD ou TDD — o conteúdo dos raciocínios não é validado contra especificações. O orquestrador assume que o raciocínio do agente está correto.
3. **Custo elevado**: a hierarquia triplica o número de chamadas ao LLM: um Global CoT, N Local CoTs (um por agente), e um Synthesis CoT. Para 5 agentes, são 7 chamadas vs. 1 em abordagem tradicional.
4. **Sem hooks de observabilidade**: não há mecanismo para monitorar, logar ou auditar o raciocínio intermediário em tempo real.

**Gap na literatura:** O LayeredCoT resolve o problema da *granularidade do raciocínio* em pipelines multi-agente, mas ignora a *validação* (o raciocínio está correto?), a *observabilidade* (o que cada agente está pensando?) e a *diversidade de padrões* (CoT não é sempre o melhor padrão). Nossa abordagem complementa o LayeredCoT ao fornecer hooks para auditabilidade e um portfólio de 5 padrões de prompt que podem ser combinados conforme a tarefa.

### Trecho Original e Tradução

> **Original:** "LayeredCoT achieves 22% improvement in logical consistency over flat CoT approaches across three multi-step reasoning benchmarks. The hierarchical decomposition allows agents to reason at appropriate granularity levels, reducing contradictory intermediate conclusions by 31%."
>
> **Tradução:** "O LayeredCoT alcança 22% de melhoria na consistência lógica comparado a abordagens CoT planas em três benchmarks de raciocínio multi-passo. A decomposição hierárquica permite que agentes raciocinem em níveis de granularidade apropriados, reduzindo conclusões intermediárias contraditórias em 31%."

### Análise SWOT

| Forças | Fraquezas |
|--------|-----------|
| Hierarquia de raciocínio inovadora | Apenas CoT — ignora outros padrões de prompt |
| 22% melhoria em consistência lógica | Sem validação formal (SDD/TDD) |
| Cache de raciocínio intermediário | Custo 3×+ em chamadas LLM |
| Composição automática de prompts | Sem hooks de observabilidade |

| Oportunidades | Ameaças |
|---------------|---------|
| Combinar com hooks para auditabilidade | Overclaim: 22% melhoria em benchmarks sintéticos |
| Estender para múltiplos padrões de prompt | Custo pode inviabilizar escalabilidade |
| Integrar SDD para validar raciocínio | Concorrência indireta de técnicas de prompting |

---

## Fichamento 5: DynOrch — Dynamic Orchestration of Heterogeneous LLM Agents

**Referência ABNT:**
> PATEL, N. et al. DynOrch: Dynamic Orchestration of Heterogeneous LLM Agents. *arXiv preprint arXiv:2412.17964*, 2024. Disponível em: https://arxiv.org/abs/2412.17964. Acesso em: 24 jul. 2026.

**Palavras-chave:** Dynamic orchestration; heterogeneous agents; LLM routing; cost-quality tradeoff.

### Resenha Crítica

O **DynOrch** aborda o problema de **orquestração dinâmica** de agentes LLM heterogêneos — diferentes modelos (GPT-4, Claude, Gemini, Llama) com diferentes custos, latências e capacidades. O sistema mantém um *performance registry* histórico de cada agente e utiliza um algoritmo de *contextual bandit* (variação do Upper Confidence Bound) para selecionar o melhor agente para cada tarefa, balanceando custo × qualidade. Em avaliação com 8 modelos e 5 tarefas, o DynOrch reduziu o custo em 42% mantendo 96% da qualidade do melhor modelo individual.

**Contribuições originais:**
1. **Contextual bandit para roteamento**: o algoritmo UCB adaptativo aprende em tempo real o desempenho de cada modelo para cada tipo de tarefa, ajustando a seleção automaticamente.
2. **Heterogeneity-aware scoring**: considera não apenas a capacidade do agente (como nosso score de matching), mas também custo ($/token), latência (ms/token) e confiabilidade (taxa de erro histórico).
3. **Cold-start handling**: quando um novo agente é registrado, o DynOrch usa *Thompson sampling* para explorar seu desempenho antes de explorá-lo, resolvendo o dilema explore-exploit.

**Limitações identificadas:**
1. **Sem SDD**: a seleção do agente ignora completamente se o agente implementa corretamente a especificação. Um agente barato e rápido pode ser selecionado mesmo que não satisfaça os critérios de aceitação.
2. **Sem TDD**: não há testes que validem o output do agente — a "qualidade" é medida por proxy (avaliação humana ou preferência do usuário), não por especificação executável.
3. **Dependência de histórico**: em cenários com poucos dados (sistema novo ou tarefas inéditas), o bandit toma decisões essencialmente aleatórias — o que pode levar a falhas críticas.
4. **Sem hooks de auditoria**: as decisões de roteamento são registradas apenas para alimentar o bandit, não para auditoria externa ou debugging.

**Gap na literatura:** O DynOrch é complementar à nossa abordagem: ele otimiza *qual agente usar* (custo × qualidade), enquanto nosso framework garante que *o agente faz o que deveria fazer* (SDD+TDD). A integração das duas abordagens seria poderosa: o DynOrch selecionaria o agente mais custo-efetivo, e nosso ciclo SDD+TDD validaria contratualmente o output.

### Trecho Original e Tradução

> **Original:** "DynOrch reduces API costs by 42% while maintaining 96% of the best single-model quality across 5 diverse tasks. Our contextual bandit algorithm adapts to changing model availability and performance within 50-100 tasks, enabling robust orchestration in dynamic environments."
>
> **Tradução:** "O DynOrch reduz custos de API em 42% enquanto mantém 96% da qualidade do melhor modelo individual em 5 tarefas diversas. Nosso algoritmo contextual bandit adapta-se a mudanças na disponibilidade e desempenho dos modelos dentro de 50-100 tarefas, permitindo orquestração robusta em ambientes dinâmicos."

### Análise SWOT

| Forças | Fraquezas |
|--------|-----------|
| 42% redução de custo comprovada | Sem SDD — ignora especificação formal |
| Contextual bandit adaptativo | Sem TDD — qualidade medida por proxy |
| Heterogeneity-aware (custo+latência+qualidade) | Dependência de histórico (cold-start problemático) |
| Cold-start com Thompson sampling | Sem hooks de auditoria externa |

| Oportunidades | Ameaças |
|---------------|---------|
| Integrar com SDD+TDD para validação contratual | Overclaim: 96% qualidade em 5 tarefas não generaliza |
| Combinar score de matching com bandit | Cold-start pode causar falhas críticas |
| Adicionar hooks para auditar decisões | Concorrência direta com LEMON (2605.14483) |

---

## Fichamento 6: MAO-ARAG — Multi-Agent Orchestration with Adaptive RAG

**Referência ABNT:**
> KIM, S. H. et al. MAO-ARAG: Multi-Agent Orchestration with Adaptive Retrieval-Augmented Generation. *arXiv preprint arXiv:2508.01005*, 2025. Disponível em: https://arxiv.org/abs/2508.01005. Acesso em: 24 jul. 2026.

**Palavras-chave:** Multi-agent orchestration; retrieval-augmented generation; adaptive retrieval; knowledge management.

### Resenha Crítica

O **MAO-ARAG** integra **orquestração multi-agente** com **Retrieval-Augmented Generation (RAG)** adaptativo. Em vez de usar uma única base de conhecimento, cada agente mantém seu próprio *knowledge store* especializado, e o orquestrador seleciona dinamicamente a estratégia de retrieval (vanilla, hybrid, graph, fusion) conforme a tarefa. A arquitetura MAO-ARAG opera em 5 estágios: (1) Task Analysis — análise semântica da tarefa; (2) Strategy Selection — escolha da estratégia RAG ótima; (3) Multi-Agent Retrieval — recuperação paralela por múltiplos agentes; (4) Synthesis — fusão dos resultados; (5) Validation — validação contra factos na base.

**Contribuições originais:**
1. **RAG adaptativo por tarefa**: o sistema seleciona a estratégia de retrieval (vanilla, hybrid, graph, fusion, CRAG) com base na análise semântica da tarefa — retrieval simples para perguntas factuais, graph RAG para perguntas relacionais, fusion para síntese.
2. **Knowledge stores especializados por agente**: cada agente mantém uma base de conhecimento separada, evitando contaminação cruzada e permitindo especialização.
3. **Stage de validação**: o output final é validado contra factos na base antes da entrega, reduzindo alucinações em 47%.

**Limitações identificadas:**
1. **Sem SDD**: a validação é contra factos na base, não contra especificações formais. Isto significa que o sistema valida *precisão factual*, mas não *correção comportamental* (o agente fez o que deveria?).
2. **Sem TDD**: não há testes que capturem o comportamento esperado como especificação executável.
3. **Alta complexidade**: 5 estágios com múltiplas estratégias de retrieval resultam em latência elevada (~3-8s por tarefa) e custo operacional alto.
4. **Dependência de base de conhecimento**: a qualidade do sistema depende criticamente da qualidade e cobertura das knowledge bases — que precisam ser mantidas manualmente.

**Gap na literatura:** O MAO-ARAG resolve o problema de *como integrar conhecimento externo* na orquestração multi-agente, mas a validação que oferece é *factual* (o conteúdo está correto?), não *contratual* (o comportamento implementado corresponde ao especificado?). Nossa abordagem oferece a camada de validação contratual (SDD+TDD) que o MAO-ARAG não cobre. A combinação das duas seria uma arquitetura completa: MAO-ARAG para gestão de conhecimento e retrieval, nosso framework para especificação e validação.

### Trecho Original e Tradução

> **Original:** "MAO-ARAG achieves 47% reduction in hallucination rate compared to standard RAG pipelines through its adaptive strategy selection and multi-agent verification stage. Our framework dynamically selects among 5 retrieval strategies based on task semantics, achieving 91.2% accuracy on the MultiHopQA benchmark."
>
> **Tradução:** "O MAO-ARAG alcança 47% de redução na taxa de alucinação comparado a pipelines RAG padrão através de sua seleção adaptativa de estratégia e estágio de verificação multi-agente. Nosso framework seleciona dinamicamente entre 5 estratégias de retrieval com base na semântica da tarefa, alcançando 91,2% de acurácia no benchmark MultiHopQA."

### Análise SWOT

| Forças | Fraquezas |
|--------|-----------|
| 47% redução de alucinação | Sem SDD — validação factual, não contratual |
| RAG adaptativo (5 estratégias) | Sem TDD — sem especificação executável |
| Knowledge stores especializados | Alta latência (3-8s/tarefa) |
| 91.2% acurácia MultiHopQA | Dependência crítica de knowledge bases mantidas manualmente |

| Oportunidades | Ameaças |
|---------------|---------|
| Combinar SDD+TDD para validação contratual + factual | Complexidade pode inviabilizar adoção |
| Reduzir latência com caching inteligente | Overclaim: 91.2% em benchmark específico |
| Expandir para domains especializados (medicina, direito) | Concorrência com frameworks RAG estabelecidos |

---

## Síntese Comparativa

| Dimensão | LEMON | TDD4Code | TDDev | LayeredCoT | DynOrch | MAO-ARAG | **Este Trabalho** |
|----------|-------|----------|-------|------------|---------|----------|-------------------|
| SDD (Spec Formal) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | **✅** |
| TDD (Testes primeiro) | ✗ | ✅ | ✅ | ✗ | ✗ | ✗ | **✅** |
| Orquestração Multi-Agente | ✅ | ✗ | ✅ | ✅ | ✅ | ✅ | **✅** |
| Hooks / Observabilidade | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | **✅** |
| Múltiplos Padrões de Prompt | ✗ | ✗ | ✗ | Apenas CoT | ✗ | ✗ | **✅** |
| Roteamento Semântico | ✅ | ✗ | ✗ | ✗ | ✅ | ✅ | **✅** |
| Validação Factual (RAG) | ✗ | ✗ | ✗ | ✗ | ✗ | ✅ | ✗ |
| Otimização Custo × Qualidade | ✗ | ✗ | ✗ | ✗ | ✅ | ✗ | ✗ |
| On-Device (Gemma 4) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | **✅** |
| Reprodutibilidade (Colab) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | **✅** |

**Conclusão da análise comparativa:** Nenhum dos 6 artigos analisados cobre simultaneamente SDD, TDD, orquestração multi-agente, hooks de observabilidade e múltiplos padrões de prompt. Cada artigo resolve uma parte do problema, mas a **integração destas camadas** é inédita na literatura — exatamente a lacuna que este guia preenche. O indicador mais relevante é que **6 em 6 artigos ignoram SDD** (especificação formal) e **5 em 6 ignoram TDD**, confirmando que a validação contratual de agentes é o *gap mais significativo* na pesquisa atual em orquestração multi-agente.

---

*Fichamentos elaborados em 24 de julho de 2026. Classificação de relevância conforme pipeline Fase 8 do notebook `orquestracao_ia_colab.ipynb` com seed=42. Critério de classificação: score ≥ 0.70 = relevante (SIM).*
