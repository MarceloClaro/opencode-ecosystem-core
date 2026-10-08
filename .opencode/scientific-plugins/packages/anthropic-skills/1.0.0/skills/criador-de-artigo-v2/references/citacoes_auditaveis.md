# 可审计引用 — 通用规则与完整格式

## 重要说明
**本文件以中文编写，供内部指令参考。**
**所有面向用户的输出内容，须以正式巴西葡萄牙语书写。**

---

## 绝对强制性通用规则

**所有引用 = 作者 + 年份 + 页码** (除非国际样式Vancouver强制数字引述)

无一例外。"apud"来源须可追溯。年份不可缺页码。
无页码来源（网站）：使用编号段落或章节。

> [!NOTE] 
> 默认配置展示为巴西ABNT标准，但若任务目标为国际顶刊出版物，必须隐式触发 **A33 | Automação Multi-Norma Citações (APA, Vancouver, IEEE, Chicago)** 进行最终查验与文献库转换。即使如此，工作库中依然要保证可审计的证据链不丢失。

---

## ABNT NBR 10520:2023格式 — 正文引用

### 间接引用（转述）— 最常见
```
(SOBRENOME, Ano, p. XX)
例：(FREIRE, 1987, p. 29)
例：(VYGOTSKY, 1934/1991, p. 112)    ← 译本：原始年份/译本年份
```

### 短直接引用（不超过3行）— 正文中加引号
```
"[精确文字]" (SOBRENOME, Ano, p. XX)
例："A educação é um ato de amor" (FREIRE, 1987, p. 79).
```

### 长直接引用（超过3行）— 缩进段落
```
缩进：从左边距缩进4cm
字体：小于正文（正文12pt则用10pt）
不加引号
不加斜体
段落后标注：(SOBRENOME, Ano, p. XX)
```

### 机构作者引用
```
(BRASIL, 2023, p. 15)
(IBGE, 2022, p. 34)
(OMS, 2021, p. 8)
```

### 法律条文引用
```
(BRASIL, 1988, Art. 5º, inciso III)     ← 联邦宪法
(BRASIL, 2002, Art. 186)                ← 民法典
(BRASIL, 1940, Art. 121, §2º)          ← 刑法典
```

### 判例引用
```
(BRASIL, STF, ADI 3.330, 2012, p. 1)
(BRASIL, STJ, REsp 1.234.567/SP, 2020, p. 15)
```

### 二位作者
```
(SILVA; SANTOS, 2020, p. 45)
```

### 三位及以上作者
```
(SILVA et al., 2021, p. 22)
```

### 转引（apud）— 仅在无法获取原文时使用
```
(FREUD, 1915 apud LAPLANCHE; PONTALIS, 2001, p. 234)
强制要求：参考文献列表中只列出实际阅读的文献（本例中为Laplanche）
绝不将未直接阅读的著作列入参考文献
```

### 无页码来源（网站、电子文档）
```
使用段落编号：(SOBRENOME, Ano, par. 4)
或章节：(SOBRENOME, Ano, seção "Metodologia")
绝不省略位置信息
```

---

## ABNT NBR 6023:2018格式 — 参考文献列表

### 期刊文章
```
SOBRENOME, Nome; SOBRENOME2, Nome2. Título do artigo. Nome do Periódico, cidade,
v. X, n. X, p. XX-XX, mês abrev. Ano. DOI: 10.XXXX/XXXXXXX.

示例：
MALLOY-DINIZ, L. F. et al. Funções executivas e cognição social em pacientes com
transtorno bipolar. Revista de Psiquiatria Clínica, São Paulo, v. 36, n. 5,
p. 177-183, out. 2009. DOI: 10.1590/S0101-60832009000500001.
```

### 完整图书
```
SOBRENOME, Nome. Título da obra: subtítulo. Número de ed. Cidade: Editora, Ano.

示例：
FREIRE, Paulo. Pedagogia do oprimido. 17. ed. Rio de Janeiro: Paz e Terra, 1987.
```

### 文集章节
```
SOBRENOME, Nome. Título do capítulo. In: SOBRENOME, Nome (org.). Título do livro.
Cidade: Editora, Ano. cap. X, p. XX-XX.
```

### 学位论文
```
SOBRENOME, Nome. Título da tese/dissertação: subtítulo. Ano. X f. Tese (Doutorado
em [Área]) / Dissertação (Mestrado em [Área]) — [Nome do Programa], [Instituição],
[Cidade], Ano.
```

