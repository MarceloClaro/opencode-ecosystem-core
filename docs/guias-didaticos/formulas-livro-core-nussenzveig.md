# Fórmulas e Cálculos do Livro-Core — Guia Didático no Estilo de Herch Moysés Nussenzveig

> **Princípio orientador (Nussenzveig):** a ênfase não está no tratamento matemático por si, e sim nos conceitos. Os símbolos matemáticos são introduzidos **só quando se tornam necessários**, sempre motivados pelo problema físico, sem pressupor conhecimentos prévios. Nada de decoreba: cada igualdade é justificada por um princípio explícito, cada cálculo numérico é executado passo a passo, e todo resultado é acompanhado de seus limites de validade.

---

## Escopo da revisão R907

Os exemplos são modelos didáticos; não são medições atuais do Core. Frações exigem universo positivo, e universo vazio fica não aplicável. O modelo de custo e a janela de lances não descrevem a implementação corrente do CFP, que usa redução ou ranking de utilidade. Na edição atual, as fontes locais indicadas no livro prevalecem sobre as associações históricas deste guia. O texto não reproduz nem atribui uma transcrição literal de Nussenzveig.

## SUMÁRIO

1. [Probabilidade de pelo menos uma saída errada entre N saídas independentes](#1-probabilidade-de-pelo-menos-uma-saida-errada-entre-n-saidas-independentes)
2. [Cobertura de checklist ($\kappa$) e o gate do item crítico](#2-cobertura-de-checklist-kappa-e-o-gate-do-item-critico)
3. [Disponibilidade de executores externos ($s$)](#3-disponibilidade-de-executores-externos-s)
4. [Cobertura comparativa externa ($b$)](#4-cobertura-comparativa-externa-b)
5. [Valor Preditivo Positivo (PPV) — argumento de Ioannidis](#5-valor-preditivo-positivo-ppv--argumento-de-ioannidis)
6. [Tempo total de delegação negociada](#6-tempo-total-de-delegacao-negociada)
7. [Similaridade de Jaccard para roteamento de capacidades](#7-similaridade-de-jaccard-para-roteamento-de-capacidades)
8. [Taxa de ativação de DOIs](#8-taxa-de-ativacao-de-dois)
9. [Cobertura de dimensões de ficha](#9-cobertura-de-dimensoes-de-ficha)
10. [PRISMA — contagem de registros em revisão sistemática](#10-prisma---contagem-de-registros-em-revisao-sistematica)

---

## 1. Probabilidade de que pelo menos uma entre N saídas independentes esteja errada

**Ocorrência no livro:** `mod-01-fundacoes.tex` (exemplo resolvido com $N=216$ e $p=0{,}99$).

### 1.1. O problema concreto (motivação física)

Imagine que um sistema produza 216 respostas (saídas). Cada resposta, considerada sozinha, tem 99 % de chance de estar correta. Um auditor quer saber: **qual é a chance de que, entre essas 216 respostas, pelo menos uma esteja errada?**

Esta não é uma pergunta abstrata. É a pergunta que alguém faz ao examinar um lote grande de entregas: "se cada uma é quase sempre certa, será que, reunindo tantas, não aparece pelo menos um erro?" Queremos calcular exatamente essa certeza.

### 1.2. Definição dos símbolos (introduzidos só quando necessários)

Antes de escrever qualquer fórmula, fixamos o que cada letra significa:

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $N$ | Número total de saídas | $N = 216$ |
| $p$ | Probabilidade de **uma única** saída estar correta | $p = 0{,}99 = 99\%$ |
| $1-p$ | Probabilidade de **uma única** saída estar errada | $1 - 0{,}99 = 0{,}01 = 1\%$ |
| Independência | Hipótese de que o acerto ou erro de uma saída **não influencia** o acerto ou erro de nenhuma outra | Suposição do modelo |

### 1.3. Dedução da fórmula $P = 1 - p^N$

#### Passo 1 — Probabilidade de que **todas** as $N$ saídas estejam corretas

Se os eventos são independentes, a probabilidade de que todos ocorram ao mesmo tempo é o **produto** das probabilidades individuais. Este é o **axioma de multiplicação para eventos independentes**.

Por que produto e não soma? Porque estamos exigindo que a saída 1 esteja correta **E** a saída 2 esteja correta **E** … **E** a saída $N$ esteja correta. "E" na probabilidade, para eventos independentes, significa multiplicar.

Como o fator $p$ se repete exatamente $N$ vezes:

\[
P(\text{todas corretas}) = p \times p \times \cdots \times p = p^N
\]

#### Passo 2 — O evento complementar

O evento "pelo menos uma saída está errada" é o **oposto exato** de "todas as saídas estão corretas". Em teoria dos conjuntos, se $A$ é o evento "todas corretas", então o complemento $A^c$ é "existe pelo menos uma errada".

#### Passo 3 — Axioma da probabilidade total

Para qualquer evento $A$ e seu complemento $A^c$:

\[
P(A) + P(A^c) = 1
\]

**Por que?** Porque todo resultado possível ou pertence a $A$ ou pertence a $A^c$, e a soma das probabilidades de todos os resultados possíveis é sempre 1 (unidade).

#### Passo 4 — Isolamento da quantidade procurada

Queremos $P(A^c)$. Rearranjando a igualdade do Passo 3:

\[
P(A^c) = 1 - P(A)
\]

Substituindo $P(A) = p^N$ do Passo 1:

\[
\boxed{P(\text{pelo menos uma errada}) = 1 - p^N}
\]

**Justificativa:** isolamento de incógnita por subtração elementar. Nenhum chutismo.

---

### 1.4. Cálculo numérico detalhado com $N=216$ e $p=0{,}99$

Queremos avaliar:

\[
P = 1 - (0{,}99)^{216}
\]

O número $(0{,}99)^{216}$ é muito próximo de zero. Calculá-lo diretamente é trabalhoso. Usamos **logaritmos naturais**, que transformam potências em produtos.

#### Passo 5 — Aplicação do logaritmo natural

Seja $x = (0{,}99)^{216}$. Tomando $\ln$ dos dois lados:

\[
\ln x = \ln\bigl((0{,}99)^{216}\bigr)
\]

Pela propriedade dos logaritmos, $\ln(a^b) = b \cdot \ln a$:

\[
\ln x = 216 \times \ln(0{,}99)
\]

**Por que fazemos isso?** Porque $(0{,}99)^{216}$ é um número difícil de calcular à mão, mas $216 \times \ln(0{,}99)$ é um produto simples.

#### Passo 6 — Avaliação de $\ln(0{,}99)$

O logaritmo natural de $0{,}99$ não é um número elementar. Usamos a **série de Taylor** de $\ln(1-u)$ em torno de $u=0$:

\[
\ln(1-u) = -u - \frac{u^2}{2} - \frac{u^3}{3} - \cdots, \qquad |u|<1
\]

Com $u = 0{,}01$ (porque $0{,}99 = 1 - 0{,}01$):

\[
\ln(0{,}99) = \ln(1-0{,}01) \approx -0{,}01 - \frac{(0{,}01)^2}{2} = -0{,}01 - 0{,}00005 = -0{,}01005
\]

Termos de ordem $(0{,}01)^3/3 \approx 0{,}000000333$ são desprezíveis para a precisão que buscamos.

#### Passo 7 — Multiplicação por $N=216$

\[
\ln x = 216 \times (-0{,}01005)
\]

Calculando:

\[
216 \times 0{,}01005 = 2{,}1708
\]

Portanto:

\[
\ln x \approx -2{,}1708 \approx -2{,}17
\]

#### Passo 8 — Retorno da escala logarítmica

Se $\ln x = -2{,}1708$, então, por definição de logaritmo natural:

\[
x = e^{-2{,}1708}
\]

Calculando o exponencial:

\[
e^{-2{,}1708} \approx 0{,}1141
\]

Aproximando a três algarismos significativos:

\[
(0{,}99)^{216} \approx 0{,}114
\]

#### Passo 9 — Aplicação da fórmula final

\[
P = 1 - 0{,}114 = 0{,}886
\]

Expresso em porcentagem:

\[
\boxed{P \approx 0{,}886 \approx 88{,}6\%}
\]

---

### 1.5. Interpretação do resultado

Há aproximadamente **88,6 % de chance** de que, entre 216 saídas independentes cada uma com 99 % de probabilidade individual de acerto, **pelo menos uma saída esteja errada**.

**O que isso NÃO significa:**
- Não significa que o sistema esteja "estragado".
- Não significa que cada resposta individual seja pouco confiável.
- Não afirma que o Core combina ou agrega todas as respostas.

**O que significa:** Quando se reúne um grande número de saídas, a chance de aparecer ao menos um erro cresce rapidamente, mesmo que cada saída individual seja muito confiável.

---

### 1.6. Limites de validade

1. A fórmula **não mede** a taxa de erro real do repositório. $p=0{,}99$ e a independência são **suposições didáticas**, não medições do Core.
2. Se os erros forem **correlacionados** (todas as saídas usam o mesmo modelo com o mesmo viés), a hipótese de independência colapsa e o resultado $1-p^N$ deixa de valer.
3. O número 216 é usado apenas para ilustrar a fórmula; não significa que o Core faça essa agregação.

---

### 1.7. Exercício de fixação (sugerido)

Recalcule $P$ com $p=0{,}999$ e $N=216$. Explique por que o valor muda. Se todas as saídas repetissem o mesmo erro, a hipótese de independência continuaria válida?

---

## 2. Cobertura de checklist ($\kappa$) e o gate do item crítico

**Ocorrência no livro:** `mod-06-ciencia.tex` (leitura guiada, SRI e cobertura de checklist).

### 2.1. O problema concreto

Uma rubrica de avaliação lista 20 itens. Um relatório atende a 18 deles, mas falta um item **obrigatório** (por exemplo, o pacote de dados). A cobertura bruta é alta (90 %), mas o relatório deve ser reprovado por falta do requisito crítico. Queremos uma fórmula que capture isso.

### 2.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $t$ | Número total de itens da rubrica |
| $a$ | Número de itens atendidos |
| $\kappa$ | Cobertura (fração de atendidos sobre totais) |
| Item crítico | Requisito cuja ausência implica reprovação automática, independentemente de $\kappa$ |

### 2.3. Dedução de $\kappa = a/t$

#### Passo 1 — Razão entre parte e todo

A cobertura é definida como a fração de itens atendidos em relação ao total:

\[
\boxed{\kappa = \frac{a}{t}}
\]

**Justificativa:** Esta é a definição elementar de proporção: parte sobre todo. Não há cálculo diferencial nem integral; é aritmética de contagem.

#### Passo 2 — Regra do gate para item crítico

Se houver pelo menos um item crítico não atendido, o resultado é **reprova**, independentemente do valor de $\kappa$. Formalmente:

\[
\text{Resultado} =
\begin{cases}
\text{reprova}, & \text{se algum item crítico falhar, independentemente de }\kappa,\\
\text{avalie }\kappa, & \text{caso contrário.}
\end{cases}
\]

**Justificativa:** Esta é uma regra de decisão externa imposta pela metodologia, não derivada da fórmula de $\kappa$. O requisito crítico tem precedência sobre o valor da cobertura.

---

### 2.4. Cálculo numérico

Exemplo do livro: rubrica com $t=20$ itens, dos quais $a=18$ estão atendidos.

\[
\kappa = \frac{18}{20} = \frac{9}{10} = 0{,}90 = 90\%
\]

Mesmo com $\kappa = 0{,}90$, se o item faltante for crítico (pacote de dados obrigatório), o gate **reprova**.

---

### 2.5. Interpretação

Cobrir 90 % de uma checklist **não equivale** a 90 % de mérito científico. Um único item crítico pode anular a cobertura alta. Isto separa **cobertura** (o que foi feito) de **mérito** (o que vale).

---

## 3. Disponibilidade de executores externos ($s$)

**Ocorrência no livro:** `mod-07-integracoes.tex` (leitura guiada, definições e exemplo resolvido).

### 3.1. O problema concreto

O manual declara seis executores externos (Gemini, Reasonix, Plandex, Goose, Haystack, NotebookLM/MiroFish). Em determinada máquina, apenas quatro estão instalados. Qual é a fração de disponibilidade?

### 3.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $d$ | Número de executores declarados na configuração |
| $p$ | Número de executores presentes (com instalação identificada) |
| $s$ | Presença instalada (fração sobre o universo pretendido) |

### 3.3. Dedução

\[
\boxed{s = \frac{p}{d}}
\]

**Justificativa:** Proporção elementar. Contagem de itens em dois conjuntos finitos.

### 3.4. Cálculo numérico

Exemplo: $d=6$ executores declarados, $p=4$ instalados.

\[
s = \frac{4}{6} = \frac{2}{3} \approx 0{,}666\ldots \approx 0{,}67
\]

Faltam:

\[
d - p = 6 - 4 = 2 \text{ executores ausentes}
\]

### 3.5. Interpretação e limites

$s \approx 0{,}67$ significa que cerca de dois terços do conjunto declarado estão presentes no ambiente. Isto **não** mede qualidade do Core, nem eficácia de integração, nem desempenho. É um inventário instantâneo de uma máquina específica.

---

## 4. Cobertura comparativa externa ($b$)

**Ocorrência no livro:** `mod-09a-comparada.tex` (leitura guiada, exemplo resolvido).

### 4.1. O problema concreto

O capítulo compara 11 elementos do Core com alternativas externas. Quantos desses 11 elementos têm uma comparação externa medida (mesma tarefa, mesma métrica, mesma condição)?

### 4.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $e$ | Número total de elementos comparados |
| $n$ | Número de elementos com comparação externa medida |
| $b$ | Cobertura comparativa externa |

### 4.3. Dedução

\[
\boxed{b = \frac{n}{e}}
\]

### 4.4. Cálculo numérico

O livro declara que, nesta conferência, não há medição externa comparável documentada para nenhum dos 11 elementos:

\[
n = 0, \qquad e = 11
\]

\[
b = \frac{0}{11} = 0 = 0\%
\]

Se houvesse medição em um único elemento:

\[
b = \frac{1}{11} \approx 0{,}0909 \approx 9{,}1\%
\]

### 4.5. Interpretação

$b = 0 \%$ indica **ausência total de evidência comparativa medida** neste inventário. Não prova que o Core é pior ou melhor que alternativas; prova apenas que não há comparação externa documentada aqui para sustentar afirmações de superioridade empírica.

---

## 5. Valor Preditivo Positivo (PPV) — argumento de Ioannidis

**Ocorrência no livro:** `mod-09a-comparada.tex` (exemplo de cálculo ilustrativo com $R=0{,}1$, $\alpha=0{,}05$).

### 5.1. O problema concreto

Quando um estudo estatístico declara um resultado "significativo" (p-valor abaixo de $\alpha$), qual é a probabilidade de que esse resultado seja de fato verdadeiro (e não um falso positivo)?

### 5.2. Definição dos símbolos

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $R$ | Razão prévia entre hipóteses verdadeiras e falsas no campo | $R = 0{,}1$ (uma hipótese verdadeira para dez falsas) |
| $\alpha$ | Taxa de falso positivo (nível de significância) | $\alpha = 0{,}05$ |
| $\beta$ | Taxa de falso negativo | $\beta = 0{,}8$ (poder 0,2) ou $\beta = 0{,}2$ (poder 0,8) |
| $1-\beta$ | Poder estatístico | 0,2 ou 0,8 |
| $PPV$ | Valor preditivo positivo (probabilidade de que um achado significativo seja verdadeiro) | — |

### 5.3. Dedução passo a passo da fórmula

#### Passo 1 — Normalização

Seja o número de hipóteses falsas igual a 1 unidade. Então, pela definição de $R$, o número de hipóteses verdadeiras é $R$. Total de hipóteses: $R + 1$.

**Por que normalizamos?** Porque apenas a **razão** entre verdadeiras e falsas importa para o cálculo de probabilidades condicionais.

#### Passo 2 — Verdadeiros positivos

Entre as $R$ hipóteses verdadeiras, o teste detecta (declara significativas) uma fração igual ao poder estatístico $1-\beta$.

\[
\text{VP} = R \cdot (1-\beta)
\]

**Justificativa:** Poder estatístico é definido como $P(\text{rejeitar } H_0 \mid H_0 \text{ falsa})$.

#### Passo 3 — Falsos positivos

Entre as 1 hipótese falsa (normalizada), o teste declara significativas uma fração igual ao nível de significância $\alpha$.

\[
\text{FP} = 1 \cdot \alpha = \alpha
\]

**Justificativa:** $\alpha$ é definido como $P(\text{rejeitar } H_0 \mid H_0 \text{ verdadeira})$.

#### Passo 4 — Total de achados significativos

Todo resultado declarado significativo é ou um verdadeiro positivo ou um falso positivo:

\[
\text{Total significativo} = \text{VP} + \text{FP} = R(1-\beta) + \alpha
\]

#### Passo 5 — Definição de PPV

O valor preditivo positivo é a fração de verdadeiros positivos entre todos os resultados significativos:

\[
PPV = \frac{\text{VP}}{\text{VP} + \text{FP}} = \frac{R(1-\beta)}{R(1-\beta) + \alpha}
\]

\[
\boxed{PPV = \frac{(1-\beta)R}{(1-\beta)R + \alpha}}
\]

#### Passo 6 — Forma algébrica equivalente

Expandindo o numerador:

\[
(1-\beta)R = R - \beta R
\]

Portanto:

\[
\boxed{PPV = \frac{(1-\beta)R}{R - \beta R + \alpha}}
\]

---

### 5.4. Cálculos numéricos detalhados

Fixamos $R = 0{,}1$ e $\alpha = 0{,}05$.

#### Caso A — Baixo poder estatístico: poder $= 0{,}2$, logo $\beta = 0{,}8$

\[
PPV = \frac{(1-0{,}8) \times 0{,}1}{0{,}1 - 0{,}8 \times 0{,}1 + 0{,}05}
\]

Numerador:

\[
(1-0{,}8) \times 0{,}1 = 0{,}2 \times 0{,}1 = 0{,}02
\]

Denominador:

\[
0{,}1 - 0{,}8 \times 0{,}1 + 0{,}05 = 0{,}1 - 0{,}08 + 0{,}05 = 0{,}02 + 0{,}05 = 0{,}07
\]

Dividindo:

\[
PPV = \frac{0{,}02}{0{,}07} = \frac{2}{7} \approx 0{,}2857\ldots \approx 0{,}286
\]

\[
\boxed{PPV \approx 28{,}6\%}
\]

#### Caso B — Alto poder estatístico: poder $= 0{,}8$, logo $\beta = 0{,}2$

\[
PPV = \frac{(1-0{,}2) \times 0{,}1}{0{,}1 - 0{,}2 \times 0{,}1 + 0{,}05}
\]

Numerador:

\[
(1-0{,}2) \times 0{,}1 = 0{,}8 \times 0{,}1 = 0{,}08
\]

Denominador:

\[
0{,}1 - 0{,}2 \times 0{,}1 + 0{,}05 = 0{,}1 - 0{,}02 + 0{,}05 = 0{,}08 + 0{,}05 = 0{,}13
\]

Dividindo:

\[
PPV = \frac{0{,}08}{0{,}13} = \frac{8}{13} \approx 0{,}61538\ldots \approx 0{,}615
\]

\[
\boxed{PPV \approx 61{,}5\%}
\]

---

### 5.5. Interpretação e argumento

Mesmo com nível de significância padrão ($\alpha = 0{,}05$), se a taxa-base de hipóteses verdadeiras é baixa ($R=0{,}1$) e o poder é baixo ($0{,}2$), apenas cerca de **28,6 %** dos achados significativos são verdadeiros. Com alto poder ($0{,}8$), sobe para **61,5 %**, mas nunca chega a 100 %.

**Argumento:** Isto sustenta a postura de cautela do livro: achados publicados precisam de confirmação independente. Não se deve declarar superioridade empírica sem controle de viés de desenho e relato completo. A fórmula não diz que "a maioria dos resultados é falsa" em absoluto; diz que, sob certas condições de baixa pré-probabilidade e baixo poder, a maioria dos resultados *significativos* pode ser falsa.

---

## 6. Tempo total de delegação negociada

**Ocorrência no livro:** `mod-07-integracoes.tex` (interpretação do Contract Net de Smith, 1980).

### 6.1. O problema concreto

Quando o orquestrador anuncia uma tarefa no Blackboard e agentes se voluntariam, qual é o tempo total desde o anúncio até a validação final da entrega?

### 6.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $T_{\text{total}}$ | Tempo total do ciclo de delegação |
| $T_{\text{anuncio}}$ | Tempo para publicar a tarefa no Blackboard |
| $T_{\text{janela}}$ | Duração da janela de proposta |
| $T_{\text{selecao}}$ | Tempo para avaliar candidatos e escolher o agente |
| $T_{\text{execucao}}$ | Tempo de execução da tarefa pelo agente escolhido |
| $T_{\text{validacao}}$ | Tempo de validação da entrega contra os critérios de aceitação |

### 6.3. Dedução

As etapas ocorrem em sequência (anúncio $\to$ janela $\to$ seleção $\to$ execução $\to$ validação). O tempo total de um processo sequencial é a soma dos tempos das etapas:

\[
\boxed{T_{\text{total}} = T_{\text{anuncio}} + T_{\text{janela}} + T_{\text{selecao}} + T_{\text{execucao}} + T_{\text{validacao}}}
\]

**Justificativa:** Adição de intervalos de tempo disjuntos e sucessivos.

### Observação sobre paralelos

Propostas podem chegar **em paralelo** durante a janela, mas a janela obedece a um prazo definido ($T_{\text{janela}}$); não se somam os tempos de preparação de cada proposta.

---

## 7. Similaridade de Jaccard para roteamento de capacidades

**Ocorrência no livro:** `gen_mod14_ativacao.py` (cálculo para `mod-02-orquestracao.tex`).

### 7.1. O problema concreto

Dado um gatilho de tarefa (conjunto de tokens $K$) e as capacidades declaradas de um agente $a$ (conjunto $C_a$), qual é o grau de sobreposição entre eles?

### 7.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $K$ | Conjunto de tokens extraídos do gatilho da tarefa |
| $C_a$ | Conjunto de tokens de capacidades declaradas pelo agente $a$ |
| $K \cap C_a$ | Interseção (tokens comuns a ambos) |
| $K \cup C_a$ | União (todos os tokens distintos que aparecem em pelo menos um dos conjuntos) |
| $|X|$ | Cardinalidade (número de elementos) do conjunto $X$ |
| $A(a)$ | Escore de ativação do agente $a$ |

### 7.3. Dedução

O índice de Jaccard mede a sobreposição entre dois conjuntos finitos como a fração de elementos comuns sobre o total de elementos distintos:

\[
\boxed{A(a) = \frac{|K \cap C_a|}{|K \cup C_a|}}
\]

**Justificativa:** Definição padrão do coeficiente de similaridade de Jaccard para conjuntos finitos. O numerador conta o que é compartilhado; o denominador conta o universo de tokens relevantes.

---

### 7.4. Cálculo numérico exemplo

Suponha:
- $K = \{ \text{busca, fonte, artigo} \}$, então $|K| = 3$
- $C_a = \{ \text{busca, resumo, artigo} \}$, então $|C_a| = 3$

Interseção:

\[
K \cap C_a = \{ \text{busca, artigo} \}, \qquad |K \cap C_a| = 2
\]

União:

\[
K \cup C_a = \{ \text{busca, fonte, artigo, resumo} \}, \qquad |K \cup C_a| = 4
\]

Aplicando a fórmula:

\[
A(a) = \frac{2}{4} = 0{,}5
\]

\[
\boxed{A(a) = 0{,}5 = 50\%}
\]

### 7.5. Interpretação

Quanto mais próximo de 1, maior a sobreposição entre o que a tarefa pede e o que o agente declara saber fazer. É um critério de casamento semântico, **não** uma garantia de qualidade da entrega. O gate SDD/TDD continua obrigatório.

---

## 8. Taxa de ativação de DOIs

**Ocorrência no livro:** `mod-11-apendices.tex` (seção de ativação e cálculo da biblioteca de citações).

### 8.1. O problema concreto

A biblioteca do manual contém referências com DOI. Qual é a fração de DOIs ativos (resolvíveis) em relação ao total de DOIs cadastrados?

### 8.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $D_t$ | Número total de DOIs na biblioteca |
| $D_a$ | Número de DOIs ativos (resolvíveis) |

### 8.3. Dedução

\[
\boxed{\text{taxa de ativação} = \frac{D_a}{D_t}}
\]

**Justificativa:** Proporção elementar. Falha de acesso exige triagem de metadados, nova tentativa e eventual correção. Indisponibilidade temporária não comprova DOI inválido e não determina remoção automática da referência.

---

## 9. Cobertura de dimensões de ficha

**Ocorrência no livro:** `mod-12-fichas-nucleo.tex` (leitura das fichas).

### 9.1. O problema concreto

Cada ficha do núcleo deve preencher 13 dimensões. Qual é a cobertura de uma ficha dada?

### 9.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $d_p$ | Número de dimensões preenchidas na ficha |
| $d_t = 13$ | Número total de dimensões exigidas |

### 9.3. Dedução

\[
\boxed{\text{cobertura} = \frac{d_p}{13}}
\]

**Justificativa:** Proporção elementar; o denominador é fixo (13) por definição da estrutura da ficha. O leitor confere 13/13 antes de aceitar a ficha.

---

## 10. PRISMA — contagem de registros em revisão sistemática

**Ocorrência no livro:** `mod-06-ciencia.tex` e `mod-11-apendices.tex` (interpretação de PAGE et al., 2021).

### 10.1. O problema concreto

Em uma revisão sistemática, registros são identificados, duplicatas removidas, triados, buscados, excluídos e incluídos. Como garantir que as contagens são coerentes em cada etapa?

### 10.2. Definição dos símbolos

| Símbolo | Significado |
|---------|-------------|
| $N_i$ | Registros identificados inicialmente |
| $N_d$ | Duplicatas removidas |
| $N_s$ | Registros submetidos à triagem |
| $N_e$ | Registros excluídos na triagem |
| $N_b$ | Relatórios buscados para leitura integral |
| $N_{nr}$ | Relatórios não recuperados |
| $N_f$ | Relatórios avaliados integralmente |
| $N_x$ | Excluídos após leitura integral |
| $N_{inc}$ | Relatórios incluídos na revisão |

### 10.3. Dedução das igualdades de conservação

#### Passo 1 — Da identificação à triagem

Todo registro identificado é ou uma duplicata (removida) ou segue para triagem:

\[
\boxed{N_i = N_d + N_s}
\]

**Justificativa:** Partição do conjunto de registros identificados em duas classes disjuntas: duplicatas e não duplicatas.

#### Passo 2 — Da triagem à busca integral

Todo registro triado é ou excluído na triagem ou segue para busca de leitura integral:

\[
\boxed{N_s = N_e + N_b}
\]

**Justificativa:** Partição do conjunto triado em excluídos e não excluídos (buscados).

#### Passo 3 — Da busca à avaliação integral

Todo relatório buscado é ou não recuperado ou avaliado integralmente:

\[
\boxed{N_b = N_{nr} + N_f}
\]

**Justificativa:** Partição do conjunto buscado em não recuperados e recuperados (avaliados).

#### Passo 4 — Da avaliação à inclusão

Todo relatório avaliado é ou excluído após leitura integral ou incluído na revisão:

\[
\boxed{N_f = N_x + N_{inc}}
\]

**Justificativa:** Partição do conjunto avaliado em excluídos finais e incluídos finais.

---

### 10.4. Interpretação

Estas igualdades expõem lacunas de contagem: se os números não batem, algo foi perdido ou mal contabilizado. Porém, **não certificam** a qualidade metodológica nem a verdade dos estudos incluídos. São verificações de consistência interna do fluxo, não validação científica externa.

---

## 11. Cobertura de rastro ($c = n_p/n_r$)

**Ocorrência no livro:** `mod-09-infra.tex` (leitura guiada, definições e exemplo resolvido).

### 11.1. O problema concreto

Um pacote de evidências precisa dizer quais testes foram executados. Como medir a fração de operações que possuem registro pertinente em relação ao total de operações observadas?

### 11.2. Definição dos símbolos

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $n_p$ | Número de operações com registro pertinente | — |
| $n_r$ | Número total de operações observadas | — |
| $c$ | Cobertura de rastro | — |

### 11.3. Dedução de $c = n_p/n_r$

\paragraph{Passo 1 — O que queremos medir.}
Queremos saber qual fração das operações observadas possui um registro pertinente. Isso é uma simples divisão: operações com registro dividido pelo total de operações observadas.

\paragraph{Passo 2 — Divisão de contagens.}

\[
\boxed{c = \frac{n_p}{n_r}}
\]

**Justificativa:** Esta é a definição elementar de proporção: parte sobre todo. Não há cálculo diferencial nem integral; é aritmética de contagem.

### 11.4. Interpretação e limites

A cobertura de rastro documenta que operações tiveram registro, mas **não mede** a qualidade desse registro nem a correção do mundo externo. A simples existência de registros não mede disponibilidade operacional; para isso, exige-se uma definição de sucesso, intervalo e população de chamadas.

---

## 12. Orçamento de peso para publicação

**Ocorrência no livro:** `mod-09-infra.tex` (exemplo resolvido, guarda de peso).

### 12.1. O problema concreto

Um pacote de publicação contém 68 arquivos, 1.240 MiB no total, e um único arquivo de áudio de 1.180 MiB. Os limites configurados são: 1.000 MiB por diretório e 25 MiB por arquivo. O pacote passa na guarda de publicação?

### 12.2. Definição dos símbolos

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $W$ | Peso total do diretório | $W = 1.240$ MiB |
| $W_{limite}$ | Limite de peso do diretório | $W_{limite} = 1.000$ MiB |
| $w_a$ | Peso de um arquivo individual | $w_a = 1.180$ MiB |
| $w_{limite}$ | Limite de peso por arquivo | $w_{limite} = 25$ MiB |

### 12.3. Dedução e cálculo

\paragraph{Passo 1 — Guarda de total.}
Comparamos o peso total com o limite de diretório:

\[
1.240 > 1.000 \text{ MiB} \Rightarrow \text{\textbf{denegado}} \text{ (limite de diretório excedido)}
\]

\paragraph{Passo 2 — Guarda de arquivo.}
Comparamos o peso do arquivo com o limite por arquivo:

\[
1.180 > 25 \text{ MiB} \Rightarrow \text{\textbf{denegado}} \text{ (limite de arquivo excedido)}
\]

\paragraph{Passo 3 — Correção.}
O arquivo de áudio precisa ser dividido ou reprocessado. A segunda falha é mais grave porque obriga a mudar a arquitetura do feed, não apenas um parâmetro de build.

### 12.4. Observação sobre unidades

Um MiB corresponde a $2^{20}$ bytes, enquanto um MB decimal corresponde a $10^6$ bytes. Confundi-los altera a comparação. O orçamento é um teto, e a folga é a diferença entre teto e consumo medido. Não há uma fração universal de ocupação que certifique publicação segura.

---

## 13. FAIR como índice de completude ($C_m = n_p/n_r$)

**Ocorrência no livro:** `mod-09-infra.tex` (interpretação de Wilkinson et al., 2016).

### 13.1. O problema concreto

Como medir, como diagnóstico interno (não como certificação FAIR), se um artefato atende aos campos obrigatórios de um esquema de proveniência?

### 13.2. Definição dos símbolos

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $n_p$ | Número de campos obrigatórios preenchidos | — |
| $n_r$ | Número total de campos obrigatórios requeridos | — |
| $C_m$ | Índice de completude do esquema | — |

### 13.3. Dedução

\[
\boxed{C_m = \frac{n_p}{n_r}}
\]

**Justificativa:** Proporção elementar. Se todos os campos obrigatórios estão preenchidos, $n_p = n_r$ e $C_m = 1$, indicando completude do esquema adotado.

### 13.4. Interpretação e limites

$C_m = 1$ indica completude do esquema adotado, **não** correção do conteúdo. A correção ainda depende da conferência da fonte e da validação do resultado. Este é um diagnóstico interno — não uma certificação FAIR.

---

## Conclusão didática

Todas as fórmulas apresentadas seguem o mesmo princípio nussenzveígiano: partem de uma situação concreta, definem cada símbolo antes do uso, deduziu-se a relação sem pular etapas, calcula-se com números reais e interpreta-se com modéstia. Nenhuma delas prova qualidade científica, eficácia ou verdade absoluta por si só. Elas são instrumentos de **transparência**: tornam explícitos os critérios, os contornos e os limites do que pode ser afirmado sobre o sistema. Decoreba é substituída por compreensão da estrutura lógica de cada igualdade.

---

## 14. Redução do conjunto de candidatos ($M/k$)

**Ocorrência no livro:** `mod-02-orquestracao.tex` (exercício de fixação).

### 14.1. O problema concreto

No roteamento do Blackboard, há $M$ candidatos disponíveis e apenas $k$ posições a serem examinadas com mais atenção. Qual é a fração de redução do conjunto a examinar?

### 14.2. Definição dos símbolos

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $M$ | Número total de candidatos | $M = 40$ |
| $k$ | Número de posições a examinar | $k = 5$ |
| $M/k$ | Fator de redução hipotética | — |

### 14.3. Dedução de $M/k$

\paragraph{Passo 1 — O que queremos medir.}
Queremos saber quantas vezes o conjunto total é maior do que o subconjunto selecionado para análise mais detalhada. Isso é uma simples divisão: total dividido pelo subconjunto.

\paragraph{Passo 2 — Divisão de contagens.}

\[
\boxed{\frac{M}{k} = \frac{40}{5} = 8}
\]

**Justificativa:** Proporção elementar. O resultado 8 significa que o conjunto total é 8 vezes maior do que o subconjunto selecionado.

### 14.4. Interpretação e limites

O quociente $M/k = 8$ trata da redução hipotética do conjunto a examinar, **não** como um ganho de velocidade medido. É uma conta didática para ilustrar filtragem, não uma medição de desempenho do sistema.

---

## 15. Seleção por custo mínimo ($i^*=\mathrm{arg\,min}_{i\in C}K_i$)

**Ocorrência no livro:** `mod-02-orquestracao.tex` (interpretação do protocolo de rede por contratos de Smith, 1980).

### 15.1. O problema concreto

No protocolo de rede por contratos, o gerente compara propostas de candidatos e escolhe aquele com menor custo declarado entre os que satisfazem os requisitos. Como formalizar essa escolha?

### 15.2. Definição dos símbolos

| Símbolo | Significado | Valor no exemplo |
|---------|-------------|------------------|
| $C$ | Conjunto de candidatos que satisfazem os requisitos | — |
| $i$ | Um candidato qualquer | — |
| $K_i$ | Custo declarado pelo candidato $i$ | — |
| $i^*$ | Candidato escolhido (menor custo) | — |
| $\mathrm{arg\,min}$ | Operação que retorna o índice que minimiza | — |

### 15.3. Dedução de $i^*=\mathrm{arg\,min}_{i\in C}K_i$

\paragraph{Passo 1 — O conjunto elegível.}
Apenas candidatos que satisfazem todos os requisitos obrigatórios entram no conjunto $C$. Um candidato fora de $C$ não se torna elegível apenas por oferecer menor custo.

\paragraph{Passo 2 — A operação de escolha.}
Entre os candidatos em $C$, escolhe-se aquele cujo custo declarado $K_i$ é mínimo. A notação $\mathrm{arg\,min}$ retorna o índice $i$ que minimiza a função:

\[
\boxed{i^* = \mathrm{arg\,min}_{i\in C} K_i}
\]

**Justificativa:** Essa fórmula expressa que a escolha é feita sobre o conjunto restrito de elegíveis, usando o custo declarado como critério de ordenação. Ela separa elegibilidade (pertencer a $C$) de seleção (menor custo dentro de $C$).

### 15.4. Exemplo numérico

Neste modelo hipotético de custo, suponha cinco candidatos: três atendem capacidades; apenas $c_1$ e $c_2$ também passam pelo gate comportamental. Portanto $C=\{c_1,c_2\}$. O candidato $c_3$ está excluído antes da minimização. Os custos declarados são:

| Candidato | Atende requisitos? | Custo $K_i$ |
|-----------|-------------------|-------------|
| $c_1$ | Sim | 10 |
| $c_2$ | Sim | 7 |
| $c_3$ | Não: falhou o gate | 12 (excluído) |

\[
i^* = \mathrm{arg\,min}_{i\in\{c_1,c_2\}} K_i = c_2
\]

O candidato escolhido é $c_2$, com custo 7.

### 15.5. Interpretação e limites

Essa conta ilustra filtragem e seleção por custo mínimo; **não mede precisão** nem o número de modelos executados. Um candidato com menor custo declarado não é automaticamente o melhor entregador; a validação da entrega continua sendo obrigatória via gate SDD/TDD.

---

## Conclusão didática

Todas as fórmulas apresentadas seguem o mesmo princípio nussenzveígiano: partem de uma situação concreta, definem cada símbolo antes do uso, deduziu-se a relação sem pular etapas, calcula-se com números reais e interpreta-se com modéstia. Nenhuma delas prova qualidade científica, eficácia ou verdade absoluta por si só. Elas são instrumentos de **transparência**: tornam explícitos os critérios, os contornos e os limites do que pode ser afirmado sobre o sistema. Decoreba é substituída por compreensão da estrutura lógica de cada igualdade.
