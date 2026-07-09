<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# 风格质量守卫 — 句子/段落/副词/hedging/引用页码

## 重要说明
**本文件以中文编写，供内部指令参考。所有输出须以正式巴西葡萄牙语书写。**

---

## 🔴 每章撰写前和完成后必须阅读本文件

本文件定义了贯穿全文的风格质量底线。
违反任何一项均会导致该章节自评降分。

---

## 1. 句子长度控制

```
绝对上限：55词/句
目标范围：18-35词/句（学术葡萄牙语的清晰区间）

检查方法（每章完成后）：
  □ 统计所有句子字数
  □ 标记所有>55词的句子
  □ 逐一分割或重写超长句

分割策略：
  · 寻找逻辑断点（因果、转折、条件）
  · 将从句独立为新句子
  · 使用分号(;)将并列成分分割为独立句
  · 关系从句(que/o qual)若>15词 → 独立为新句

示例（错误 → 正确）：
  ✗ "A implementação da inteligência artificial nos processos industriais,
    que tem sido amplamente discutida na literatura recente, apresenta
    desafios significativos relacionados à infraestrutura tecnológica,
    à capacitação profissional e à resistência organizacional, conforme
    demonstrado por diversos estudos empíricos conduzidos em economias
    emergentes durante a última década."（62词）

  ✓ "A implementação da inteligência artificial nos processos industriais
    tem sido amplamente discutida na literatura recente. Essa implementação
    apresenta desafios significativos: infraestrutura tecnológica,
    capacitação profissional e resistência organizacional. Estudos empíricos
    conduzidos em economias emergentes durante a última década corroboram
    esses obstáculos (SILVA et al., 2021, p. 45)."（3句，每句<30词）
```

---

## 2. 段落长度控制

```
绝对上限：350词/段落
目标范围：120-280词/段落（6句结构的自然区间）

检查方法：
  □ 统计所有段落字数
  □ 标记所有>350词的段落
  □ 分割为两个独立段落，每个保持6句结构

分割策略：
  · 在论据转换点分割（从证据→分析 或 从分析→深化）
  · 确保两个新段落各自有主题句
  · 添加过渡词连接两段
```

---

## 3. 副词-mente密度控制

```
目标密度：≤5.0个/1000词
计算：(副词-mente总数 / 总字数) × 1000

常见过度使用：
  significativamente → de modo significativo / com significância
  relativamente → em termos relativos / de forma relativa
  especificamente → em específico / de modo específico
  particularmente → em particular / de modo particular
  essencialmente → em essência / no essencial
  necessariamente → de forma necessária / por necessidade
  frequentemente → com frequência / de modo frequente
  adicionalmente → além disso / ademais / em adição
  consequentemente → como consequência / por conseguinte
  posteriormente → em seguida / na sequência

策略：
  · 每写完一段，检查-mente副词数量
  · 若段落中>2个 → 替换至少1个
  · 优先替换位于句首的副词（更突兀）
  · 保留真正必要的（如"estatisticamente significativo"可保留）
```

---

## 4. 词汇重复控制

```
高频词汇警报（全文上限）：
  "presente estudo"     → ≤5次/章 | ≤30次/全文
  "constitui"           → ≤4次/章 | ≤20次/全文
  "nesse sentido"       → ≤3次/章
  "diante do exposto"   → ≤2次/章
  "é importante"        → ≤3次/章
  "vale ressaltar"      → ≤2次/章

替换库：
  "presente estudo" → "esta investigação" / "a pesquisa em tela" /
    "o estudo ora conduzido" / "a análise aqui desenvolvida"
  "constitui" → "representa" / "configura" / "caracteriza" /
    "compõe" / "integra" / "forma"
  "nesse sentido" → "nessa direção" / "sob essa ótica" /
    "a partir dessa perspectiva" / "em consonância"
```

---

## 5. Hedging（atenuação）密度控制

```
适用章节：讨论（Cap. 5）
目标密度：≤4.0 hedges/1000词

hedging词汇列表：
  pode/podem | parece/parecem | sugere/sugerem | indica/indicam
  possivelmente | provavelmente | aparentemente | eventualmente
  tende a | é possível que | é provável que

规则：
  · 讨论中需要hedging以避免overclaiming
  · 但过多hedging削弱论证力度
  · 平衡策略：事实用确定语言，解释用hedging
  · 统计显著的结果 → 不需要hedging
  · 因果推断（非实验设计）→ 需要hedging
```

---

## 6. 引用页码守卫

