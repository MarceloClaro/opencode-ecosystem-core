<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Protocolo de Citações Auditáveis de Alta Densidade (PHD-Level)

Este protocolo define o padrão obrigatório para todas as citações e referências utilizadas na produção de artigos científicos, teses e dissertações pelo `criador-de-artigo-v2` (MASWOS V4.1 Enhanced).

O objetivo é garantir a máxima rastreabilidade, verificabilidade e profundidade analítica de cada fonte citada, superando os requisitos Qualis A1 e padrões internacionais de rigor acadêmico.

## 1. Estrutura da Nota de Rodapé (Obrigatória para Citações Diretas e Indiretas)

Cada nota de rodapé deve seguir o formato abaixo, contendo todos os elementos especificados:

```
[Número da Citação] SOBRENOME, Nome. Título do Artigo/Livro. Revista/Editora, Volume(Número): Páginas, Ano. DOI: [Link DOI Completo].

**Trecho Original:** "[Trecho exato da citação no idioma original]"

**Tradução (se aplicável):** "[Tradução fiel do trecho original para o português brasileiro]"

**Fichamento Crítico Contextualizado:**

Este trecho é relevante para o parágrafo atual porque [justificativa detalhada da pertinência da citação ao argumento desenvolvido no parágrafo específico]. A citação [apoia/contradiz/complementa] a ideia de [ideia principal do parágrafo], fornecendo [evidência/perspectiva/dado] que [explica/aprofundar/questiona] [conceito ou afirmação específica]. A inclusão desta referência é crucial para [impacto no estudo, por exemplo: validar a metodologia, fundamentar a discussão teórica, apresentar um contraponto, etc.].
```

### Exemplo de Nota de Rodapé:

```
[1] SILVA, João. A Complexidade dos Sistemas Multiagentes. Journal of Agentic Computing, 15(2): 112-125, 2023. DOI: https://doi.org/10.1234/jac.2023.12345.

**Trecho Original:** "The inherent complexity of multi-agent systems often stems from emergent behaviors that are difficult to predict and control, necessitating robust orchestration mechanisms."

**Tradução:** "A complexidade inerente aos sistemas multiagentes frequentemente decorre de comportamentos emergentes que são difíceis de prever e controlar, necessitando de mecanismos de orquestração robustos."

**Fichamento Crítico Contextualizado:**

Este trecho é relevante para o parágrafo atual porque fundamenta a discussão sobre a necessidade de mecanismos de orquestração avançados em arquiteturas multiagentes, como o Nexus-Multiagents-v6. A citação apoia a ideia de que a imprevisibilidade dos comportamentos emergentes exige um "harness" robusto para garantir a estabilidade e a eficácia do sistema. A inclusão desta referência é crucial para validar a premissa de que a engenharia de sistemas multiagentes não pode se basear apenas em componentes isolados, mas requer uma visão holística de controle e sincronização.
```

## 2. Requisitos para o DOI (Digital Object Identifier)

*   **Obrigatório**: Todo material citável (artigos, capítulos de livros, anais de congresso) deve possuir um DOI válido e acessível.
*   **Verificação**: O agente deve verificar a validade do DOI e a acessibilidade do recurso antes de incluí-lo.
*   **Prioridade**: Em caso de múltiplas versões de um documento, priorizar a versão com DOI mais estável (geralmente a versão final publicada).

## 3. Fichamento Crítico Contextualizado

*   **Profundidade Analítica**: O fichamento não é um resumo, mas uma análise crítica da relevância do trecho para o *ponto específico* do parágrafo onde a citação é inserida.
*   **Conexão Explícita**: Deve haver uma conexão clara e explícita entre o conteúdo da citação e o argumento desenvolvido no texto.
*   **Justificativa**: Justificar *por que* aquela citação é a melhor escolha para apoiar ou discutir o ponto em questão, em vez de outras possíveis referências.
*   **Evitar Redundância**: O fichamento deve agregar valor e não repetir o que já foi dito no parágrafo ou na própria citação.

## 4. Integração com o Loop de Correção Ativa (MASWOS V4.1)

*   **Agentes de Validação (A13/A14)**: Serão responsáveis por auditar cada nota de rodapé, garantindo a conformidade com este protocolo.
*   **Módulos de Correção (A44/A45)**: Em caso de não conformidade, os módulos de correção serão ativados para solicitar a revisão ou aprofundamento do fichamento, ou a busca por um DOI válido.
*   **Feedback Evolutivo**: O sistema aprenderá com as correções, otimizando a seleção e o fichamento de citações ao longo do tempo.

Este protocolo eleva o padrão de qualidade das produções acadêmicas, garantindo que cada citação seja uma peça fundamental e auditável na construção do conhecimento.
