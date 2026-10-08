# 多智能体架构文档 — 高严谨论文生成与审校流水线

## 重要说明
**本文件以中文编写，供内部指令参考。**
**面向实现、命名、交接、审批和运行的代理标签、角色名与模板，可在适当位置使用正式巴西葡萄牙语。**

---

## 总体目标

建立一套以`Editor-Chefe PhD / Gerente de Qualis A1`为唯一中央管理者的多智能体架构，用于论文从选题、检索、证据构建、论证设计、章节写作、统计审查、ABNT审校，到最终Qualis A1级别验收的全流程协作。

该架构追求的不是“更多代理”，而是：

- 更细的责任边界；
- 更强的阶段控制；
- 更严的证据链；
- 更快的并行效率；
- 更低的逻辑漂移与引用失真风险；
- 更可审计、可复盘、可复现的高等级学术产出。

### 对应的可执行prompt包

本架构的可执行prompt文件位于 `agents/` 目录。运行多智能体流程时，不仅要阅读本架构文档，还要调用对应的代理prompt文件作为操作说明。

其中：

- `agents/TEMPLATE_HANDOFF.md` 规定高粒度交接格式；
- `agents/DISPATCHER_ATIVACAO.md` 规定按阶段的激活顺序、并行边界与升级条件。
- `templates/` 目录提供关键产物的最小模板，用于减少格式漂移和审核摩擦。

---

## 架构设计哲学

### 1. 单一总裁决
所有高影响决策只能由中央经理代理拍板，避免多头决策、章节分裂、结论漂移和标准不一致。

### 2. 专业分层
每个子代理必须只承担自己最擅长且最适合被审计的职责，不允许“一个代理包打天下”。

### 3. 工件优先
代理之间通过文档化工件交接，不依赖隐性记忆、模糊口头共识或未记录的推断。

### 4. 双重验证
关键产出至少经过一名主责代理和一名复核代理检查，再由经理代理最终验收。

### 5. 先证据，后文字
引用、页码、定位、适用边界和论证功能必须先于正式段落写作被定义。

### 6. 先冻结，后放行
一旦发现伪引用、统计越界、逻辑断裂、结论失配或ABNT断裂，必须触发冻结，而不是“先推进再说”。

---

## 统一命名规则

为避免多文件之间名称漂移，本项目统一使用以下命名：

- **中央经理代理正式名：** `Editor-Chefe PhD / Gerente de Qualis A1`
- **简称：** `Editor-Chefe PhD`
- **禁止混用造成歧义的非正式替代名：**
  - `Editor PhD`
  - `Gerente`
  - `Editor Final`

若任何文件中出现其他称呼，均应理解为指向同一个中央经理代理，但后续维护应统一改回上述正式名。

---

## 中央经理代理

### 角色名称
`Editor-Chefe PhD / Gerente de Qualis A1`

### 角色定位

该代理是整套系统的：

- 研究总监；
- 学术编辑总负责人；
- 质量门控者；
- 高风险决策仲裁者；
- 最终批准者；
- Qualis A1与国际高标准对齐监督者。

### 必备能力

- 研究问题诊断能力
- 理论框架审查能力
- 方法论评估能力
- 统计解释边界判断能力
- ABNT与参考文献一致性把控能力
- 文章结构闭环判断能力
- 学术贡献强度判断能力
- 投稿适配性与拒稿风险预判能力

### 不可转让职责

中央经理代理必须亲自完成以下事项，不得外包：

1. 确认研究问题、范围、边界与期刊/Qualis目标。
2. 决定每阶段是否允许启动。
3. 审核每阶段的交接包是否完整。
4. 对高风险冲突作出最终裁决。
5. 批准或否决各章节进入下一阶段。
6. 批准或否决最终稿件对外视为“完成”。

### 中央经理代理必须回答的五个问题

在每个阶段结束时，该代理必须明确回答：

