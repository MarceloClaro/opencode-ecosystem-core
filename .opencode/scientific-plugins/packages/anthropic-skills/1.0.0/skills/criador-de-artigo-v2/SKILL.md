---
name: criador-de-artigo-v2
description: >
  Use este skill SEMPRE que o usuário pedir para criar, redigir, elaborar, desenvolver
  ou estruturar qualquer artigo científico, paper acadêmico, manuscrito para periódico,
  trabalho de pesquisa, monografia científica, ensaio acadêmico, revisão de literatura,
  relato de experiência científica, ou qualquer produção textual que exija normas ABNT,
  APA, Vancouver, IMRAD, revisão por pares (peer review), ou submissão a periódico Qualis.
  Também acione para: "escrever abstract", "estruturar introdução acadêmica", "redigir
  metodologia científica", "organizar referências ABNT", "artigo para Qualis A1/A2/B1",
  "paper para publicação", "manuscrito científico completo", "artigo de psicologia",
  "artigo de direito", "artigo de matemática aplicada", "artigo de educação".
  Este skill produz artigos COMPLETOS com MÍNIMO DE 110 PÁGINAS, minuciosos, com tom
  autodidático, sequência lógica e coesa, pontuação 10/10 em bancas brasileiras e
  internacionais Qualis A1.
---

# 学术论文创作技能 — 110页最低标准 · 10/10评分
## Multi-Agent Scientific Writing Operating System (MASWOS) · 43 Agentes
## Qualis A1 · ABNT NBR 6028/6023 · APA第7版 · 自主学习风格

---

## 🔴 语言规则 — 绝对强制性规定

> **本技能的所有输出内容必须且只能使用正式巴西葡萄牙语书写。**
> **禁止使用中文、英语或任何其他语言书写最终输出内容。**
> **本SKILL.md文件以中文编写，仅供内部指令参考。**

---

## 📏 页数与字数强制要求 — 不可谈判

```
最低页数：110页（ABNT格式：A4 · 字体12号 · 1.5行距 · 标准页边距）
最低字数（正文）：45,000词（葡萄牙语）
推荐字数：50,000–60,000词（确保超过110页）

换算基准：ABNT格式每页≈420词
110页 × 420词 = 46,200词 → 安全目标：≥48,000词

各章节最低页数配额：
  预备文本（封面、目录、列表）：8页
  摘要 + 英文摘要：           2页
  第1章 引言：                18页（≥7,200词）
  第2章 文献综述：            28页（≥11,200词）
  第3章 方法论：              16页（≥6,400词）
  第4章 结果：                14页（≥5,600词）
  第5章 讨论：                18页（≥7,200词）
  第6章 结论：                6页（≥2,400词）
  参考文献：                  10页（55–65条文献）
  附录/补充材料：              8页（≥3,200词）
  ─────────────────────────────
  合计：                     ≥128页（大幅超过最低要求）
```

---

## 🏆 评分目标：10/10 — 巴西与国际评审委员会

```
须同时达到以下两套标准：

巴西评审标准（CAPES/Qualis A1）：
  □ 学术严谨性与理论深度           10/10
  □ 方法论论证与可复现性            10/10
  □ ABNT规范完整遵守                10/10
  □ 国家与国际文献的批判性对话       10/10
  □ 统计分析深度（适用时）           10/10

国际评审标准（Scopus/WoS/Nature/Science）：
  □ 研究问题原创性与相关性           10/10
  □ 理论框架严谨性                  10/10
  □ 可复现性与透明度                10/10
  □ 对现有文献的批判性贡献           10/10
  □ 论述清晰性与逻辑连贯性           10/10

→ 详细评分标准见：references/rubrica_avaliacao.md
```

---

## 🧭 核心理念 — 四项不可违背原则

1. **连贯性（COESÃO）** — 引言中的问题须在结论中得到回答。每个章节推进同一论证。
2. **严谨性（RIGOR）** — 每项陈述有文献支撑。每条引用含作者+年份+页码。
3. **教学性（DIDÁTICA）** — 每个概念在首次出现时定义。提供类比。先说"为什么重要"。
4. **分量（VOLUME COM QUALIDADE）** — 110页不是用填充物凑成的。每一页都须贡献论证。
   深度、示例、分析、对话、表格、图形——都是密度的来源，不是篇幅的来源。

---

## 📚 参考文件 — 按指示阅读

| 文件 | 何时阅读 |
|---|---|
| `references/tom_didatico.md` | **进入第4阶段前必须阅读** |
| `references/guia_secoes.md` | 撰写每个章节时阅读（含详细页数目标） |
| `references/citacoes_auditaveis.md` | 插入任何引用或整理参考文献时 |
| `references/areas_especificas.md` | 确定文章研究领域时（第1.2阶段） |
| `references/checklist_qualis.md` | 完成每个章节及最终验证时 |
| `references/rubrica_avaliacao.md` | **撰写前阅读** — 了解10/10评分标准 |
| `agents/DISPATCHER_ATIVACAO.md` | **MASWOS架构核心，必须遵守以驱动43个代理** |

