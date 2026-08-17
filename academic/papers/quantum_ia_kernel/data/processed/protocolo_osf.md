# Geometry-Survival Evidence Gates for Reproducible and Cost-Aware Quantum Kernel Applications Under Noise

**Autor responsável:** Marcelo Claro Laranjeira  
**Projeto:** Fundamentos quânticos aplicados à pesquisa em IA  
**Data de congelamento:** 2026-08-16  
**SHA-256:** `89c08f07f2f03a56c144bd4c4b7eddb71813bb1b043bb90920de8e5e70140eaf`

## Pergunta e hipóteses

- Pergunta primária: A acurácia balanceada do kernel quântico supera o SVM-RBF sob seleção interna justa e validação cruzada externa repetida?
- Hipótese primária: H1: média pareada de ΔBAC = BAC_QML − BAC_RBF > 0
- Hipótese mecanística: H2: maior sobrevivência geométrica ideal→shots→ruído está associada a menor degradação preditiva.

## Desenho confirmatório

- Desfecho primário: `delta_acuracia_balanceada`.
- Baseline pré-especificado: SVM-RBF.
- Validação externa: 4 folds estratificados × 3 repetições.
- Seleção interna: 3 folds estratificados.
- Grade C: [0.1, 1.0, 10.0].
- Gamma RBF: ['scale', 'auto'].
- Alfa: 0.05.
- Margem de equivalência em BAC: ±0.02.

## Sequência e regra de progressão

1. CV aninhada repetida e inferência corrigida para folds dependentes.
2. Suíte multibase com pré-processamento ajustado exclusivamente no treino.
3. Escada statevector → shots → ruído Aer.
4. Pares-âncora na QPU somente após os itens 1–3.
5. Classificador completo na QPU somente se correlação ideal–QPU ≥ 0,90 e MAE ≤ 0,10 nos pares-âncora, além de viabilidade de custo.

## Controle de alegações

não usar a expressão vantagem quântica sem ganho, custo de escala, teste externo e validação em hardware. Toda análise acrescentada após o carimbo OSF será identificada como exploratória ou como desvio justificado.