### 巴西立法
```
BRASIL. Lei nº XXXXX, de DD de mês de AAAA. Descrição da lei. Diário Oficial da
União: seção X, Brasília, DF, v. XXX, n. XX, p. XX, DD mês AAAA.
```

### 判例
```
BRASIL. Superior Tribunal de Justiça. [Tipo de recurso] nº XXXXX/UF. [Ementa resumida].
Relator: [Nome]. Brasília, DF, XX de mês de AAAA. Diário da Justiça Eletrônico,
Brasília, DF, XX mês AAAA. Disponível em: [URL]. Acesso em: DD mês AAAA.
```

### DSM-5-TR（心理学/精神病学）
```
AMERICAN PSYCHIATRIC ASSOCIATION. Manual diagnóstico e estatístico de transtornos
mentais: DSM-5-TR. 5. ed. texto rev. Porto Alegre: Artmed, 2023.
```

### 软件/代码库
```
R CORE TEAM. R: A language and environment for statistical computing. Vienna:
R Foundation for Statistical Computing, 2024. Disponível em: https://www.r-project.org.
```

---

## 可审计脚注模板 — 强制使用

引用任何来源时，须添加脚注：

```
¹ [SOBRENOME, Ano, p. XX] — Título completo da obra. Periódico/Editora, Ano.
  DOI: 10.XXXX/XXXXX（或完整URL + 访问日期）.
  物理位置：图书馆X / 馆藏Y / 永久链接Z.
```

### Nota de rodape explicativa em padrao ABNT

Neste projeto, a citacao no corpo do texto permanece em sistema `autor-data`, conforme ABNT. A nota de rodape e `explicativa e auditavel`: ela nao substitui a citacao no corpo; ela documenta por que a fonte foi escolhida, por que o autor ou artigo e relevante e qual e a funcao exata da referencia naquele paragrafo.

### Parametros minimos da nota

- Numeracao sequencial em algarismos arabicos, com chamada sobrescrita no corpo do texto.
- Nota inserida no rodape da mesma pagina da chamada.
- Fonte menor que a do corpo do texto, preferencialmente 10 pt.
- Espacamento simples dentro da nota.
- Conteudo redigido em tom tecnico, objetivo e verificavel.
- A nota deve complementar a citacao autor-data; jamais repetir apenas a referencia sem analise.

填写示例：
```
¹ [LEZAK et al., 2004, p. 35] — Neuropsychological Assessment. 4. ed. Oxford:
  Oxford University Press, 2004. ISBN: 978-0-19-511121-7.

² [BRASIL, 2002, Art. 186] — Código Civil Brasileiro. Lei nº 10.406/2002.
  Disponível em: https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm
  Acesso em: 8 mar. 2026.
```

---

## Estrutura reforcada da nota de rodape auditavel

Cada nota deve conter, nesta ordem, os blocos abaixo:

```md
¹ [SOBRENOME, Ano, p. XX-YY] — Referencia completa em forma abreviada, coerente com a lista final em ABNT.
  DOI: ... / Disponível em: ... / Acesso em: ...

  [Selecao]: por que esta fonte foi escolhida para este ponto especifico.
  [Autoridade]: por que este autor, artigo, obra ou documento tem peso academico ou tecnico para o tema.
  [Funcao no paragrafo]: o que exatamente a citacao faz neste paragrafo.
  [Relevancia para a pesquisa]: como a fonte se conecta ao problema, objetivo, hipotese, variavel ou decisao metodologica do estudo.
  [Limite de uso]: o que a fonte sustenta e o que ela nao autoriza concluir.
  [Indicadores]: Qualis / indexacao / DOI / citacoes / natureza da fonte, quando pertinente.
```

### O que cada bloco precisa deixar claro

#### [Selecao]
- Qual lacuna do paragrafo a fonte preenche.
- Por que ela foi preferida a outras fontes disponiveis.
- Se ela foi escolhida por pioneirismo, atualidade, validacao brasileira, desenho metodologico robusto ou aderencia direta ao objeto.

#### [Autoridade]
- Se o autor e referencia fundadora, especialista reconhecido, autor de validacao, orgao oficial, corte superior, guideline ou estudo seminal.
- Se o artigo saiu em periodico relevante para o campo.
- Se ha indicador objetivo de autoridade: Qualis, indexacao, fator de impacto, citacoes, papel institucional ou centralidade teorica.
- Nunca usar autoridade vazia, como "autor importante", sem criterio verificavel.

