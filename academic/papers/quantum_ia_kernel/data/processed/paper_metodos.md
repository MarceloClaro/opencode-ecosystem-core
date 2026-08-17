# Métodos — versão gerada automaticamente

## Desenho

Estudo computacional comparativo, pré-especificado pelo hash `89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf`. O desfecho primário foi a diferença pareada de acurácia balanceada entre um SVM com kernel quântico de fidelidade e um SVM-RBF. A seleção de hiperparâmetros ocorreu exclusivamente nos dados de desenvolvimento.

## Validação

Foi definida validação cruzada aninhada repetida com quatro folds externos e três repetições (12 avaliações externas). Em cada fold externo, a transformação imputação–padronização–PCA–escala angular foi ajustada apenas no treino. A seleção interna utilizou três folds estratificados, `C ∈ [0.1, 1.0, 10.0]` para ambos os SVMs e `gamma ∈ ['scale', 'auto']` para o RBF.

## Kernel quântico

O mapa ZZ utilizou dois qubits, uma repetição e entrelaçamento linear. A matriz foi avaliada em referência exata, 2048 shots, ruído Aer e, opcionalmente, pares-âncora em QPU. Foram registrados alinhamento kernel–alvo, posto efetivo, erro de Frobenius relativo, tempo e avaliações lógicas.

## Estatística

O teste primário unilateral utilizou a correção de Nadeau–Bengio para dependência entre folds (α=0.05). O IC bilateral de 95%, a permutação exata de sinais, o tamanho de efeito pareado dz e TOST com margem ±0.02 foram análises pré-especificadas. Desfechos secundários receberam ajuste de Holm.

## Limites

Simulação em pequena escala, compressão para dois componentes, custo quadrático do kernel, dependência residual entre folds e ausência de validade clínica/operacional direta.
