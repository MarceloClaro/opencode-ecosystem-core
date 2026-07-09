<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# 图表与视觉叙事指南 — Qualis A1标准

## 重要说明
**本文件以中文编写，供内部指令参考。所有输出须以正式巴西葡萄牙语书写。**

---

## 🔴 撰写结果(Cap.4)和讨论(Cap.5)前必须阅读本文件

---

## 1. 数量与分布要求

```
全文总量：8-15个图/表
  结果章节（Cap.4）：4-8个（核心数据呈现）
  方法论章节（Cap.3）：1-2个（流程图+前提检验表）
  文献综述（Cap.2）：1-2个（综合比较表+理论框架图）
  讨论章节（Cap.5）：1-2个（更新后理论框架+文献比较表）
  引言/结论：0-1个（仅当必要）

强制性元素（不可缺少）：
  □ 方法论流程图（Cap.3）— 展示研究设计全流程
  □ 文献综合比较表（Cap.2）— 比较≥10篇核心文献
  □ 每个具体目标/假设 → 至少1个对应图或表
```

---

## 2. 图形类型决策矩阵

```
根据数据类型和分析目标选择最佳图形：

┌─────────────────────┬──────────────────────────────────┐
│ 分析目标             │ 推荐图形类型                      │
├─────────────────────┼──────────────────────────────────┤
│ 组间比较             │ 柱状图+误差棒（IC95%）或箱线图    │
│ 趋势/时间序列        │ 折线图（含标注关键事件）           │
│ 相关/关系            │ 散点图+回归线 或 热力图            │
│ 分布                 │ 直方图、箱线图或小提琴图           │
│ 模型性能             │ ROC曲线、森林图、残差图            │
│ 流程                 │ CONSORT/PRISMA流程图              │
│ 理论框架             │ 概念图/路径图                     │
│ 文献比较             │ 表格（综合比较矩阵）               │
│ 比例/组成            │ 堆叠柱状图（替代饼图）             │
│ 多维关系             │ 热力图 或 平行坐标图               │
└─────────────────────┴──────────────────────────────────┘

绝对禁止：
  ✗ 3D图（扭曲数据感知）
  ✗ 饼图（改用堆叠柱状图或华夫饼图）
  ✗ 纯装饰性图（无信息价值）
  ✗ 未标注的图（缺少n、统计量或来源）
```

---

## 3. 5A设计原则

```
每个图/表须满足以下5项原则：

A1 — Autoexplicativo（自解释性）：
  · 标题本身传达核心发现（信息型标题，非描述型）
  · 描述型（差）："Gráfico de barras dos resultados"
  · 信息型（好）："Empresas com IA apresentam eficiência 23% superior
    (n = 245, p < 0,001)"
  · 标题须含：变量名 + 方向/大小 + 样本量 + 显著性

A2 — Anotado（标注丰富）：
  · 关键数据点直接标注在图上（不仅在图例中）
  · 显著性标记：* p<0,05  ** p<0,01  *** p<0,001
  · 误差棒类型明确标注（SD、SE或IC95%）
  · 趋势线含方程和R²

A3 — Acessível（可访问性）：
  · 色盲友好调色板（见下方Python标准）
  · 黑白印刷时仍可区分（使用不同线型/标记形状）
  · 字体≥8pt（图中文字）
  · 对比度充足

A4 — Alinhado（层次对齐）：
  · 视觉层次反映信息重要性
  · 主要发现使用更粗线条/更深颜色
  · 次要信息使用更细线条/更浅颜色
  · 网格线轻淡（灰色，不干扰数据）

A5 — Auditável（可审计）：
  · 来源标注（Fonte:）在图/表下方
  · 样本量(n)可见
  · 统计量可见（至少p值和效应量）
  · 所有缩写在注释中解释
```

---

## 4. RIDA四层视觉叙事模型

```
视觉元素在文章中的呈现须遵循RIDA层次递进：

第1层 — Reconhecimento（认知）：
  位置：结果章节开篇
  目的：让读者了解数据的基本特征
  元素：描述性统计表（M, DP, n）、频率分布图
  特点：客观呈现，无解读

第2层 — Investigação（探究）：
  位置：结果章节中段
  目的：揭示变量间的关系和模式
  元素：散点图、相关热力图、交叉表
  特点：展示关系但不做因果推断

第3层 — Demonstração（论证）：
  位置：结果章节后段
  目的：用统计证据检验假设
  元素：含IC和p值的柱状图/箱线图、ROC曲线、森林图
  特点：每个图直接对应一个假设检验结果

第4层 — Articulação（整合）：
  位置：讨论章节
  目的：将发现整合回理论框架
  元素：更新后的理论框架图（含实证结果标注）
  特点：综合性，连接数据与理论

叙事流程：
  认知（"数据是什么样？"）
  → 探究（"数据间有什么关系？"）
  → 论证（"假设是否成立？"）
  → 整合（"这对理论意味着什么？"）
```

---

## 5. ABNT格式规范

```
图（Figura）：
  □ 编号连续：Figura 1, Figura 2...
  □ 标题在下方（不在上方）
  □ 格式："Figura X — 信息型标题"
  □ 来源标注在标题下方："Fonte: Elaboração própria (2026)."
    或 "Fonte: Adaptado de SOBRENOME (Ano, p. XX)."
  □ 注释在来源下方："Nota: IC95% representado pelas barras de erro."

表（Tabela）：
  □ 编号连续：Tabela 1, Tabela 2...
  □ 标题在上方（不在下方）
  □ 格式："Tabela X — 信息型标题"
  □ IBGE规范：
    · 仅3条水平线：表头上方、表头下方、表尾下方
    · 无垂直线
    · 无单元格阴影/填充色
    · 数据右对齐（数字）或左对齐（文字）
  □ 来源标注在表下方

图与表在正文中的引用：
  □ 首次提及时使用完整引用："conforme apresentado na Figura 1"
  □ 后续提及可缩写："(Figura 1)"
  □ 每个图/表在正文中至少引用一次
  □ 引用须在图/表出现之前或同一页
```

---

## 6. Python图形生成标准

```python
# 标准设置（每个图形脚本的开头）
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# 字体设置
matplotlib.rcParams['font.family'] = 'Times New Roman'
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.labelsize'] = 12
matplotlib.rcParams['axes.titlesize'] = 13
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10

# 色盲友好调色板（4色）
PALETTE = ['#2171B5', '#D94801', '#238B45', '#6A3D9A']
# 扩展版（8色，需要时）
PALETTE_EXT = ['#2171B5', '#D94801', '#238B45', '#6A3D9A',
               '#E6AB02', '#66A61E', '#A6761D', '#666666']

# 去掉顶部和右侧边框线
sns.set_style('ticks')
sns.despine()

# 保存标准
# fig.savefig('figura_X.png', dpi=300, bbox_inches='tight')
# fig.savefig('figura_X.svg', bbox_inches='tight')  # 矢量版备份
```

---

## 7. 图目录和表目录

```
须在预备文本中生成：
  □ 图目录（Lista de Figuras）：按顺序列出所有图及页码
  □ 表目录（Lista de Tabelas）：按顺序列出所有表及页码

一致性验证：
  □ 目录中的标题 = 正文中的标题（完全一致）
  □ 目录中的页码 = 实际页码
  □ 同一变量在全文使用一致的颜色/符号/缩写
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