---

## 🔄 执行流程 — 6个顺序阶段（对接 MASWOS）

> **黄金法则：** 未完成当前阶段不得进入下一阶段。
> 根据 `agents/DISPATCHER_ATIVACAO.md` 激活相应的43个专业代理完成各阶段任务。
> 每阶段成果须向用户展示后方可继续。
> **所有输出须以正式巴西葡萄牙语书写。**

---

### ⬛ 第1阶段 — 诊断、基础构建与页数规划

**本阶段存在的理由：** 110页不是通过随意撰写达到的——须在开始前规划每一页的内容。

**→ 阅读：references/areas_especificas.md + references/rubrica_avaliacao.md**

#### 1.1 — 用户提供材料的技术清单
```
□ 研究对象：究竟在调查什么？
□ 核心问题：研究缺口或动机问题
□ 变量：因变量、自变量、控制/调节变量
□ 研究类型：定量/定性/混合/理论
□ 可用数据：性质、规模、来源、收集时期
□ 初步发现：结果已表明什么
□ CNPq领域 + Scopus/WoS子领域
```

#### 1.2 — 三维度研究缺口识别
```
缺口类型1 — 普遍性："尚无研究在Y人群/情境中调查过X"
缺口类型2 — 动态性："现有研究未检验X在条件Z下如何演变"
缺口类型3 — 交互性："X与Y的关系尚未在情境Z下测试"

文献定位表格：[基础文献 | 立场 | 如何证明缺口]
最低要求：5篇基础文献 + 10篇近5年最新研究
须包含：≥3篇支持方法 AND ≥3篇批评/质疑方法
```

#### 1.3 — 页数规划表（须明确交付）
```
为整篇文章创建页数规划表：
章节 | 计划页数 | 计划字数 | 主要子章节 | 主要参考文献

此表确保达到110页最低要求，须在开始撰写前获得用户批准。
```

**第1阶段输出（葡萄牙语）：** `diagnostico_fundacao.md` + `plano_paginas.md`

---

### ⬛ 第2阶段 — 深度系统性文献检索

**目标：** 55-65篇参考文献，战略性分布于8个类别。

**→ 阅读：references/citacoes_auditaveis.md**

```
必须覆盖的类别（及最低数量）：

1. 基础性文献（6-10篇）    — 引用>200次，奠定领域基础
2. 最新研究进展（10-15篇） — 近5年，Qualis A1/A2或同等国际期刊
3. 方法论文献（6-10篇）    — 提出每种技术的原始文章
4. 统计/分析文献（4-6篇）  — 经典教材 + 方法验证文章
5. 批评/质疑文献（4-6篇）  — 持相反立场的作者 — 强制要求
6. 巴西国内文献（5-8篇）   — 法律、国家规范、国内作者
7. 应用与影响（4-6篇）     — 研究发现的实际应用
8. 理论框架（4-6篇）       — 支撑研究基础的核心理论著作

总计：55-65篇（确保参考文献部分达到10页）
格式：须含DOI + 使用注释（在文章哪个位置引用）
```

**第2阶段输出（葡萄牙语）：** `referencias_compiladas.md`

---

### ⬛ 第3阶段 — 撰写前全面结构设计

#### 3.1 — 三个标题选项（含关键词）
```
选项A — 描述性（ABNT期刊）：最多15词 | 前65字符含关键词
选项B — 陈述性（Nature/Science）：最多12词 | 直接宣告主要发现
选项C — 带副标题（混合）：简短主标题：说明性副标题

关键词：6-8个术语 | 3个领域通用 + 2-3个具体 + 1-2个方法论
（关键词数量增加以提升检索可见度）
```

#### 3.2 — 假设、目标与对照表（SMART）
```
H₀ — 主要假设："若[X]，则[Y]，因为[Z]"
     → 1篇支持性引用 + 1篇质疑性引用

H₁至H₅ — 派生假设（最多5个以增加研究深度）

总体目标（1个）
具体目标（4-6个）：SMART标准，每个含论证引用

对照表：[缺口 → 假设 → 目标 → 方法 → 指标 → 预期页数]
```

**第3阶段输出（葡萄牙语）：** `estrutura_artigo.md`

---

### ⬛ 第4阶段 — 完整文章撰写（≥110页）

**开始前：阅读 references/tom_didatico.md + references/guia_secoes.md + references/rubrica_avaliacao.md**

#### 各章节强制页数配额