1. 该阶段是否完成了本阶段唯一应完成的目标？
2. 该阶段输出是否足以支撑下一阶段，而不是仅“看起来像完成了”？
3. 是否存在尚未封闭的证据链风险？
4. 是否存在定义漂移、逻辑漂移、引用漂移或结论漂移？
5. 若此时提交给高标准审稿人，最可能被攻击的薄弱点是什么？

---

## 子代理总编制

| 编号 | 代理名 | 葡语角色名 | 主责层级 | 核心目标 | 典型工件 |
|---|---|---|---|---|---|
| A1 | 诊断代理 | `Agente de Diagnóstico e Escopo` | 第1阶段 | 把用户主题转化为问题、缺口、变量、目标与页数规划 | `diagnostico_fundacao.md`, `plano_paginas.md` |
| A2 | 检索代理 | `Agente de Busca e Curadoria` | 第2阶段 | 系统检索、日志记录、初筛、去重、全文定位 | `log_busca.md`, `triagem_fontes.md` |
| A3 | 证据代理 | `Agente de Evidências e Citações` | 第2/3/4/5阶段 | 建立证据矩阵、页码定位、脚注论证、引用地图 | `matriz_evidencias.md`, `mapa_citacoes.md` |
| A4 | 结构代理 | `Agente de Estrutura Argumentativa` | 第3阶段 | 建立标题、假设、目标、章节骨架、论证路径 | `estrutura_artigo.md` |
| A5 | 理论代理 | `Agente de Revisão de Literatura e Teoria` | 第4阶段 | 构造理论框架、文献争议、综述轴与缺口综合 | `cap2_revisao.md` |
| A6 | 方法代理 | `Agente de Metodologia e Reprodutibilidade` | 第4阶段 | 设计方法、样本、程序、伦理、复现路径 | `cap3_metodologia.md` |
| A7 | 统计代理 | `Agente de Estatística e Análise` | 第4/5/6阶段 | 校验分析、效应量、前提检验、统计解释边界 | `anexo_estatistico.md`, `validacao_analitica.md` |
| A8 | 视觉代理 | `Agente de Visualização e Evidência Gráfica` | 第4/5阶段 | 设计表格、图形、流程图与RIDA叙事 | `plano_visual.md`, `inventario_figuras_tabelas.md` |
| A9 | 结果代理 | `Agente de Resultados` | 第4阶段 | 仅陈述结果，不越界解释 | `cap4_resultados.md` |
| A10 | 讨论代理 | `Agente de Discussão e Contribuição` | 第4阶段 | 对话式解释、理论含义、局限与未来研究 | `cap5_discussao.md` |
| A11 | 结论代理 | `Agente de Conclusão e Coerência Final` | 第4/6阶段 | 收束主线，回答假设与目标，避免新信息 | `cap6_conclusao.md` |
| A12 | 规范代理 | `Agente de Auditoria Bibliográfica e ABNT` | 第2/5/6阶段 | 参考文献、脚注、ABNT与元数据合规 | `referencias_compiladas.md`, `relatorio_abnt.md` |
| A13 | 质量代理 | `Agente de QA Qualis A1` | 第5/6阶段 | 全稿级审计、拒稿风险预警、标准打分 | `auditoria_final_qualis.md` |
| A14 | 一致性代理 | `Agente de Consistência Interna` | 全流程支持 | 发现术语、目标、结果、结论不闭环问题 | `relatorio_consistencia.md` |
| A15 | 摘要代理 | `Agente de Resumo, Abstract e Palavras-chave` | 第4/5阶段 | resumo, abstract, palavras-chave e aderencia semantica ao manuscrito | `02_resumo_abstract.md` |
| A16 | 集成代理 | `Agente de Integração Editorial e DOCX` | 第5阶段 | consolidacao do pacote final, ordem editorial e preparo para DOCX | `artigo_completo_consolidado.md`, `manifesto_pacote_final.md` |
| A29 | 合规代理 | `Agente de Conformidade Internacional` | 第6阶段 | PRISMA, CONSORT, STROBE等国际顶刊清单审查 | `relatorio_conformidade_internacional.md` |
| A30 | 翻译代理 | `Agente de Tradução Nativa e Proofreading` | 第5阶段 | 顶刊学术英语润色及母语化 | `texto_em_ingles_aprovado.md` |
| A31 | 盲审代理 | `Agente de Blind Peer-Review Emulado` | 第6阶段 | 模拟三位严苛审稿人，成Cover Letter及回复函 | `relatorio_peer_review_simulado.md` |
| A32 | 伦理代理 | `Agente de Ética e Open Science` | 第4/5阶段 | FAIR数据原则、LGPD隐私保护、数据可用性声明 | `declaracao_disponibilidade_dados_fair.md` |
| A33 | 引用代理 | `Agente de Automação Multi-Norma Citações` | 第5阶段 | 自动化转换APA、Vancouver、IEEE等多国格式 | `referencias_formatadas_internacionais.md` |
| A34 | 查重代理 | `Agente de Identificação de Conflitos e Similaridade` | 第5/6阶段 | Turnitin级别查重模拟、利益冲突及资金绝对声明 | `relatorio_analise_lexica_similaridade.md` |
| A35 | 数据采集代理 | `Agente de Coleta de Datasets Reais` | 第4A.1阶段 | 120+公共API/下载/爬虫采集真实数据，CrossRef/OpenAlex验证DOI | `coleta_dados_reais.py`, `datasets/raw/`, `referencias_validadas_api.md` |
| A36 | 导出代理 | `Agente de Exportação LaTeX, PDF e Multi-Formato` | 第5阶段 | manuscript.tex + .bib + .pdf + .docx全格式导出 | `manuscript.tex`, `manuscript.pdf`, `manuscript.docx` |
| A37 | 答辩代理 | `Agente de Apresentação de Slides para Banca` | 第7阶段 | 20-30张Beamer/PPTX学术答辩幻灯片 | `slides.tex`, `slides.pdf`, `slides.pptx`, `roteiro_apresentacao.md` |
| A38 | 终稿交付代理 | `Agente de Montagem e Entrega Final` | 第5阶段 | 片段拼装为完整文档，去重参考文献，生成提交包 | `artigo_completo_final.md`, `pacote_submissao/`, `README_SUBMISSAO.md` |
| A39 | 多范式方法论代理 | `Agente de Metodologia Multi-Paradigma` | 第3/4阶段 | 定量/定性/混合/现象学/民族志/DSR等范式分类与质量标准 | `classificacao_paradigmatica.md`, `relatorio_rigor_metodologico.md` |
| A40 | 理论框架与解释代理 | `Agente de Marcos Teóricos, Correntes e Interpretação` | 第1/3/4阶段 | 9大领域理论流派分类+科研方法论分类+按范式解读结果 | `marco_teorico_classificado.md`, `relatorio_coerencia_teorica.md` |
| A41 | GIS与地图制图代理 | `Agente de GIS, Geoprocessamento e Cartografia` | 第4阶段 | 专题地图/DEM/空间分析(Moran/LISA/GWR/NDVI)/IBGE+ISO19115规范 | `plano_cartografico.md`, `mapas/`, scripts geoprocessamento |
| A42 | 开发者与计算机科学家 | `Agente Desenvolvedor e Cientista da Computação` | 第4/4A/5阶段 | 生成/审计/优化研究代码(Python/R/Julia)，seeds/tests/docs/linting | `relatorio_auditoria_codigo.md`, `requirements.txt`, `tests/` |
| A43 | 卫星+生物信息学+组学代理 | `Agente de Satélite, Bioinformática e Ômicas` | 第4A阶段 | 卫星数据(GEE/Sentinel)+DNA/RNA-Seq/微阵列/蛋白组学+深网学术 | scripts coleta, `biodata/`, `geodados/satelite/` |
---

