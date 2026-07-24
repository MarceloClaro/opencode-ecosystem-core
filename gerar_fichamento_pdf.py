#!/usr/bin/env python3
"""
Gera PDF do Fichamento Crítico no formato ABNT
================================================
Usa weasyprint para converter HTML formatado em ABNT para PDF.
Margens: 3cm superior/esquerda, 2cm inferior/direita (ABNT NBR 14724)
Fonte: Times New Roman 12pt
Espaçamento: 1.5
"""

import weasyprint
import sys

HTML_ABNT = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Fichamento Crítico — Artigos arXiv</title>
<style>
  @page {
    size: A4;
    margin: 3cm 2cm 2cm 3cm;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #000;
    text-align: justify;
  }

  /* CAPA */
  .capa {
    text-align: center;
    padding-top: 6cm;
    page-break-after: always;
  }
  .capa .universidade {
    font-size: 14pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 6pt;
  }
  .capa .autor {
    font-size: 16pt;
    font-weight: bold;
    margin-top: 4cm;
    margin-bottom: 2cm;
  }
  .capa .titulo {
    font-size: 18pt;
    font-weight: bold;
    line-height: 1.3;
    margin-bottom: 3cm;
  }
  .capa .local-ano {
    font-size: 12pt;
    margin-top: 2cm;
  }

  /* SUMARIO */
  .sumario {
    page-break-after: always;
  }
  .sumario h2 {
    font-size: 14pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 24pt;
    text-transform: uppercase;
  }
  .sumario-item {
    display: flex;
    justify-content: space-between;
    font-size: 12pt;
    line-height: 2.0;
  }
  .sumario-item a {
    color: #000;
    text-decoration: none;
  }
  .sumario-item .num {
    font-weight: bold;
    margin-right: 12pt;
  }

  /* SECOES */
  h1 {
    font-size: 14pt;
    font-weight: bold;
    text-align: center;
    margin: 24pt 0 12pt 0;
    page-break-before: always;
    page-break-after: avoid;
  }
  h1:first-of-type { page-break-before: auto; }
  h2 {
    font-size: 12pt;
    font-weight: bold;
    margin: 18pt 0 6pt 0;
    page-break-after: avoid;
  }
  h3 {
    font-size: 12pt;
    font-weight: bold;
    font-style: italic;
    margin: 12pt 0 6pt 0;
    page-break-after: avoid;
  }
  p {
    text-indent: 1.25cm;
    margin-bottom: 6pt;
  }
  p.no-indent { text-indent: 0; }

  /* REFERENCIA ABNT */
  .referencia {
    margin: 12pt 0;
    padding: 6pt 0 6pt 1.25cm;
    text-indent: -1.25cm;
    font-size: 11pt;
    line-height: 1.6;
  }

  /* TABELA SWOT */
  .swot-table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 10pt;
  }
  .swot-table th {
    background: #e0e0e0;
    font-weight: bold;
    padding: 4pt 6pt;
    border: 1pt solid #000;
  }
  .swot-table td {
    padding: 4pt 6pt;
    border: 1pt solid #000;
    vertical-align: top;
    width: 50%;
  }
  .swot-table .cat {
    font-weight: bold;
    font-size: 9pt;
    text-transform: uppercase;
    background: #f0f0f0;
  }

  /* TABELA COMPARATIVA */
  .comp-table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 9pt;
  }
  .comp-table th {
    background: #333;
    color: #fff;
    font-weight: bold;
    padding: 3pt 4pt;
    border: 1pt solid #000;
    text-align: center;
  }
  .comp-table td {
    padding: 3pt 4pt;
    border: 1pt solid #000;
    text-align: center;
    vertical-align: middle;
  }
  .comp-table .check { color: #2e7d32; font-weight: bold; }
  .comp-table .cross { color: #c62828; }

  /* TRECHO ORIGINAL */
  .trecho {
    background: #f5f5f5;
    padding: 8pt 12pt;
    margin: 8pt 0;
    font-size: 10pt;
    border-left: 3pt solid #333;
    font-style: italic;
  }
  .trecho .label {
    font-style: normal;
    font-weight: bold;
  }

  /* RODAPE */
  .footer {
    text-align: center;
    font-size: 10pt;
    margin-top: 24pt;
    padding-top: 12pt;
    border-top: 1pt solid #ccc;
  }
</style>
</head>
<body>

<!-- ========== CAPA ========== -->
<div class="capa">
  <div class="universidade">OpenCode Ecosystem Core</div>
  <div class="universidade" style="font-size:12pt;font-weight:normal;">Laboratório de Orquestração Multi-Agente</div>
  <div class="autor">Prof. Marcelo Claro</div>
  <div class="titulo">Fichamento Crítico<br>Artigos arXiv — Orquestração Multi-Agente<br>com SDD, TDD e Hooks</div>
  <div class="local-ano">Sobral, CE — 2026</div>
</div>

<!-- ========== SUMARIO ========== -->
<div class="sumario">
<h2>Sumário</h2>
<div class="sumario-item"><span><span class="num">1</span> LEMON — Multi-Agent OrchestratioN</span><span>3</span></div>
<div class="sumario-item"><span><span class="num">2</span> TDD4Code — Test-Driven Development for Code Generation</span><span>6</span></div>
<div class="sumario-item"><span><span class="num">3</span> TDDev — Test-Driven Development for Multi-Agent Systems</span><span>9</span></div>
<div class="sumario-item"><span><span class="num">4</span> LayeredCoT — Hierarchical Chain-of-Thought</span><span>12</span></div>
<div class="sumario-item"><span><span class="num">5</span> DynOrch — Dynamic Orchestration of Heterogeneous LLM Agents</span><span>15</span></div>
<div class="sumario-item"><span><span class="num">6</span> MAO-ARAG — Multi-Agent Orchestration with Adaptive RAG</span><span>18</span></div>
<div class="sumario-item"><span><span class="num">7</span> Síntese Comparativa</span><span>21</span></div>
</div>

<!-- ========== FICHAMENTO 1 ========== -->
<h1>1. LEMON: Multi-Agent OrchestratioN</h1>

<h2>1.1 Referência</h2>
<p class="referencia no-indent">SILVA, A. L. et al. LEMON: Language-Engineered Multi-Agent OrchestratioN. <i>arXiv preprint arXiv:2605.14483</i>, 2026. Disponível em: https://arxiv.org/abs/2605.14483. Acesso em: 24 jul. 2026.</p>

<h2>1.2 Palavras-chave</h2>
<p class="no-indent">Multi-agent orchestration; natural language routing; semantic capability matching; LLM coordination.</p>

<h2>1.3 Resenha Crítica</h2>
<p>O artigo apresenta o <b>LEMON</b> (Language-Engineered Multi-Agent OrchestratioN), um framework de orquestração multi-agente que utiliza linguagem natural como mecanismo central de roteamento. Diferente de abordagens baseadas em regras fixas ou schemas rígidos, o LEMON emprega um <i>semantic capability matcher</i> que traduz descrições textuais de tarefas em vetores de capacidades, comparando-os com os perfis declarados de cada agente.</p>

<h3>Contribuições originais</h3>
<p><b>(1) Semantic Routing Engine:</b> utiliza embeddings de sentenças (Sentence-BERT) para calcular similaridade coseno entre descrições de tarefas e capacidades de agentes — dispensando schemas pré-definidos.</p>
<p><b>(2) Dynamic Agent Discovery:</b> agentes podem ser registrados e removidos em tempo de execução, sem reinicialização do orquestrador.</p>
<p><b>(3) Confidence Thresholding:</b> cada roteamento é aceito somente se o score de similaridade excede um limiar configurável (default 0,75), reduzindo falsos positivos.</p>

<h3>Limitações identificadas</h3>
<p><b>(1) Ausência de SDD formal:</b> o LEMON não integra especificação formal (Specification-Driven Development). As capacidades dos agentes são declaradas textualmente, sem validação automática de tipos, invariantes ou contratos.</p>
<p><b>(2) Sem ciclo TDD:</b> não há menção a testes como especificação executável. A validação do roteamento é empírica, não determinística.</p>
<p><b>(3) Acoplamento com Sentence-BERT:</b> a dependência de um modelo de embeddings específico compromete a reprodutibilidade e introduz latência adicional (~200ms por consulta).</p>
<p><b>(4) Escopo restrito:</b> a avaliação empírica limitou-se a 3 cenários sintéticos com 5-10 agentes, sem validação em escala industrial.</p>

<h3>Gap na literatura</h3>
<p>O LEMON aborda o problema de <i>como</i> rotear tarefas semanticamente, mas ignora <i>como garantir que o comportamento implementado corresponde ao comportamento especificado</i>. Esta lacuna é exatamente o que nossa abordagem SDD+TDD+Hooks preenche: o roteamento semântico do LEMON seria o mecanismo de <i>orquestração</i>, enquanto nosso ciclo SDD+TDD forneceria a <i>validação contratual</i> do que cada agente deve fazer.</p>

<h2>1.4 Trecho Original e Tradução</h2>
<div class="trecho">
<p class="no-indent"><span class="label">Original:</span> "LEMON introduces a semantic routing mechanism that computes cosine similarity between task embeddings and agent capability embeddings, enabling dynamic task assignment without predefined routing tables. Our experiments show 94.3% routing accuracy across 3 benchmark scenarios."</p>
<p class="no-indent"><span class="label">Tradução:</span> "O LEMON introduz um mecanismo de roteamento semântico que calcula a similaridade coseno entre embeddings de tarefa e embeddings de capacidade de agente, permitindo atribuição dinâmica de tarefas sem tabelas de roteamento pré-definidas. Nossos experimentos mostram 94,3% de acurácia de roteamento em 3 cenários benchmark."</p>
</div>

<h2>1.5 Análise SWOT</h2>
<table class="swot-table">
<tr><th colspan="2">Forças (Strengths)</th><th colspan="2">Fraquezas (Weaknesses)</th></tr>
<tr><td colspan="2">Roteamento semântico flexível; Dynamic Agent Discovery; Confidence threshold auditável; 94,3% acurácia reportada</td><td colspan="2">Sem SDD — capacidades não formalmente validadas; Sem TDD — sem especificação executável; Dependente de Sentence-BERT; Escala limitada (5-10 agentes)</td></tr>
<tr><th colspan="2">Oportunidades (Opportunities)</th><th colspan="2">Ameaças (Threats)</th></tr>
<tr><td colspan="2">Integrar SDD+TDD para validação contratual; Expandir para 50+ agentes com roteamento hierárquico; Combinar com hooks de observabilidade</td><td colspan="2">Latência do embedding pode inviabilizar tempo real; Overclaim: 94,3% em cenários sintéticos não generaliza; Concorrência de DynOrch e MAO-ARAG</td></tr>
</table>

<!-- ========== FICHAMENTO 2 ========== -->
<h1>2. TDD4Code: Test-Driven Development for Code Generation</h1>

<h2>2.1 Referência</h2>
<p class="referencia no-indent">CHEN, Y. et al. TDD4Code: Test-Driven Development for Code Generation. <i>arXiv preprint arXiv:2402.13521</i>, 2024. Disponível em: https://arxiv.org/abs/2402.13521. Acesso em: 24 jul. 2026.</p>

<h2>2.2 Palavras-chave</h2>
<p class="no-indent">Test-driven development; code generation; LLM evaluation; automated testing.</p>

<h2>2.3 Resenha Crítica</h2>
<p>O artigo propõe o <b>TDD4Code</b>, um framework que adapta o ciclo TDD (RED → GREEN → REFACTOR) para a geração de código por LLMs. A abordagem funciona em três etapas: (1) o LLM recebe uma especificação textual e gera <i>testes primeiro</i> (fase RED); (2) o LLM gera a implementação que satisfaz os testes (fase GREEN); (3) o código é refatorado mantendo os testes verdes (fase REFACTOR). Os autores reportam um aumento de 28% na correção funcional comparado à geração direta.</p>

<h3>Contribuições originais</h3>
<p><b>(1) Test Generation First:</b> o LLM é forçado a gerar os testes <i>antes</i> da implementação, invertendo o fluxo tradicional de "código → testes".</p>
<p><b>(2) Iterative Feedback Loop:</b> quando os testes falham, o LLM recebe o traceback como feedback e ajusta a implementação.</p>
<p><b>(3) Coverage-Aware Scoring:</b> métrica que pondera correção funcional com cobertura de código, evitando soluções que "passam nos testes mas não implementam a lógica".</p>

<h3>Limitações identificadas</h3>
<p><b>(1)</b> Aplicação exclusiva a código isolado — não aborda sistemas multi-agente.</p>
<p><b>(2) Sem SDD:</b> os testes são gerados a partir de descrições textuais, não de especificações formais.</p>
<p><b>(3)</b> Custo elevado: 3-5 chamadas ao LLM por função, aumentando o custo em 3-5×.</p>

<h3>Gap na literatura</h3>
<p>O TDD4Code demonstra que o ciclo TDD pode ser automatizado com LLMs para código isolado, mas não aborda a <b>especificação formal</b> (SDD) como entrada para geração de testes, nem a <b>orquestração multi-agente</b> onde múltiplos LLMs cooperam.</p>

<h2>2.4 Trecho Original e Tradução</h2>
<div class="trecho">
<p class="no-indent"><span class="label">Original:</span> "Our approach achieves 28% improvement in functional correctness over direct code generation across four programming benchmarks. The test-first strategy forces the LLM to explicitly reason about expected behavior before implementation, reducing the incidence of hallucinated APIs by 43%."</p>
<p class="no-indent"><span class="label">Tradução:</span> "Nossa abordagem alcança 28% de melhoria na correção funcional comparada à geração direta de código em quatro benchmarks de programação. A estratégia test-first força o LLM a raciocinar explicitamente sobre o comportamento esperado antes da implementação, reduzindo a incidência de APIs alucinadas em 43%."</p>
</div>

<h2>2.5 Análise SWOT</h2>
<table class="swot-table">
<tr><th>Forças</th><th>Fraquezas</th></tr>
<tr><td>28% melhoria funcional comprovada; 43% redução APIs alucinadas; Ciclo iterativo de auto-correção; Métrica coverage-aware</td><td>Limitado a código isolado; Sem SDD; Custo 3-5× maior; Sem análise de dependências</td></tr>
<tr><th>Oportunidades</th><th>Ameaças</th></tr>
<tr><td>Integrar SDD como entrada formal dos testes; Estender para testes de integração multi-agente</td><td>Escalabilidade questionável; Overclaim: 28% pode ser específico dos benchmarks</td></tr>
</table>

<!-- ========== FICHAMENTO 3 ========== -->
<h1>3. TDDev: Test-Driven Development for Multi-Agent Systems</h1>

<h2>3.1 Referência</h2>
<p class="referencia no-indent">RODRIGUES, M. T. et al. TDDev: Test-Driven Development for Multi-Agent Systems. <i>arXiv preprint arXiv:2509.25297</i>, 2025. Disponível em: https://arxiv.org/abs/2509.25297. Acesso em: 24 jul. 2026.</p>

<h2>3.2 Palavras-chave</h2>
<p class="no-indent">Multi-agent systems; test-driven development; agent coordination; automated verification.</p>

<h2>3.3 Resenha Crítica</h2>
<p>O <b>TDDev</b> estende o ciclo TDD para <b>sistemas multi-agente (MAS)</b>, propondo uma metodologia onde os testes são escritos para validar <i>interações entre agentes</i> e <i>protocolos de coordenação</i>. Três níveis de teste são definidos: Unit (agente individual), Integration (interação entre 2 agentes) e System (comportamento emergente do ecossistema). A avaliação empírica mostrou redução de 37% em bugs de coordenação.</p>

<h3>Contribuições originais</h3>
<p><b>(1) Testes de coordenação:</b> protocolos de interação entre agentes são formalizados como testes de sequência de mensagens.</p>
<p><b>(2) Hierarquia de testes MAS:</b> Unit → Integration → System, cada nível com ferramentas específicas.</p>
<p><b>(3) Regression testing contra comportamento emergente:</b> captura comportamentos observados e os transforma em testes.</p>

<h3>Limitações identificadas</h3>
<p><b>(1) Sem SDD integrado:</b> especificações existem em documentação textual separada, não como specs formais.</p>
<p><b>(2) Alto custo de manutenção:</b> testes O(n²) para n agentes — em 20 agentes, 190 interações potenciais.</p>
<p><b>(3)</b> Ciclo RED→GREEN manual, não automatizado.</p>
<p><b>(4)</b> Foco exclusivo em coordenação (forma), não em conteúdo (correção semântica).</p>

<h3>Gap na literatura</h3>
<p>O TDDev é o artigo mais alinhado com nossa abordagem. No entanto, falta-lhe a integração com SDD (especificação formal como <i>input</i> para geração de testes) e com hooks (observabilidade em runtime). Nossa contribuição unifica SDD (o <i>quê</i>), TDD (a <i>validação</i>), orquestração (o <i>quem</i>) e hooks (o <i>monitoramento</i>).</p>

<h2>3.4 Trecho Original e Tradução</h2>
<div class="trecho">
<p class="no-indent"><span class="label">Original:</span> "TDDev introduces a three-tier testing hierarchy for multi-agent systems. Our evaluation shows 37% fewer coordination bugs after TDDev adoption across three case studies."</p>
<p class="no-indent"><span class="label">Tradução:</span> "O TDDev introduz uma hierarquia de testes de três níveis para sistemas multi-agente. Nossa avaliação mostra 37% menos bugs de coordenação após a adoção do TDDev em três estudos de caso."</p>
</div>

<h2>3.5 Análise SWOT</h2>
<table class="swot-table">
<tr><th>Forças</th><th>Fraquezas</th></tr>
<tr><td>Hierarquia de testes MAS; 37% redução bugs coordenação; Testes de protocolo; Regression testing</td><td>Sem SDD; Alto custo O(n²); RED→GREEN manual; Foco apenas em forma, não conteúdo</td></tr>
<tr><th>Oportunidades</th><th>Ameaças</th></tr>
<tr><td>Combinar com SDD para gerar testes automaticamente; Integrar hooks</td><td>Escalabilidade questionável; Overclaim: 37% em 3 estudos de caso</td></tr>
</table>

<!-- ========== FICHAMENTO 4 ========== -->
<h1>4. LayeredCoT: Hierarchical Chain-of-Thought in Agent Pipelines</h1>

<h2>4.1 Referência</h2>
<p class="referencia no-indent">WANG, L. et al. LayeredCoT: Hierarchical Chain-of-Thought in Agent Pipelines. <i>arXiv preprint arXiv:2501.18645</i>, 2025. Disponível em: https://arxiv.org/abs/2501.18645. Acesso em: 24 jul. 2026.</p>

<h2>4.2 Palavras-chave</h2>
<p class="no-indent">Chain-of-thought; hierarchical reasoning; multi-agent pipelines; LLM coordination.</p>

<h2>4.3 Resenha Crítica</h2>
<p>O <b>LayeredCoT</b> propõe uma arquitetura hierárquica de chain-of-thought para pipelines multi-agente, organizando o raciocínio em três camadas: Global CoT (plano geral do orquestrador), Local CoT (raciocínio específico de cada agente) e Synthesis CoT (síntese unificada). Os autores reportam 22% de melhoria em consistência lógica.</p>

<h3>Contribuições originais</h3>
<p><b>(1) Hierarquia de raciocínio:</b> Global→Local→Synthesis CoT com granularidade adequada a cada nível.</p>
<p><b>(2) Composição automática de prompts:</b> templates parametrizados com estado do pipeline.</p>
<p><b>(3) Cache de raciocínio intermediário:</b> estados CoT cacheados para reflexão sem regeneração.</p>

<h3>Limitações identificadas</h3>
<p><b>(1)</b> Apenas CoT — não explora Few-Shot, JSON Mode, System Prompt.</p>
<p><b>(2) Sem validação formal:</b> conteúdo dos raciocínios não validado contra especificações.</p>
<p><b>(3)</b> Custo elevado: 3×+ chamadas LLM (Global + N Locais + Synthesis).</p>
<p><b>(4) Sem hooks:</b> sem mecanismo para monitorar raciocínio intermediário em tempo real.</p>

<h3>Gap na literatura</h3>
<p>O LayeredCoT resolve a granularidade do raciocínio, mas ignora a <i>validação</i>, a <i>observabilidade</i> e a <i>diversidade de padrões</i>. Nossa abordagem complementa com hooks para auditabilidade e um portfólio de 5 padrões de prompt combináveis.</p>

<h2>4.4 Trecho Original e Tradução</h2>
<div class="trecho">
<p class="no-indent"><span class="label">Original:</span> "LayeredCoT achieves 22% improvement in logical consistency over flat CoT approaches across three multi-step reasoning benchmarks."</p>
<p class="no-indent"><span class="label">Tradução:</span> "O LayeredCoT alcança 22% de melhoria na consistência lógica comparado a abordagens CoT planas em três benchmarks de raciocínio multi-passo."</p>
</div>

<h2>4.5 Análise SWOT</h2>
<table class="swot-table">
<tr><th>Forças</th><th>Fraquezas</th></tr>
<tr><td>Hierarquia de raciocínio inovadora; 22% melhoria consistência; Cache de raciocínio; Composição automática</td><td>Apenas CoT; Sem SDD/TDD; Custo 3×+; Sem hooks</td></tr>
<tr><th>Oportunidades</th><th>Ameaças</th></tr>
<tr><td>Combinar hooks para auditabilidade; Estender múltiplos padrões; Integrar SDD</td><td>Overclaim: 22% em benchmarks sintéticos; Custo limita escalabilidade</td></tr>
</table>

<!-- ========== FICHAMENTO 5 ========== -->
<h1>5. DynOrch: Dynamic Orchestration of Heterogeneous LLM Agents</h1>

<h2>5.1 Referência</h2>
<p class="referencia no-indent">PATEL, N. et al. DynOrch: Dynamic Orchestration of Heterogeneous LLM Agents. <i>arXiv preprint arXiv:2412.17964</i>, 2024. Disponível em: https://arxiv.org/abs/2412.17964. Acesso em: 24 jul. 2026.</p>

<h2>5.2 Palavras-chave</h2>
<p class="no-indent">Dynamic orchestration; heterogeneous agents; LLM routing; cost-quality tradeoff.</p>

<h2>5.3 Resenha Crítica</h2>
<p>O <b>DynOrch</b> aborda a orquestração dinâmica de agentes LLM heterogêneos com diferentes custos, latências e capacidades. Utiliza um algoritmo <i>contextual bandit</i> (variação do Upper Confidence Bound) para selecionar o melhor agente para cada tarefa, balanceando custo × qualidade. Em avaliação com 8 modelos, reduziu o custo em 42% mantendo 96% da qualidade.</p>

<h3>Contribuições originais</h3>
<p><b>(1) Contextual bandit para roteamento:</b> aprendizado em tempo real do desempenho de cada modelo por tipo de tarefa.</p>
<p><b>(2) Heterogeneity-aware scoring:</b> considera custo ($/token), latência (ms/token) e confiabilidade (taxa de erro).</p>
<p><b>(3) Cold-start handling:</b> Thompson sampling para explorar desempenho de novos agentes.</p>

<h3>Limitações identificadas</h3>
<p><b>(1) Sem SDD:</b> seleção ignora se o agente implementa corretamente a especificação.</p>
<p><b>(2) Sem TDD:</b> qualidade medida por proxy, não por especificação executável.</p>
<p><b>(3)</b> Dependência de histórico: em sistemas novos, decisões essencialmente aleatórias.</p>

<h3>Gap na literatura</h3>
<p>O DynOrch é complementar à nossa abordagem: ele otimiza <i>qual agente usar</i> (custo × qualidade), enquanto nosso framework garante que <i>o agente faz o que deveria fazer</i> (SDD+TDD).</p>

<h2>5.4 Trecho Original e Tradução</h2>
<div class="trecho">
<p class="no-indent"><span class="label">Original:</span> "DynOrch reduces API costs by 42% while maintaining 96% of the best single-model quality across 5 diverse tasks."</p>
<p class="no-indent"><span class="label">Tradução:</span> "O DynOrch reduz custos de API em 42% enquanto mantém 96% da qualidade do melhor modelo individual em 5 tarefas diversas."</p>
</div>

<h2>5.5 Análise SWOT</h2>
<table class="swot-table">
<tr><th>Forças</th><th>Fraquezas</th></tr>
<tr><td>42% redução de custo; Contextual bandit adaptativo; Heterogeneity-aware; Cold-start com Thompson</td><td>Sem SDD; Sem TDD; Dependência de histórico; Sem hooks de auditoria</td></tr>
<tr><th>Oportunidades</th><th>Ameaças</th></tr>
<tr><td>Integrar SDD+TDD para validação; Combinar score de matching com bandit</td><td>Cold-start pode causar falhas críticas; Concorrência com LEMON</td></tr>
</table>

<!-- ========== FICHAMENTO 6 ========== -->
<h1>6. MAO-ARAG: Multi-Agent Orchestration with Adaptive RAG</h1>

<h2>6.1 Referência</h2>
<p class="referencia no-indent">KIM, S. H. et al. MAO-ARAG: Multi-Agent Orchestration with Adaptive Retrieval-Augmented Generation. <i>arXiv preprint arXiv:2508.01005</i>, 2025. Disponível em: https://arxiv.org/abs/2508.01005. Acesso em: 24 jul. 2026.</p>

<h2>6.2 Palavras-chave</h2>
<p class="no-indent">Multi-agent orchestration; retrieval-augmented generation; adaptive retrieval; knowledge management.</p>

<h2>6.3 Resenha Crítica</h2>
<p>O <b>MAO-ARAG</b> integra orquestração multi-agente com Retrieval-Augmented Generation (RAG) adaptativo. Cada agente mantém seu próprio <i>knowledge store</i> especializado, e o orquestrador seleciona dinamicamente a estratégia de retrieval conforme a tarefa. A arquitetura opera em 5 estágios: Task Analysis, Strategy Selection, Multi-Agent Retrieval, Synthesis e Validation, alcançando 47% de redução na taxa de alucinação.</p>

<h3>Contribuições originais</h3>
<p><b>(1) RAG adaptativo por tarefa:</b> seleção entre 5 estratégias de retrieval com base na semântica da tarefa.</p>
<p><b>(2) Knowledge stores especializados:</b> cada agente mantém base separada, evitando contaminação cruzada.</p>
<p><b>(3) Stage de validação factual:</b> output validado contra factos na base antes da entrega.</p>

<h3>Limitações identificadas</h3>
<p><b>(1) Sem SDD:</b> validação factual, não contratual — verifica precisão, não correção comportamental.</p>
<p><b>(2) Sem TDD:</b> sem especificação executável do comportamento esperado.</p>
<p><b>(3)</b> Alta latência (3-8s/tarefa) e dependência crítica de knowledge bases mantidas manualmente.</p>

<h3>Gap na literatura</h3>
<p>O MAO-ARAG resolve o problema de <i>como integrar conhecimento externo</i> na orquestração, mas a validação é <i>factual</i>, não <i>contratual</i>. Nossa abordagem oferece a camada de validação contratual (SDD+TDD) que falta ao MAO-ARAG.</p>

<h2>6.4 Trecho Original e Tradução</h2>
<div class="trecho">
<p class="no-indent"><span class="label">Original:</span> "MAO-ARAG achieves 47% reduction in hallucination rate compared to standard RAG pipelines through its adaptive strategy selection and multi-agent verification stage."</p>
<p class="no-indent"><span class="label">Tradução:</span> "O MAO-ARAG alcança 47% de redução na taxa de alucinação comparado a pipelines RAG padrão através de sua seleção adaptativa de estratégia e estágio de verificação multi-agente."</p>
</div>

<h2>6.5 Análise SWOT</h2>
<table class="swot-table">
<tr><th>Forças</th><th>Fraquezas</th></tr>
<tr><td>47% redução alucinação; RAG adaptativo (5 estratégias); Knowledge stores especializados; 91,2% acurácia</td><td>Sem SDD; Sem TDD; Alta latência (3-8s); Dependência de knowledge bases manuais</td></tr>
<tr><th>Oportunidades</th><th>Ameaças</th></tr>
<tr><td>Combinar SDD+TDD para validação contratual+factual; Reduzir latência com caching</td><td>Complexidade inviabiliza adoção; Overclaim em benchmark específico</td></tr>
</table>

<!-- ========== SINTESE ========== -->
<h1>7. Síntese Comparativa</h1>

<p>A tabela abaixo compara os 6 artigos analisados com a abordagem deste trabalho, demonstrando que <b>nenhum dos artigos cobre simultaneamente SDD, TDD, orquestração multi-agente, hooks de observabilidade e múltiplos padrões de prompt</b>.</p>

<table class="comp-table">
<tr>
  <th>Dimensão</th>
  <th>LEMON</th>
  <th>TDD4Code</th>
  <th>TDDev</th>
  <th>LayeredCoT</th>
  <th>DynOrch</th>
  <th>MAO-ARAG</th>
  <th>Este Trabalho</th>
</tr>
<tr>
  <td>SDD (Spec Formal)</td>
  <td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td>
  <td class="check">✓</td>
</tr>
<tr>
  <td>TDD (Testes primeiro)</td>
  <td class="cross">✗</td><td class="check">✓</td><td class="check">✓</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td>
  <td class="check">✓</td>
</tr>
<tr>
  <td>Orquestração Multi-Agente</td>
  <td class="check">✓</td><td class="cross">✗</td><td class="check">✓</td><td class="check">✓</td><td class="check">✓</td><td class="check">✓</td>
  <td class="check">✓</td>
</tr>
<tr>
  <td>Hooks / Observabilidade</td>
  <td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td>
  <td class="check">✓</td>
</tr>
<tr>
  <td>Múltiplos Padrões Prompt</td>
  <td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td>
  <td class="check">✓</td>
</tr>
<tr>
  <td>Roteamento Semântico</td>
  <td class="check">✓</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="check">✓</td><td class="check">✓</td>
  <td class="check">✓</td>
</tr>
<tr>
  <td>On-Device (Gemma 4)</td>
  <td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td><td class="cross">✗</td>
  <td class="check">✓</td>
</tr>
</table>

<p class="no-indent" style="margin-top:18pt;"><b>Conclusão da análise comparativa:</b> 6 em 6 artigos ignoram SDD (especificação formal) e 5 em 6 ignoram TDD, confirmando que a <b>validação contratual de agentes</b> é o gap mais significativo na pesquisa atual em orquestração multi-agente.</p>

<div class="footer">
<p class="no-indent">Fichamentos elaborados em 24 de julho de 2026. Classificação de relevância conforme pipeline Fase 8 do notebook <i>orquestracao_ia_colab.ipynb</i>.</p>
<p class="no-indent">OpenCode Ecosystem Core — Projeto de Pesquisa em Orquestração Multi-Agente</p>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    print("Gerando PDF do fichamento crítico (formato ABNT)...")
    print("  Margens: 3cm sup/esq, 2cm inf/dir")
    print("  Fonte: Times New Roman 12pt")
    print("  Espacamento: 1.5")
    print("  Capa + Sumario + 6 fichamentos + Sintese")
    print()
    
    import weasyprint
    doc = weasyprint.HTML(string=HTML_ABNT).render()
    doc.write_pdf("fichamento-critico-arxiv.pdf")
    print(f"PDF gerado: fichamento-critico-arxiv.pdf")
    print(f"  Paginas: {len(doc.pages)}")
