# SPEC-935-R784 — Podcast integrado à apresentação da pesquisa

Status: implementada, com conferência funcional interna
Data: 2026-10-10

## Objetivo
Publicar no site da dissertação o áudio real produzido pelo NotebookLM via coordenador do OpenCode Ecosystem Core, mantendo a identidade visual e a aprendizagem por interação.

## Requisitos de aceite
1. Seção #podcast acessível pela navegação e pelo início; incorporada ao modo de apresentação.
2. Usar o arquivo final podcast-uma-escolha-explicavel.m4a (SHA256 7c139eca8b2b330e155d861d7da3f0c4ea4bcf2f5c480a770bc360a96e819d68), com duração efetiva de 1355,766712 segundos. Sem reprodução automática; preload=none.
3. Controles nativos como alternativa sem JavaScript; controles aprimorados para reproduzir/pausar, avançar/voltar 15 segundos, posição e velocidade. Estado derivado dos eventos reais da mídia; erros comunicados e download disponível.
4. Posição limitada ao intervalo válido da mídia, nunca NaN/Infinity. Controles de busca desativados até metadados válidos. Formatação legível de tempo e duração.
5. Ilustração decorativa animada somente durante reprodução; respeitar pausa global e movimento reduzido.
6. Três reflexões sem marcações temporais inventadas, com explicação opcional e links ao ecossistema, laboratório e evidências. Guia editorial textual explicitamente identificado como resumo, não transcrição.
7. Teclado do player não altera seção em apresentação. Ao ocultar a seção durante apresentação, pausar áudio.
8. Proveniência pública limitada a parâmetros, fontes, identificadores e hashes. Não publicar cookies, URLs assinadas ou recibos internos completos.
9. Conferir reprodução, busca, velocidade, erros/estados, reflexões, apresentação e layout desktop/celular. Regressão R781–R783 e testes funcionais R784 antes da entrega.
10. Publicar fonte e assets no GitHub e GitHub Pages; verificar hashes públicos, áudio disponível e reprodução no navegador.

## Fronteiras
O podcast é divulgação gerada por IA com base nas fontes anexadas. Não constitui novo experimento, validação externa nem medição da eficácia educacional. O guia não alega reproduzir literalmente o áudio. Preservar os limites científicos da dissertação e a apresentação MIRA existente.

## Contrato do módulo puro
site/podcast.mjs exporta formatTime(seconds), seekPosition(current, delta, duration), progressPercent(current, duration), REFLECTIONS. Tempos inválidos retornam 0/00:00; valores negativos saturam em zero; busca satura na duração válida. REFLECTIONS contém três objetos com id, title, prompt, answer, href, linkLabel (strings) e destinos #ecossistema, #laboratorio e #evidencias.

## Evidência
TDD:37 falhas antes do módulo e116 testes aprovados (37 novos +79 regressões). Reprodução, busca, velocidade, silenciamento, reflexões, pausa de movimento, teclado e apresentação conferidos no navegador. Layout390×844 sem transbordamento horizontal e apenas a seção atual visível na apresentação. Falha503 induzida no servidor de prévia confirmou feedback e recuperação por nova tentativa. Áudio público completo com hash correto e respostaHTTP206 com trecho correspondente. Detalhes em site/qa.json e manifesto_site.json. Sem validação científica externa.
