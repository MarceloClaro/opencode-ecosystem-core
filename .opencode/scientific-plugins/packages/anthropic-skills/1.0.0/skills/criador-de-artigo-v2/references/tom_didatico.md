# 自主学习文风 — 风格、叙事与密度指南

## 重要说明
**本文件以中文编写，供内部指令参考。所有输出须以正式巴西葡萄牙语书写。**

---

## 为何存在本文件（以及为何关键）
95页的文章若每页仅是堆砌文字，价值等同于0页。
自主学习文风确保每一页都具有实质性的学术价值：
教育读者、推进论证、深化理解、建立对话。
这正是10/10与7/10的区别。

---

## 原则1：不预设知识（首次出现即定义）

**错误（不得采用）：**
"Utilizou-se o algoritmo LSTM para modelagem temporal."

**正确（须采用）：**
"Utilizou-se a Rede Neural LSTM (Long Short-Term Memory, ou Memória de Longo
e Curto Prazo), uma arquitetura de aprendizado profundo especialmente projetada para
capturar dependências temporais em sequências de dados (HOCHREITER; SCHMIDHUBER,
1997, p. 1735). Diferentemente de redes neurais convencionais, o LSTM possui células
de memória que controlam o fluxo de informação ao longo do tempo — analogamente a
um sistema de arquivos que decide o que manter, o que descartar e o que recuperar
a cada instante — tornando-a adequada para análises longitudinais como a conduzida
neste estudo."

**原则：** 类比 → 正式定义（含引用+页码）→ 与文章用途的关联。

---

## 原则2：锚定类比（抽象概念须有具体类比）

对于每个抽象概念，须在正式定义之前提供具体类比。

**结构（固定顺序）：**
1. 日常类比（1句，读者熟悉的事物）
2. 正式技术定义（1-2句，含引用+页码）
3. 在本文章语境中的应用（1句）

**示范（须以葡萄牙语书写）：**
"Assim como um filtro de café retém o pó e deixa passar apenas o líquido,
um filtro de Kalman retém o ruído de mensuração e extrai o estado real
subjacente do sistema. Formalmente, o filtro de Kalman é um algoritmo recursivo
de estimação de estados que minimiza o erro quadrático médio em sistemas lineares
com ruído gaussiano (KALMAN, 1960, p. 35-45). No presente estudo, este algoritmo
foi empregado para [具体用途]."

---

## 原则3：明确过渡（每章节开篇须宣告目的）

每个章节须以宣告其与前一章节关系及其目的的段落开始。

**各章节必须使用的过渡语（须以葡萄牙语书写）：**

开始文献综述时：
> "Tendo delimitado o problema central e os objetivos deste estudo, torna-se
> necessário mapear o estado atual do conhecimento sobre [tema]. Esta revisão
> não é um inventário exaustivo da literatura — é, antes, uma argumentação
> fundamentada sobre o que se sabe, o que se debate e o que permanece sem
> resposta, justificando assim a necessidade e a originalidade deste artigo."

开始方法论时：
> "Com base no problema delineado na Introdução e no referencial teórico
> construído na seção anterior, apresenta-se agora o percurso metodológico
> escolhido para responder à questão de pesquisa. Cada decisão metodológica
> é acompanhada de sua justificativa explícita, pois a transparência
> procedimental é condição sine qua non de replicabilidade científica."

开始结果时：
> "Esta seção apresenta os achados empíricos obtidos mediante o percurso
> metodológico descrito anteriormente. Os resultados são expostos seguindo
> a ordem dos objetivos específicos declarados na Introdução, garantindo
> rastreabilidade entre propósito e achado. A interpretação e contextualização
> desses resultados é integralmente reservada para a seção de Discussão."

开始讨论时：
> "Os resultados reportados na seção anterior adquirem sentido pleno apenas
> quando confrontados com o referencial teórico e com os achados da literatura
> do campo. Esta discussão percorre quatro movimentos: (1) interpretação dos
> achados principais; (2) diálogo com estudos concordantes e discordantes;
> (3) implicações teóricas e práticas; e (4) limitações e agenda futura."

开始结论时：
> "Este artigo partiu do seguinte problema: [重述P]. Percorreu-se um itinerário
> que compreendeu [综合方法]。Retoma-se agora esse percurso para avaliar em
> que medida os objetivos foram cumpridos, as hipóteses, respondidas, e qual
> contribuição efetiva este trabalho oferece ao campo."

---

## 原则4："为何重要"原则（先于"如何完成"）

在每个基础性或方法论子章节之前，须有1-2行说明该主题对文章中心论点的相关性。

