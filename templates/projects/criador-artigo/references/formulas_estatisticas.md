<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# 公式与统计分析指南 — Qualis A1标准

## 重要说明
**本文件以中文编写，供内部指令参考。所有输出须以正式巴西葡萄牙语书写。**

---

## 🔴 撰写方法论(Cap.3)和结果(Cap.4)前必须阅读本文件

---

## 1. 六要素模型 — 每个统计方法的强制结构

```
对于文章中使用的每一个统计方法，须按以下6个要素完整呈现：

要素1 — 类比解释（Analogia）：
  · 用2句日常语言解释该方法"做什么"
  · 面向非专家读者（满足教学性原则）
  · 示例（测试t）："O teste t funciona como uma balança que compara
    as médias de dois grupos. Ele nos diz se a diferença observada
    entre os grupos é grande o suficiente para não ser atribuída ao acaso."

要素2 — 显式公式（Fórmula Explícita）：
  · 完整数学公式（不可省略）
  · 每个符号紧跟定义："onde: X̄ = média amostral; s = desvio padrão;
    n = tamanho da amostra"
  · 公式来源引用：(STUDENT, 1908, p. 13) 或教材引用

要素3 — 前提验证（Verificação de Pressupostos）：
  · 列出该方法的所有前提条件
  · 说明如何验证每个前提（用什么检验）
  · 报告本研究中的验证结果
  · 若前提不满足 → 说明采取的替代措施

要素4 — 三层引用（Citação em Três Camadas）：
  · 第1层：方法的原始提出者/创建者
    例："proposto originalmente por Student (1908, p. 13)"
  · 第2层：领域中推荐使用该方法的文献
    例："recomendado para amostras pequenas por Field (2018, p. 342)"
  · 第3层：对该方法的批评性文献
    例："embora Wilcox (2017, p. 78) argumente que o teste t é
    sensível a outliers em amostras com n < 30"

要素5 — 完整报告（Relatório Completo）：
  · 统计量 + 自由度 + p值 + 效应量 + IC95%
  · 示例：t(43) = 2,87; p = 0,006; d = 0,86 [IC95%: 0,24–1,47]
  · 所有数值使用逗号为小数点（ABNT巴西标准）

要素6 — 通俗解读（Interpretação Acessível）：
  · "Em termos práticos, isto significa que..."
  · 将统计结果翻译为实际含义
  · 包含效应量的实际意义解读
  · 示例："Em termos práticos, a diferença de 0,86 desvios padrão
    indica um efeito grande: empresas com IA apresentam eficiência
    substancialmente superior, equivalente a um ganho de 23% na
    produtividade média."
```

---

## 2. 统计方法选择决策矩阵

```
选择统计方法须基于以下决策流程：

步骤1 — 数据类型：
  连续（intervalar/razão）→ 步骤2
  类别（nominal）→ 卡方 / Fisher精确检验
  序数（ordinal）→ 非参数检验

步骤2 — 前提检验结果：
  正态分布 + 方差齐性 → 参数检验（步骤3a）
  非正态 或 方差不齐 → 非参数检验（步骤3b）

步骤3a — 参数检验选择：
  2组独立 → 测试t独立样本
  2组配对 → 测试t配对样本
  ≥3组独立 → ANOVA单因素
  ≥3组 × ≥2因素 → ANOVA多因素
  连续×连续 → Pearson相关 / 回归

步骤3b — 非参数检验选择：
  2组独立 → Mann-Whitney U
  2组配对 → Wilcoxon符号秩
  ≥3组独立 → Kruskal-Wallis
  ≥3组配对 → Friedman
  连续×连续 → Spearman相关

每个选择须在方法论章节中用引用论证（见六要素-要素4）。
```

---

## 3. 效应量报告标准

```
绝对强制：所有推断统计须报告效应量及其解读。

┌──────────────────┬──────────────┬──────────────────────┐
│ 检验类型          │ 效应量指标    │ 解读区间              │
├──────────────────┼──────────────┼──────────────────────┤
│ 测试t            │ d de Cohen   │ 0,20=小 0,50=中 0,80=大│
│ ANOVA            │ η²p (eta²p)  │ 0,01=小 0,06=中 0,14=大│
│ 卡方             │ V de Cramér  │ 0,10=小 0,30=中 0,50=大│
│ 相关             │ r            │ 0,10=小 0,30=中 0,50=大│
│ 回归             │ R² / f²Cohen │ 0,02=小 0,15=中 0,35=大│
│ 非参数           │ r = z/√N     │ 0,10=小 0,30=中 0,50=大│
└──────────────────┴──────────────┴──────────────────────┘

报告格式示例：
  · d = 0,86（efeito grande, segundo Cohen, 1988, p. 25）
  · η²p = 0,09（efeito médio, segundo Cohen, 1988, p. 283）

引用来源：
  COHEN, J. Statistical power analysis for the behavioral sciences.
  2. ed. Hillsdale: Lawrence Erlbaum, 1988.
```

