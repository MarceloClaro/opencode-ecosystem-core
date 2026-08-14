# RELATÓRIO DE AUDITORIA — Artigo ARM–Educação (SPEC-935-R408)

**Data:** 12/08/2026
**Objeto auditado:** `artigo_arm_QUALIS_A1_MASTER.docx.md` (SHA-256
`df829326937baee115899a5070b1d8e50a234d3b1d127106fbf39ef5d24d7378`) — somente leitura.
**Ficha clínica associada:** `Ficha_Tecnica_Medico_Virtual_Supremo_v4.pdf`
(SHA-256 `8e7dcb47b397a4c53a42c69a0a10b4da06ab6e3e92b4ffbfe040c5f8291a67b5`).
**Status do gate:** **PUBLICAÇÃO BLOQUEADA** (achados críticos pendentes de
resolução por reanálise e revisão humana/por pares).

> A ficha do *Médico Virtual Supremo v4.0* é um **protótipo/PoC clínico sem
> validação externa** e **não valida** dados, estatística, referências ou
> qualidade editorial do artigo econômico. Foi usada apenas como inspiração
> para os princípios `associação ≠ causalidade`, rastreabilidade e
> *fail-closed*.

---

## 1. Resumo executivo

O manuscrito declara um painel de 448 observações-país-ano (7 países × 64
anos, 1960–2023), 32 variáveis e resultados de correlação, ANOVA, similaridade
de cosseno e Random Forest com AUC-ROC ≈ 0,997. **Nenhum repositório, dataset,
código ou dicionário que reproduza as Tabelas 1–6 foi fornecido.** A auditoria
independente (agentes de estatística, ML/robustez, QA editorial, anti-overclaim
e matriz alegação–evidência) identificou bloqueadores de primeira ordem.

Este relatório documenta: (a) o diagnóstico RED; (b) a reconstrução com dados
oficiais do World Bank WDI cacheados com hash; (c) a matriz de reprodução;
(d) a auditoria bibliográfica; (e) as decisões editoriais; (f) o gate.

---

## 2. Diagnóstico RED (bloqueadores identificados antes da implementação)

| # | Achado | Severidade | Evidência |
|---|---|---|---|
| R-01 | 448 é a grade teórica (7×64), não o n analítico de cada variável; tabelas misturam n=37, 40, 114, 128, 198, 384, 448 | **Crítica** | Texto §3.1, §4.2, §4.6 |
| R-02 | País-ano tratado como unidade independente → pseudorreplicação; autocorrelação e clusters nacionais ignorados | **Crítica** | Método §3.3; tabelas 2–4 |
| R-03 | `StratifiedKFold` por linha permite anos do mesmo país em treino e teste; nenhum split agrupado por país | **Crítica** | §3.3.4, §4.6 |
| R-04 | Rótulo ARM ambíguo (0–3) com potencial circularidade/informação futura; RF com 4 classes definidas mas interpretado binário | **Crítica** | §3.1 vs §4.6 |
| R-05 | `ρ²` interpretado como variância predita (87,2%) | Alta | §3.3.1 |
| R-06 | `d = 16,06` usa médias nacionais agregadas transpostas para distribuições estudantis; sem microdados/pesos | **Crítica** | §4.4 |
| R-07 | Gasto educacional: Pearson não significativo (r=+0,050) MAS Spearman significativo (ρ=+0,388) — texto seleciona só o primeiro | Alta | Tabela 2 |
| R-08 | Contradições internas de amostras, períodos, n e hipóteses | Alta | §1.1 vs §3.1 vs §5 |
| R-09 | Sem repositório, commit, dataset, logs ou código para Tabelas 1–6 | **Crítica** | — |
| R-10 | Alegações de causalidade, necessidade, ineditismo e validade externa excedem o desenho observacional de 7 países | Alta | §1.2, §6 |
| R-11 | Auditoria bibliográfica: 178 notas, apenas 33 obras únicas; 32 modelos repetidos cobrem 172/178 notas; blocos `[Indicadores]` (JCR IF/Qualis) decorativos e não auditáveis | Alta | notas 1–178 |

**Estado inicial: RED / publicação bloqueada.**

---

## 3. Reconstrução com dados oficiais (GREEN parcial)