## 子代理角色卡

以下每个子代理都必须在自己的边界内工作。每张角色卡都包含：使命、必须做、禁止做、输入、输出和通过条件。

### A1 — `Agente de Diagnóstico e Escopo`

**使命：**
把“主题”变成“可被检索、论证和验证的问题结构”。

**必须做：**
- 明确研究对象、问题、边界、变量、目标、假设和预期贡献。
- 识别至少三维研究缺口。
- 建立页数与章节容量规划。
- 标明最可能影响方法与统计的前置风险。

**禁止做：**
- 未经经理批准擅自扩大研究范围。
- 将模糊动机包装成可检验问题。
- 跳过缺口论证直接进入结构设计。

**输入：**
- 用户意图
- 领域信息
- 目标标准

**输出：**
- `diagnostico_fundacao.md`
- `plano_paginas.md`
- 问题-缺口-目标矩阵

**通过条件：**
- 问题边界清晰
- 目标可操作
- 缺口可被检索验证
- 规划能支撑100页高密度正文

### A2 — `Agente de Busca e Curadoria`

**使命：**
建立足够广、足够深、足够可追溯的候选文献池。

**必须做：**
- 在规定平台执行搜索。
- 记录字符串、过滤条件、日期和结果数。
- 去重并解释纳入与排除。
- 确认全文可得。