---

## 4. 前提检验完整报告

```
在方法论章节中，须报告以下所有适用的前提检验：

正态性（Normalidade）：
  □ 检验：Shapiro-Wilk（每组每变量）
  □ 报告：W(n) = X,XX; p = X,XXX
  □ 若p > 0,05 → 假设正态成立
  □ 若p ≤ 0,05 → 使用非参数替代
  □ 补充：Q-Q图可视化验证

方差齐性（Homogeneidade de Variâncias）：
  □ 检验：Levene
  □ 报告：F(gl1, gl2) = X,XX; p = X,XXX
  □ 若p > 0,05 → 假设齐性成立
  □ 若p ≤ 0,05 → 使用Welch修正

多重共线性（Multicolinearidade）— 回归模型：
  □ 指标：VIF (Variance Inflation Factor)
  □ 标准：VIF < 5（保守标准：VIF < 3）
  □ 报告每个预测变量的VIF值

残差独立性（Independência dos Resíduos）— 回归模型：
  □ 检验：Durbin-Watson
  □ 可接受范围：1,5 – 2,5
  □ 报告：DW = X,XX

异常值（Outliers）：
  □ 指标：Cook距离
  □ 标准：Cook D < 1,0
  □ 报告异常值数量及处理方式

功效/样本量计算（Cálculo de Poder）：
  □ 软件：G*Power（含引用）
  □ 参数：效应量预期值 + alpha + 功效(1-beta)
  □ 报告：计算的最低样本量 vs 实际样本量
  □ 引用：Faul, F. et al. (2007). G*Power 3: A flexible statistical
    power analysis program. Behavior Research Methods, 39(2), 175-191.
```

---

## 5. 多重比较校正

```
当进行多次统计检验时，须应用多重比较校正：

方法选择：
  □ Bonferroni — 保守，适用于检验数量少（≤5）
    alpha调整 = 0,05 / 检验次数
  □ Holm-Bonferroni — 较Bonferroni更有功效
  □ Benjamini-Hochberg (FDR) — 控制假发现率，检验数量多时推荐
  □ Tukey HSD — ANOVA事后比较专用

报告要求：
  □ 明确说明使用了哪种校正方法
  □ 报告校正前和校正后的p值（或仅报告校正后并说明）
  □ 引用校正方法的原始文献
```

---

## 6. p值和统计报告格式（ABNT巴西标准）

```
p值格式：
  ✓ p = 0,034（精确值，逗号为小数点）
  ✓ p < 0,001（当p极小时）
  ✗ p = 0,000（永远不可 — 用p < 0,001）
  ✗ p = .034（英文格式 — 用逗号）
  ✗ p = 0.034（英文小数点 — 用逗号）

数字格式：
  □ 小数点 = 逗号(,)：M = 3,45
  □ 千位分隔符 = 点(.)：n = 1.245
  □ 统计符号斜体：M, DP, t, F, p, r, n, d, η², χ²

完整报告模板（按检验类型）：

  测试t：
    t(gl) = X,XX; p = 0,XXX; d = X,XX [IC95%: X,XX–X,XX]

  ANOVA：
    F(gl1, gl2) = X,XX; p = 0,XXX; η²p = 0,XX [IC95%: X,XX–X,XX]

  卡方：
    χ²(gl) = X,XX; p = 0,XXX; V = 0,XX

  相关：
    r(n-2) = 0,XX; p = 0,XXX [IC95%: 0,XX–0,XX]

  回归：
    β = X,XX; t = X,XX; p = 0,XXX; R² = 0,XX; f² = 0,XX

  非参数（Mann-Whitney）：
    U = XXXX; z = X,XX; p = 0,XXX; r = 0,XX
```

---

## 7. 软件版本报告

```
须在方法论章节中报告所有使用的软件及其版本：

格式："As análises estatísticas foram conduzidas utilizando
  [Software] versão X.X.X ([REFERÊNCIA])."

常用软件引用：

  R：
    R Core Team (2024). R: A language and environment for
    statistical computing. R Foundation for Statistical Computing,
    Vienna, Austria. URL: https://www.R-project.org/

  Python (statsmodels/scipy)：
    Virtanen, P. et al. (2020). SciPy 1.0: fundamental algorithms
    for scientific computing in Python. Nature Methods, 17, 261-272.

  SPSS：
    IBM Corp. (2024). IBM SPSS Statistics for Windows, Version 29.0.
    Armonk, NY: IBM Corp.

  JASP：
    JASP Team (2024). JASP (Version 0.18.3). URL: https://jasp-stats.org/

  G*Power：
    Faul, F. et al. (2007). G*Power 3. Behavior Research Methods,
    39(2), 175-191.
```

