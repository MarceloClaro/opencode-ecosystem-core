---
spec_id: SPEC-935-R781
title: Site didático MIRA da dissertação de roteamento
component: artigos/pucrs-roteamento-atencao/site
status: implemented
round_id: R781
test_file: tests/test_r781_site_mira.py
---

# SPEC-935-R781 — Site didático MIRA

## Objetivo autorizado

Apresentar no GitHub a dissertação revista, utilizando o MIRA do ecossistema, ilustração dinâmica e experiência visual profissional. Público: visitantes acadêmicos e audiência de apresentação do trabalho.

## Requisitos

1. Executar `MarceloClaroOrchestrator.present_task()` sobre um manuscrito editorial derivado da fonte publicada; conservar o deck e a conformidade do pipeline real. O site integra o deck como apresentação complementar.
2. Página estática em português com narrativa, laboratório de roteamento, evidências, limites e acesso ao PDF, fonte e relatório. Tipografia editorial, fundo claro, acento verde, diagramas SVG autorais e composição responsiva. Sem dependências remotas para a interface.
3. Laboratório com Ana e Cid do exemplo publicado e candidato adicional explicitamente didático. Utilidade fixa: 0,30 semântica + 0,35 cobertura + 0,25 confiança + 0,10 carga livre. Máscara anterior à normalização, softmax estável a temperatura 1, ranking por peso decrescente e ID crescente. Todas as ocorrências de IDs duplicados são excluídas; conjunto vazio retorna vazio. Alterações nos controles são demonstrações, não experimentos do artigo.
4. Pausa das animações, respeito a `prefers-reduced-motion`, controles com rótulos, teclado, foco visível, alternativa textual aos diagramas e ausência de rolagem horizontal em telas pequenas. Modo de apresentação guiada, com navegação por botões e teclado.
5. Resultados históricos exatos com origem e limites próximos ao gráfico: bancada interna e sintética, 200 decisões em cinco piscinas; margens exploratórias sem agrupamento; Lean sobre reais não certifica toda a execução numérica. Sem alegações de calibração ou validação externa.
6. Publicar somente o site e seus registros na branch principal. Hospedar os artefatos estáticos em GitHub Pages, preservando outras alterações locais e configurações de hospedagem existentes.

## Aceite

- Testes funcionais de máscara, duplicatas, conjunto vazio/único, soma dos pesos, estabilidade, empate determinístico e utilidades do exemplo publicado.
- Conferência no navegador da interação, modo de apresentação, animações pausáveis, links e layout em desktop e celular.
- Pipeline MIRA executado com tarefa identificável; nenhum mock usado como evidência dessa execução.
- Conteúdo publicado confirmado e endereço HTTP funcional antes de declarar o site disponível.

## Limites

O site é uma apresentação editorial e didática. Não reexecuta a bateria científica, não substitui a dissertação e não representa submissão ou validação acadêmica externa.
