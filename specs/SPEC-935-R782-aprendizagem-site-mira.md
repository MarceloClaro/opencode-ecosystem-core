---
spec_id: SPEC-935-R782
title: Explicação para leigos e aprendizagem interativa no site MIRA
component: artigos/pucrs-roteamento-atencao/site
status: implemented
round_id: R782
test_file: tests/test_r782_aprendizagem_site.py
---

# SPEC-935-R782 — Aprendizagem interativa

## Objetivo

Tornar o site existente mais didático para leigos e interativo, preservando o projeto visual profissional e a precisão científica. Manter o endereço e a hospedagem já autorizados.

## Requisitos

1. Explicar agente como programa especializado e roteamento como encaminhamento. Introduzir uma analogia de equipe explicitamente didática, com quatro etapas navegáveis: pedido, disponibilidade, comparação e escolha.
2. Traduzir critérios em perguntas cotidianas antes dos termos técnicos. Manter fórmulas e pormenores em expansão opcional. Incluir glossário acessível e explicação leiga dos resultados.
3. Laboratório com três desafios, pistas opcionais e feedback baseado no cálculo real: fazer Cid vencer sem excluir Ana; deixar Cid como único elegível; obter conjunto vazio. Não concluir desafios apenas pela seleção de um botão ou pela abertura de uma pista.
4. Três perguntas de compreensão com feedback explicativo para acerto e erro: disponibilidade antes da comparação, peso não é chance de sucesso, prova matemática não certifica toda execução. Permitir tentar novamente, avançar e recomeçar. Progresso restrito à sessão; sem coleta ou cadastro.
5. Preservar cores, tipografia, espaços e navegação do site. Layout em celular, foco visível, teclado, regiões de feedback anunciadas e preferência por movimento reduzido. Integrar seções ao modo de apresentação.
6. Atualizar o manuscrito editorial do MIRA e executar novamente o orquestrador, mantendo relatório e proveniência. Não alterar a dissertação, seus números ou a fórmula de roteamento.
7. Publicar a revisão na main e atualizar codex/gh-pages sem reescrever histórico, preservando qualquer arquivo alheio ao site.

## Critérios de aceite

- Testes de desafios com estados de sucesso e alternativas incorretas; casos de vazio, candidato único e exclusão indevida.
- Testes de respostas corretas/incorretas e dados inválidos do questionário.
- Conferência no navegador das quatro etapas, pistas, conclusão e reinício de desafios, tentativa e reinício do questionário, teclado, apresentação e ausência de overflow em celular.
- Verificar arquivos servidos após a implantação e manter registro da execução real do MIRA.

## Limites

Os recursos oferecem apoio à compreensão; não alegar melhora de aprendizagem medida ou validada. As porcentagens representam pesos do mecanismo, não probabilidades calibradas. A analogia não representa agentes executados, pessoas reais ou um novo experimento científico.