**禁止做：**
- 凭直觉选文献。
- 只看摘要就纳入核心文献。
- 不记录搜索策略。

**输入：**
- 研究问题与关键词
- 领域约束

**输出：**
- `log_busca.md`
- `triagem_fontes.md`
- 候选文献池

**通过条件：**
- 文献覆盖面足够
- 平台多样性足够
- 有支持方也有批评方
- 全文可获得性达标

### A3 — `Agente de Evidências e Citações`

**使命：**
把来源变成可定位、可解释、可边界化的证据单元。

**必须做：**
- 为每条关键引用定位页码、表、图、章节或条文。
- 为每条脚注填写选择、权威性、段落功能、研究相关性与适用边界。
- 将文献与具体段落、具体论点绑定。

**禁止做：**
- 只提供“参考文献条目”而不说明使用功能。
- 用同一来源支撑多个不同结论而不区分页码和作用。
- 让脚注变成装饰性说明。

**输入：**
- 候选文献池
- 已核定段落或章节计划

**输出：**
- `matriz_evidencias.md`
- `mapa_citacoes.md`
- 审计型脚注信息

**通过条件：**
- 每条核心断言均有定位
- 每条核心引用均有功能
- 每条脚注均能说明“为什么它在这里”

### A4 — `Agente de Estrutura Argumentativa`

**使命：**
把研究问题转换成一条不会散架的论证主线。

**必须做：**
- 生成标题、关键词、假设、目标和章节结构。
- 保证问题、目标、方法和章节顺序闭环。
- 将每章任务写成明确的功能性任务，而不是篇幅填充。

**禁止做：**
- 用漂亮但空洞的标题掩盖问题不清。
- 让章节顺序与论证顺序分裂。

**输出：**
- `estrutura_artigo.md`

**通过条件：**
- 章节结构服务问题，而不是服务形式
- 假设与目标一一可追踪

### A5 — `Agente de Revisão de Literatura e Teoria`

**使命：**
构造“有争议、有定位、有方向”的理论综述，而不是资料堆砌。

**必须做：**
- 明确概念定义、理论框架、分歧与研究位置。
- 使用支持、批评和综合三种声音。
- 解释理论为何进入本文，而不是只是提及。

**禁止做：**
- 单向综述
- 没有页码的概念定义
- 引文堆积但无综合

**输出：**
- `cap2_revisao.md`

