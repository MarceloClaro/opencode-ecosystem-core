# Roteamento inspirado em atenção

## O projeto por trás da pesquisa

O OpenCode Ecosystem Core reúne agentes de software, ferramentas, memória e registros. Pense em uma oficina: programas diferentes têm papéis especializados, e um coordenador organiza o trabalho. A pesquisa examina uma peça desse conjunto: o roteador.

## O caminho de uma tarefa

A pessoa informa um pedido. O coordenador recupera contexto e organiza seu encaminhamento. Nos fluxos que usam o roteador estudado, ele compara candidatos aptos e disponíveis.

## Escolher e concluir são etapas diferentes

Com um programa ou uma ferramenta preparada e disponível, uma tarefa pode ser realizada. O estado e os resultados são registrados para conferência. A ilustração no site representa esse caminho; não executa agentes nem comprova o funcionamento do ecossistema completo.

## MIRA apresenta as ideias

O MIRA recebe um manuscrito e gera uma apresentação com roteiro, texto e animação. O coordenador pode encaminhar essa tarefa diretamente ao MIRA. Sua conformidade interna confere o artefato visual; a avaliação científica do trabalho é uma questão própria.

## Uma escolha explicável

Um agente é um programa especializado. Roteamento é encaminhar um pedido a um desses programas. Quando vários podem ajudar, como escolher? O estudo combina critérios definidos previamente; seus pesos não foram aprendidos.

## Uma equipe para entender

Imagine um pedido de pesquisa e resumo. Ana e Cid têm as capacidades e estão disponíveis. Bia é uma personagem didática indisponível para novas tarefas. Os nomes ilustram programas; nenhum deles é executado nesta apresentação.

## Filtrar antes de comparar

- Só participa quem está disponível e tem todas as capacidades exigidas.
- Identificadores inválidos e duplicados ficam fora.
- Muita carga reduz a nota, mas não exclui por si só.
- Indisponibilidade exclui antes de comparar.

## Quatro perguntas, uma nota

Quanto combina com o pedido? Tem as capacidades? Qual a nota de confiança? Quanto está livre? Os coeficientes são fixos: 0,30; 0,35; 0,25; 0,10. Entre participantes aptos, a cobertura é completa.

## Imagine cem fichas

O softmax transforma as notas em pesos que somam 1. Imagine repartir 100 fichas: cerca de 53 para Ana e 47 para Cid. Fichas são parcelas da comparação, não chances de sucesso nem partes da tarefa. A tarefa seria encaminhada apenas ao primeiro colocado.

## Ana e Cid no exemplo

- Ana: combinação com o pedido 0,8417; confiança 0,9; carga livre 0,9.
- Cid: combinação com o pedido 0,7703; confiança 0,7; carga livre 0,6.
- Notas combinadas: aproximadamente 0,9175 e 0,8161.
- Pesos: aproximadamente 0,5253 e 0,4747.

## Experimente e explique

O site propõe três desafios: fazer Cid ficar em primeiro mantendo Ana disponível; deixar só Cid disponível; e observar a ausência de escolha quando ninguém pode atender. Perguntas com feedback retomam disponibilidade, significado dos pesos e alcance das provas.

## Regras e testes

- Onze propriedades documentadas em Lean 4 sobre números reais exatos.
- Teste interno com 200 decisões simuladas em cinco grupos de candidatos.
- Distância média da melhor nota de referência: 0,0421.
- Comparadores simples: aleatório 0,1882; menor carga 0,2167; maior cobertura 0,2118.

## O alcance dos resultados

As margens são exploratórias e ignoram o agrupamento por grupo de candidatos. A confiança foi criada pelo simulador como sinal da qualidade atribuída aos candidatos. As provas matemáticas não certificam toda execução do programa ou dos agentes. A revisão editorial não repetiu os experimentos científicos.

## Continuidade da pesquisa

- Estudar o arredondamento do cálculo no computador.
- Analisar decisões considerando seu agrupamento.
- Comparar com dados externos e reprodução independente.
- Conferir a minuta com o modelo institucional antes da submissão.

## Fonte da apresentação

Conteúdo editorial derivado de dissertacao-abnt.tex, versão revista de 10 de outubro de 2026. Autor: Marcelo Claro Laranjeira. As interações são didáticas; não constituem novos experimentos nem avaliação de aprendizagem.