#### [Funcao no paragrafo]
- Se a fonte esta sendo usada para `definir`, `sustentar`, `contrastar`, `historicizar`, `justificar metodo`, `delimitar contexto`, `apresentar dado` ou `registrar limitacao`.
- Qual frase ou proposicao do paragrafo ela ancora.
- Se houver mais de uma funcao, indicar a principal e a secundaria.

#### [Relevancia para a pesquisa]
- Como a fonte contribui para a pergunta central da pesquisa.
- Qual a ligacao direta com objetivo, hipotese, variavel, recorte empirico, contexto brasileiro ou escolha metodologica.
- Por que a ausencia dessa fonte enfraqueceria a coerencia do argumento.

#### [Limite de uso]
- O escopo da fonte: teoria, contexto, metodo, norma, dado empirico ou contraponto.
- O que nao pode ser inferido a partir dela.
- Se o estudo e contextual, antigo, local, exploratorio ou metodologicamente limitado, isso deve ser dito.

---

## Modelo preferencial de nota de rodape

```md
¹ [AUTOR, Ano, p. XX-YY] — Título do artigo. Nome do Periódico, v. X, n. X, p. XX-YY, Ano.
  DOI: 10.XXXX/XXXXX. Disponível em: [URL]. Acesso em: DD mmm. AAAA.

  [Selecao]: Fonte escolhida por abordar diretamente [tema/subtema] no mesmo recorte conceitual
  empregado neste parágrafo.

  [Autoridade]: Artigo publicado em periódico [Qualis/Scopus/WoS/etc.], de autoria de [descrição objetiva:
  autor fundador / grupo de referência / órgão oficial / estudo seminal / validação brasileira].

  [Funcao no paragrafo]: Sustenta a afirmação de que [proposição exata do parágrafo] e fornece base para
  [definição / contraste / justificativa metodológica / dado empírico].

  [Relevancia para a pesquisa]: A referência se conecta ao estudo ao fundamentar [objetivo / hipótese / variável /
  lacuna / contexto], sendo essencial para a coerência deste eixo argumentativo.

  [Limite de uso]: A fonte sustenta [alcance real], mas não autoriza concluir [extrapolação indevida].

  [Indicadores]: Qualis [X] / Indexação [base] / DOI [sim] / [n] citações / natureza [artigo empírico, revisão,
  norma oficial, obra fundadora].
```

---

## Exemplo reforcado

```md
¹ [SILVA et al., 2021, p. 45-47] — Impacto da IA na eficiência industrial brasileira.
  Revista de Administração, v. 56, n. 3, p. 201-219, 2021.
  DOI: 10.1590/S0034-75902021000300005. Disponível em: https://www.scielo.br/j/rausp/a/XXXXX.
  Acesso em: 16 mar. 2026.

  [Selecao]: A fonte foi selecionada por examinar diretamente a adoção de IA em contexto industrial brasileiro,
  que coincide com o recorte empírico do parágrafo.

  [Autoridade]: Trata-se de artigo empírico publicado em periódico indexado e relevante para administração e
  gestão, com aderência temática direta ao problema investigado.

  [Funcao no paragrafo]: A citação sustenta a afirmação de que a adoção de IA esteve associada a ganhos
  operacionais mensuráveis no contexto analisado, servindo como evidência empírica principal do argumento.

  [Relevancia para a pesquisa]: A referência reforça a hipótese de efeito positivo da IA sobre a eficiência e
  reduz a lacuna contextual ao fornecer evidência brasileira, e não apenas internacional.

  [Limite de uso]: O estudo sustenta a associação observada no setor e período analisados, mas não autoriza
  generalização automática para todos os segmentos industriais nem inferência causal irrestrita.

  [Indicadores]: Qualis A2 / SciELO / DOI válido / 47 citações / artigo empírico.
```

---

## Regras de redacao da nota

- A nota deve se referir ao `uso da fonte no paragrafo atual`, e nao apenas resumir o artigo de forma generica.
- A relevancia do autor e do artigo deve ser `contextual`, nunca decorativa.
- Cada nota deve mostrar `por que esta citacao esta aqui`.
- Se a fonte for usada como contraponto, isso deve aparecer explicitamente.
- Se a fonte for fundacional, deixar claro `qual conceito ou premissa fundadora` ela ancora.
- Se a fonte for normativa, deixar claro `qual obrigacao, criterio ou definicao oficial` ela estabelece.
- Se a fonte for metodologica, deixar claro `qual decisao tecnica` ela legitima e em quais condicoes.
- Se a nota nao conseguir explicar a relevancia da fonte para o paragrafo e para a pesquisa, a citacao deve ser reconsiderada.