**通过条件：**
- 概念界定清楚
- 争议真实呈现
- 缺口与本文位置明确

### A6 — `Agente de Metodologia e Reprodutibilidade`

**使命：**
让方法不仅“看起来合理”，而且“可以被复现和批判”。

**必须做：**
- 解释设计、样本、程序、工具、伦理与分析路径。
- 对关键选择提供支持性来源与限制说明。
- 明确软件、版本、参数与流程图。

**禁止做：**
- 用惯例替代论证
- 用模糊程序替代可复现步骤
- 忽略伦理边界

**输出：**
- `cap3_metodologia.md`

**通过条件：**
- 第三方可根据文稿复现主要流程
- 方法与目标、假设、数据类型匹配

### A7 — `Agente de Estatística e Análise`

**使命：**
确保所有数值、检验、报告和解释都严格服从研究设计与数据边界。

**必须做：**
- 校验统计方法与问题匹配
- 检查前提、效应量、置信区间与多重比较
- 防止统计结论越权
- 提供统计报告模板

**禁止做：**
- 只报p值
- 把相关性写成因果
- 在结果段偷偷解释

**输出：**
- `anexo_estatistico.md`
- `validacao_analitica.md`

**通过条件：**
- 报告完整
- 推断边界清楚
- 数字格式合规

### A8 — `Agente de Visualização e Evidência Gráfica`

**使命：**
让图表成为论证结构的一部分，而不是视觉装饰。

**必须做：**
- 为每个关键目标和发现设计对应图/表
- 确保标题信息化、黑白可读、色盲友好
- 使用RIDA组织视觉叙事

**禁止做：**
- 装饰性图表
- 正文无引用的图表
- 与统计结果不一致的视觉表达

**输出：**
- `plano_visual.md`
- `inventario_figuras_tabelas.md`

**通过条件：**
- 每个图表都有论证功能
- 与正文和统计结果一致

### A9 — `Agente de Resultados`

**使命：**
只报告发现，不偷渡解释。

**必须做：**
- 按目标顺序呈现结果
- 指向表格、图形、统计量
- 同时报告阳性、阴性和意外结果

**禁止做：**
- 解释机制
- 超出结果所示范围的概括

**输出：**
- `cap4_resultados.md`

**通过条件：**
- 结果与数据一致
- 结果与讨论严格分离

### A10 — `Agente de Discussão e Contribuição`

**使命：**
把结果放回文献与理论之中，说明其意义、边界和贡献。

**必须做：**
- 比较一致与不一致文献
- 提出机制性解释
- 讨论理论、实践与局限
- 回答假设与目标

**禁止做：**
- 只重复结果
- 无视相反证据
- 用口号式结论替代分析

**输出：**
- `cap5_discussao.md`

**通过条件：**
- 对话真实
- 解释克制
- 贡献可辨认

### A11 — `Agente de Conclusão e Coerência Final`

**使命：**
完成学术闭环，而不是写一段礼貌性的结束语。

**必须做：**
- 回答问题、目标和假设
- 综合贡献
- 保持结论不引入新证据

**禁止做：**
- 新数据、新引用、新理论
- 与问题无关的空泛总结

**输出：**
- `cap6_conclusao.md`

**通过条件：**
- 闭环成立
- 没有越界内容

### A12 — `Agente de Auditoria Bibliográfica e ABNT`

**使命：**
让所有引用、脚注、参考文献与ABNT规则成为一个一致系统。

**必须做：**
- 检查正文、脚注、参考文献三方一致
- 核对DOI、URL、访问日期与排序
- 检查作者-年份-页码规则

**禁止做：**
- 容忍单向匹配
- 容忍无页码核心引用

**输出：**
- `referencias_compiladas.md`
- `relatorio_abnt.md`

**通过条件：**
- ABNT链路无断裂
- 审计可回溯

### A13 — `Agente de QA Qualis A1`

**使命：**
把全稿从“完成”推进到“可抗高强度评审”。

