# Deduções locais do livro — R910

A revisão aproxima as fórmulas dos capítulos de enunciados efetivamente formalizados.
Cada quadro separa enunciado, hipóteses, lemas e dedução, nomes Lean, axiomas e alcance.
Não usa número de quadros como medida de qualidade científica nem de cobertura funcional.

## Fundamentos e cadeia de prova

`leanref` apresenta a declaração nominal e as dependências do recibo da compilação:
P = propext; C = Classical.choice; Q = Quot.sound; nenhum = sem esses axiomas adicionais.
A teoria de tipos continua sendo a base. Hipóteses como independência, denominador
positivo e domínio real não são axiomas locais nem fatos empíricos demonstrados.
`gen_lean_axioms.py` rejeita fonte Lean divergente, auditoria incompleta e axioma proibido;
seu resultado determinístico é `livro-core/lean-axiomas.tex`.

A identidade por independência conjunta foi ligada explicitamente à probabilidade real
via `independent_error_probability_real`; valores de probabilidade não negativa estendida
não foram identificados silenciosamente com reais. O complemento deriva de normalização
e aditividade. O texto distingue lemas chamados de provas diretas por normalização,
álgebra de anéis, análise de casos ou aritmética linear.

Os exemplos repetidos no prólogo, projeto pedagógico, podcast e catálogos recebem
instanciação local. A escala da matriz2×2 e a identidade WI=W foram acrescentadas,
sem alegar que Q e K tenham sido inferidos de dados. Novas contas didáticas e máximo
elegível foram formalizados, conservando os domínios e limites. O risco do cenário
p=0,999 ganhou intervalo suficiente para justificar o arredondamento informado.

## Gates independentes

1. `scripts/book_local_deductions.py`: confere pares família/fonte, campos e nomes
   auditados. Não decide fidelidade semântica da tradução matemática em linguagem natural.
2. Leitura dirigida independente: confronta hipóteses e conclusões com Lean. Encontrou
   e motivou correção das massas PPV normalizadas e da precisão de um intervalo softmax.
3. `scripts/verify_book_lean.py`: kernel real, auditoria individual, controles de erro,
   dependências fixadas e custódia de fontes. Sem fallback sintático.
4. Livro completo: compilação existente, gates editoriais, coordenadas e amostra visual.

Os resultados executados, comandos, hashes, contagens e limites da edição estão em
`docs/verification-book-r910.json`; a compilação matemática fica no recibo vivo
`docs/verification-book-lean-r908.json`. Os manifestosR908/R909 são fotografias históricas.

## Limites

A matriz foi ampliada por inspeção dirigida de ocorrências; não é uma prova automática
de ausência absoluta de fórmulas omitidas. Exercícios sem solução são tarefas do leitor,
com o teorema geral correspondente quando aplicável. F27 continua fora do domínio de
prova de ocorrência: logs, coleta, Pearson/Welch, resultados de modelos, qualidade
científica e atualidade de DOI exigem seus próprios dados e procedimentos.
O prefácio humanístico permanece interpretativo. Não há validação científica externa,
prova de equivalência com runtime Python, garantia IEEE-754 ou eficácia didática medida.
