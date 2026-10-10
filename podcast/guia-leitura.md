# Uma escolha explicável — guia de leitura

Este resumo editorial retoma ideias das fontes usadas para gerar o podcast de 22 minutos e 36 segundos. Não é uma transcrição literal do áudio e não possui capítulos sincronizados.

## 1. O conjunto e a peça estudada
O OpenCode Ecosystem Core organiza agentes especializados, ferramentas, contexto e registros. Um coordenador conecta essas partes. O roteador compara candidatos para encaminhar uma tarefa. A dissertação estuda essa regra; o MIRA comunica o trabalho em apresentações.

Pergunta: o que a pesquisa estuda dentro do projeto?
Resposta: o mecanismo de roteamento em um escopo definido, e não todo o ecossistema.

## 2. Filtrar, comparar, escolher
Só participa quem está apto e disponível. Uma nota combina semântica (0,30), cobertura (0,35), confiança (0,25) e quanto o candidato está livre, calculado como 1 − carga (0,10). A importância dos critérios é fixa. O softmax converte notas em pesos que somam 1 quando há participantes. No exemplo da dissertação, Ana recebe cerca de 53 fichas e Cid, 47, em uma comparação de 100 fichas. No exemplo, a tarefa inteira seria encaminhada apenas ao primeiro da lista.

Pergunta: 53% de peso significa 53% de chance de sucesso?
Resposta: não. O peso representa participação na comparação. O estudo não demonstrou calibração como probabilidade de sucesso.

## 3. Ler as evidências com seus limites
As demonstrações em Lean 4 tratam de propriedades matemáticas sobre números reais exatos. Os testes empíricos são internos, com situações simuladas e comparadores simples. Escolher a melhor opção segundo uma referência do simulador difere de executar uma tarefa real com sucesso. As provas não certificam todo o software nem o arredondamento computacional. A pesquisa não treinou uma rede Transformer.

Pergunta: as provas garantem que todos os agentes funcionarão?
Resposta: não; fórmulas, implementação e execução possuem fronteiras diferentes.

## Depois da escuta
Explore o laboratório do site, altere a confiança e a carga de Ana e explique o que mudou. Confira seu entendimento nas três perguntas interativas. Consulte a dissertação para fórmulas, resultados e limitações completos.

[Site e atividades](https://marceloclaro.github.io/opencode-ecosystem-core/)
[Dissertação](https://github.com/MarceloClaro/opencode-ecosystem-core/blob/main/artigos/pucrs-roteamento-atencao/output/pdf/dissertacao-abnt.pdf)