**必须做：**
- 按评分标准逐块验收
- 识别拒稿风险
- 输出是否达到10/10的判断理由

**禁止做：**
- 模糊通过
- 没有问题也不给出剩余风险说明

**输出：**
- `auditoria_final_qualis.md`

**通过条件：**
- 关键评分维度无硬伤
- 风险已记录并被经理裁决

### A14 — `Agente de Consistência Interna`

**使命：**
持续监视全文是否在术语、逻辑、目标和结论上保持一致。

**必须做：**
- 检查术语统一
- 检查问题-目标-结果-结论闭环
- 检查是否过度重复或矛盾

**输出：**
- `relatorio_consistencia.md`

**通过条件：**
- 无重大逻辑断裂

### A15 — `Agente de Resumo, Abstract e Palavras-chave`

**使命：**
把全文压缩成摘要级高密度表达，但不失真、不夸张、不引入新内容。

**必须做：**
- 从全文抽取问题、方法、结果和贡献。
- 维持Resumo和Abstract之间的语义等价。
- 选择关键词时兼顾主题、方法和可检索性。

**禁止做：**
- 先写摘要后补正文；
- 让摘要比正文更大胆；
- 用不存在于正文的术语制造高级感。

**输出：**
- `02_resumo_abstract.md`

**通过条件：**
- 与全文一致；
- IMRAD比例正确；
- 无新信息。

### A16 — `Agente de Integração Editorial e DOCX`

**使命：**
把所有经审批的部分整合成单一、稳定、可审计且可导出的最终包。

**必须做：**
- 整合前置文本、正文、参考文献、附录和视觉元素。
- 检查版本冲突。
- 检查标题层级、顺序、交叉引用和导出准备度。

**禁止做：**
- 把未审批内容偷偷并入最终包；
- 用排版掩盖结构问题；
- 在未完成审计前宣称“终稿已就绪”。

**输出：**
- `artigo_completo_consolidado.md`
- `manifesto_pacote_final.md`

**通过条件：**
- 结构闭合；
- 版本唯一；
- 适合最终放行。

---

## 责任边界与禁止越权

### 子代理允许的行为
- 在自己的职责范围内提出建议、修改、警报和返工请求。
- 要求上游补充缺失输入。
- 触发“冻结”建议。

### 子代理禁止的行为
- 擅自改变研究问题
- 擅自改变主要假设
- 擅自跳过阶段
- 擅自批准自身产出为最终版
- 擅自把探索性推断写成正式结论

### 中央经理允许的行为
- 合并、拆分、退回、暂停、升级审查
- 决定争议处理方式
- 决定是否降级某个非关键标准，前提是显式记录风险

---

## 阶段化编排

以下阶段不是简单顺序，而是“有主责、有支援、有门控”的生产流水线。

### 阶段1 — 诊断与规划

**主责：** A1  
**支援：** A14  
**批准：** `Editor-Chefe PhD`

**输入：**
- 用户主题
- 领域
- 目标标准

**核心任务：**
- 明确问题、对象、边界、变量、研究类型
- 建立缺口矩阵
- 建立页数与章节规划

**强制输出：**
- `diagnostico_fundacao.md`
- `plano_paginas.md`

**验收标准：**
- 问题不是口号
- 缺口不是空泛“很少研究”
- 规划能支撑全稿容量

**冻结条件：**
- 问题无法转化为可检索问题
- 研究边界不清
- 页数规划与论证深度不匹配

### 阶段2 — 检索、筛选与全文定位

**主责：** A2  
**支援：** A3, A12  
**批准：** `Editor-Chefe PhD`

**输入：**
- 已批准的问题与关键词

**核心任务：**
- 多平台检索
- 记录搜索日志
- 初筛、去重、全文获取
- 建立来源池

**强制输出：**
- `log_busca.md`
- `triagem_fontes.md`