---

## 绝对禁止的错误

❌ 无页码引用："(SILVA, 2020)" — 错误
✅ 含页码引用："(SILVA, 2020, p. 45)" — 正确

❌ 参考文献列表中有未在正文中引用的文献
❌ 正文中有引用但参考文献列表中无对应条目
❌ 对可直接获取的文献使用"apud"
❌ DOI无效或URL无法访问
❌ 引用未完整阅读的文献


---

## 强制性多平台学术搜索协议（第2阶段前置步骤）

**在编撰任何引用之前，须在以下平台进行系统性搜索。此步骤不可跳过。**

### 巴西平台（按优先顺序）

```
1. Plataforma Sucupira / Qualis Periódicos CAPES
   → 验证期刊等级（A1/A2/B1等）
   → URL: https://sucupira.capes.gov.br/sucupira/

2. SciELO Brasil (Scientific Electronic Library Online)
   → 搜索主题关键词 + 获取完整PDF
   → URL: https://www.scielo.br/

3. Portal de Periódicos CAPES
   → 搜索全文 + 下载PDF
   → URL: https://www.periodicos.capes.gov.br/

4. BDTD (Biblioteca Digital Brasileira de Teses e Dissertações)
   → 博士/硕士论文全文
   → URL: https://bdtd.ibict.br/

5. Google Acadêmico (Scholar) — 葡萄牙语搜索
   → 补充搜索 + 引用计数验证
```

### 国际平台

```
6. Scopus (Elsevier)
   → 高影响力国际文献 + 引用指标

7. Web of Science (Clarivate)
   → JCR影响因子验证

8. PubMed / PubMed Central
   → 生物医学/健康科学全文

9. Google Scholar — 英语搜索
   → 广泛覆盖 + 引用追踪

10. 专业平台（按研究领域选择）：
    ERIC（教育）/ IEEE Xplore（技术）/ JSTOR（人文社科）/
    APA PsycINFO（心理学）/ Cochrane（医学系统评价）
```

### 搜索策略记录（每次搜索须填写）

```
搜索日志模板（log_busca_plataformas.md）：

| 编号 | 平台 | 查询词 | 日期 | 结果数 | 选中数 | 备注 |
|---|---|---|---|---|---|---|
| 01 | SciELO | "inteligência artificial" AND "indústria" | 2026-03-16 | 234 | 5 | 过滤近5年 |
| 02 | Scopus | "artificial intelligence" AND "industrial efficiency" | 2026-03-16 | 1.203 | 8 | 排序by cited |
```

### PDF全文获取与逐页扫描协议

```
对于每篇被选为引用的文献：

步骤1 — 获取全文：
  □ web_search搜索标题 + "PDF" + "full text"
  □ web_fetch获取完整PDF或HTML全文
  □ 记录获取来源URL和访问日期

步骤2 — 逐页扫描：
  □ 阅读文档全文（不可仅读摘要）
  □ 识别与各章节相关的关键段落
  □ 标记精确页码范围（p. XX-YY）

步骤3 — 引用精确定位：
  □ 精确页码（p. XX 或 p. XX-YY）
  □ 禁止模糊页码
  □ 无页码文档：段落编号或章节名

步骤4 — 引用选择论证脚注：
  a) 为何选择此文献
  b) 在当前段落中的作用
  c) 学术权威性说明
  d) 与研究缺口/假设的联系
```

### 引用地图模板（mapa_citacoes.md）

```
| 引用编号 | 作者(年份) | 使用章节 | 引用页码 | 作用 | 论证理由 |
|---|---|---|---|---|---|
| C01 | SILVA (2021) | Cap.2 §2.3 | p. 45-47 | 支持缺口 | 唯一在巴西情境中测试X的研究 |
| C02 | JONES (2020) | Cap.3 §3.2 | p. 112 | 方法论证 | 验证了本研究所用量表 |
| C03 | CHEN (2019) | Cap.5 §5.1 | p. 78-80 | 反对H2 | 提供替代解释 |
```

---

## 增强版论证脚注模板

