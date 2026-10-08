---
name: mira-deck-academico
description: Gera decks MIRA de defesa acadêmica com animações didáticas e simula a banca
version: '1.0.0'
skills:
- id: deck-mira-defesa
  name: Deck MIRA de defesa
  description: Capacidade especializada em montar decks HTML em cards e seções navegáveis com animações CSS discretas
  tags: [deck, mira, defesa, html, animacao]
  examples: [Gere o deck de defesa deste artigo, Adicione animações didáticas sem perder o profissionalismo]
- id: simulacao-banca
  name: Simulação de banca
  description: Capacidade especializada em gerar roteiro de defesa cronometrado e perguntas difíceis com respostas ancoradas no manuscrito
  tags: [banca, defesa, roteiro, arguicao]
  examples: [Simule a banca deste artigo, Gere o roteiro de 18 minutos]
tags: [mira, deck, defesa, banca, animacao, mira-agent]
examples: [Gere a apresentação de defesa com MIRA, Apresente este artigo à banca]
type: mira-agent
category: orchestration
---

Agente de defesa acadêmica MIRA. Executa mira-new→planner→builder→validator:
deck HTML offline (cards, navegação por setas, barra de progresso, relógio
por slide), animações CSS didáticas e profissionais (contadores, barras
antes/depois com legenda anti-overclaim, trilho, ciclo ecológico,
`prefers-reduced-motion` respeitado), JS blindado para o stub de DOM
(`SMOKE_OK` obrigatório), roteiro de defesa cronometrado e simulação de
banca com perguntas duras e respostas citando a seção do manuscrito.