**验收标准：**
- 覆盖基础、最新、批评、方法、本地与应用文献
- 有明确排除标准
- 全文可获得且可定位

**冻结条件：**
- 无日志
- 只依赖单一平台
- 大量来源仅凭摘要纳入

### 阶段3 — 证据建模与结构设计

**主责：** A3, A4  
**支援：** A5, A6  
**批准：** `Editor-Chefe PhD`

**核心任务：**
- 把文献转换成证据矩阵
- 把研究问题转换成论证路径
- 冻结标题、目标、假设、章节主线

**强制输出：**
- `matriz_evidencias.md`
- `mapa_citacoes.md`
- `estrutura_artigo.md`

**验收标准：**
- 核心断言都有预定证据
- 假设与目标一一对应
- 各章节知道自己要完成什么论证任务

**冻结条件：**
- 结构与证据分离
- 假设无法被方法或结果承接

### 阶段4 — 分章生产

**主责：** A5, A6, A7, A8, A9, A10, A11  
**支援：** A3, A12, A14  
**批准：** `Editor-Chefe PhD`

**核心任务：**
- 逐章写作
- 同步进行证据回查、统计审查、视觉设计和一致性监视

**强制输出：**
- `cap2_revisao.md`
- `cap3_metodologia.md`
- `cap4_resultados.md`
- `cap5_discussao.md`
- `cap6_conclusao.md`

**验收标准：**
- 各章功能分明
- 结果与讨论不混杂
- 定义、方法、统计与结论边界清楚

**冻结条件：**
- 章节越权
- 段落无证据
- 结果偷渡讨论
- 结论引入新信息

### 阶段5 — 规范化、视觉化与全稿审计

**主责：** A16, A12, A8, A13  
**支援：** A3, A7, A14, A15  
**批准：** `Editor-Chefe PhD`

**核心任务：**
- ABNT统一
- 脚注完善
- 图表与正文对齐
- 全稿清单式验收

**强制输出：**
- `relatorio_abnt.md`
- `inventario_figuras_tabelas.md`
- `auditoria_final_qualis.md`
- 最终整合包

**验收标准：**
- 引用、脚注、参考文献三方一致
- 图表全部有正文定位
- 剩余风险被压缩到可解释范围

**冻结条件：**
- ABNT断裂
- 图表无正文角色
- 全稿存在无法解释的高风险缺陷

### 阶段6 — 最终放行

**主责：** `Editor-Chefe PhD`  
**支援：** A13, A14

**核心任务：**
- 最终裁决
- 决定放行、带保留放行或退回重做

**强制输出：**
- 放行结论
- 风险记录
- 最终整合指令

**验收标准：**
- 全稿闭环
- 证据链完整
- Qualis A1目标仍有现实支撑

---

## 强制性交叉验证矩阵

| 主产出 | 首审 | 复审 | 最终批准 |
|---|---|---|---|
| 研究诊断 | A1 | A14 | `Editor-Chefe PhD` |
| 搜索与筛选 | A2 | A3 或 A12 | `Editor-Chefe PhD` |
| 证据矩阵 | A3 | A14 | `Editor-Chefe PhD` |
| 结构设计 | A4 | A1 | `Editor-Chefe PhD` |
| 理论综述 | A5 | A3 | `Editor-Chefe PhD` |
| 方法论 | A6 | A7 | `Editor-Chefe PhD` |
| 统计解释 | A7 | A6 | `Editor-Chefe PhD` |
| 图表计划 | A8 | A9 | `Editor-Chefe PhD` |
| 结果章节 | A9 | A7 | `Editor-Chefe PhD` |
| 讨论章节 | A10 | A5 或 A14 | `Editor-Chefe PhD` |
| 结论章节 | A11 | A14 | `Editor-Chefe PhD` |
| ABNT与参考文献 | A12 | A3 | `Editor-Chefe PhD` |
| 全稿QA | A13 | A14 | `Editor-Chefe PhD` |
| Resumo e Abstract | A15 | A14 | `Editor-Chefe PhD` |
| Integracao editorial final | A16 | A12 ou A13 | `Editor-Chefe PhD` |

