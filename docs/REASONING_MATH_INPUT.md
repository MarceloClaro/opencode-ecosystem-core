# Entrada matemática dos motores de raciocínio

O motor `SymPyEngine` aceita uma gramática matemática restrita e preserva
`reason(query, expression=None)` e `ReasoningResult`. Quando a consulta for
descritiva, forneça a expressão separadamente: `reason("resolver", expression="2*x = 8")`.
O modo automático da fachada seleciona SymPy para esse argumento explícito.
Uma pergunta textual sobre equações pode indicar intenção matemática, mas
não é silenciosamente transformada em uma expressão.

Expressões permitidas incluem números finitos, identificadores ASCII simples,
constantes `pi`, `E`, `I`, parênteses e operadores `+`, `-`, `*`, `/`, `%`, `**`.
Use multiplicação explícita (`2*x`) e `**` para potência. Uma equação usa uma
única igualdade (`2*x = 8`); comparações e atribuições internas são recusadas.
Nomes de variáveis são símbolos formais, sem consulta a objetos Python.

As únicas chamadas disponíveis são `sin`, `cos`, `tan`, `sqrt`, `exp`, `log`,
`Abs`, `solve`, `integrate` e `diff`, com aridades controladas. Exemplos:

- `sin(x)**2 + cos(x)**2` simplifica para `1`.
- `solve(x**2 - 4, x)` retorna `[-2, 2]`.
- `integrate(x, x)` retorna `x**2/2`.
- `integrate(x, (x, 0, 1))` retorna `1/2`.
- `diff(x**3, x)` retorna `3*x**2`.
- `diff(x**3, x, 2)` retorna `6*x`.

São recusados atributos, subscritos, containers, comprehensions, imports,
lambdas, strings, booleanos, chamadas fora da tabela, argumentos nomeados,
expansões de argumentos, nomes privados ou mágicos, comentários e continuação
de linha. A tupla de limites da integral é uma exceção controlada aos containers.
Nenhuma entrada externa chega ao parsing de strings do SymPy: a árvore inteira
é validada antes de construir objetos ou executar operações permitidas.

Os limites são 4.096 caracteres, 256 nós agregados, profundidade 32,
identificadores de 64 caracteres e inteiros de até 256 bits. Potências aninhadas
são recusadas. O expoente numérico, inclusive aritmética de constantes, tem
magnitude máxima 256; a base tem no máximo 16 nós, com orçamento de 512 para
seu tamanho combinado com o expoente. Resultados numéricos estimados de
potências têm orçamento de 4.096 bits. Expoentes simbólicos precisam ser um
símbolo isolado, com sinal opcional. Chamadas e expressões simbólicas compostas
no expoente são recusadas para evitar expansão após simplificações. A ordem
explícita de derivação é um inteiro entre zero e 32.

Esses limites de parsing não garantem prazo ou consumo de memória para toda
expressão matemática aceita. Simplificação, resolução e integração continuam
usando algoritmos do SymPy. A gramática restrita não equivale a uma garantia
geral contra cálculos matematicamente custosos.

Resultados intermediários e finais indefinidos ou infinitos (`nan`, `zoo`,
`oo` e `-oo`) são recusados com confiança zero, inclusive quando uma operação
posterior poderia ocultá-los. Exemplos recusados incluem `0/0`, `1/0`,
`0*(1/0)` e `log(0)`. Valores complexos finitos, como `sqrt(-1)`, continuam
permitidos. A finitude desconhecida de uma expressão simbólica, como `1/x`,
não a torna inválida: o motor não afirma que ela esteja definida para toda
substituição de seus símbolos.

Sem SymPy, o fallback aceita somente a parte numérica dessa gramática e não
remove caracteres para aproveitar números de uma entrada inválida. Falhas
têm confiança zero e uma conclusão de recusa. `available` continua indicando
disponibilidade do backend, inclusive quando a entrada é recusada. A confiança
legada de um cálculo concluído não é validação científica ou clínica externa.

Contrato: `specs/SPEC-935-R818-parsing-matematico-restrito.md`. Testes:
`tests/test_r818_restricted_math_engine.py`. Evidências locais:
`outputs/core-r818`.