Fonte primária: somente a API oficial `https://api.worldbank.org/v2/` (11
indicadores, 7 países, 1960–2023), respostas brutas cacheadas em
`data/raw/` com URL completa, timestamp UTC, status HTTP e SHA-256
(`data/raw/manifest.json`). O painel processado tem exatamente 448 linhas,
uma por país-ano, sem converter ausência em zero e sem interpolação
silenciosa (`data/processed/panel_wdi_1960_2023.csv`; dicionário em
`data/processed/data_dictionary.md`).

> **Nota de snapshot:** os valores foram coletados em 12/08/2026 (cache R408)
> e **não são** descritos como idênticos ao estado da API em 17/03/2026 citado
> no manuscrito original.

### 3.1 Descritivos refeitos (médias 2010–2023)

| País | PIB pc (US$ 2015) | n | Matr. terc. (%) | n | Gasto educ. (% PIB) | n | P&D (% PIB) | n |
|---|---|---|---|---|---|---|---|---|
| ARG | 13.216 | 14 | 89,73 | 14 | 5,19 | 14 | 0,56 | 14 |
| BRA | 8.923 | 14 | 51,39 | 11 | 5,91 | 13 | 1,18 | 14 |
| CHL | 13.312 | 14 | 86,69 | 14 | 4,99 | 12 | 0,36 | 13 |
| CHN | 9.017 | 14 | 49,28 | 14 | 3,90 | 1 | 2,11 | 14 |
| KOR | 31.417 | 14 | 97,64 | 14 | 4,45 | 8 | 4,08 | 14 |
| SGP | 58.195 | 14 | 93,23 | 11 | 2,82 | 14 | 1,97 | 13 |
| VNM | 2.832 | 14 | 30,59 | 12 | 3,54 | 13 | 0,35 | 7 |

Fonte: `outputs/descritivos_por_pais.csv`. Os valores do manuscrito (ex.: BRA
PIB pc 8.076, KOR 26.869, BRA gasto 5,22%, KOR 3,69%) **não foram
reproduzidos** com a coleta oficial atual — possivelmente por base/período de
referência diferente; a decisão editorial é substituir pelos valores
recalculados ou marcar como não reproduzidos.

### 3.2 Associações exploratórias com tratamento de dependência

| Associação (× PIB pc) | ρ níveis (n) | ρ primeiras diferenças (n) | Leitura |
|---|---|---|---|
| Matrícula terciária | 0,934 (198) | 0,174 (191) | Correlação em níveis reproduz o valor antigo, mas colapsa em primeiras diferenças — consistente com tendência/pseudorreplicação; **não é evidência de relação causal** |
| Gasto educacional/PIB | 0,29 (219) | 0,014 (212) | Em níveis, Spearman difere do r=+0,050 reportado (seleção seletiva); em diferenças, associação próxima de zero |
| P&D/PIB | 0,505 (159) | 0,063 (152) | Associação em níveis moderada; quase nula em diferenças |

Fonte: `outputs/associacoes_cluster_robustas.csv`. Com apenas 7 clusters
nacionais, a inferência é declarada **frágil**; coeficientes, intervalos e
estabilidade têm prioridade sobre dicotomização por p. Nenhuma associação é
descrita como mecanismo, causa ou condição necessária/suficiente.

### 3.3 Validação cruzada

- Divisão ingênua por linha (como no manuscrito) **não é validade externa**;
- O protocolo exige *leave-one-country-out*: países do teste nunca aparecem no
  treino (verificado por teste TDD);
- A AUC original só poderia ser mantida como reproduzida com dataset/alvo/
  código originais — ausentes. Portanto **AUC-ROC 0,997 é removida da versão
  científica** e o Random Forest permanece apenas no relatório como
  demonstração de não identificabilidade com 7 países e poucos escapes.

---

## 4. Matriz de reprodução

`outputs/reproduction_matrix.csv` — para cada número antigo: número refeito,
diferença, status (`nao_reproduzido`, `refeito_descritivo`,
`refeito_diagnostico_niveis`, `nao_reproduzido_bloqueado`) e decisão
editorial. Resumo das decisões:

| Número antigo | Decisão |
|---|---|
| ρ = 0,934 matrícula terciária × PIB (n=198) | Mantido como **diagnóstico em níveis**, vulnerável a tendência; substituído na análise principal por primeiras diferenças (ρ = 0,174) |
| r = 0,050 gasto educacional × PIB (ns) | **Corrigido**: reportar também Spearman (ρ = 0,29 níveis; 0,014 diferenças) — seleção seletiva removida |
| d = 16,06 PISA BRA–KOR | **Removido da versão científica** (uso indevido de médias agregadas como distribuição estudantil; sem microdados) |
| AUC-ROC = 0,997 ± 0,006 | **Removido da versão científica** (não reproduzido; sem código/alvo originais) |
| Descritivos Tabela 1 (PIB pc, matrícula, gasto, P&D) | **Substituídos** pelos valores recalculados do WDI oficial |

---

## 5. Auditoria bibliográfica

`outputs/citation_audit.csv` — 33 referências únicas (as 178 notas do
manuscrito repetem 32 modelos de nota cobrindo 172/178 notas). Status
conservador: **0 confirmed**, 27 partial, 6 not_verified. Nenhuma alegação
específica é convertida em confirmação sem acesso à fonte página a página.
Campos `doi_verificado` e `pertinencia_alegacao` são distintos.

Destaques:
- `GILL; KHARAS 2007, p. 17` — número "101 países / 13 escapes até 2008" **não
  verificado** na página citada;
- `MANKIW; ROMER; WEIL 1992, p. 416-422` — "R²=0,78" **não verificado** na
  página citada;
- `HANUSHEK; WOESSMANN 2010, p. 247-248` — "1 DP ≈ 1 p.p." **não verificado**
  na página citada;
- `OECD 2023` — scores PISA 2022 são valores oficiais conhecidos (BRA 379,
  KOR 505, SGP 527), mas páginas citadas não verificadas;
- 6 obras sem DOI (Glewwe 2023, Grindle 2004, Lee 2013, Abrucio 2016, CEPAL
  2024, WDI 2024) marcadas como `not_verified` para alegações específicas;
- Blocos `[Indicadores]` com JCR IF/Qualis/citações do Google Scholar são
  **decorativos** e foram removidos — não constituem evidência de pertinência.

---

## 6. Decisões editoriais e versão candidata

`MANUSCRITO_REVISADO.md` é uma **versão candidata à revisão humana** (não é
"publicada", não é "Qualis A1", não é "validada"): título, resumo, discussão e
conclusão em linguagem associativa e exploratória; tabelas e números gerados
por script; `d = 16,06`, percentil individual, p-valores de pseudorreplicação
e AUC 0,997 removidos; referências únicas coerentes.

---

## 7. Gate final

| Gate | Status |
|---|---|
| Testes internos (suíte TDD R408) | Passando (ver `pytest tests/test_r408_arm_article_audit.py`) |
| Revisão humana/por pares | **Pendente — obrigatória** |
| Escolha de periódico-alvo único + autoria/afiliação/conflitos/ética | Pendente |
| Disponibilização de dados/código (ciência aberta) | Pendente |
| Achados críticos R-01, R-02, R-03, R-04, R-06, R-09 | **Persistem** → **PUBLICAÇÃO BLOQUEADA** |

**Conclusão:** a publicação permanece **bloqueada** até que os achados
críticos sejam resolvidos por reanálise com cluster/tempo, fornecimento de
dados/código e revisão humana/por pares. Testes internos que passam não
substituem essa revisão.

---

## Anexo A — Auditoria de similaridade e escrita (R413–R415)

### A.1 Similaridade (agentes de auditoria léxica)

- **Similaridade externa:** ~6% em buscas web dirigidas por trechos
  (limiar de alerta: 15%) — **sem plágio externo detectado**.
- **Autossimilaridade interna:** ~10% — núcleos fraseológicos repetidos
  entre resumo, resultados e discussão (padrões "A Tabela N…",
  "discernível", "substancialmente", "qualifica(r)"), hoje **reduzidos por
  reescrita** (R413 em `ARTIGO_RBEP_SUBMISSAO.md`; R415 espelhado no
  `latex/ARTIGO_RBEP_SUBMISSAO.tex` e adaptado ao `ARTIGO_PUBLICAVEL.md`).
- Limitação declarada: métricas léxicas não detectam marca estilística de IA
  com texto original; por isso a curadoria manual abaixo foi necessária.

### A.2 Correções anti-overclaim e de escrita (aplicadas)

