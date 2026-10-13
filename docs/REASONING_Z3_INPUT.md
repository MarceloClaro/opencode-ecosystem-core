# Restrições formais no motor Z3

O `Z3Engine.reason(query, constraints=...)` consulta o solver somente para um
conjunto de restrições formais aceitas. A query é uma descrição: o motor não
traduz automaticamente prosa em fórmulas. SAT significa que as restrições
fornecidas têm um modelo; UNSAT significa que esse conjunto é inconsistente.
Esses resultados não validam empiricamente uma alegação descrita na query.

Use uma lista ou tupla de strings, por exemplo:

```python
Z3Engine().reason("x positivo", constraints=["x == 2", "x > 0"])
Z3Engine().reason("contradição", constraints=["x == 2", "not (x == 2)"])
```

Se qualquer restrição tiver sintaxe, tipo ou inserção inválidos, a operação
inteira é recusada com confiança zero. O solver não consulta um subconjunto
que tenha sobrevivido ao erro. `None`, uma coleção vazia ou a ausência de uma
fórmula não respondem à query: o resultado explicita somente o escopo de
tautologia vazia e tem confiança zero.

A gramática aceita variáveis inteiras com nomes ASCII, constantes numéricas
finitas, comparações simples, `and`, `or`, `not` e operadores aritméticos
`+`, `-`, `*`, `/`, `**`. O operador `%` continua fora da gramática Z3 e é
recusado, inclusive quando seu denominador seria não nulo.
Constantes fracionárias são preservadas como reais, sem arredondamento para
inteiros. O operador `/` sempre representa divisão real usual, inclusive
entre inteiros: `1/2 == 0.5` é satisfatível e `1/2 == 0` é inconsistente.
Um denominador comprovadamente nulo recusa a operação inteira antes da
consulta ao solver. Cada divisor simbólico acrescenta uma condição de domínio
`divisor != 0` à restrição inteira; essas condições ficam fora de `not` e
`or`, e não podem ser negadas ou ocultadas por outro ramo. Por exemplo,
`["x == 1/y", "y == 0"]` é inconsistente sob o domínio definido, sem
admitir um modelo de divisão por zero. Isso não garante a decidibilidade de
toda fórmula envolvendo divisão simbólica.

Calls, atributos, subscritos, comprehensions e sintaxes fora da
gramática são recusados. Todas as partes da AST de uma restrição são validadas
antes de construir objetos Z3.

Os limites são 64 restrições e 16384 caracteres totais; cada restrição admite
até 4096 caracteres, 256 nós, profundidade 32, nomes de 64 caracteres e
constantes inteiras de 256 bits. Potências seguem o orçamento R818: não podem
ser aninhadas; a base admite 16 nós, expoentes numéricos têm magnitude máxima
256, produto do número de nós pela magnitude até 512 e tamanho estimado de
resultado até 4096 bits. Expoentes compostos com símbolos são recusados.
Expoentes simbólicos simples continuam sujeitos aos limites do solver.
Uma base comprovadamente zero com expoente negativo recusa a operação antes
da consulta. Para expoentes simbólicos, a condição de domínio
`expoente >= 0 ou base != 0` fica agrupada com a fórmula inteira, fora de
`not`/`or`. A fachada adota a convenção `base**0 = 1`, incluindo `0**0`,
inclusive quando o expoente zero é determinado pelas demais restrições.
Essa convenção é explícita; não é inferida do tratamento totalizado do backend.

O solver recebe timeout de 5000 ms e limite de recursos `rlimit=100000`.
`unknown`, um retorno inesperado ou uma exceção não produzem um modelo nem uma
conclusão SAT, e têm confiança zero. Os limites sintáticos e o timeout do solver
não garantem um teto de memória ou duração total do processo para toda fórmula
aceita.

`available` indica a disponibilidade do backend, incluindo quando a operação
é recusada. Sem Z3, o fallback legado faz somente uma comparação superficial de
negações textuais; não é uma prova SAT/UNSAT. Os valores legados de confiança de
resultados SAT/UNSAT são indicadores internos, sem validação externa ou
calibração científica.

O contrato R821 e suas contraprovas estão em
`specs/SPEC-935-R821-z3-fail-closed.md` e
`tests/test_r821_z3_fail_closed.py`. Os registros em `outputs/core-r821` distinguem
execuções reais do backend de retornos `unknown` injetados nos testes.