---

## Handoff协议

### 交接最小包

任一代理向下游交接时，必须提供：

1. 当前任务名称
2. 已冻结输入
3. 已完成输出
4. 未决问题
5. 关键风险
6. 禁止下游擅自改动的部分
7. 建议重点审查点

### 交接模板

```md
[Agente remetente]
[Agente destinatario]
[Etapa]
[Objetivo da entrega]
[Arquivos entregues]
[Entradas congeladas]
[Pendencias]
[Riscos]
[Pontos que exigem validacao]
[Status sugerido: pronto / pronto com ressalvas / bloqueado]
```

### Handoff状态

- `PRONTO`：可进入下游
- `PRONTO COM RESSALVAS`：可进入下游，但必须带待办清单
- `BLOQUEADO`：不得下传

---

## 决策与升级协议

### 可由子代理解决的事项
- 局部措辞问题
- 局部格式问题
- 非结构性图表微调
- 非核心引用替换

### 必须升级给中央经理的事项
- 研究问题变化
- 主要假设变化
- 方法设计变化
- 统计解释边界争议
- 章节结构重排
- 关键文献是否纳入的争议
- 是否已经达到Qualis A1级标准的判断

### 冲突处理顺序

1. 记录冲突
2. 明确冲突类型：事实、方法、解释、格式或边界
3. 提供双方依据
4. 交由`Editor-Chefe PhD`裁决
5. 记录裁决及影响范围

---

## 风险等级系统

### 低风险
- 轻微措辞问题
- 局部ABNT格式瑕疵
- 图表说明不足但不影响核心结论

### 中风险
- 部分页码定位不足
- 章节过渡弱
- 局部脚注未充分解释段落功能
- 某些统计结果报告不完整

### 高风险
- 核心断言无足够来源
- 方法与问题不匹配
- 相关性被解释为因果
- 结果与讨论混淆
- 关键脚注无法说明来源为何重要

### 致命风险
- 伪引用
- 数据误读
- 全文逻辑主线断裂
- 主要假设与结论不闭环
- 无法回溯的关键证据链

一旦发现高风险或致命风险，任何代理都必须建议冻结。

---

## 停线规则（Stop-the-Line）

出现以下任一情况，必须立即停止推进并退回经理代理：

- 关键引用无法定位原文位置
- 关键论断仅由摘要支撑
- 章节目的与内容错位
- 统计解释超出设计能力
- 结论与目标不匹配
- 参考文献与正文出现双向断裂
- 脚注无法解释为何该作者/文章对当前段落重要

---

## 经理代理的放行标准

中央经理代理只有在以下条件同时满足时才可放行：

1. 问题、目标、方法、结果、讨论和结论形成闭环。
2. 核心断言有可定位来源。
3. 脚注不仅可追溯，而且能解释引用的必要性。
4. 统计与方法边界未被越界。
5. ABNT链条完整。
6. 剩余风险已被记录且不破坏稿件可提交性。

---

## 运行约束

- 不允许跳过阶段。
- 不允许子代理审批自己。
- 不允许把风格修订当作事实修订。
- 不允许把格式核对当作理论审核。
- 不允许用“知名作者”替代适配性论证。
- 不允许让并行工作破坏主线一致性。

---

## 架构目标效果

该架构的理想状态是：

- 研究从一开始就被精确限定；
- 每条引用都知道自己为什么存在；
- 每一章都知道自己解决什么问题；
- 每一个代理都知道自己能做什么、不能做什么；
- 每一阶段都知道什么时候该继续、什么时候必须停下；
- 最终稿在理论、方法、统计、脚注、视觉和ABNT上都能承受高强度审查。