**模板（须以葡萄牙语书写）：**
> "[Nome do conceito/método] é central para este estudo porque [直接与问题/假设/目标的联系].
> Sem compreender [X], não é possível avaliar [Y], que constitui o cerne
> da questão investigada."

---

## 原则5：复杂性递进（简单→正式→细微差别→应用）

在综述和方法论章节中，按固定顺序排列：
1. **基础概念**：任何受过教育的读者能理解的定义
2. **正式展开**：技术术语+引用+页码
3. **细微差别与争议**：文献分歧之处+对立立场
4. **在本文章中的应用**：如何在本研究背景下应用

---

## 原则6：六句段落结构（密度保证）

**Demonstração do Erro (O que o MASWOS recusa):**
- Textos robóticos que apenas preenchem os 6 slots mecanicamente.
- Repetição do mesmo argumento com palavras diferentes apenas para ganhar volume (fluffing).

### Regra Anti-Redundância e Fluidez (Densidade ≠ Verbosidade)
Cumprir a meta de 110 páginas e usar parágrafos estruturados **jamais** pode resultar em um texto desconectado ou massante.
1. **Avanço Substancial:** Cada parágrafo deve introduzir uma ideia, dado ou análise NOVA técnica e logicamente conectada à anterior.
2. **Coesão Orgânica:** As transições entre os blocos das 6 frases devem ser invisíveis e elegantes, promovendo uma leitura envolvente e não mecânica.
3. **Profundidade, não Repetição:** Volume se atinge descendo verticalmente no tema (explicando as controvérsias, os microdados, os impactos teóricos), e NÃO andando em círculos verbais.

```
[第1句] 主题句 — 段落中心思想（明确、无歧义，推进论点）
[第2句] 展开 — 扩展或具体说明该思想（有机衔接，绝不重复上一句）
[第3句] 证据 — 数据/引用（含页码）/具体示例
[第4句] 分析 — 证据说明什么？含义是什么？
[第5句] 深化 — 对立观点/细微差别/限制条件（含引用）
[第6句] 连接 — 与文章中心论点或下一段落的流畅过渡
```

**示范（须以葡萄牙语书写）：**
[第1句] "A regulação emocional constitui um dos construtos centrais na
         compreensão do comportamento adaptativo humano.
[第2句]  Trata-se da capacidade de modular a intensidade, duração e qualidade
         das respostas emocionais em função das demandas situacionais.
[第3句]  Gross (1998, p. 275) demonstrou, em estudo seminal com 120 participantes,
         que estratégias de reavaliação cognitiva produzem redução significativa
         da experiência emocional negativa [d = 0.72, IC95%(0.51, 0.93)].
[第4句]  Esses dados indicam que a regulação emocional não é um traço fixo,
         mas um processo maleável passível de treinamento e intervenção.
[第5句]  Contudo, Aldao et al. (2010, p. 218) alertam que a eficácia das
         estratégias de regulação varia substancialmente conforme o contexto
         clínico, sugerindo que generalizações indiscriminadas são problemáticas.
[第6句]  Essa tensão entre maleabilidade e contextualidade é diretamente
         relevante para o presente estudo, que investiga [具体联系]."

---

## 原则7：语言实用指南（输出语言：葡萄牙语）

### 人称
- 主要使用第三人称/无人称（ABNT标准）
- 推荐："investigou-se"、"observou-se"、"verificou-se"、"procedeu-se a"
- 国际期刊可使用第一人称复数："investigamos"、"observamos"
- 巴西学术文章中禁止单数第一人称：✗ "eu observei"

### 时态（须严格遵守）
- **方法论**：完成时 — "utilizou-se"、"foram coletados"
- **结果**：完成时 — "os resultados indicaram"、"verificou-se"
- **既有理论**：现在时 — "a teoria prevê"、"o modelo propõe"
- **含义/结论**：现在时 — "isso implica"、"os achados sugerem"
- **未来研究**：将来时 — "investigações futuras poderão"

### 段落密度规则
- 每段4-6句（最多8句）
- 每句最多35个词
- 每段一个思想——不在一段中"倾倒"多个概念
- 禁止孤立的单句段落（碎片化）
- **95页的密度来源：** 分析深度 | 文献对话 | 类比 | 表格 | 例证——不是重复

