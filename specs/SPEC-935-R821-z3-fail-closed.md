---
spec_id: SPEC-935-R821
title: Recusa integral de restrições inválidas e resultados inconclusivos no Z3
component: reasoning/engines.py
status: implemented
round_id: R821
test_file: tests/test_r821_z3_fail_closed.py
---

# SPEC-935-R821 — Z3 sem conclusão a partir de restrições descartadas

Z3Engine.reason ignora uma restrição cujo parsing ou inserção falha e consulta
o solver com as restantes. Todas as restrições inválidas deixam um solver vazio
que retorna SAT com confiança 0,95. Uma mistura também pode concluir sobre um
problema diferente do solicitado. O ramo de resultados diferentes de SAT
atribui confiança 0,9 inclusive a unknown.

## Contrato

1. Preservar ReasoningResult, interfaces, backend opcional, parser existente e
   resultados SAT/UNSAT legítimos. Uma entrada válida é uma coleção list/tuple
   de strings; None continua representando nenhuma restrição.
2. Rejeitar a operação inteira quando qualquer restrição falhar no parsing ou
   na inserção no solver. Não chamar solver.check e não obter modelo nesse
   caso, mesmo se outras restrições forem válidas. A recusa tem confiança zero
   e mantém available como disponibilidade do backend.
3. Somente sat permite obter um modelo e a conclusão SATISFATÍVEL. Somente
   unsat recebe a confiança legada 0,9. Unknown e respostas inesperadas são
   inconclusivas, têm confiança zero e não consultam um modelo.
4. Exceções do backend também produzem recusa com confiança zero. Manter o
   fallback sem Z3 como análise superficial, sem apresentá-lo como resultado
   SAT/UNSAT. Não alterar a AST ou os contratos matemáticos R818.
5. Contraprovas usam restrições inofensivas e instrumentação de um solver real;
   verificar a fronteira antes de check. A injeção de unknown é uma simulação
   explícita do retorno, distinta de uma execução que produziu unknown.
6. Sem restrições formais, informar somente o escopo de tautologia vazia e que
   a query não foi avaliada, com confiança zero, sem consultar o solver.
7. Validar a AST inteira antes de construir qualquer objeto Z3: limite de 4096
   caracteres, 256 nós, profundidade 32, nomes ASCII de até 64 caracteres,
   constantes inteiras de 256 bits e reais finitas. Coleção de até 64 restrições
   e 16384 caracteres totais. Potências usam o orçamento restrito R818 sem
   alterar esse parser. Calls, atributos e demais sintaxes fora da gramática
   são recusados. Not booleano e constantes fracionárias legítimos mantêm
   semântica, sem converter frações em inteiros.
8. Configurar timeout finito de 5000 ms e limite de recursos no solver.
   Limites sintáticos reduzem entradas patológicas; não garantem um teto de
   memória ou duração total do processo para toda fórmula aceita.
9. O operador `/` usa divisão real usual, mesmo com operandos inteiros.
   Denominadores comprovadamente nulos recusam a operação antes de check;
   divisores simbólicos acrescentam condições de domínio não nulo agrupadas
   com a fórmula inteira. Not/Or não podem negar ou ocultar essas condições.
   SAT/UNSAT considera a fórmula junto ao seu domínio aritmético definido.
10. Base comprovadamente zero com expoente negativo recusa a operação antes
    de check. Expoentes simbólicos recebem a guarda de domínio
    `expoente >= 0 ou base != 0`, agrupada com a fórmula inteira. Expoente zero
    representa resultado 1, incluindo 0**0, também quando zero é determinado
    por outra restrição. `%` permanece fora da gramática Z3; nenhuma operação
    nova é acrescentada.

## Verificação

Logs RED/GREEN em `outputs/core-r821`. Regressões com R818, raciocínio
evolutivo, subsistemas avançados e R114. Gate geral e ciclos pelo primário.

RED inicial: 15 falhas e 4 passes (1,29 s); RED expandido: 34 falhas e 8
passes (1,80 s). GREEN específico: 42 passes (0,78 s). A execução expandida
intercepta os construtores para provar que entradas inválidas e potências
excessivas são recusadas antes de construir ou calcular objetos do backend.
Nenhuma contraprova calcula uma expressão expansiva.

Regressão R821/R818/reasoning_evolution/advanced_subsystems/R114: 198 passes
(8,46 s). Regressão de fronteiras de segurança R450 e scaffolds R369: 29
passes (2,31 s). `real-z3-results.json` registra sete chamadas reais no Z3
4.16.0, incluindo SAT, UNSAT, Not, fração e recusas; unknown permanece uma
contraprova injetada, sem alegação de execução real que tenha produzido unknown.
Produto e testes congelados para o gate consolidado do primário. Registro de
ciclos permanece sob responsabilidade do primário.

Correção posterior de domínio, em 11/10/2026: a revisão independente reproduziu
divisão inteira implícita e SAT em divisão por zero. R818/R821 receberam 35
contraprovas adicionais, sem novo arquivo de testes ou spec. RED conjunto:
29 falhas e 139 aprovações; GREEN conjunto: 168 aprovações (4,27 s).
Regressão ampliada: 262 aprovações (15,95 s). Quatro mutantes isolados foram
detectados, incluindo remoção de divisão real, guardas de domínio, recusa de
zero e resultados SymPy indefinidos. Evidências posteriores em
`outputs/core-r820/math-domain-*`; evidências anteriores foram preservadas.

Fechamento de potências da mesma gramática: a sonda real reproduziu SAT para
0**-1 e um valor arbitrário para 0**0; RED focado: 12 falhas/9 aprovações.
GREEN final R818/R821: 189 aprovações (2,67 s); regressão final em processo
novo: 283 aprovações (15,79 s). Os seis mutantes finais foram detectados,
incluindo remoção da guarda de potência negativa e da convenção de expoente
zero simbólico. As provas reais anteriores e posteriores são distintas.
