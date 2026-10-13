---
spec_id: SPEC-935-R838
title: Raciocínio seguro após revisão cega
status: proposed
test_file: tests/test_r838_razao_segura_revisao_cega.py
---

# SPEC-935-R838 — Raciocínio seguro após revisão cega

Estado: em implementação; aceite humano pendente.

## Problema e escopo

A revisão R2 identificou avaliação dinâmica, demonstração constante apresentada
como resposta e expressão SMT ignorada. A alteração recente R834 retirou a
avaliação dinâmica, mas continuou a ignorar atribuições e encaminhou texto
externo diretamente ao parser do SymPy. Esta rodada reutiliza as gramáticas
restritas de `reasoning/engines.py`; não cria outro parser permissivo.

## Contratos

1. `z3_solver.check` traduz integralmente a fórmula e suas atribuições numéricas
   explícitas. Não inventa x=2. SAT/UNSAT só podem decorrer do solver instalado;
   indisponibilidade, sintaxe recusada ou resultado inconclusivo retornam fallback.
2. A antiga tradução x>1 / x==v era um stub e não provava a expressão recebida.
   O novo contrato declara domínio inteiro para símbolos livres e substituição
   literal de atribuições finitas; divisão segue a gramática canônica R821.
3. `reasoning_engines.route` responde à entrada matemática efetiva por AST
   integralmente validada. Texto descritivo não parseável é recusado, sem resposta
   demonstrativa. Confiança/trust não são probabilidades e ficam não registradas.
4. Nenhuma chamada de execução dinâmica ou reparsing de texto externo pelo
   SymPy é admitida em `reasoning/*.py`. A verificação de fonte integra pytest/CI.
5. Casos adversariais nunca executam importação, atributos, subscritos ou chamadas
   fora da tabela matemática. Verificam-se soma, integral explícita, contradição,
   atribuição x=0/x=2, indisponibilidade e rejeição integral.

## Aceitação

`tests/test_r838_razao_segura_revisao_cega.py`, regressões R818/R821/R830/R832,
recibos RED/GREEN em `outputs/core-r838/`, diagnóstico local e revisão humana.
Não constitui validação externa nem desempenho equivalente a outro projeto.