```
绝对规则：所有引用 = 作者 + 年份 + p. XX（或p. XX-YY）

同一作者同一页码引用上限：≤3次/全文
  · 若需多次引用同一作者 → 引不同页码的不同段落
  · 这证明实际阅读了完整文献

检查方法（每章完成后）：
  □ 提取所有引用
  □ 统计每个(作者, 年份, 页码)组合的出现次数
  □ 标记>3次的组合 → 替换为不同页码或不同文献
```

---

## 7. ABNT格式守卫

```
多作者分隔符：
  ✗ SILVA. SANTOS. OLIVEIRA（句号 — 错误）
  ✓ SILVA; SANTOS; OLIVEIRA（分号 — 正确）

外语术语：
  ✗ machine learning（无格式）
  ✓ *machine learning*（斜体）
  规则：所有非葡萄牙语术语首次出现须用斜体

数字格式（ABNT巴西标准）：
  小数点 → 逗号：3,14（不是3.14）
  千位分隔符 → 点：1.245（不是1,245）
  p值 → p = 0,034 或 p < 0,001（绝不写p = 0,000）
  统计符号 → 斜体：M, DP, t, F, p, r, n
```

---

## 8. 章节间去重

```
目标：15词ngram重复 ≤ 50个（Cap.1↔Cap.2之间）

检查时机：每写完新章节后
检查方法：
  □ 提取新章节和所有已完成章节的15词ngram
  □ 统计重复数量
  □ 若>50个重复：
    · 识别重复段落
    · 在后续章节中改写为概述+引导（"conforme discutido no Capítulo X"）
    · 保留详细论述在首次出现的章节

常见重复来源：
  · 引言和综述中对同一文献的描述
  · 方法和结果中对同一程序的描述
  · 讨论和结论中对同一发现的解读
```

---

## 9. 每章完成后的自动检查清单

```
□ 句子>55词数量 = ___（须为0）
□ 段落>350词数量 = ___（须为0）
□ 副词-mente密度 = ___/1000词（须≤5.0）
□ "presente estudo"出现次数 = ___（须≤5）
□ "constitui"出现次数 = ___（须≤4）
□ 同一引用同一页码>3次 = ___（须为0）
□ 外语术语无斜体 = ___（须为0）
□ ABNT多作者句号替代分号 = ___（须为0）
□ 小数点使用点替代逗号 = ___（须为0）
□ hedging密度（仅讨论章节）= ___/1000词（须≤4.0）
□ 15词ngram重复 = ___（须≤50）

若任何项目不达标 → 修改后重新检查 → 再交付
```

---

## 10. Auditoria Frase a Frase

O texto so pode ser considerado pronto quando cada frase puder ser auditada quanto a funcao, lastro, alcance e limite.

### Classificacao obrigatoria

```md
[D] Definicao
[E] Evidencia
[A] Analise
[C] Contraste
[L] Limitacao
[T] Transicao
[J] Justificativa metodologica
```

### Regras de estilo auditavel

- Nenhum paragrafo deve conter apenas `A` e `T`; e obrigatorio haver pelo menos uma frase `E`, `D` ou `J` conforme o tipo de secao.
- Duas frases analiticas consecutivas sem ancora documental exigem revisao imediata.
- Verbos vagos como "mostra", "revela", "indica", "reforca" e "comprova" devem vir acompanhados do que exatamente foi observado e onde isso aparece.
- Quantificadores vagos como "muitos", "diversos", "amplo", "relevante", "consistente" ou "significativo" devem ser substituidos por numero, comparacao, criterio ou citacao.
- A distancia maxima entre afirmacao verificavel e citacao e de uma frase.
- Toda afirmacao normativa, historica ou classificatoria exige fonte primaria ou justificativa explicita de excecao.

### Mini-roteiro de auditoria interna

```md
| Paragrafo | Frase | Tag | Faz afirmacao verificavel? | Fonte | Localizacao | Ajuste |
|---|---|---|---|---|---|---|
| 2.2/P3 | F1 | D | Sim | AUTOR (2018) | p. 44-46 | Nenhum |
| 2.2/P3 | F2 | A | Sim | AUTOR (2018); AUTOR (2023) | p. 44-46; p. 91 | Explicitar que a conclusao final e inferencia do artigo |
```

### Sinais de alerta imediato

- Paragrafo "bonito", mas sem pagina ou dado.
- Frase que resume literatura sem nomear autores.
- Conclusao forte baseada em uma unica fonte fraca.
- Uso repetido da mesma referencia para suportar proposicoes diferentes sem paginas diferentes.




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