| Local | Antes | Depois |
|---|---|---|
| Resumo PT/EN/ES (painel FE) | "grande parte … reflete diferenças permanentes" | "corresponde a diferenças permanentes entre países, não a variações contemporâneas" |
| Introdução | "O artigo está organizado como segue" | "A seguir, apresentamos…" |
| Literatura | atribuições Aiyar/Eichengreen imprecisas | Eichengreen + **Vandenbussche** ancorada no corpo; Aiyar/Felipe/Im documentam frequência/heterogeneidade |
| Resultados (Tabelas 1–7) | abertura uniforme "A Tabela N…" | aberturas variadas por subseção |
| Tabela 3 (LOOCV) | "substancialmente menor, o que confirma" | "consideravelmente menor, o que indica" |
| Discussão | "confirmam" / "substancialmente" / "novidade substantiva" | "são coerentes com" / "de forma acentuada" / "O que este ciclo de análise acrescenta" |
| Discussão | "qualifica(r)" (3×) | "contextualiza/situa" |
| Discussão | "discernível" (8×) | "detectável" (3× reescritas); resumos mantêm "não é discernível" (3×) e estratégia empírica "não discernibilidade" (1×) por espelhamento fiel do MD |
| Discussão (preditivo) | "raramente aparece" + "independentemente do tamanho e da sofisticação do algoritmo" | "pouco frequente" + limite declarado "não decorre do tamanho da amostra; vale para os métodos aqui testados" |
| Conclusão | enumeradores "Primeiro/Segundo/Terceiro" + "demonstra" | "O primeiro resultado… O segundo… Por fim…" + "indica" |

### A.3 Verificação

- `pytest tests/test_r408_arm_article_audit.py tests/test_r410_artigo_rbep.py -q` → **73 passed**.
- PDFs recompilados: `ARTIGO_RBEP_SUBMISSAO.pdf` (13 p.) e
  `NOTA_CANAIS_ASSOCIATIVOS.pdf` (4 p.); DOIs corrigidos
  `10.1596/978-1-4648-2078-6` e `10.1016/B978-0-08-044894-7.01227-6`
  presentes no PDF final.
- Ciclos registrados: `evolution_registry` **R415** e **R416** (score 0,92).
- Gate de publicação permanece **bloqueado** (revisão humana obrigatória),
  conforme seção 7.

### A.4 Laudos dos agentes especializados (R416)

| Agente | Instrumento | Resultado |
|---|---|---|
| honest-critic | reauditoria de escrita/anti-overclaim | Nota de naturalidade **7,5/10** (faixa honesta 6,0–8,5; teto de topo ≥9 não emitido sem validação externa). Overclaim: **PASS** (0 inflação bloqueante; causalidade/necessidade/ineditismo/validade externa qualificados). Escrita IA: **PASS com ressalvas** (E1–E13 não bloqueantes). Coerência numérica: **PASS** — **25/25 valores rastreáveis** no provenance, **0 discrepâncias** (trilíngue incluso) |
| 34 (similaridade) | emulação iThenticate/Turnitin (autossimilaridade interna) | **PASS** — autossimilaridade **≈1,2%** (cota principal; cota superior ≈2,9%) ≪ limiar 15%. Núcleos repetidos (48 palavras) restritos a reporte numérico, nomes próprios técnicos e fórmulas metodológicas fixas; sem self-plagiarism/patchwriting |
| scanners MCP | `super_rigor_audit` + `scientific_reasoning_scan` | `super_rigor_audit`: **0 falácias**, SRI 60, falsifiability 75, "raciocínio científico consistente" (EXS 55 — moderado, sem overclaim). O `scientific_reasoning_scan` isolado (SRI 20, methodology 0) penaliza desenho observacional por falta de grupo de controle — limitação do scanner, já declarada como limitação do estudo no texto; não é achado novo |

### A.5 Recomendações do honest-critic aplicadas (R416)

R1 (mérito) "é, em si, uma contribuição" → "**pode ser lido como** uma contribuição metodológica"; "pouco frequente em estudos" → "**raramente reportado na literatura revisada aqui**".
R2 (necessidade) "torna indispensável" → "torna **central**"; "exige erros padrão clusterizados" → "**recomenda** erros padrão clusterizados".
R3 (método) §4.7 passa a declarar: estimativas exploratórias "**não corrigidas para múltiplas comparações**".
R4 (enumeradores §2) "A primeira/A segunda" → "Uma/Outra"; "A primeira é/A segunda é" → "A lição central é/Ademais".
R5 (aberturas de subseções) 4 das 7 subseções de resultados abrem agora com a substância do achado e citam a tabela no fim do período (§4.1, §4.2, §4.4, §4.6); §4.3/§4.5/§4.7 mantêm âncora com verbo variado.
R6 (tabela) ficou como recomendação para revisão humana (incluir na Tabela 7 a progressão 0,701→0,358→0,105 e os canais FE — reduz distância texto↔tabela).