```
正文引用后的脚注须包含以下所有信息：

[SOBRENOME, Ano, p. XX-YY] — Título completo. Periódico, v. X, n. X, Ano.
  DOI: 10.XXXX/XXXXX. Disponível em: [URL]. Acesso em: DD mês AAAA.

  [Selecao]: [为何选择此文献用于这个具体段落。]
  [Autoridade]: [为何该作者/文章/机构在该论点上具有学术或技术权重。]
  [Funcao no paragrafo]: [该引用在本段中的具体作用——支持、反驳、补充、对比、定义或方法论证。]
  [Relevancia para a pesquisa]: [与本文研究缺口、目标、假设、变量或方法的直接联系。]
  [Limite de uso]: [该来源能证明什么，不能证明什么，避免外推过度。]

  [Indicadores]: Qualis [等级] / JCR IF [数值] /
  Google Scholar [引用次数] citações.

示例：
  [SILVA et al., 2021, p. 45-47] — Impacto da IA na eficiência
  industrial brasileira. Revista de Administração, v. 56, n. 3, 2021.
  DOI: 10.1590/S0034-75902021000300005.
  Disponível em: https://www.scielo.br/j/rausp/a/XXXXX.
  Acesso em: 16 mar. 2026.

  [Selecao]: Esta fonte foi selecionada por ser um estudo empírico diretamente
  aderente ao recorte industrial brasileiro tratado no parágrafo.

  [Autoridade]: O artigo foi publicado em periódico relevante da área e
  apresenta aderência temática direta ao problema investigado.

  [Funcao no paragrafo]: No parágrafo atual, a fonte fornece evidência
  empírica principal para sustentar H1 sobre associação positiva entre IA e
  eficiência.

  [Relevancia para a pesquisa]: A referência contribui para reduzir a lacuna
  contextual identificada no estudo ao oferecer evidência brasileira, e não
  apenas internacional.

  [Limite de uso]: O estudo sustenta a associação observada no recorte
  investigado, mas não autoriza generalização irrestrita nem inferência causal
  automática.

  [Indicadores]: Qualis A2 / JCR IF 1,89 / 47 citações
  no Google Scholar.
```

---

## Protocolo Operacional de Busca, Selecao e Validacao

Aplicar conjuntamente com [protocolo_rigor_auditavel.md](protocolo_rigor_auditavel.md). A referencia nao e apenas um item bibliografico; ela e uma unidade de prova que precisa de origem, funcao, localizacao e limite.

### Campos minimos no log de busca

```md
| ID | Pergunta | Base | String literal | Filtros | Data | Resultados | Abertos | Lidos integralmente | Incluidos | Motivo |
|---|---|---|---|---|---|---|---|---|---|---|
```

Obrigatorio registrar:

- a pergunta ou subquestao a que a busca responde;
- a string literal usada na base;
- filtros de idioma, periodo, area, tipo documental e ordenacao;
- numero bruto de resultados e numero final de inclusoes;
- motivo de inclusao e motivo de exclusao.

### Criterios de elegibilidade de uma referencia

Uma fonte so pode ser citada se cumprir todos os itens abaixo:

1. Pertinencia direta para o argumento em que sera usada.
2. Texto integral localizado e efetivamente lido.
3. Localizacao exata marcada: pagina, tabela, figura, secao, artigo de lei ou equivalente.
4. Papel argumentativo definido: definicao, suporte, contraste, metodo, contexto, norma ou limitacao.
5. Lastro documental verificavel: DOI, URL oficial, ISBN, repositorio institucional ou fonte primaria equivalente.

### Verificacao referencia a referencia

Antes de inserir uma referencia no texto:

1. Registrar em que busca ela apareceu.
2. Confirmar metadados basicos: autoria, ano, titulo, veiculo e identificador.
3. Confirmar integridade do arquivo e disponibilidade do texto integral.
4. Ler o texto completo e anotar paginas uteis.
5. Preencher uma ficha curta de uso.
6. So entao redigir a citacao no paragrafo correspondente.

### Ficha curta obrigatoria de uso

```md
| ID | Referencia | Papel no artigo | O que prova | O que nao prova | Localizacao exata | Forca da fonte | Observacao critica |
|---|---|---|---|---|---|---|---|
```

### Regras de tolerancia zero

- Nao citar apenas a partir de resumo, titulo, abstract grafico ou slide.
- Nao usar citacao secundaria sem marcar claramente o `apud` e a razao da excecao.
- Nao atribuir a um autor uma afirmacao que aparece apenas na interpretacao de terceiros.
- Nao usar referencia sem papel argumentativo claro.
- Nao usar referencia "bonita" ou prestigiosa se ela nao responde de fato a pergunta do paragrafo.
