---
spec_id: SPEC-935-R818
title: Parsing matemático restrito dos motores de raciocínio
component: reasoning/engines.py
status: implemented
round_id: R818
test_file: tests/test_r818_restricted_math_engine.py
---

# SPEC-935-R818 — Entrada matemática sem avaliação dinâmica de texto

O motor SymPy encaminha expressões e lados de equações diretamente a sympify,
embora a documentação instalada do SymPy 1.14.0 informe avaliação dinâmica de
texto. O fallback remove caracteres em vez de rejeitar entradas, e o roteador
seleciona matemática para palavras presentes em consultas não matemáticas.
Doctor pré-edição: 21/21 checks estruturais aprovados, sem prova de inferência.

## Contrato

1. Preservar interfaces dos motores e ReasoningResult, cálculo aritmético,
   simplificação, equações `lhs = rhs` e operações matemáticas explícitas.
   Não encaminhar texto externo a sympify, parsing dinâmico ou funções de
   execução de código.
2. Validar a AST inteira antes de construir objetos SymPy. Permitir números
   finitos, símbolos simples, operadores `+ - * / % **`, sinais unários e
   parênteses. Chamadas só são permitidas para uma tabela explícita de funções
   matemáticas, incluindo sin/cos/sqrt/log/exp, solve/integrate/diff. Limites
   de integral `(x, inferior, superior)` são a única tupla permitida.
3. Rejeitar chamadas arbitrárias, atributos, subscritos, listas/dicionários,
   comprehensions, imports, lambdas, strings, booleanos, atribuições internas,
   keywords e expansões de argumentos. Identificadores privados ou mágicos,
   comentários, continuação de linha e caracteres fora da gramática não são
   linguagem matemática aceita.
4. Limitar tamanho de texto, número e profundidade de nós, tamanho de
   identificadores e inteiros e custo de potências literais; rejeitar potências
   aninhadas. Expoentes podem ser constantes aritméticas finitas limitadas ou
   símbolos isolados com sinal; chamadas e expressões simbólicas compostas no
   expoente são recusadas antes de qualquer construção. Isso impede que uma
   simplificação ou chamada converta texto aparentemente simbólico em inteiro
   expansivo. Limites sintáticos não garantem prazo de resolução algébrica.
5. Fallback sem SymPy usa a mesma validação, só calcula árvores numéricas e
   rejeita entradas sem apagar caracteres ou aproveitar números de prosa.
   Rejeições mantêm a disponibilidade do backend e confiança zero.
6. Roteamento reconhece intenção matemática por palavras completas e
   expressões válidas. `resolver equação x=2` continua selecionando SymPy;
   `resolver um conflito` e `integralidade dos dados` não selecionam SymPy.
   Um argumento expression explícito seleciona SymPy no modo automático;
   query descritiva nunca é silenciosamente extraída ou executada como código.
7. Contraprovas não executam exploits: bloquear a fronteira antiga por
   monkeypatch e verificar que nenhuma entrada externa a alcança. Preservar
   motores, contratos de fachada e integração do orquestrador, sem alterar
   evolution/cycles.json ou outros módulos.
8. Recusar resultados intermediários e finais indefinidos ou infinitos do
   SymPy, sem promover nan/zoo/oo a cálculo concluído. Preservar complexos
   finitos e expressões simbólicas cuja finitude é desconhecida. Uma operação
   subsequente não pode ocultar um resultado intermediário indefinido.

## Verificação

Logs RED/GREEN e provas matemáticas locais em `outputs/core-r818`.
Regressões incluem contratos existentes de raciocínio e a integração pelo
orquestrador. O gate geral e os ciclos são coordenados pelo agente primário.

Resultados executados: RED inicial **62 failed, 7 passed**; primeiro GREEN
**69 passed**; RED de limites derivados **6 failed, 1 passed**, com construtor
monkeypatched antes de qualquer operação expansiva. Regressão final:
**185 passed** em 22,03 s, incluindo R818, raciocínio evolutivo, subsistemas
avançados, R114, R450 e R369. Apenas a execução operacional local foi testada;
confiança do motor é preservada por compatibilidade e não valida ciência.

Correção posterior de resultados indefinidos, em 11/10/2026: a revisão
independente reproduziu `0/0` como nan com confiança 0,95. Após a recusa de
resultados intermediários/finais indefinidos, as 168 contraprovas conjuntas
R818/R821 passaram (4,27 s), e a regressão ampliada passou em 262 testes
(15,95 s). O mutante que remove essa recusa falhou em dez contraprovas. Logs
e provas posteriores ficam em `outputs/core-r820/math-domain-*`, preservando
os registros anteriores.

Após completar o domínio de potências Z3 na mesma gramática, o gate conjunto
final aprovou 189 testes (2,67 s); a regressão ampliada em processo novo
aprovou 283 testes (15,79 s). Nenhuma fonte de execução dinâmica foi
reintroduzida e nenhuma função foi acrescentada à tabela matemática.