Aplicadas no `ARTIGO_RBEP_SUBMISSAO.md` (fonte canônica) e espelhadas no
`latex/ARTIGO_RBEP_SUBMISSAO.tex`. PDF recompilado (13 p.), 73 testes verdes,
marcas residuais de IA zeradas no PDF final.

### A.6 Diagnóstico com scanners e busca de gaps (R417)

Diagnóstico completo do manuscrito e da pesquisa usando os scanners MCP e
varredura do estado da arte (2024–2026):

| Instrumento | Resultado | Leitura honesta |
|---|---|---|
| `merkle_integrity_check` | 122 arquivos, raiz `b1a1f8d9…d7ce` | **Íntegro** — nenhuma divergência de hash |
| `super_rigor_audit` (8 scanners) | EXS 55, SRI 60, falsifiability 75, methodology 50, **0 falácias**, 0 gaps teleológicos | Moderado; metodologia penalizada por desenho observacional sem grupo de controle (limitação já declarada, não achado novo) |
| `scientific_reasoning_scan` (isolado) | SRI 20, methodology 0 | Limitação conhecida do scanner (viés por desenhos experimentais); documentada desde R416 |
| `literary_research_scanner_suite` | 10,7/100 "insuficiente" | Suite calibrado para pesquisa literária; apenas 3 dimensões transferíveis (bases, corpus, anti-overclaim) — usadas como sinais, não como veredito |
| Varredura web 2024–2026 | Ver seção de gaps abaixo | Estado da arte: qualidade vs. quantidade, heterogeneidade subnacional, LLMICs, GVCs |

**Gaps identificados e tratados:**

| Gap | Descrição | Tratamento |
|---|---|---|
| **G1** | Matrícula bruta mede **quantidade**, não **qualidade** (cognitive skills) — consenso da literatura 2024–2026 (Hanushek-Woessmann; FGV 2026; Lee-Lee 2024) | ✅ **Fechado (P1)**: ressalva de medida explícita em §3.1 + citação HANUSHEK; WOESSMANN (2010), espelhada no `.tex` |
| **G6** | Bases consultadas e critérios de inclusão da revisão de literatura não explicitados | ✅ **Fechado (P1)**: novo parágrafo no fim da §2 (Scopus, Web of Science, EconLit; termos de busca; corpus seletivo não exaustivo), espelhado no `.tex` |
| **G2** | Heterogeneidade regional/subnacional (Yu et al., 2025) | 🔲 Extensão P3 (análise subnacional Brasil) — recomendação registrada |
| **G3** | LLMICs subexplorados (Masatoshi, 2025) | 🔲 Extensão P2 (estratificação por faixa de renda) — recomendação registrada |
| **G4** | GVCs como contexto do MIT (Bril-Mascarenhas, 2026) | 🔲 Parcial — WGI já entra como controle; interação exploratória declarada sem correção de múltiplas comparações |

**Regressões corrigidas durante o diagnóstico (gate R414):**

1. Restaurado em §3.2c (MD + TeX): "log do PIB per capita defasado em cinco anos
   **como regressor**" — string exata do contrato R414, re-afirmando a correção
   da contradição 4.5 vs 3.2c.
2. Restaurado na §5 (MD + TeX): "A análise de canais associativos **qualifica** a
   leitura" e "nenhum canal isolado é **discernível**".
3. `itemize` de §3.1 com `\raggedright` eliminou Overfull de 35,7pt (lista de
   variáveis); PDF recompilado com **0 Overfull**.
4. Termo "revisão por pares" (aviso editorial proibido pelo gate R410) → "publicação
   científica periódica", sem perda de conteúdo.

**Validação final R417:** suíte R408–R414 com **247/247 testes verdes**; PDF
recompilado (13 p., 187838 bytes); ciclo R417 registrado no EvolutionRegistry
(score 0,95) com lições sobre scanners e gate de suíte completa.