### 推荐的篇章标记词（须以葡萄牙语书写）
**递进：** "Ademais"、"Além disso"、"Acrescenta-se que"、"Cumpre destacar que"
**对比：** "Entretanto"、"Em contraposição"、"Não obstante"、"Diversamente"
**因果：** "Em virtude de"、"Dado que"、"Porquanto"、"Haja vista que"
**结论：** "Portanto"、"Dessa forma"、"Logo"、"Depreende-se que"
**举例：** "A título de ilustração"、"Como exemplo paradigmático"、"Cite-se o caso de"
**综合：** "Em síntese"、"Depreende-se, portanto"、"Conclui-se que"
**位置：** "À luz do exposto"、"Diante do que foi apresentado"

### 须避免的表达（立即降分）
❌ "É importante ressaltar que..." → 直接陈述，不需要宣告
❌ "Como foi mencionado anteriormente..." → 注明章节和段落
❌ "Obviamente" / "Claramente" / "Evidentemente" → 学术文章禁用
❌ "Etc." → 须始终具体列举所有项目
❌ 无证据的形容词：须以数据或引用证明
❌ "Existem vários estudos que..." → 须引用具体研究
❌ "De acordo com alguns autores..." → 须引用哪些作者

---

## 原则8：对话式写作（而非独白式写作）

每个主要主张须有声音对话。禁止将文章写成一系列无争议的陈述。

**每个实质性声明的对话结构（须以葡萄牙语书写）：**
> "[作者A, 年份, p. XX] afirma que [主张X]。
> Corroborando essa perspectiva, [作者B, 年份, p. XX] demonstrou que [补充证据]。
> Em contraposição, [作者C, 年份, p. XX] argumenta que [批评/替代观点],
> apontando como limitação [具体局限]。
> [作者D, 年份, p. XX] oferece uma posição intermediária ao sugerir que
> [综合]。
> Diante dessas perspectivas divergentes, o presente estudo adota [立场],
> porque [论证]。"

---

## 自主学习文风最终核查清单

在提交任何章节之前，核查：

□ 所有技术术语在首次出现时均已定义（含类比）？
□ 每个抽象概念有类比或具体示例？
□ 每个章节以连接前一章节的明确过渡段开始？
□ 每个子章节有"为何重要"句子？
□ 每段具有6句结构（主题-展开-证据-分析-深化-连接）？
□ 每个主要主张有多种声音的对话（支持方+批评方+综合）？
□ 读者能从问题到结论跟随叙述主线？
□ 该章节是否因分析深度而厚实，而非因填充而厚实？
□ 一位非该领域专家的硕士研究生能完全理解该内容？

---

## Protocolo de Microauditoria Didatica

Todo capitulo deve ser verificavel frase a frase, paragrafo a paragrafo e referencia a referencia. A didatica deixa de ser apenas um ideal de estilo e passa a ser tambem um criterio de auditabilidade.

### Sequencia obrigatoria por paragrafo

1. Classificar cada frase por funcao: `D` definicao, `E` evidencia, `A` analise, `C` contraste, `L` limitacao ou `T` transicao.
2. Garantir que toda frase `E`, `A`, `C` ou `L` esteja ancorada em fonte identificavel ou em resultado proprio explicitamente apontado.
3. Distinguir no texto o que e dado da fonte, o que e interpretacao do autor citado e o que e inferencia do artigo.
4. Encerrar o paragrafo com uma frase de conexao ao problema, objetivo, hipotese ou implicacao do estudo.

### Regra de proximidade

- A citacao deve aparecer na mesma frase da afirmacao ou, no maximo, na frase imediatamente seguinte.
- Se uma frase sintetiza duas ou mais fontes, a sintese deve explicitar convergencia, divergencia ou complementaridade.
- Se a interpretacao ultrapassa o que a fonte declara expressamente, o texto deve dizer isso de forma honesta.

### Regra de densidade evidencial

- Paragrafos conceituais: pelo menos uma fonte definicional e, quando houver disputa terminologica, uma fonte de contraste.
- Paragrafos de revisao: pelo menos uma fonte de suporte e uma de tensao critica, sempre que a literatura relevante for controversa.
- Paragrafos metodologicos: pelo menos uma fonte de suporte ao metodo e uma observacao explicita sobre limites, vieses ou condicoes de aplicacao.
- Paragrafos de resultados: toda afirmacao substantiva deve remeter a tabela, figura, estatistica ou saida analitica correspondente.

### Checklist adicional de fechamento

□ Cada frase possui funcao discursiva clara?
□ Cada afirmacao verificavel tem ancoragem documental identificavel?
□ Cada paragrafo separa definicao, evidencia e interpretacao sem mistura opaca?
□ Cada paragrafo termina reconectando o texto ao fio principal do artigo?
□ Existe pelo menos uma tensao, limite ou contraponto onde a literatura relevante nao e consensual?