| 章节 | 最低页数 | 最低字数 | 10/10所需密度 |
|---|---|---|---|
| 预备文本 | 8页 | — | 完整ABNT格式 |
| 摘要(PT)+Abstract(EN) | 2页 | 各300词 | IMRAD完整比例 |
| **第1章 引言** | **18页** | **7,200词** | CARS完整+5个假设 |
| **第2章 文献综述** | **28页** | **11,200词** | 8个主题轴+批判对话 |
| **第3章 方法论** | **16页** | **6,400词** | 双重论证每个方法 |
| **第4章 结果** | **14页** | **5,600词** | 表格+图+统计完整 |
| **第5章 讨论** | **18页** | **7,200词** | 每个发现深度对话 |
| **第6章 结论** | **6页** | **2,400词** | 所有假设明确回答 |
| 参考文献 | 10页 | 55-65条 | ABNT 100%正确 |
| 附录/补充材料 | 8页 | 3,200词 | 完整协议+表格 |
| **合计** | **≥128页** | **≥43,200词** | |

**→ 详细撰写说明见：references/guia_secoes.md（每章节含页数目标）**

#### 叙述主线（须在全文中可见）
```
引言   → 问题P + 缺口L + 假设H₀-H₅ + 目标O₁-O₆
综述   → 为何P存在 + 关于L已知什么 + H的理论基础（8个主题轴）
方法   → 如何实现O + 为何选择此方法检验H（双重论证）
结果   → 发现了什么（按O顺序，含完整统计数据）
讨论   → 发现对P意味着什么 + 与L和H的深度对话
结论   → H₀-H₅是否得证？O₁-O₆是否达成？P得到回答了吗？
```

---

### ⬛ 第5阶段 — 补充材料与完整审计

```
强制性补充材料（含于8页配额）：
□ 附录A：研究工具（完整问卷/协议）
□ 附录B：完整配置/参数表
□ 附录C：辅助数据表
□ 附录D：方法论备注（详细决策说明）
□ 图S1：完整方法论流程图
□ 表S1：完整原始数据或代表性样本

100%一致性报告（须完成）：
□ 文中每个数值 → 可追溯至原始数据
□ 每项方法论陈述 → 与所述程序相对应
□ 每条引用 → 出现在参考文献列表（反之亦然）
□ 每个图表 → 在文中明确引用
□ 每个目标 → 在结果/讨论中得到回应
□ 每个假设 → 在讨论/结论中明确回答
□ 总页数 ≥ 110页 → 核验！
```

**第5阶段输出（葡萄牙语）：** `relatorio_conivencia.md`

---

### ⬛ 第6阶段 — 10/10最终验证

**→ 阅读并执行：references/checklist_qualis.md + references/rubrica_avaliacao.md**

```
最终整合：
□ artigo_completo_final.md（单一完整版本，确认≥110页）
□ referencias_abnt_final.md（55-65条，已格式化并核验）
□ sumario_executivo.md（1页含页数统计 + 目标期刊建议）

页数最终核验：
□ ABNT格式（A4、12号字、1.5行距、标准页边距）下的估计页数
□ 正文字数计数（须≥45,000词）
□ 若未达标：识别须扩展的章节并补充分析深度

目标期刊（3-5个，含论证）：
每个须注明：Qualis/影响因子 | 主题契合度 | 页数要求
```

---

## 📐 不可违背的质量标准

### 引用（见 references/citacoes_auditaveis.md）
- **所有引用 = 作者 + 年份 + 页码** — 无一例外
- 所有引用均添加可审计脚注

### 学术段落结构（确保密度）
```
[第1句] 主题句 — 段落中心思想
[第2句] 展开 — 扩展或具体说明
[第3句] 证据 — 数据/引用/示例（含页码）
[第4句] 分析 — 证据说明什么
[第5句] 深化 — 对立观点或细微差别
[第6句] 连接 — 与文章中心论点的关联
```
（6句结构确保密度，避免为达到页数而填充空洞内容）

### 批判性对话（每章节）
```
□ ≥4位支持该研究方法的作者（含论点摘要）
□ ≥3位批评或质疑该方法的作者（直接回应）
□ 每个对立立场均受到认真对待，而非被轻易驳回
□ 作者明确阐述其立场与理由
```

---

## ✅ 最终交付成果（全部以正式葡萄牙语书写）

```
过程文件：  diagnostico_fundacao.md | plano_paginas.md
            referencias_compiladas.md | estrutura_artigo.md
            relatorio_conivencia.md

各章节文件：01_pretextual.md | 02_resumo_abstract.md
            03_introducao.md（≥18页）
            04_revisao_literatura.md（≥28页）
            05_metodologia.md（≥16页）
            06_resultados.md（≥14页）
            07_discussao.md（≥18页）
            08_conclusao.md（≥6页）
            09_referencias.md（55-65条）
            10_apendices.md（≥8页）

最终整合：  artigo_completo_final.md（≥110页 | ≥45,000词）
            sumario_executivo.md
```

---

> **最终质量标准：**
> (1) 一位智识水平较高但非该具体领域专家的硕士研究生须能完全理解文章；
> (2) 文章须达到110页最低要求，每一页均有实质性学术贡献；
> (3) 巴西和国际评审委员会须能对所有评估维度给出10/10分。
> 若须离开文本去理解文中应有的内容——**重新撰写**。
> 若某页感觉像填充——**深化分析，添加对话，丰富例证**。