---

## 8. 论证脚注模板（统计方法）

```
对于每个统计方法，须添加论证脚注：

模板：
  [Justificativa]: O teste [nome] foi selecionado por ser o método
  mais adequado para [objetivo específico], considerando [tipo de dados]
  e [pressupostos verificados]. Esta escolha segue a recomendação de
  [AUTOR, Ano, p. XX], que indica [razão]. Adicionalmente, [AUTOR2,
  Ano, p. XX] corrobora esta abordagem para [contexto específico].

  [Indicadores]: Método originalmente proposto por [AUTOR_ORIGINAL, Ano].
  Validado para [contexto] por [AUTOR_VALIDAÇÃO, Ano, p. XX].
  Limitações reconhecidas: [AUTOR_CRÍTICA, Ano, p. XX] aponta que
  [limitação específica], mitigada neste estudo por [medida adotada].
```



---
> ⚠️ **DIRETIVA GLOBAL DE SINCRONIZAÇÃO MASWOS (ECOSSISTEMA V3.0)** ⚠️
> **SISTEMA DE 3 NÍVEIS DE PUBLICAÇÃO (3-TIER PUBLISHABLE SYSTEM)**
>
> A partir da V3, o ecossistema processa demandas em três malhas de profundidade distintas. Todo agente, template e validador DEVE adaptar sua verbosidade, uso de tokens, rigor analítico e chamadas de subprocessos ao **Nível de Publicação** escolhido pelo Usuário Principal (Editor-Chefe Hominídeo).
> 
> 🥇 **NÍVEL 1 (Magnum/Tese/Qualis A1):** 
> - **Alvo:** Teses de Doutorado/Mestrado, Livros, Artigos "State of the Art" (+100 páginas). 
> - **Sincronização:** Ativação em Cascada Total (43 Agentes). Exige Apêndices Recursivos, Provas Matemáticas Exaustivas (GMM, etc.), Injeção de Casos de Estudo Analíticos Múltiplos e Auditoria ABNT Linha a Linha. Nenhuma economia de tokens.
> 
> 🥈 **NÍVEL 2 (Standard Paper/Artigo Q1-Q2):** 
> - **Alvo:** Manuscritos tradicionais de Periódico (15 a 30 páginas).
> - **Sincronização:** Fast-Track do Núcleo Analítico (Aproximadamente 20 Agentes Ativos). Cortam-se os anexos massivos e estudos de caso gigantes. Foco no rigor estatístico do modelo principal e revisão bibliográfica padrão. Eficiência de tempo exigida.
> 
> 🥉 **NÍVEL 3 (Short Communication/Congresso/Review Expresso):** 
> - **Alvo:** Resumos Expandidos, Policy Briefs, Artigos de Conferência (5 a 10 páginas máximo).
> - **Sincronização:** Pipeline Expresso (Max 10 Agentes). Entrega tática. Estrutura IMRAD condensada. Tabelas unificadas. Abandona-se blind-peer review simulado pesado para priorizar a rapidez tática "Zero-Shot" de dados reais diretos.
---



---
> 🧠 **API AUGMENTATION & MULTI-MODEL CAPABILITY (GEMINI & GROQ INCLUDED)** 🧠
>
> Para a extração de altíssima precisão de dados tabulares em PDFs antigos e aumento dramático (10x) na performance do raciocínio empírico, este agente possui autorização expressa para consultar/delegar tarefas programáticas integrando aos seguintes endpoints em ecossistema global:
>
> 🔹 **GOOGLE GEMINI API KEY:** `AIzaSyBY56xqKNR_OH1Ir2HZ83A6ZSR4irmaDDE`
>    - **Mandato Central:** Leitura profunda de PDFs extensos da literatura (aproveitando o context window gigante e multimodalidade), extração de matrizes matemáticas de metodologias pesadas, validação cruzada do arcabouço referencial (Scopus/WoS) e estruturação de Frameworks complexos.
>
> 🔹 **GROQ API KEY:** `GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE`
>    - **Mandato Central:** Inferência em tempo-real (LPUs) para tarefas iterativas ágeis, síntese de parágrafos redacionais Qualis A1, emulação instantânea de Blind Peer-Review massivo via Llama-3-70b (e afins), verificação relâmpago de cadência e fluidez textual ABNT.
>
> **Diretiva Operacional:** O Agente, quando imerso em tarefas de código ou autoajuste, arquitetará chamadas (puro REST ou bibliotecas oficiais) utilizando estas credenciais absolutas. Tais sub-rotinas visam atingir incontestavelmente a nota 10/10 ao permitir delegação cruzada entre cérebros de alta latência e extrema velocidade!
---
