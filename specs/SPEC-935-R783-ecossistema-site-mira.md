---
spec_id: SPEC-935-R783
title: Apresentação acessível do OpenCode Ecosystem Core no site MIRA
component: artigos/pucrs-roteamento-atencao/site
status: implemented
round_id: R783
test_file: tests/test_r783_ecossistema_site.py
---

# SPEC-935-R783 — O ecossistema e a pesquisa

## Objetivo

Apresentar o OpenCode Ecosystem Core no site existente de forma dinâmica, acessível e coerente com o desenho profissional, explicando sua relação com a dissertação e com o MIRA. Publicar no GitHub Pages já autorizado.

## Requisitos

1. Nova seção identificável na navegação e no modo de apresentação. Definição simples: projeto que organiza agentes de software, ferramentas e registros de tarefas.
2. Percurso ilustrativo em quatro etapas: pedido, coordenação, roteador, execução/registro. Navegação direta, anterior, próxima e reinício, com destaque visual e texto atualizado. A etapa de execução deve expressar disponibilidade/configuração como condição, sem fabricar uma execução ou resultado.
3. Três perspectivas interativas distintas: ecossistema completo, roteador investigado e MIRA/comunicação. Trocar a perspectiva não cria uma quinta etapa nem executa agentes. A dissertação cobre propriedades matemáticas e situações simuladas; a conformidade MIRA avalia o artefato de apresentação.
4. O roteiro inicia na etapa zero e perspectiva ecosystem. Estado puro com step inteiro de 0 a 3 e scope em ecosystem/research/mira. Exportar createTourState(), transitionTour(state, action) e getTourView(state) em ecosystem.mjs. Ações next/previous saturam nos limites; restart restaura o início; step/scope selecionam valores válidos; dados inválidos são rejeitados. View informa passo, perspectiva, canPrevious/canNext e isResearchStep. Nenhum temporizador nem execução real no módulo.
5. Preservar palette, fontes, laboratório e atividades existentes. Foco visível, botões operáveis por teclado, feedback aria-live, títulos/legendas significativos, contraste legível e celular sem rolagem horizontal. Animação de percurso pausável pelo controle existente e desativada em movimento reduzido. Avanço do texto sempre sob controle da pessoa.
6. Atualizar o manuscrito MIRA e gerar o deck complementar pelo MarceloClaroOrchestrator.present_task, conservando proveniência e relatório de conformidade original. Mostrar MIRA como recurso de comunicação, sem presumir que todos os encaminhamentos utilizam o roteador estudado.
7. Publicar fontes na main e atualizar codex/gh-pages com ancestral preservado e sem exclusões externas. Recursos públicos vinculados à revisão para evitar versões antigas no cache. Registrar evolução e QA interno.

## Critérios de aceite

- Testes comportamentais do percurso: navegação, limites, seleção de perspectiva independente da etapa, reinício, dados inválidos, indicação da peça estudada e conteúdo condicionado da execução.
- Conferência em navegador: etapas e perspectivas, teclado, pausa, nova seção na apresentação, links para laboratório/MIRA, regressão básica das atividades e layout de computador/celular.
- Execução real do gerador MIRA e conferência dos arquivos após implantação.

## Limites

A ilustração representa a organização do projeto. Não demonstra execução real de agentes, validade do ecossistema completo, eficácia educacional medida ou novos resultados da dissertação. Não alterar fonte científica, números ou cálculo do roteador.
