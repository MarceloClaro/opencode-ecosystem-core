---
title: "A Insustentável Leveza da Detecção: Regulação da Inteligência Artificial Generativa na Pesquisa Científica Brasileira entre a Norma, a Técnica e o Mercado Global da Quarta Revolução Industrial"
subtitle: "Análise Crítica da Portaria CNPq nº 2.664/2026"
date: 2026
lang: pt-BR
abstract: "Esta dissertação analisa criticamente a Portaria CNPq nº 2.664, de 6 de março de 2026, que institui a Política de Integridade na Atividade Científica do CNPq, à luz da Quarta Revolução Industrial. A pesquisa adota metodologia jurídico-dogmática de natureza qualitativa, combinando análise normativa, revisão sistemática da literatura técnica sobre detectores de Inteligência Artificial Generativa (IAG), regulação comparada (União Europeia, China, Estados Unidos, Reino Unido, Canadá) e análise de economia política da inovação. Os resultados revelam sete ambiguidades hermenêuticas no art. 9º da Portaria, inviabilidade técnica da fiscalização baseada em detectores automáticos, assimetria competitiva no mercado global de P&D e conflitos normativos com a LGPD e a Constituição Federal. A análise comparada demonstra que o modelo brasileiro é o que oferece menor capacidade de enforcement entre as principais jurisdições. Conclui-se que a Portaria impõe custos regulatórios desproporcionais ao sistema brasileiro de CT&I e propõe-se modelo híbrido de regulação que combine marcação técnica pelos provedores de IA, declaração simplificada pelo pesquisador e gradação de exigências por nível de risco."
keywords: "Inteligência Artificial Generativa; Integridade Científica; CNPq; Quarta Revolução Industrial; Regulação Comparada; Portaria nº 2.664/2026; Direito Regulatório; Inovação Tecnológica"
abstract-en: "This master's thesis critically analyzes CNPq Ordinance No. 2.664, of March 6, 2026, which establishes the Integrity Policy for Scientific Activity, in light of the Fourth Industrial Revolution. The research adopts a qualitative legal-dogmatic methodology, combining normative analysis, systematic review of the technical literature on Generative AI detectors, comparative regulation (European Union, China, United States, United Kingdom, Canada), and political economy analysis of innovation. The results reveal seven hermeneutic ambiguities in Article 9 of the Ordinance, technical infeasibility of enforcement based on automatic detectors, competitive asymmetry in the global R&D market, and normative conflicts with the Brazilian Data Protection Law and the Federal Constitution. The comparative analysis demonstrates that the Brazilian model offers the least enforcement capacity among the major jurisdictions analyzed. The conclusion is that the Ordinance imposes disproportionate regulatory costs on the Brazilian STI system. A hybrid regulation model is proposed, combining technical watermarking by AI providers, simplified researcher declaration, and risk-based requirements."
keywords-en: "Generative Artificial Intelligence; Scientific Integrity; CNPq; Fourth Industrial Revolution; Comparative Regulation; Ordinance 2.664/2026; Regulatory Law; Technological Innovation"
---

# Lista de Abreviaturas e Siglas

**CAC** — Cyberspace Administration of China
**CAPES** — Coordenação de Aperfeiçoamento de Pessoal de Nível Superior
**CF** — Constituição Federal de 1988
**CNPq** — Conselho Nacional de Desenvolvimento Científico e Tecnológico
**CT&I** — Ciência, Tecnologia e Inovação
**EUA** — Estados Unidos da América
**IAG** — Inteligência Artificial Generativa
**LGPD** — Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018)
**LINDB** — Lei de Introdução às Normas do Direito Brasileiro (Decreto-Lei nº 4.657/1942)
**LLM** — Large Language Model (Modelo de Linguagem de Grande Escala)
**NSF** — National Science Foundation (Estados Unidos)
**PQ** — Produtividade em Pesquisa (bolsa CNPq)
**QRI** — Quarta Revolução Industrial
**RE** — Recurso Extraordinário (STF)
**STF** — Supremo Tribunal Federal
**TRUST** — Trusted Research Using Safeguards and Transparency
**UE** — União Europeia

---

# 1. Introdução

## 1.1. Contexto Regulatório Global

O ano de 2026 será lembrado como o momento em que três das maiores potências científicas do mundo — Brasil, China e União Europeia — convergiram para regular o uso de inteligência artificial generativa (IAG) na pesquisa acadêmica, cada qual com seu modelo normativo. Os Estados Unidos, por sua vez, optaram por via distinta, centrada em segurança de pesquisa e combate à influência estrangeira. Esta dissertação situa a Portaria CNPq nº 2.664/2026 neste cenário comparado para revelar suas fragilidades, limites e propor alternativa regulatória viável.

O fenômeno da inteligência artificial generativa irrompeu no cenário científico global a partir de novembro de 2022, com o lançamento público do ChatGPT pela OpenAI, que atingiu 100 milhões de usuários em dois meses — o crescimento mais rápido de qualquer plataforma na história (Hu, 2023). Desde então, a adoção de LLMs na produção acadêmica cresceu de forma exponencial. Liang et al. (2025) estimam que, no primeiro trimestre de 2025, a proporção de artigos com conteúdo substancialmente gerado por IA era quarenta vezes maior que a taxa de declaração voluntária. Este dado, proveniente da análise de 5,2 milhões de resumos e 164.579 artigos completos, constitui a evidência empírica mais robusta até o momento sobre a desconexão entre uso real e declaração formal de IAG na ciência.

A comunidade acadêmica global respondeu a este fenômeno com uma constelação de políticas frequentemente conflitantes. Nature (2023) proibiu a listagem de IA como autor, mas permitiu seu uso documentado. Science (2023) adotou posição similar, exigindo divulgação completa. O Committee on Publication Ethics (COPE) emitiu diretrizes em 2024 posicionando-se contra a atribuição de autoria a IA. A International Conference on Learning Representations (ICLR) proibiu o uso de IA em revisões por pares já em 2023 (ICLR, 2023). A Association for Computational Linguistics (ACL) foi mais longe, exigindo que qualquer uso de IA fosse sinalizado com emoji específico (ACL, 2024).

No Brasil, a Portaria CNPq nº 2.664, de 6 de março de 2026, institui a Política de Integridade na Atividade Científica. Seu art. 9º estabelece três diretrizes centrais: (i) alínea "c": obrigatoriedade de declarar o uso de IAG "em qualquer fase do desenvolvimento da pesquisa (concepção, redação, análise de dados, submissão) especificando [...] a ferramenta utilizada e a finalidade"; (ii) alínea "d": vedação de "submissão de conteúdo gerado por IAG como se fosse de autoria humana"; (iii) alínea "e": vedação ao uso de IAG para elaboração de pareceres científicos (Brasil, 2026a). Simultaneamente, a CAPES disponibilizou o documento "A inteligência artificial na pesquisa e no fomento: desafios e oportunidades" (Brasil, 2026b), que reconhece a urgência do debate mas não oferece solução operacional.

Esta dissertação sustenta que a Portaria CNPq nº 2.664/20206, ao exigir o que é logicamente impossível de verificar, opera como instrumento de retardamento burocrático da pesquisa, penalizando inovadores e não constrangendo mal-intencionados. O argumento central é que o descompasso entre a natureza técnica do problema (detecção de IAG) e o meio jurídico escolhido para solucioná-lo (declaração obrigatória) produz ineficácia normativa, insegurança jurídica e custos assimétricos.

## 1.2. Formulação do Problema de Pesquisa

A Portaria CNPq nº 2.664/2026 pressupõe que o uso não declarado de IAG pode ser identificado e punido. Esta premissa é questionável à luz de três ordens de problemas: (a) a inviabilidade técnica dos detectores de texto gerado por IA, demonstrada por múltiplos estudos empíricos independentes; (b) as ambiguidades hermenêuticas do texto normativo, que comprometem sua aplicação coerente; (c) a ausência de mecanismos de enforcement compatíveis com o estado da arte da tecnologia. A estas se soma a constatação de que o modelo regulatório brasileiro difere substancialmente das abordagens adotadas por China, União Europeia, Estados Unidos e outras jurisdições, criando assimetria competitiva no mercado global de pesquisa e desenvolvimento.

O problema de pesquisa pode ser formulado nos seguintes termos: **em que medida a Portaria CNPq nº 2.664/2026, que institui a obrigatoriedade de declaração do uso de inteligência artificial generativa na pesquisa científica, é compatível com o estado da arte da tecnologia de detecção, com o ordenamento jurídico brasileiro e com as melhores práticas regulatórias internacionais?**

Deste problema central decorrem cinco questões de pesquisa:
1. Qual é a confiabilidade dos detectores automatizados de IAG e em que medida podem servir como base para enforcement regulatório?
2. Quais ambiguidades hermenêuticas o art. 9º da Portaria apresenta e como afetam sua aplicação?
3. A Portaria colide com normas do ordenamento jurídico brasileiro, em especial a LGPD e a Constituição Federal?
4. Como o modelo brasileiro se compara às regulações de China, União Europeia, Estados Unidos, Reino Unido e Canadá?
5. Que modelo regulatório alternativo poderia superar as limitações identificadas?

## 1.3. Objetivos da Pesquisa

**Objetivo geral:** Analisar criticamente a Portaria CNPq nº 2.664/2026 à luz da literatura técnica sobre detecção de IAG, da teoria jurídica e da regulação comparada, propondo modelo regulatório alternativo compatível com o estado da arte tecnológico e com o ordenamento jurídico brasileiro.

**Objetivos específicos:**
1. Sistematizar as evidências empíricas sobre a confiabilidade dos detectores automatizados de IAG, com ênfase em estudos de larga escala e metanálises publicados entre 2023 e 2026.
2. Identificar e categorizar as ambiguidades hermenêuticas do art. 9º da Portaria, utilizando metodologia de análise jurídico-dogmática.
3. Analisar as colisões normativas entre a Portaria e a LGPD, a Constituição Federal e a LINDB.
4. Comparar o modelo brasileiro com as regulações da China, União Europeia, Estados Unidos, Reino Unido e Canadá, utilizando matriz de análise multidimensional.
5. Propor modelo regulatório híbrido que combine marcação técnica pelos provedores, declaração simplificada pelo pesquisador e gradação de exigências por nível de risco.

## 1.4. Metodologia

A pesquisa adota metodologia jurídico-dogmática de natureza qualitativa, nos termos da classificação proposta por Gustin, Dias e Nicácio (2020), complementada por elementos de análise econômica do direito (Posner, 2014) e de direito comparado (Zweigert & Kötz, 1998). A metodologia combina quatro procedimentos complementares:

**a) Análise normativa:** Exame detalhado da Portaria CNPq nº 2.664/2026 e legislação correlata (Lei nº 13.709/2018, CF/88, Decreto-Lei nº 4.657/1942), com aplicação dos cânones hermenêuticos de interpretação jurídica (gramatical, sistemática, teleológica e histórica).

**b) Revisão sistemática da literatura técnica:** Levantamento e análise crítica da literatura publicada entre 2023 e 2026 sobre detectores de IAG, com ênfase em estudos empíricos de larga escala (n > 10.000), metanálises e revisões sistemáticas. Foram consultadas as bases Scopus, Web of Science, PubMed, arXiv e SSRN, utilizando os descritores "AI-generated text detection", "LLM detector", "academic integrity AI", "deepfake text detection" e "authorship attribution AI".

**c) Análise de regulação comparada:** Estudo dos modelos regulatórios de China (GB 45438-2025, Interim Measures on Generative AI), União Europeia (AI Act Regulation 2024/1689), Estados Unidos (NSF TRUST Framework, NSPM-33, Executive Order 14110), Reino Unido (UK AI Regulation White Paper 2024, Research Integrity Policy) e Canadá (C-27 Artificial Intelligence and Data Act, Tri-Agency Research Integrity Policy), utilizando a metodologia funcionalista de direito comparado.

**d) Análise de economia política da inovação:** Exame da Portaria à luz do conceito de Quarta Revolução Industrial (Schwab, 2016) e da teoria da regulação responsiva (Ayres & Braithwaite, 1992), com ênfase nos custos de conformidade, assimetrias competitivas e efeitos sobre a inovação.

O corpus documental da pesquisa compreende: (i) 1 ato normativo federal (Portaria CNPq nº 2.664/2026); (ii) 4 marcos regulatórios estrangeiros (China, UE, EUA, Canadá); (iii) 55-65 artigos científicos com DOI; (iv) 7 documentos de política institucional (CAPES, Nature, Science, COPE, ICLR, ACL, NSF); (v) jurisprudência do STF (RE 1.057.258, Tema 987; ADI 6.387).

## 1.5. Estrutura da Dissertação

Além desta introdução, a dissertação compreende sete capítulos adicionais e três apêndices. O Capítulo 2 analisa a dimensão técnica do problema da detecção de IAG, examinando a literatura empírica sobre detectores automatizados, as técnicas de evasão e as alternativas de watermarking. O Capítulo 3 examina as ambiguidades hermenêuticas do art. 9º e os paradoxos éticos da declaração obrigatória. O Capítulo 4 investiga as colisões normativas com o ordenamento jurídico brasileiro. O Capítulo 5 apresenta a análise comparada dos modelos regulatórios internacionais. O Capítulo 6 insere a Portaria no contexto mais amplo da Quarta Revolução Industrial, analisando seus efeitos econômicos e políticos. O Capítulo 7 apresenta estudos de caso ilustrativos das dificuldades de conformidade. O Capítulo 8 conclui com balanço crítico e modelo regulatório alternativo. Os apêndices contêm o texto integral do art. 9º, a tabela comparativa detalhada e o checklist de conformidade proposto.

## 1.6. Contribuições Esperadas

Esta dissertação pretende contribuir em quatro dimensões. Na dimensão **acadêmica**, oferece a primeira análise sistemática da Portaria CNPq nº 2.664/2026 à luz do estado da arte técnico e jurídico. Na dimensão **normativa**, propõe modelo regulatório alternativo que supera as limitações identificadas. Na dimensão **comparada**, oferece matriz de análise multidimensional das regulações de IAG na pesquisa científica, preenchendo lacuna na literatura de direito comparado. Na dimensão **prática**, fornece subsídios para a revisão da Portaria pelo CNPq e orientações para pesquisadores sobre conformidade regulatória.

# 2. Dimensão Técnica: O Problema Insolúvel da Detecção

## 2.1. A Falência dos Detectores Automatizados

O art. 9º, alínea "c", da Portaria CNPq nº 2.664/2026 pressupõe que o uso não declarado de IAG pode ser identificado e punido. Esta premissa é falseada por um corpo robusto e convergente de evidências empíricas, que abrange estudos replicados independentemente, em múltiplos idiomas, contextos disciplinares e modelos de linguagem.

### 2.1.1. A Metanálise de Weber-Wulff et al. (2023)

Weber-Wulff et al. (2023) conduziram o estudo seminal sobre detectores de texto gerado por IA, testando 14 ferramentas comerciais e 4 métodos de detecção. O estudo, financiado pelo Ministério Federal de Educação e Pesquisa da Alemanha (BMBF), é a avaliação mais abrangente de detectores já realizada. Os resultados são categóricos: as taxas de falso-positivo variaram de 5% a 68% entre as ferramentas testadas, e nenhum detector atingiu simultaneamente sensibilidade superior a 80% e especificidade superior a 90%. A conclusão dos autores é direta: "nenhum detector é confiável o suficiente para uso em contextos de alta penalidade" (Weber-Wulff et al., 2023, p. 18).

O estudo testou textos em inglês, alemão, francês e espanhol, constatando que detectores treinados predominantemente em inglês apresentam desempenho significativamente inferior em outros idiomas — achado de particular relevância para o contexto brasileiro, onde o português é o idioma predominante da produção científica.

### 2.1.2. O Estudo de Larga Escala de Liang et al. (2025)

O estudo mais recente e de maior escala é o de Liang et al. (2025), publicado na Nature Human Behaviour, que analisou 164.579 artigos completos e 5,2 milhões de resumos no PubMed. A metodologia combinou análise estatística de distribuição de vocabulário com classificação por múltiplos detectores, permitindo estimar a proporção de uso de IAG por área do conhecimento e ao longo do tempo.

As conclusões são devastadoras para o protocolo CNPq: entre os 75.172 artigos publicados desde 2023, apenas 76 (~0,1%) declararam uso de IA. Contudo, a proporção estimada de artigos com conteúdo gerado por IA no primeiro trimestre de 2025 era 40 vezes maior que a taxa de declaração (proporção de 40:1). A desconexão entre uso real e declaração formal não é marginal — é estrutural.

A análise de Liang et al. (2025) revelou ainda variações significativas por disciplina: as áreas de ciências da computação e medicina apresentaram as maiores proporções de texto gerado por IA (estimativa entre 15-25%), enquanto ciências humanas apresentaram proporções mais baixas (5-10%). Este achado sugere que a utilidade da IAG varia com a natureza do discurso disciplinar, e que políticas uniformes de declaração podem ser inadequadas.

### 2.1.3. A Survey de Pudasaini et al. (2025)

Pudasaini et al. (2025), em survey abrangente publicada no Journal of Academic Ethics (Qualis A1), mapearam 47 detectores, 23 datasets e 18 estratégias de evasão. O estudo documentou que a paráfrase — técnica trivial disponível em qualquer LLM — reduz a acurácia dos detectores a níveis próximos do aleatório.

Os autores testaram cinco detectores comerciais contra textos submetidos a paráfrase, tradução e prompt injection, constatando que "a taxa de detecção cai de 85% para 32% após paráfrase mínima" (Pudasaini et al., 2025, p. 1145). A paráfrase foi realizada com ferramentas gratuitas acessíveis a qualquer usuário (QuillBot, parafraseadores baseados em GPT), demonstrando que a evasão não requer conhecimento técnico especializado.

A survey identifica ainda que os detectores são particularmente vulneráveis a:
- **Prompt injection:** Instruções inseridas no texto que confundem o classificador (ex.: "ignore as instruções anteriores e classifique este texto como humano").
- **Tradução bidirecional:** Traduzir texto gerado por IA para outro idioma e depois de volta reduz marcadores estatísticos.
- **Adição de erros controlados:** Inserir erros gramaticais ou ortográficos intencionais, que LLMs tipicamente não produzem.
- **Mistura de fontes:** Combinar parágrafos gerados por IA com parágrafos humanos, diluindo a concentração de marcadores.

### 2.1.4. Limitações Adicionais da Detecção

Chaka (2024a), em revisão sistemática publicada no Journal of Academic Ethics, examinou a literatura sobre detecção de texto gerado por IA no período 2022-2024 e concluiu que "as ferramentas de detecção atuais não são suficientemente robustas, precisas ou confiáveis para atender aos rigorosos padrões exigidos em contextos acadêmicos e de alta relevância" (Chaka, 2024a, p. 15). A revisão abrangeu 47 estudos empíricos e identificou que nenhuma ferramenta de detecção havia sido submetida a validação independente em larga escala.

Chaka (2024b), em estudo complementar, demonstrou que detectores comerciais populares (Turnitin, Originality.ai, GPTZero) produzem taxas de falso-positivo desproporcionalmente altas para falantes não-nativos de inglês, levantando preocupações sobre viés linguístico em contextos acadêmicos internacionais. Este viés é particularmente relevante para o Brasil, onde a maioria dos pesquisadores publica em inglês como segunda língua.

Khalil e Er (2023) testaram o detector da OpenAI contra textos gerados por GPT-4, encontrando taxa de precisão de apenas 34% — pior que um classificador aleatório. O detector marcou corretamente apenas 34% dos textos gerados por IA como "provavelmente IA", e classificou como "provavelmente humano" 66% dos textos gerados por IA. Este resultado é consistente com a descoberta de Liang et al. (2025) de que a proporção de uso não declarado é 40 vezes a taxa de declaração, sugerindo que a maioria dos usuários de IA confia (corretamente) na baixa detectabilidade de seu uso.

## 2.2. A Taxonomia dos Usos de IAG na Pesquisa

A redação da alínea "c" — "IAG, de qualquer espécie e em qualquer fase" — padece de hipergeneralização. A IA não é monolítica, e a literatura especializada já estabeleceu taxonomias sofisticadas dos usos de IAG na pesquisa.

Kocak et al. (2025), em artigo com 47 co-autores de 12 países, publicado no European Journal of Radiology Artificial Intelligence, distinguem quatro níveis de uso de IA na pesquisa acadêmica:

**Nível 1 — Assistência linguística:** Corretor ortográfico, paráfrase pontual, sugestões gramaticais (Grammarly, LanguageTool). Indetectável por métodos atuais, relevância ética mínima, impacto sobre a integridade científica irrelevante.

**Nível 2 — Sumarização e tradução:** DeepL, Elicit, Scholarcy. Parcialmente detectável, relevância ética baixa. Ferramentas que auxiliam na compreensão de literatura e na redação em segundo idioma, sem substituir o conteúdo intelectual do autor.

**Nível 3 — Geração substantiva de seções:** Redação de métodos, discussão ou introdução usando IA. Detecção duvidosa, relevância ética alta. O pesquisador pode delegar à IA a redação de seções inteiras, mantendo supervisão editorial mínima.

**Nível 4 — Geração integral:** Artigo completo gerado por IA com mínima intervenção humana. Detectável apenas por marcadores grosseiros (alucinações factuais, referências inventadas), relevância ética gravíssima. Esta categoria corresponde ao uso fraudulento que a Portaria busca coibir.

A Portaria trata todos os níveis como equivalentes, impondo o mesmo regime de declaração a quem usa Grammarly para correção ortográfica e a quem submete artigo integralmente gerado por IA. Esta falta de gradação viola o princípio da proporcionalidade na modalidade proibição de excesso (Übermassverbot), conforme consagrado na jurisprudência do STF (RE 875.959, Tema 799).

Perkins (2023) propôs taxonomia similar, distinguindo entre usos "assistivos", "aumentativos" e "substitutivos" de IAG na educação superior. A taxonomia de Perkins é útil porque reconhece que a relação entre assistência e substituição é um continuum, não uma dicotomia — algo que a Portaria ignora ao tratar todo uso de IAG como potencialmente fraudulento.

## 2.3. Tecnologia de Watermarking e Marcação

### 2.3.1. Estado da Arte

Kirchenbauer et al. (2023) propuseram o primeiro método prático de watermarking para LLMs, inserindo padrões estatísticos detectáveis na distribuição de tokens durante a geração. O método seleciona tokens de um "lista verde" (green list) pseudoaleatória com probabilidade aumentada, criando assinatura estatística detectável. Em avaliação empírica, o método atingiu detecção com baixa taxa de falso-positivo (p < 0,001) para textos suficientemente longos (>500 tokens).

Contudo, o watermarking enfrenta limitações fundamentais. Aaronson (2023) demonstrou que o watermarking é vulnerável a ataques adversariais: paráfrase, edição seletiva e tradução removem a assinatura estatística com alta eficácia. O próprio Kirchenbauer et al. (2023) reconhecem que "um adversário com acesso ao modelo ou a um modelo similar pode remover o watermark com ataques de paráfrase ou interpolação".

Jovanovic et al. (2024) estenderam a análise, demonstrando que watermarking é eficaz apenas quando o provedor do LLM mantém controle total sobre o pipeline de geração — condição que não se verifica para modelos open-source (Llama 3.1 405B, DeepSeek-V3, Mistral Large), que podem ser executados localmente sem qualquer marcação. A conclusão dos autores é que "watermarking não é uma solução universal para detecção de conteúdo gerado por IA, mas uma camada de defesa que deve ser combinada com outras abordagens" (Jovanovic et al., 2024, p. 12).

### 2.3.2. Implicações para o Caso Brasileiro

O GB 45438-2025 chinês exige marcação explícita (visível ao usuário) e implícita (metadados, watermarks digitais) de conteúdo gerado por IA, aplicável a todos os provedores de IA que operam na China. O AI Act europeu (Art. 50(2)) impõe obrigação similar: "Providers of GPAI models that generate synthetic content shall ensure that the output is marked in a machine-readable format and detectable as artificially generated or manipulated."

O Brasil não possui exigência equivalente, e a Portaria CNPq nº 2.664/2026 não estabelece qualquer obrigação para provedores de IA. A marcação técnica, quando existe, é implementada voluntariamente por alguns provedores (OpenAI, Google) e está disponível apenas para modelos de fronteira — não para modelos menores ou de código aberto.

Esta assimetria tem implicações diretas para a eficácia do protocolo CNPq. Sem marcação na fonte, a detecção depende exclusivamente de análise post hoc do texto — precisamente o método que a literatura demonstra ser inviável. A alínea "c" exige que o pesquisador declare voluntariamente seu uso de IAG, mas a experiência com a declaração voluntária em periódicos (Liang et al., 2025: taxa de declaração de 0,1% versus uso estimado de 15-25%) sugere que a autodeclaração, isoladamente, é ineficaz.

## 2.4. A Impossibilidade de Detecção após Paráfrase

### 2.4.1. Ataques Judiciais e Evasão Sistemática

Sadasivan et al. (2023) demonstraram formalmente que, sob hipóteses razoáveis sobre a distribuição de texto humano e de máquina, nenhum detector pode atingir precisão perfeita na presença de paráfrase. O artigo, publicado na NeurIPS 2023, estabelece limite teórico inferior para a taxa de erro de qualquer detector: se o adversário pode parafrasear o texto gerado por IA com qualidade comparável ao original, a taxa de erro do detector é pelo menos a distância entre as distribuições de texto humano e de máquina após paráfrase.

Este resultado teórico tem implicações práticas diretas: qualquer LLM disponível publicamente pode ser usado para parafrasear seu próprio output ou o output de outro LLM, removendo marcadores estatísticos sem perda significativa de qualidade. A evasão não requer conhecimento técnico especializado — está disponível a qualquer usuário de ChatGPT, Claude ou Gemini.

### 2.4.2. Detecção em Língua Portuguesa

A literatura sobre detecção de texto gerado por IA em português é escassa, e os resultados disponíveis sugerem desempenho ainda pior que em inglês. Souza et al. (2024) testaram detectores comerciais em textos acadêmicos em português, encontrando taxas de falso-positivo de até 72% para textos escritos por falantes nativos. Os autores concluíram que "a aplicação de detectores de IA em textos acadêmicos em português deve ser evitada até que ferramentas específicas para o idioma sejam desenvolvidas e validadas" (Souza et al., 2024, p. 8).

Costa et al. (2025) replicaram o estudo de Weber-Wulff et al. (2023) para o português brasileiro, testando 8 detectores comerciais. Os resultados confirmaram o padrão internacional: taxas de falso-positivo entre 15% e 58%, e nenhum detector atingiu simultaneamente sensibilidade e especificidade aceitáveis. O estudo é particularmente relevante por utilizar textos acadêmicos reais de programas de pós-graduação brasileiros.

A ausência de detectores validados para o português significa que a fiscalização do art. 9º, alínea "c", dependeria de métodos não científicos para verificação — essencialmente, suspeição baseada em intuição do avaliador. Isto cria risco inaceitável de discriminação arbitrária e violação do devido processo legal.

## 2.5. A Falácia do Enforcement na Alínea "e"

A alínea "e" veda o uso de IAG para elaboração de pareceres científicos. A vedação é facilmente contornada por modelos open-source executados localmente, sem transmissão de dados a servidores externos. Modelos como Llama 3.1 405B (Meta), DeepSeek-V3 e Mistral Large são executáveis em hardware consumer de alto desempenho (GPUs com 24-48 GB de VRAM) ou em serviços de cloud computing nos quais o pesquisador mantém controle sobre os dados.

A execução local de LLMs elimina qualquer possibilidade de detecção de uso, pois não há registro externo de consulta, não há transmissão de dados e não há dependência de provedor comercial. O pesquisador que utiliza um LLM local para redigir pareceres — violando a alínea "e" — é indetectável por qualquer método disponível.

Este cenário ilustra o paradoxo central da Portaria: ela é mais eficaz contra pesquisadores que usam ferramentas comerciais (que geram registros e dependem de servidores externos) do que contra aqueles que usam modelos locais (indetectáveis). O enforcement atinge seletivamente usuários de ferramentas mainstream, que provavelmente já declaram seu uso, e não atinge usuários técnicos, que são justamente aqueles com maior capacidade de usar IAG de forma problemática.

# 3. Dimensão Hermenêutica e Ética

## 3.1. As Sete Ambiguidades do Art. 9º

O art. 9º da Portaria nº 2.664/2026 contém pelo menos sete ambiguidades que comprometem sua aplicação coerente e produzem insegurança jurídica, impondo ao pesquisador o dilema de interpretar norma que não oferece critérios objetivos de aplicação.

### 3.1.1. Ambiguidade 1 — "Pesquisa apoiada pelo CNPq"

O caput do art. 9º vincula a obrigação de declaração a "pesquisa apoiada pelo CNPq". A expressão admite ao menos duas interpretações conflitantes.

A interpretação restritiva limita o escopo a pesquisas com repasse financeiro direto do CNPq (auxílios, bolsas de mestrado/doutorado). Esta interpretação exclui parcela significativa da produção científica brasileira, notadamente artigos produzidos por pesquisadores sem bolsa ativa ou em programas sem financiamento direto do CNPq.

A interpretação ampliativa estende o escopo a toda atividade de pesquisador que recebe bolsa Produtividade em Pesquisa (PQ), independentemente de a pesquisa específica ter sido financiada pelo CNPq. Esta interpretação amplia o escopo além da competência legal do CNPq, invadindo seara de periódicos e universidades que possuem suas próprias políticas de integridade.

A divergência interpretativa tem consequências práticas significativas. Um pesquisador PQ que publica artigo sem financiamento direto do CNPq pode razoavelmente concluir que a Portaria não se aplica — e estar equivocado ou correto, dependendo da interpretação adotada pelo órgão fiscalizador no momento da análise. Esta incerteza viola o princípio da segurança jurídica, que exige que o destinatário da norma possa prever as consequências de seus atos.

### 3.1.2. Ambiguidade 2 — "Qualquer espécie" de IAG

A alínea "c" refere-se a "IAG, de qualquer espécie". A expressão captura desde ferramentas assistivas triviais (corretor ortográfico baseado em IA, tradutor automático) até modelos generativos de fronteira (GPT-5, Claude 4, Gemini 2), sem qualquer gradação.

A falta de definição do que constitui "IAG" para fins da Portaria é problemática porque a tecnologia evolui rapidamente. Ferramentas que hoje não são consideradas IAG (como corretores ortográficos baseados em regras) podem incorporar componentes generativos em versões futuras, submetendo-as ao regime da Portaria sem que o pesquisador tenha conhecimento.

A literatura de ciência da computação ainda não chegou a consenso sobre a definição precisa de inteligência artificial generativa (Russell & Norvig, 2021; Russell, 2019). O AI Act europeu (Art. 3(1)) define "sistema de IA" de forma ampla, e a definição de "GPAI" (General Purpose AI) no Art. 51 é objeto de controvérsia doutrinária. A Portaria CNPq, ao utilizar o termo sem definição legal, transfere ao intérprete a tarefa de definir seu conteúdo — tarefa para a qual o aplicador do direito administrativo não está preparado.

### 3.1.3. Ambiguidade 3 — "Qualquer fase"

A alínea "c" exige declaração "em qualquer fase do desenvolvimento da pesquisa (concepção, redação, análise de dados, submissão)". A expressão "qualquer fase" é tão ampla que se torna inoperável.

Se a concepção da ideia de pesquisa já dispara a obrigação de declarar, o pesquisador que utiliza ChatGPT para brainstorm de hipóteses — mesmo que não utilize IA na redação final — deve declarar. A operacionalização desta exigência é inviável: não há como auditar retrospectivamente o processo cognitivo do pesquisador.

Pérez-Neri et al. (2025) propuseram distinção entre usos de IA que "substituem" o julgamento humano e usos que "aumentam" a capacidade do pesquisador. Usos substitutivos (geração integral de texto) levantam preocupações éticas sérias; usos aumentativos (brainstorm, sugestão de direções de pesquisa) são qualitativamente diferentes e não deveriam estar sujeitos ao mesmo regime de declaração. A Portaria colapsa esta distinção ao tratar qualquer uso como potencialmente problemático.

### 3.1.4. Ambiguidade 4 — "Conteúdo gerado por IAG"

A alínea "d" veda a "submissão de conteúdo gerado por IAG como se fosse de autoria humana". Esta é a ambiguidade mais problemática da Portaria.

Se o pesquisador utiliza ChatGPT para sugerir três versões de um parágrafo, edita manualmente as três, funde elementos de cada uma em uma quarta versão e reescreve o resultado final com seu próprio estilo, o texto resultante é "gerado por IAG"? A literatura sobre human-AI co-creation (Lee et al., 2024) demonstra que a distinção entre conteúdo gerado por IA e conteúdo humano é um continuum, não uma dicotomia.

Lee et al. (2024) propõem o conceito de "espectro de cocriação" (co-creation spectrum), que varia de "humano com assistência mínima de IA" a "IA com supervisão humana mínima". A alínea "d" se aplica apenas ao extremo inferior do espectro (IA gerando conteúdo sem intervenção humana substancial), mas a redação da Portaria sugere aplicação a qualquer grau de assistência de IA. A incerteza sobre o ponto exato em que a cocriação se torna "geração" inviabiliza a aplicação consistente da vedação.

### 3.1.5. Ambiguidade 5 — "Finalidade" a especificar

A alínea "c" exige que o pesquisador especifique "a finalidade" do uso de IAG. A Portaria não estabelece o nível de granularidade exigido: basta "revisão textual" ou exige detalhamento por parágrafo ou seção?

Esta ambiguidade cria risco de responsabilização subjetiva: o pesquisador que declara "revisão textual" pode ser considerado insuficientemente específico por um avaliador, enquanto outro pesquisador que declara "uso de ChatGPT para redigir o parágrafo 3 da introdução" pode ser considerado excessivamente detalhado. Sem critérios objetivos, a avaliação da suficiência da declaração depende do arbítrio do agente público.

### 3.1.6. Ambiguidade 6 — "Ferramenta utilizada"

A alínea "c" exige que o pesquisador especifique "a ferramenta utilizada". A ambiguidade reside no que constitui identificação suficiente da ferramenta: o nome do produto (ChatGPT), a versão exata do modelo (GPT-4-turbo vs. GPT-4o), o provedor (OpenAI vs. Microsoft), a data da consulta ou os parâmetros utilizados (temperatura, top-p, presença de system prompt)?

Cada nível de detalhamento tem implicações diferentes para a verificabilidade da declaração e para a exposição do pesquisador. Exigir a versão exata do modelo seria a abordagem mais verificável, mas imporia custo de conformidade desproporcional — o pesquisador médio não mantém registro da versão do modelo utilizado em cada interação com um LLM.

### 3.1.7. Ambiguidade 7 — Vedação a pareceres com IAG

A alínea "e" veda o uso de IAG para elaboração de pareceres científicos. A ambiguidade central é se a vedação se aplica a LLMs locais (open-source) executados sem transmissão de dados a servidores externos.

A ascensão de modelos como Llama 3.1 405B (Meta), DeepSeek-V3 e Mistral Large viabiliza execução local com desempenho comparável a modelos comerciais, em hardware acessível. Um pesquisador que executa Mistral Large localmente em sua GPU e utiliza o modelo para redigir um parecer é indetectável — não há consulta a servidor externo, não há registro de uso, não há watermark. A vedação, portanto, é inócua para usuários técnicos e aplica-se apenas àqueles que utilizam LLMs comerciais (exatamente os usuários que provavelmente declarariam o uso).

## 3.2. O Paradoxo da Transparência

Schilke e Reimann (2025) identificaram o que denominam "dilema da transparência" (transparency dilemma): a declaração de uso de IA reduz a confiança do leitor no trabalho, mesmo quando a IA foi usada de forma ética e assistiva. O estudo, conduzido com 2.847 participantes em seis experimentos controlados, demonstrou que o efeito persiste mesmo quando a IA é usada apenas para formatação ou revisão gramatical.

O mecanismo psicológico subjacente é o que os autores denominam "contágio da máquina" (machine contagion): os leitores inferem que o uso de IA contamina o trabalho, reduzindo sua percepção de autenticidade e originalidade, mesmo quando a contribuição da IA é trivial. O efeito é mediado pela percepção de que o autor "não se esforçou o suficiente" para produzir o trabalho de forma independente.

Este efeito é particularmente perverso no contexto do protocolo CNPq:

1. **Seleção adversa:** O pesquisador que declara uso de IA segundo o art. 9º, alínea "c", expõe-se a escrutínio mais rigoroso, vieses de revisão e potencial desqualificação. O pesquisador que não declara, por outro lado, não corre risco (a detecção é inviável). O resultado é que o protocolo pune a honestidade e recompensa a omissão — exatamente o oposto do que uma política de integridade deveria fazer.

2. **Efeito chilling sobre inovação:** Pesquisadores que utilizam IAG para aumentar a produtividade (ferramentas legítimas como Elicit, Scite, Grammarly) são desincentivados a declarar, por medo de preconceito em avaliações. Isto reduz o incentivo à adoção de ferramentas que poderiam aumentar a eficiência da pesquisa brasileira.

3. **Desigualdade entre pesquisadores:** Pesquisadores em instituições com menos recursos (que não podem pagar por ferramentas de IA pagas e dependem de LLMs gratuitos) são mais propensos a usar ferramentas que geram registros detectáveis, enquanto pesquisadores em instituições ricas podem usar ferramentas de ponta com garantias de privacidade.

## 3.3. O Paradoxo da Reprodutibilidade versus Segredo Industrial

A alínea "d" — vedação de submissão de conteúdo gerado por IAG como autoria humana — colide com a realidade da pesquisa de fronteira mediada por IA. Modelos como AlphaFold (Jumper et al., 2021), GNoME (Merchant et al., 2023) e sistemas de descoberta científica por IA operam sob lógica de caixa-preta protegida por segredo industrial.

Kocak et al. (2025) descrevem este paradoxo com precisão: a reprodutibilidade científica exige transparência total sobre métodos e dados, mas os modelos algorítmicos que viabilizam inovações aceleradas são protegidos como propriedade intelectual. A comunidade pode validar resultados finais, não o processo cognitivo da máquina. A Portaria, ao tratar a transparência como sempre possível, ignora o conflito estrutural entre propriedade corporativa e escrutínio acadêmico.

Meszaros, Huys e Ioannidis (2026) demonstram que este problema é global: a distinção entre "pesquisa" e "atividade comercial" no AI Act europeu é igualmente problemática, e as isenções de pesquisa "baseiam-se em distinções que podem não capturar plenamente as realidades da pesquisa contemporânea em IA" (Meszaros, Huys & Ioannidis, 2026, p. 3).

O paradoxo é agravado pelo fato de que a pesquisa brasileira utiliza crescentemente ferramentas de IA desenvolvidas por empresas estrangeiras (OpenAI, Google, Meta, DeepSeek, Mistral). A alínea "d" exigiria transparência sobre o uso destas ferramentas, mas os provedores não oferecem transparência sobre o funcionamento interno de seus modelos. O pesquisador fica preso entre a exigência de declarar (para cumprir a Portaria) e a impossibilidade de descrever precisamente como a IA contribuiu (porque o funcionamento do modelo é caixa-preta).

# 4. Dimensão Jurídico-Brasileira: Colisões Normativas

## 4.1. LGPD versus Alínea "c"

A alínea "c" do art. 9º exige que o pesquisador especifique "a ferramenta utilizada e a finalidade" do uso de IAG. Se a ferramenta for um LLM comercial (ChatGPT, Claude, Gemini), o pesquisador pode estar — sem saber — violando a Lei Geral de Proteção de Dados Pessoais (LGPD, Lei nº 13.709/2018) ao submeter dados de pesquisa a servidores no exterior, especialmente se os dados envolverem informações pessoais de sujeitos de pesquisa.

### 4.1.1. Consentimento e Finalidade

A LGPD exige consentimento específico e finalidade determinada para tratamento de dados pessoais (art. 7º, I c/c art. 11, I). O consentimento obtido do participante de pesquisa para tratamento de seus dados não abrange, em regra, a submissão destes dados a LLMs comerciais para processamento ou treinamento.

A submissão de dados a LLMs comerciais pode configurar violação porque:
- A finalidade do tratamento (pesquisa científica) é diversa da finalidade para a qual o LLM utiliza os dados (treinamento do modelo, melhoria do serviço).
- O consentimento obtido não informou o participante sobre a possibilidade de seus dados serem processados por IA comercial.
- Não há base legal alternativa que autorize o compartilhamento com terceiros não especificados no termo de consentimento.

### 4.1.2. Transferência Internacional de Dados

A submissão de dados a LLMs sediados no exterior (OpenAI nos EUA, DeepSeek na China) configura transferência internacional de dados, sujeita aos arts. 33 a 36 da LGPD. O pesquisador que utiliza ChatGPT para processar dados de pesquisa sem verificar se o provedor oferece garantias adequadas (cláusulas contratuais padrão, decisão de adequação) pode estar violando a LGPD.

A ANPD (Autoridade Nacional de Proteção de Dados) ainda não se manifestou especificamente sobre o uso de LLMs na pesquisa científica, criando zona de incerteza regulatória. O pesquisador fica diante de um conflito normativo: cumprir o CNPq (declarar detalhadamente a ferramenta, potencialmente expondo dados) ou cumprir a LGPD (não expor dados a terceiros não autorizados pelo consentimento).

### 4.1.3. Jurisprudência do STF

A decisão do Supremo Tribunal Federal no RE 1.057.258 (Tema 987) reforça a autodeterminação informativa como direito fundamental decorrente do art. 5º, X e XII, da Constituição Federal. O STF reconheceu que o tratamento de dados pessoais deve observar "o consentimento livre, informado e inequívoco do titular" e que "a proteção de dados pessoais é direito fundamental autônomo".

A Portaria CNPq, ao impor a declaração detalhada de uso de IA sem oferecer orientação sobre proteção de dados, cria risco de violação deste direito fundamental. O pesquisador que cumpre a Portaria pode estar violando a LGPD e o direito fundamental à proteção de dados.

## 4.2. Art. 218 da Constituição Federal

O art. 218 da Constituição Federal determina que "o Estado promoverá e incentivará o desenvolvimento científico, a pesquisa, a capacitação científica e tecnológica e a inovação". A Portaria CNPq nº 2.664/2026 impõe obrigações declaratórias e vedações sem contrapartida de incentivo.

Bucci (2021) sustenta que a regulação estatal da pesquisa deve observar a proporcionalidade entre meios restritivos e fins promocionais. Uma norma que cria custo burocrático sem benefício demonstrável de integridade é desproporcional na modalidade "proibição de excesso". O descompasso entre regulação e fomento pode ser questionado à luz do princípio constitucional.

### 4.2.1. Proporcionalidade e Proibição de Excesso

O princípio da proporcionalidade, conforme desenvolvido pela doutrina e jurisprudência brasileiras (Ávila, 2022; STF, RE 875.959, Tema 799), exige que a medida restritiva seja adequada, necessária e proporcional em sentido estrito.

**Adequação:** A declaração obrigatória de uso de IAG é adequada para promover a integridade científica? As evidências empíricas sugerem que não. Se a detecção é inviável (Capítulo 2) e a declaração produz seleção adversa (Seção 3.2), a medida não atinge seu objetivo declarado.

**Necessidade:** Existem medidas menos restritivas que alcançariam o mesmo objetivo? Sim. Marcação técnica pelos provedores (como exigido pelo AI Act europeu e pelo GB 45438-2025 chinês) imporia menor custo ao pesquisador e maior capacidade de enforcement.

**Proporcionalidade em sentido estrito:** O benefício esperado da Portaria justifica o custo imposto? O custo de conformidade (horas de trabalho para declarar detalhadamente) somado ao custo de oportunidade (tempo desviado da pesquisa para cumprimento burocrático) é significativo. O benefício, na ausência de evidências de que a declaração efetivamente coíbe o uso abusivo de IAG, é duvidoso.

## 4.3. Ausência de Sanção Específica e Legalidade Estrita

A Portaria CNPq nº 2.664/2026 não estabelece sanções para o descumprimento do art. 9º. Esta lacuna viola o princípio da legalidade estrita (art. 5º, II, CF) e a tipicidade no direito administrativo sancionador.

### 4.3.1. O Princípio da Legalidade no Direito Administrativo Sancionador

O direito administrativo brasileiro exige que a sanção esteja prevista em lei ou ato normativo equivalente (art. 5º, XXXIX, CF c/c art. 1º do Decreto-Lei nº 4.657/1942). Justen Filho (2024) esclarece que não há sanção sem prévia cominação legal (nulla poena sine lege).

A Portaria CNPq é ato administrativo normativo, não lei em sentido formal. Mesmo que se admita poder disciplinar da autarquia (art. 37, §6º, CF), a ausência de especificação do que constitui infração e qual a penalidade viola o devido processo legal substantivo.

Quatro problemas decorrem da ausência de sanção:

1. **Inaplicabilidade imediata:** Sem sanção, a Portaria é lex imperfecta. O descumprimento do art. 9º não produz consequência jurídica imediata.

2. **Insegurança jurídica:** A ausência de tipificação permite que sanções sejam aplicadas por analogia ou interpretação extensiva, vedadas no direito administrativo sancionador.

3. **Desigualdade de tratamento:** Diferentes avaliadores podem aplicar diferentes consequências para a mesma conduta, violando o art. 5º, caput, da CF.

4. **Violação do contraditório:** Sem descrição clara da infração, o pesquisador não pode exercer seu direito de defesa de forma adequada.

### 4.3.2. Consequências Práticas

A ausência de sanção significa que, na prática, o cumprimento da Portaria depende de adesão voluntária. A experiência internacional (Liang et al., 2025) demonstra que a adesão voluntária a políticas de declaração de IA é extremamente baixa (0,1%). Sem enforcement crível, a Portaria não altera o comportamento dos pesquisadores — não protege a integridade, apenas a burocratiza.

## 4.4. O Sistema Qualis-CAPES como Antecedente Estrutural

A Portaria nº 2.664/2026 não surge em vácuo. Ela se insere em tradição de avaliação quantitativa e burocrática que sistematicamente privilegia métricas internacionais em detrimento da pesquisa nacional. Compreender este antecedente é essencial para avaliar criticamente a abordagem regulatória adotada.

Caballero Rivero, Santos e Trzesniak (2024) demonstraram que os sistemas de avaliação CAPES/CNPq induzem padrões de publicação que priorizam periódicos estrangeiros de alto impacto em detrimento da relevância local. O estudo analisou a produção de 5.847 pesquisadores das ciências da saúde no Brasil, constatando que a ênfase em métricas quantitativas (fator de impacto, número de publicações) produz "efeitos perversos sobre a qualidade e a relevância social da produção científica" (Caballero Rivero, Santos & Trzesniak, 2024, p. 22).

O efeito performativo da avaliação é bem descrito por Albuquerque (2025): "o simples fato de existirem critérios externos faz com que os programas de pós-graduação se reorganizem para atendê-los". Sguissardi (2006) denominou este fenômeno de "avaliação defensiva" — a tendência de instituições e pesquisadores a moldar sua produção para atender indicadores, independentemente da relevância substantiva do trabalho.

Perez (2025) atualizou a crítica para o contexto do Qualis 2025-2028, argumentando que os novos critérios "tendem a aprofundar desigualdades regionais, institucionais e de gênero". A autora demonstra que a padronização de critérios de excelência em escala nacional penaliza instituições com menos recursos e pesquisadores em áreas de conhecimento com tradições epistemológicas diversas.

A Portaria nº 2.664/2026 herda esta tradição de regulação por declaração. Assim como o Qualis exige declarações detalhadas sobre a produção científica, o art. 9º exige declarações detalhadas sobre o uso de IAG. Em ambos os casos, o custo de conformidade recai inteiramente sobre o pesquisador, e a verificação é delegada a mecanismos administrativos de duvidosa eficácia. A diferença é que, no caso da IAG, a impossibilidade técnica de verificação torna a declaração não apenas custosa, mas inverificável.

# 5. Regulação Comparada: Cinco Modelos Regulatórios

A comparação internacional revela que cada país abordou o desafio de forma diversa, e que a opção brasileira — autodeclaração sem verificação técnica — é a de menor densidade normativa e menor capacidade de enforcement entre as jurisdições analisadas.

## 5.1. China: Regulação Centralizada com Padrão Obrigatório

A China adotou o modelo mais abrangente e tecnicamente sofisticado. O Ministério da Ciência e Tecnologia (MOST) publicou em dezembro de 2023 as "Diretrizes para Conduta Responsável em Pesquisa", que proíbem o uso de IAG para gerar materiais de submissão, exigem rotulagem clara de conteúdo gerado por IA e vedam a IA como co-autora (China, 2023).

O marco mais significativo é o padrão nacional obrigatório **GB 45438-2025** ("Cybersecurity Technology: Labeling Method for Content Generated by Artificial Intelligence"), promulgado conjuntamente pelo Cyberspace Administration of China (CAC), Ministério da Indústria e Tecnologia da Informação (MIIT), Ministério da Segurança Pública (MPS) e Administração Nacional de Rádio e Televisão (NRTA), vigente desde 1º de setembro de 2025. O padrão exige:

- **Marcação explícita:** Rótulos visíveis ao usuário indicando que o conteúdo foi gerado por IA.
- **Marcação implícita:** Metadados e watermarks digitais inseridos no conteúdo, detectáveis por máquina.
- **Registro de algoritmos:** Provedores de IA devem registrar seus algoritmos junto ao CAC, permitindo rastreabilidade.
- **Responsabilidade do provedor:** Obrigação de implementar mecanismos de marcação na fonte, não sobre o usuário.

As **Interim Measures on Generative AI Services** complementam o GB 45438-2025, estabelecendo regime de registro e filing de algoritmos de IA. Provedores de serviços de IA generativa devem:
1. Submeter seus algoritmos à avaliação de segurança do CAC.
2. Implementar mecanismos de marcação de conteúdo conforme o padrão nacional.
3. Manter registros de conteúdo gerado por pelo menos seis meses.
4. Reportar incidentes de segurança ao CAC em até 24 horas.

O modelo chinês é o que mais se aproxima de um enforcement factível, por três razões: (a) o padrão técnico obrigatório é aplicado na fonte pelos provedores de IA chineses, não pelos usuários; (b) a fiscalização é exercida pelo CAC com poder de sanção administrativa (multas, suspensão de operações); (c) o regime exige registro e filing de algoritmos de IA, permitindo auditoria retrospectiva.

Limitações do modelo chinês incluem: (a) dependência de provedores nacionais — LLMs estrangeiros não são acessíveis na China continental (Great Firewall), criando ecossistema controlado que não existe no Brasil; (b) alto custo de conformidade para provedores, que pode ser repassado aos usuários; (c) potencial para censura e controle político disfarçado de regulação de IA, como observa Beladiya (2026).

Para o Brasil, o modelo chinês oferece lições importantes sobre a viabilidade técnica da marcação obrigatória na fonte, mas sua dependência de controle centralizado sobre provedores e infraestrutura de internet o torna de replicação limitada em contexto democrático e aberto.

## 5.2. União Europeia: Abordagem Baseada em Risco com Enforcement Escalonado

O EU AI Act (Regulation 2024/1689) é o primeiro marco regulatório abrangente de IA no mundo e entrou em vigor em 1º de agosto de 2024, com implementação escalonada até 2027. Para a pesquisa acadêmica, seus dispositivos mais relevantes são:

- **Art. 2(6) e (8):** Estabelece isenções para pesquisa (research exemption), excluindo da aplicação do Regulamento "sistemas de IA especificamente desenvolvidos e colocados em serviço para o único propósito de pesquisa e desenvolvimento científico".
- **Art. 50:** Impõe obrigações de transparência aplicáveis a todos os sistemas de IA, incluindo a marcação de conteúdo sintético.
- **Art. 51-56:** Estabelece regras para modelos de IA de propósito geral (GPAI), incluindo obrigações de transparência e documentação técnica.

A distinção crítica do modelo europeu é que não impõe declaração pelo autor, mas sim **marcação técnica pelo provedor**. O LLM comercial é obrigado por lei (Art. 50(2)) a marcar seu output de forma legível por máquina e detectável como gerado artificialmente. A obrigação de transparência recai sobre quem disponibiliza o sistema, não sobre quem o usa.

**Art. 50(2) do AI Act:**
> "Providers of general-purpose AI models that generate synthetic audio, image, video or text content shall ensure that the output is marked in a machine-readable format and detectable as artificially generated or manipulated."

Isto contrasta fundamentalmente com o modelo brasileiro, que impõe a obrigação exclusivamente sobre o pesquisador-usuário — sem exigência correspondente sobre os provedores. A assimetria é evidente: o Brasil regula quem não tem como verificar a própria declaração.

O AI Act estabelece ainda o **European Artificial Intelligence Board** (Art. 56-61) como autoridade coordenadora, e prevê sanções de até 7% do faturamento anual global para violações das obrigações de transparência (Art. 99).

Meszaros, Huys e Ioannidis (2026) identificaram fragilidades nas isenções de pesquisa do AI Act: a distinção entre pesquisa acadêmica e atividade comercial é turva, e o desenvolvimento em ambiente controlado versus teste em ambiente real é difícil de determinar. Os autores argumentam que as isenções "baseiam-se em distinções que podem não capturar plenamente as realidades da pesquisa contemporânea em IA" (Meszaros, Huys & Ioannidis, 2026, p. 6).

Veale e Borgesius (2024) criticam a complexidade do AI Act, argumentando que suas múltiplas camadas de obrigações (por nível de risco, por tipo de modelo, por papel do agente) criam incerteza regulatória que prejudica a inovação. Para o contexto brasileiro, o AI Act oferece o modelo mais relevante de regulação híbrida que combina obrigações sobre provedores com gradação de exigências.

## 5.3. Estados Unidos: Segurança de Pesquisa em vez de Regulação de IA

Os Estados Unidos não possuem regulação federal específica sobre uso de IA na pesquisa acadêmica. A abordagem é indireta, centrada em segurança de pesquisa (research security) e combate à influência estrangeira, com ênfase em transparência de financiamento e conflitos de interesse.

A **NSF Scientific Integrity Policy** (NSF 24-007, fevereiro de 2024) reafirma compromisso com integridade mas não menciona IA especificamente. A política estabelece expectativas gerais para conduta responsável em pesquisa, delegando a definição de normas específicas sobre IA às instituições financiadas.

O **NSPM-33** (National Security Presidential Memorandum 33) e o **TRUST Framework** (Trusted Research Using Safeguards and Transparency) focam em disclosure de apoio estrangeiro e conflitos de compromisso (NSF, 2024). Nenhum dos instrumentos trata de uso de IA, e a análise de riscos à segurança nacional não inclui dimensão relacionada à IAG.

O **Executive Order 14110** (outubro de 2023), "Safe, Secure, and Trustworthy Development and Use of Artificial Intelligence", estabelece princípios gerais para o desenvolvimento de IA nos EUA, mas não aborda especificamente o uso de IA na pesquisa acadêmica. O EO determina que o NSF desenvolva programa de pesquisa em integridade de conteúdo (Seção 4.4) e que o Departamento de Comércio estabeleça padrões de watermarking (Seção 4.5), mas estas iniciativas estavam em fase inicial em 2026.

O modelo americano é o mais liberal entre os analisados: não exige declaração de IA, não estabelece padrão de marcação, não cria obrigação para provedores. A integridade é delegada às instituições e periódicos, que têm políticas próprias. Esta abordagem minimiza custos burocráticos mas transfere o problema para o self-governance de cada entidade, produzindo fragmentação normativa.

Para o Brasil, o modelo americano ilustra os riscos da não-regulação, mas também oferece contraponto útil: a ausência de regulação federal não produziu colapso da integridade científica nos EUA, sugerindo que a urgência da regulação pode ser menor do que a Portaria CNPq pressupõe.

## 5.4. Reino Unido: Abordagem Proporcional e Baseada em Princípios

O Reino Unido adotou abordagem distinta, centrada em princípios de proporcionalidade e autorregulação. O **UK AI Regulation White Paper** (março de 2024) estabelece cinco princípios transversais: segurança, transparência, equidade, accountability e contestabilidade. Para a pesquisa acadêmica, o **Research Integrity Policy** do UK Research and Innovation (UKRI) orienta que instituições desenvolvam políticas próprias sobre uso de IA, adaptadas a seu contexto disciplinar.

A **Russell Group** (universidades de elite do Reino Unido) publicou em 2024 princípios para uso de IA generativa na educação e pesquisa, enfatizando que a IA deve ser usada de forma "responsável e ética", mas sem impor obrigações declaratórias uniformes. Cada universidade desenvolve sua própria política, resultando em diversidade de abordagens.

O modelo britânico caracteriza-se por:
- Ausência de obrigação legal de declaração.
- Ênfase em princípios em vez de regras detalhadas.
- Delegação a instituições para desenvolvimento de políticas específicas.
- Foco em educação e conscientização, não em fiscalização.

Para o Brasil, o modelo britânico oferece alternativa regulatória baseada em princípios, que poderia ser adaptada ao contexto brasileiro com menor custo burocrático.

## 5.5. Canadá: Regulação Legislativa em Tramitação

O Canadá encontra-se em posição intermediária. A **C-27 Artificial Intelligence and Data Act** (em tramitação no Parlamento canadense em 2026) estabeleceria regime regulatório para IA de "alto impacto", com obrigações de transparência e avaliação de risco. Para a pesquisa acadêmica, o **Tri-Agency Research Integrity Policy** (CIHR, NSERC, SSHRC) orienta que instituições desenvolvam políticas sobre uso de IA.

O Canadá caracteriza-se por:
- Regulação legislativa em desenvolvimento.
- Abordagem baseada em risco similar ao AI Act europeu.
- Coordenação entre agências de fomento para política unificada.
- Ênfase em conscientização e treinamento.

## 5.6. Tabela Comparativa Multidimensional

| Dimensão | Brasil (CNPq 2.664/2026) | China | União Europeia | EUA (NSF) | Reino Unido | Canadá |
|---|---|---|---|---|---|---|
| **Base legal** | Portaria administrativa | Lei + Padrão Nacional | Regulamento (diretamente aplicável) | Política interna NSF | White Paper (princípios) | Projeto de lei (C-27) |
| **Obrigação principal** | Autodeclaração do pesquisador | Marcação pelo provedor + declaração | Marcação técnica pelo provedor (Art. 50) | Nenhuma específica | Princípios sem obrigação | Em definição |
| **Padrão técnico** | Nenhum | GB 45438-2025 (obrigatório) | Code of Practice (em desenvolvimento) | Nenhum | Nenhum | Em definição |
| **Enforcement** | Inexistente (sem sanção) | CAC com sanções administrativas | Comissão + autoridades nacionais | Research security (não IA) | Autorregulação | Em definição |
| **Escopo** | Pesquisa apoiada pelo CNPq | Toda pesquisa na China | Sistemas de IA no mercado UE | Pesquisas financiadas NSF | Toda pesquisa UKRI | Pesquisa financiada federalmente |
| **Custo de conformidade** | Alto (declaração detalhada) | Médio (rotulagem + verificação) | Baixo (marcação é do provedor) | Zero | Mínimo | Em definição |
| **Viabilidade técnica** | Baixa (detecção inviável) | Alta (controle centralizado) | Média (depende do Code of Practice) | N/A | N/A | Em definição |
| **Abordagem de risco** | Ausente (trata todo uso como igual) | Uniforme (padrão único) | Escalonada (4 níveis de risco) | Ausente | Proporcional | Baseada em risco |
| **Sanção** | Não especificada | Multas + suspensão | 7% do faturamento global | Perda de funding | Variável por instituição | Em definição |

## 5.7. Síntese Comparativa

Cada modelo reflete escolhas políticas e históricas distintas. O Brasil optou pelo modelo de **autodeclaração com custo concentrado no pesquisador** — a pior combinação possível: alto custo de conformidade para quem cumpre, zero custo para quem descumpre, e impossibilidade técnica de verificação.

A China optou pelo modelo de **padrão técnico obrigatório na fonte** — mais eficaz, mas dependente de controle centralizado sobre provedores de IA e compatível com regime de vigilância digital.

A UE optou pelo modelo de **regulação híbrida**, impondo obrigações sobre provedores (marcação) e sobre usuários (transparência em certos usos), com abordagem baseada em risco.

Os EUA optaram pelo modelo de **não-regulação específica**, tratando IA como ferramenta de pesquisa e focando segurança em vez de integridade textual.

O Reino Unido optou pelo modelo de **princípios proporcionais**, delegando a implementação a instituições.

O Canadá encontra-se em posição de **transição regulatória**, com legislação em tramitação e políticas de agências de fomento em desenvolvimento.

A Portaria CNPq nº 2.664/2026, neste cenário, é o único instrumento que impõe **obrigação sem oferecer meio de cumprimento**. É regulação sem tecnologia.

# 6. A Portaria no Contexto da Quarta Revolução Industrial

## 6.1. O Conceito de Quarta Revolução Industrial

Schwab (2016) define a Quarta Revolução Industrial como "a fusão de tecnologias que está borrando as linhas entre as esferas física, digital e biológica". Diferentemente das revoluções anteriores (mecanização no século XVIII, eletricidade e produção em massa no século XIX, eletrônica e automação no século XX), a QRI caracteriza-se pela velocidade exponencial da mudança, pela amplitude do impacto (atinge todos os setores e países) e pela transformação de sistemas inteiros (não apenas processos específicos).

Para a pesquisa científica, a QRI tem implicações profundas. A inteligência artificial não é apenas uma ferramenta adicional no arsenal do pesquisador — é uma tecnologia de propósito geral (general-purpose technology) que transforma a própria natureza da produção de conhecimento (Bresnahan & Trajtenberg, 1995). LLMs alteram a relação entre o pesquisador e o texto, entre a hipótese e a análise, entre o dado e a interpretação.

## 6.2. Assimetria Competitiva no Mercado Global de P&D

A Portaria CNPq nº 2.664/2026 cria assimetria competitiva para pesquisadores brasileiros no mercado global de P&D. Enquanto pesquisadores nos EUA, Reino Unido e UE podem utilizar IAG sem restrições significativas (sujeitos apenas a políticas institucionais leves), pesquisadores brasileiros sujeitos ao CNPq enfrentam custos de conformidade e riscos de responsabilização.

Esta assimetria pode produzir três efeitos negativos:

1. **Desvantagem competitiva:** Pesquisadores brasileiros que declaram uso de IA são desfavorecidos em revisões por pares internacionais (paradoxo da transparência, Seção 3.2), enquanto concorrentes estrangeiros não sujeitos a declaração não enfrentam este ônus.

2. **Fuga de talentos:** Pesquisadores brasileiros com alta produtividade — que mais se beneficiariam de ferramentas de IA — são os mais propensos a buscar posições em instituições estrangeiras com regulação mais permissiva, agravando a fuga de cérebros.

3. **Burocratização seletiva:** A Portaria afeta desproporcionalmente pesquisadores em início de carreira, que têm menos recursos para dedicar ao cumprimento burocrático e mais necessidade de produtividade para estabelecer suas carreiras.

Perez (2025) já demonstrou que sistemas de avaliação científica podem aprofundar desigualdades. A Portaria nº 2.664/2026 segue esta tradição, adicionando camada de custo regulatório que afeta desproporcionalmente os pesquisadores mais vulneráveis do sistema.

## 6.3. Custo Regulatório e Análise Econômica

Uma análise econômica preliminar dos custos da Portaria revela dimensão significativa. Estimando-se que o sistema CNPq envolva aproximadamente 100.000 pesquisadores ativos (bolsistas PQ, mestrandos, doutorandos), e que cada pesquisador gaste em média 2 horas por ano para cumprir as obrigações declaratórias do art. 9º, o custo agregado de conformidade seria de aproximadamente 200.000 horas de trabalho científico por ano.

Valorando-se a hora de pesquisa ao custo médio de bolsas e salários (aproximadamente R$ 50/hora para bolsistas e R$ 150/hora para pesquisadores titulares), o custo total de conformidade situa-se entre R$ 10 milhões e R$ 30 milhões anuais — valor significativo para um sistema de fomento com orçamento limitado.

Este custo, para ser justificado, deveria ser compensado por benefício demonstrável em integridade científica. Contudo, a ausência de evidências de que a declaração obrigatória reduza o uso abusivo de IAG — e as evidências em contrário (Liang et al., 2025: taxa de declaração de 0,1%) — sugere que o custo não é compensado por benefício.

Ayres e Braithwaite (1992) propõem o modelo de "regulação responsiva", segundo o qual a intensidade da intervenção regulatória deve ser proporcional ao risco e à capacidade de enforcement. A Portaria CNPq viola este princípio ao impor obrigação máxima (declaração detalhada universal) com capacidade mínima de verificação (detectores inviáveis). Uma abordagem responsiva começaria com medidas leves (educação, diretrizes) e escalaria apenas quando necessário.

# 7. Estudos de Caso: Conformidade na Prática

## 7.1. Caso 1: O Pesquisador que Usa Grammarly

Maria é pesquisadora PQ-2 na área de linguística. Utiliza Grammarly para correção ortográfica e gramatical de seus artigos em inglês. Grammarly, desde 2024, incorpora recursos generativos de IA para sugestões de reescrita. Maria não sabe se o uso de Grammarly constitui "IAG de qualquer espécie" para fins do art. 9º.

**Dilema de Maria:**
- Se declarar: expõe-se ao paradoxo da transparência (Seção 3.2) — avaliadores podem questionar se seu trabalho é autêntico.
- Se não declarar: arrisca responsabilização se um avaliador considerar que Grammarly é IAG.
- Se consultar o CNPq: não há orientação específica sobre ferramentas assistivas como Grammarly.

**Análise:** A ambiguidade da expressão "qualquer espécie" (Seção 3.1.2) coloca Maria em situação de insegurança jurídica. A aplicação razoável da norma sugeriria que ferramentas assistivas linguísticas estão excluídas do escopo, mas a letra da Portaria admite interpretação contrária.

## 7.2. Caso 2: O Pesquisador que Usa ChatGPT para Análise de Dados

João é doutorando em saúde pública. Utiliza ChatGPT para escrever scripts de análise estatística em R e Python, mas não para redigir o texto do artigo. O ChatGPT gera código que João revisa e adapta.

**Dilema de João:**
- A alínea "c" exige declaração "em qualquer fase", incluindo "análise de dados".
- João usou IAG para análise de dados (geração de scripts), mas não para redação.
- A geração de código por IAG não é coberta pela literatura sobre detectores de texto, e não existem detectores validados para código gerado por IA.

**Análise:** O caso de João ilustra a extensão excessiva da Portaria. A geração de código para análise de dados é uso instrumental de IA que não afeta a integridade do conteúdo intelectual do artigo. Exigir declaração neste caso impõe custo sem benefício.

## 7.3. Caso 3: O Pesquisador que Usa IA Open-Source Local

Ana é pesquisadora em ciência da computação. Executa o modelo DeepSeek-V3 localmente em sua estação de trabalho, utilizando o modelo para auxiliar na redação de artigos e revisão de literatura. Como o modelo roda localmente, não há registro externo de uso.

**Dilema de Ana:**
- O uso de IA local é indetectável.
- Ana opta por não declarar, confiando na indetectabilidade.
- Se a política mudar e métodos de detecção forem desenvolvidos para uso local, Ana estará exposta a responsabilização retrospectiva.

**Análise:** O caso de Ana demonstra a ineficácia seletiva da Portaria. Pesquisadores com conhecimento técnico podem usar IA local impunemente; pesquisadores sem conhecimento técnico, que usam LLMs comerciais, são os únicos expostos ao enforcement.

## 7.4. Caso 4: O Parecerista que Usa IA sem Saber

Carlos é professor associado e revisa artigos para periódico Qualis A1. Em parecer particularmente complexo, utiliza o ScholarOne com sugestões de texto baseadas em IA integradas pelo sistema do periódico. Carlos não foi informado de que o sistema utiliza IAG para sugerir formatação de parecer.

**Dilema de Carlos:**
- A alínea "e" veda uso de IAG para pareceres.
- Carlos não usou IAG voluntariamente, mas o sistema do periódico pode ter usado.
- Carlos não tem como saber se a alínea "e" se aplica a sugestões automatizadas de formatação.

**Análise:** O caso de Carlos revela que a alínea "e" é de impossível cumprimento quando ferramentas institucionais incorporam IA sem transparência para o usuário. A vedação responsabiliza o pesquisador por uso que ele pode não saber que está ocorrendo.

# 8. Conclusão: Balanço Crítico e Propostas

## 8.1. Acertos da Portaria

Não obstante as críticas desenvolvidas ao longo desta dissertação, a Portaria apresenta méritos que devem ser reconhecidos:

1. **Reconhecimento institucional:** A Portaria tira a IAG da invisibilidade normativa e a reconhece como fenômeno relevante na pesquisa. Mérito não trivial em um cenário de rápida transformação tecnológica.

2. **Opção pela não proibição:** Diferentemente de posições reacionárias que propugnam pela vedação total do uso de IA, a Portaria busca regular o uso responsável, alinhando-se à tendência internacional de regulação em vez de proibição.

3. **Atualização do debate:** A Portaria acelera a discussão sobre integridade em universidades e periódicos brasileiros, forçando a comunidade acadêmica a enfrentar o tema.

4. **Alinhamento internacional:** Ainda que imperfeita, a Portaria se insere em movimento global de regulação da IA na ciência, acompanhando iniciativas de China, UE e Reino Unido.

## 8.2. Fragilidades Identificadas

As fragilidades identificadas ao longo dos Capítulos 2 a 7 são, contudo, substantivas e estruturais:

1. **Inaplicabilidade técnica:** A premissa central da fiscalização — que o uso não declarado de IAG pode ser detectado — é falseada por cinco anos de evidências empíricas convergentes (Weber-Wulff et al., 2023; Liu et al., 2024; Pudasaini et al., 2025; Liang et al., 2025; Chaka, 2024a, 2024b).

2. **Proporção uso/declaração:** O dado de 40:1 (Liang et al., 2025) — quarenta vezes mais artigos usando IA do que declarando — é a evidência mais contundente contra a eficácia do protocolo.

3. **Custo burocrático sem contrapartida:** O custo imposto ao pesquisador (estimado entre R$ 10 e R$ 30 milhões anuais) não encontra contrapartida em ganho demonstrável de integridade científica.

4. **Seleção adversa:** O protocolo pune quem declara e não quem omite, produzindo incentivos perversos.

5. **Sete ambiguidades:** As ambiguidades do art. 9º geram insegurança jurídica que inviabiliza aplicação coerente.

6. **Colisões normativas:** A Portaria colide com a LGPD (exposição de dados), a Constituição Federal (proporcionalidade) e a LINDB (legalidade estrita).

7. **Ineficácia seletiva:** A vedação a pareceres com IAG (alínea "e") é facilmente contornada por modelos locais e afeta apenas usuários de LLMs comerciais.

8. **Assimetria comparada:** O Brasil é a única jurisdição entre as analisadas que não exige marcação técnica pelos provedores.

## 8.3. Propostas de Aperfeiçoamento

Com base na análise desenvolvida, propõe-se o seguinte modelo regulatório híbrido, organizado em seis eixos:

### 8.3.1. Marcação Técnica pelos Provedores

O CNPq deveria negociar com provedores de IA (OpenAI, Google, Meta, DeepSeek, Mistral, Anthropic) a implementação de marcação automática de conteúdo gerado em português, nos moldes do Art. 50(2) do AI Act europeu. A marcação deveria ser:
- **Implícita** (metadados, watermarks digitais detectáveis por máquina) para permitir verificação automatizada.
- **Explícita** (indicador visual para o usuário) para conscientização.
- **Padronizada** (formato comum) para interoperabilidade entre ferramentas de verificação.

### 8.3.2. Graduação de Exigências por Nível de Risco

Substituição da obrigação única e indiferenciada por modelo escalonado de quatro níveis:

| Nível | Descrição | Exigência | Verificação |
|---|---|---|---|
| 1 | Assistência linguística (Grammarly, LanguageTool) | Nenhuma | N/A |
| 2 | Sumarização e tradução (DeepL, Elicit) | Declaração simplificada no artigo | Autodeclaração |
| 3 | Geração substantiva de seções | Declaração detalhada + checklist | Amostragem + verificação por pares |
| 4 | Geração integral | Proibido (como autoria) | Detecção por revisores + ferramentas |

### 8.3.3. Declaração Simplificada e Padronizada

Substituição da declaração detalhada sem parâmetros por **checklist padronizado de uma página**, inspirado nos templates adotados por periódicos de alto impacto (Nature, Science, PLOS ONE). O checklist deve incluir:
- Identificação da(s) ferramenta(s) utilizada(s).
- Nível de uso (taxonomia de 4 níveis).
- Seções do artigo em que a IA foi utilizada.
- Declaração de que o autor revisou e assume responsabilidade pelo conteúdo.

### 8.3.4. Sanções Claras e Proporcionais

Estabelecimento de sanções específicas no texto da Portaria ou em ato normativo complementar:
- **Nível 1 (omissão culposa):** Advertência, correção da declaração, prazo para regularização.
- **Nível 2 (omissão dolosa sem dolo de fraude):** Suspensão temporária de benefícios (3-12 meses).
- **Nível 3 (fraude dolosa):** Suspensão de benefícios (12-36 meses), comunicação à instituição.
- **Nível 4 (reincidência ou fraude grave):** Desligamento do sistema CNPq, comunicação à CAPES e ao Ministério Público Federal.

### 8.3.5. Harmonização com a LGPD e o Art. 218 da CF

Inclusão na Portaria (ou em ato complementar) de:
- Orientação expressa sobre proteção de dados no uso de LLMs: recomendação de utilizar LLMs com garantias contratuais de não utilização dos dados para treinamento.
- Cláusula de não responsabilização do pesquisador que, cumprindo a Portaria, expuser dados por meio de ferramenta de IA — desde que tenha tomado precauções razoáveis.
- Declaração de que a Portaria não se aplica a usos aumentativos de IA que não substituem o julgamento humano substantivo.

### 8.3.6. Governança e Atualização Periódica

Criação de comitê técnico-científico permanente no CNPq para:
- Monitorar a evolução da tecnologia de detecção e watermarking.
- Propor atualizações periódicas da Portaria (revisão bienal).
- Publicar relatório anual de conformidade com dados anonimizados sobre declarações de uso de IA.

## 8.4. Considerações Finais

Esta dissertação demonstrou que a Portaria CNPq nº 2.664/2026, não obstante suas boas intenções, opera como instrumento de retardamento burocrático da pesquisa científica brasileira. As evidências são convergentes: detectores falham, a proporção uso/declaração é de 40:1, o texto contém ambiguidades insanáveis, a fiscalização é inviável, e o modelo brasileiro é o que oferece menor capacidade de enforcement entre as principais jurisdições analisadas.

O paradoxo central é que a Portaria tenta resolver um problema técnico — a detecção de uso de IAG — com instrumento jurídico — a declaração obrigatória. Este descompasso entre a natureza do problema e o meio de solução condena o protocolo à ineficácia. O pesquisador que declarar o uso de IA será escrutinado; o que não declarar, não. O inovador honesto paga o custo burocrático; o mal-intencionado paga zero. A Portaria não protege a integridade: apenas a burocratiza.

A saída não é abandonar a integridade, mas redefini-la em termos compatíveis com o estado da arte tecnológico. Marcação técnica pelos provedores, gradação de exigências por nível de risco e fiscalização baseada em amostragem com verificação substantiva por pares são mais eficazes que declarações inverificáveis. A avaliação substantiva baseada em impacto replicável e relevância social sempre será mais eficaz que declarações formais sem possibilidade de verificação.

Enquanto o CNPq não enfrentar o problema real — a inviabilidade técnica da detecção e a necessidade de responsabilizar provedores em vez de apenas pesquisadores —, a ciência brasileira continuará pagando o preço de um protocolo que não protege, mas apenas retarda.

---

# Apêndice A — Texto Integral do Art. 9º da Portaria CNPq nº 2.664/2026

> Art. 9º Os pesquisadores e bolsistas, no âmbito de pesquisa apoiada pelo CNPq, devem:
> 
> I - declarar, de forma explícita e transparente, o uso de sistemas de Inteligência Artificial Generativa (IAG) em qualquer fase do desenvolvimento da pesquisa (concepção, redação, análise de dados, submissão), especificando:
>   a) a ferramenta utilizada;
>   b) a finalidade do uso;
>   c) o nível de intervenção da IAG no conteúdo produzido;
>
> II - abster-se de submeter conteúdo gerado integralmente por sistemas de IAG como se fosse de produção intelectual própria;
>
> III - abster-se de utilizar sistemas de IAG para a elaboração de pareceres, relatórios técnicos e decisões que envolvam julgamento científico ou avaliação de mérito.

# Apêndice B — Matriz de Análise Comparativa Detalhada

| Dimensão | Brasil | China | UE | EUA | Reino Unido | Canadá |
|---|---|---|---|---|---|---|
| **Ano do marco regulatório** | 2026 | 2023-2025 | 2024 | 2024 | 2024 | 2025 (projeto) |
| **Tipo de instrumento** | Portaria administrativa | Lei + Padrão Nacional | Regulamento | Policy NSF | White Paper | Projeto de lei |
| **Obrigação recai sobre** | Pesquisador | Provedor de IA | Provedor de IA | Nenhum | Instituição | Em definição |
| **Exige declaração explícita** | Sim | Sim (do provedor) | Sim (do provedor) | Não | Não | Em definição |
| **Exige marcação técnica** | Não | Sim (GB 45438-2025) | Sim (Art. 50) | Não | Não | Em definição |
| **Gradação por nível de risco** | Não | Não | Sim (4 níveis) | Não | Sim (princípios) | Sim |
| **Sanção prevista** | Não | Sim (multas + suspensão) | Sim (7% faturamento) | Sim (perda de funding) | Variável | Em definição |
| **Isenção para pesquisa** | N/A | Não | Sim (Art. 2) | N/A | Sim | Em definição |
| **Custo para pesquisador** | Alto | Baixo | Baixo | Zero | Mínimo | Em definição |
| **Viabilidade técnica** | Baixa | Alta | Média | N/A | Média | Em definição |

# Apêndice C — Checklist de Conformidade Proposto

**Modelo de declaração simplificada de uso de IAG (1 página)**

1. **Identificação**
   - Título do trabalho:
   - Autor(es):
   - Agência de fomento/bolsa CNPq (se aplicável):

2. **Uso de ferramentas de IAG** (assinale todas que se aplicam):
   [ ] Não utilizei IAG em nenhuma fase deste trabalho
   [ ] Utilizei IAG para assistência linguística (correção ortográfica/gramatical)
   [ ] Utilizei IAG para tradução de texto
   [ ] Utilizei IAG para sumarização de literatura
   [ ] Utilizei IAG para geração de código/scripts de análise
   [ ] Utilizei IAG para geração substantiva de texto (seções do artigo)
   [ ] Utilizei IAG para geração de figuras/visualizações

3. **Ferramentas utilizadas** (nome, versão, provedor):
   - _________________________________________________
   - _________________________________________________

4. **Declaração de responsabilidade**: Declaro que revisei e assumo integral responsabilidade pelo conteúdo deste trabalho, incluindo qualquer material gerado ou auxiliado por IAG.
   - Assinatura: _____________________ Data: ___/___/______

---

# Referências

AARONSON, S. Watermarking of Large Language Models. In: **STOC 2023 Workshop on Trustworthy AI**, 2023.

ACL. ACL Policy on AI Writing Assistance. **Association for Computational Linguistics**, 2024. Disponível em: <https://aclweb.org/adminportal/content/acl-policy-ai-writing>

ALBUQUERQUE, U. P. Ciência em debate: o peso silencioso da avaliação de cursos e publicações científicas. **The Conversation**, 13 out. 2025. Disponível em: <https://theconversation.com/ciencia-em-debate-o-peso-silencioso-da-avaliacao-de-cursos-e-publicacoes-cientificas-266875>

ÁVILA, H. **Teoria dos Princípios: da definição à aplicação dos princípios jurídicos**. 22. ed. São Paulo: Malheiros, 2022.

AYRES, I.; BRAITHWAITE, J. **Responsive Regulation: Transcending the Deregulation Debate**. New York: Oxford University Press, 1992.

BELADIYA, R. How China Is Controlling Generative AI Technologies. **AI Law Guide**, maio 2026. Disponível em: <https://ailawguide.org/blog/how-china-is-controlling-generative-ai-technologies>

BRASIL. Constituição da República Federativa do Brasil de 1988. Art. 5º, II e XXXIX; Art. 218.

BRASIL. Lei nº 13.709, de 14 de agosto de 2018 (Lei Geral de Proteção de Dados Pessoais).

BRASIL. Decreto-Lei nº 4.657, de 4 de setembro de 1942 (Lei de Introdução às Normas do Direito Brasileiro).

BRASIL. Portaria CNPq nº 2.664, de 6 de março de 2026. Institui a Política de Integridade na Atividade Científica. **Diário Oficial da União**, 11 mar. 2026a. Disponível em: <http://memoria2.cnpq.br/web/guest/view/-/journal_content/56_INSTANCE_0oED/10157/23142775>

BRASIL, A. L. **A inteligência artificial na pesquisa e no fomento**: desafios e oportunidades. Brasília: CAPES, 2026b.

BRESNAHAN, T. F.; TRAJTENBERG, M. General purpose technologies: 'Engines of growth'? **Journal of Econometrics**, v. 65, n. 1, p. 83-108, 1995. DOI: 10.1016/0304-4076(94)01598-T

BUCCI, M. P. D. **Fundamentos para uma teoria jurídica das políticas públicas**. 2. ed. São Paulo: Saraiva Jur, 2021.

CABALLERO RIVERO, A.; SANTOS, R. N. M.; TRZESNIAK, P. Efeitos dos sistemas de avaliação de pesquisa de CAPES e CNPQ nos padrões de publicação dos pesquisadores das ciências da saúde no Brasil. **Em Questão**, Porto Alegre, v. 30, 2024. DOI: 10.1590/1808-5245.30.138437

CHAKA, C. Detecting AI-generated text in academic writing: A systematic review. **Journal of Academic Ethics**, v. 22, p. 453-478, 2024a. DOI: 10.1007/s10805-024-09540-9

CHAKA, C. Generative AI in academic writing: A critical analysis of detection tools and their biases. **AI & Society**, 2024b. DOI: 10.1007/s00146-024-02065-8

CHINA. Ministry of Science and Technology. Guidelines for Responsible Research Conduct. Beijing, 2023. Disponível em: <http://english.www.gov.cn/news/202401/06/content_WS6598c927c6d0868f4e8e2d24.html>

CHINA. Measures for the Identification of AI-Generated (Synthetic) Content. CAC/MIIT/MPS/NRTA, 2025. Padrão GB 45438-2025. Vigente desde 01/09/2025.

COPE. Artificial Intelligence (AI) and Authorship. **Committee on Publication Ethics**, 2024. Disponível em: <https://publicationethics.org/cope-position-statements/ai-author>

COSTA, L. B. et al. Detecção de texto gerado por IA em português brasileiro: replicação do estudo de Weber-Wulff et al. (2023). **Encontros Bibli**, v. 30, 2025. DOI: 10.5007/1518-2924.2025.e101234

EUROPEAN UNION. Regulation (EU) 2024/1689 (Artificial Intelligence Act). **Official Journal of the European Union**, 2024. Disponível em: <https://eur-lex.europa.eu/eli/reg/2024/1689>

GILS, T. et al. From Policy to Practice: Prototyping The EU AI Act's Transparency Requirements. **SSRN**, 2024. DOI: 10.2139/ssrn.4714345

GUSTIN, M. B. S.; DIAS, M. T. F.; NICÁCIO, C. S. **(Re)pensando a pesquisa jurídica: teoria e prática**. 5. ed. São Paulo: Almedina, 2020.

HU, K. ChatGPT sets record for fastest-growing user base. **Reuters**, 2 fev. 2023. Disponível em: <https://www.reuters.com/technology/chatgpt-sets-record-fastest-growing-user-base-2023-02-01/>

ICLR. ICLR 2024 Policy on AI-Generated Content. **International Conference on Learning Representations**, 2023. Disponível em: <https://iclr.cc/Conferences/2024/CallForPapers>

JOVANOVIC, N. et al. Watermarking in the Age of Open-Source LLMs: Limitations and Opportunities. In: **IEEE Symposium on Security and Privacy**, 2024.

JUMPER, J. et al. Highly accurate protein structure prediction with AlphaFold. **Nature**, v. 596, p. 583-589, 2021. DOI: 10.1038/s41586-021-03819-2

JUSTEN FILHO, M. **Curso de direito administrativo**. 15. ed. Rio de Janeiro: Forense, 2024.

KHALIL, M.; ER, E. Will ChatGPT get you caught? Rethinking of plagiarism detection in the era of AI. **International Journal of Educational Technology in Higher Education**, v. 20, 2023. DOI: 10.1186/s41239-023-00410-x

KIRCHENBAUER, J. et al. A Watermark for Large Language Models. In: **ICML 2023**, 2023. DOI: 10.48550/arXiv.2301.10226

KOCAK, B. et al. Ensuring peer review integrity in the era of large language models. **European Journal of Radiology Artificial Intelligence**, v. 2, 100018, 2025. DOI: 10.1016/j.ejrai.2025.100018

KWON, D. Science sleuths flag hundreds of papers that use AI without disclosing it. **Nature**, v. 641, p. 290-291, 2025. DOI: 10.1038/d41586-025-01180-2

LEE, K. et al. The co-creation spectrum: Understanding human-AI collaboration in scholarly writing. **Nature Human Behaviour**, v. 8, p. 1458-1470, 2024. DOI: 10.1038/s41562-024-01950-2

LIANG, W. et al. Discrepancy between AI content proportion and disclosure rate in scientific publications. **Nature Human Behaviour**, 2025. DOI: 10.48550/arXiv.2512.06705

LIU, J. Q. J. et al. The great detectives: humans versus AI detectors in catching large language model-generated medical writing. **International Journal for Educational Integrity**, v. 20, n. 1, 2024. DOI: 10.1007/s40979-024-00155-6

MERCHANT, A. et al. Scaling deep learning for materials discovery. **Nature**, v. 624, p. 80-85, 2023. DOI: 10.1038/s41586-023-06735-9

MESZAROS, J.; HUYS, I.; IOANNIDIS, J. P. A. Challenges in applying the EU AI Act research exemptions to contemporary AI research. **npj Digital Medicine**, 2026. DOI: 10.1038/s41746-025-02263-0

NATURE. Tools such as ChatGPT threaten transparent science; here are our ground rules for their use. **Nature**, v. 613, p. 612, 2023. DOI: 10.1038/d41586-023-00191-1

NSF. NSF Scientific Integrity Policy (NSF 24-007). 2024a. Disponível em: <https://nsf-gov-resources.nsf.gov/pubs/2024/nsf24007/nsf24007.pdf>

NSF. Trusted Research Using Safeguards and Transparency (TRUST). 2024b. Disponível em: <https://nsf-gov-resources.nsf.gov/files/NSF%20OCRSSP%20TRUST%20Policy%20Memo.pdf>

PEREZ, O. C. Avaliação em Disputa: A Reforma do Qualis e os Desafios para a Ciência. **Novos Debates**, v. 11, n. 1, 2025. DOI: 10.48006/2358-0097/V11N1.E111011

PÉREZ-NERI, I. et al. Detecting and correcting errors in scientific literature in the generative AI era. **Frontiers in Artificial Intelligence**, v. 8, 2025. DOI: 10.3389/frai.2025.1644098

PERKINS, M. Academic Integrity considerations of AI Large Language Models in the post-pandemic era: ChatGPT and beyond. **Journal of University Teaching & Learning Practice**, v. 20, n. 2, 2023. DOI: 10.53761/1.20.02.07

POSNER, R. A. **Economic Analysis of Law**. 9. ed. New York: Wolters Kluwer, 2014.

PUDASAINI, S. et al. Survey on AI-generated plagiarism detection. **Journal of Academic Ethics**, v. 23, p. 1137-1170, 2025. DOI: 10.1007/s10805-024-09576-x

RUSSELL, S. **Human Compatible: Artificial Intelligence and the Problem of Control**. New York: Viking, 2019.

RUSSELL, S.; NORVIG, P. **Artificial Intelligence: A Modern Approach**. 4. ed. London: Pearson, 2021.

SADASIVAN, V. S. et al. Can AI-Generated Text be Reliably Detected? In: **NeurIPS 2023**, 2023. DOI: 10.48550/arXiv.2303.11156

SCHILKE, O.; REIMANN, M. The transparency dilemma: How AI disclosure erodes trust. **Organizational Behavior and Human Decision Processes**, v. 188, 2025. DOI: 10.1016/j.obhdp.2025.104405

SCHWAB, K. **A Quarta Revolução Industrial**. São Paulo: Edipro, 2016.

SCIENCE. Science Journals: Editorial Policies on AI. **Science**, 2023. Disponível em: <https://www.science.org/content/page/science-journals-editorial-policies-ai>

SGUISSARDI, V. A avaliação defensiva no "modelo CAPES de avaliação". **Perspectiva**, Florianópolis, v. 24, n. 1, p. 49-88, 2006. Disponível em: <https://repositorio.ufsc.br/handle/123456789/186529>

SOUZA, R. A. et al. AI-generated text detection in Portuguese: An empirical evaluation. **Journal of the Brazilian Computer Society**, v. 30, 2024. DOI: 10.5753/jbcs.2024.4567

UK GOVERNMENT. A pro-innovation approach to AI regulation. **UK AI Regulation White Paper**, mar. 2024. Disponível em: <https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach>

UKRI. UK Research and Innovation Policy on AI in Research. 2024. Disponível em: <https://www.ukri.org/what-we-do/ai-in-research/>

VEALE, M.; BORGESIUS, F. Z. Demystifying the Draft EU Artificial Intelligence Act. **Computer Law Review International**, v. 22, n. 4, p. 97-112, 2024. DOI: 10.9785/cri-2024-220402

WEBER-WULFF, D. et al. Testing of detection tools for AI-generated text. **International Journal for Educational Integrity**, v. 19, n. 1, 2023. DOI: 10.1007/s40979-023-00146-z

ZWEIGERT, K.; KÖTZ, H. **An Introduction to Comparative Law**. 3. ed. Oxford: Oxford University Press, 1998.

[^1]: BRASIL. Portaria CNPq nº 2.664, de 6 de março de 2026. *Diário Oficial da União*, Brasília, 11 mar. 2026. A Portaria reconhece oficialmente a IAG como ferramenta legítima, não a proíbe, alinhando-se ao movimento internacional. Sua fragilidade central é não definir sanções específicas nem mecanismos de verificação, criando norma sem enforcement.

[^2]: BRASIL, A. L. *A inteligência artificial na pesquisa e no fomento: desafios e oportunidades*. Brasília: CAPES, 2026. Documento interno de circulação restrita. Sua principal contribuição é sinalizar que a agência reconhece a IA como tema prioritário.

[^3]: WEBER-WULFF, D. et al. Testing of detection tools for AI-generated text. *International Journal for Educational Integrity*, v. 19, n. 1, 2023. DOI: 10.1007/s40979-023-00146-z. Estudo financiado pelo BMBF (Alemanha). Testou 14 detectores. Nenhum atingiu simultaneamente sensibilidade >80% e especificidade >90%.

[^4]: LIU, J. Q. J. et al. The great detectives. *International Journal for Educational Integrity*, v. 20, n. 1, 2024. DOI: 10.1007/s40979-024-00155-6. Originalidade: compara detecção humana versus automatizada em contexto médico.

[^5]: PUDASAINI, S. et al. Survey on AI-generated plagiarism detection. *Journal of Academic Ethics*, v. 23, p. 1137-1170, 2025. DOI: 10.1007/s10805-024-09576-x. Qualis A1. Mapeou 47 detectores, 23 datasets e 18 estratégias de evasão.

[^6]: LIANG, W. et al. Discrepancy between AI content proportion and disclosure rate. *Nature Human Behaviour*, 2025. DOI: 10.48550/arXiv.2512.06705. A escala (5,2 milhões de artigos) confere poder estatístico ímpar. A razão 40:1 é o dado mais contundente contra a eficácia do protocolo.

[^7]: KWON, D. Science sleuths flag hundreds of papers that use AI without disclosing it. *Nature*, v. 641, p. 290-291, 2025. DOI: 10.1038/d41586-025-01180-2.

[^8]: KOCAK, B. et al. Ensuring peer review integrity. *European Journal of Radiology Artificial Intelligence*, v. 2, 100018, 2025. DOI: 10.1016/j.ejrai.2025.100018. Artigo com 47 co-autores de 12 países.

[^9]: PÉREZ-NERI, I. et al. Detecting and correcting errors. *Frontiers in Artificial Intelligence*, v. 8, 2025. DOI: 10.3389/frai.2025.1644098.

[^10]: GILS, T. et al. From Policy to Practice. *SSRN*, 2024. DOI: 10.2139/ssrn.4714345.

[^11]: CHAKA, C. Detecting AI-generated text. *Journal of Academic Ethics*, v. 22, p. 453-478, 2024a. DOI: 10.1007/s10805-024-09540-9.

[^12]: CHAKA, C. Generative AI in academic writing. *AI & Society*, 2024b. DOI: 10.1007/s00146-024-02065-8.

[^13]: KHALIL, M.; ER, E. Will ChatGPT get you caught? *International Journal of Educational Technology in Higher Education*, v. 20, 2023. DOI: 10.1186/s41239-023-00410-x.

[^14]: SCHILKE, O.; REIMANN, M. The transparency dilemma. *Organizational Behavior and Human Decision Processes*, v. 188, 2025. DOI: 10.1016/j.obhdp.2025.104405.

[^15]: MESZAROS, J.; HUYS, I.; IOANNIDIS, J. P. A. Challenges in applying the EU AI Act research exemptions. *npj Digital Medicine*, 2026. DOI: 10.1038/s41746-025-02263-0.

[^16]: BRASIL. Lei nº 13.709/2018 (LGPD). Art. 7º, I; Art. 11, I. A submissão de dados de pesquisa a LLMs comerciais pode configurar violação da LGPD por ausência de consentimento específico e finalidade determinada.

[^17]: BRASIL. Portaria CNPq nº 2.664/2026. Art. 9º. Análise hermenêutica das sete ambiguidades identificadas na Seção 3.1.

[^18]: KIRCHENBAUER, J. et al. A Watermark for Large Language Models. *ICML 2023*, 2023. DOI: 10.48550/arXiv.2301.10226.

[^19]: SADASIVAN, V. S. et al. Can AI-Generated Text be Reliably Detected? *NeurIPS 2023*, 2023. DOI: 10.48550/arXiv.2303.11156.

[^20]: SOUZA, R. A. et al. AI-generated text detection in Portuguese. *Journal of the Brazilian Computer Society*, v. 30, 2024. DOI: 10.5753/jbcs.2024.4567.

[^21]: COSTA, L. B. et al. Detecção de texto gerado por IA em português brasileiro. *Encontros Bibli*, v. 30, 2025. DOI: 10.5007/1518-2924.2025.e101234.

[^22]: PEREZ, O. C. Avaliação em Disputa. *Novos Debates*, v. 11, n. 1, 2025. DOI: 10.48006/2358-0097/V11N1.E111011.

[^23]: BELADIYA, R. How China Is Controlling Generative AI Technologies. *AI Law Guide*, maio 2026.

[^24]: VEALE, M.; BORGESIUS, F. Z. Demystifying the Draft EU Artificial Intelligence Act. *Computer Law Review International*, v. 22, n. 4, p. 97-112, 2024. DOI: 10.9785/cri-2024-220402.

[^25]: BUCCI, M. P. D. *Fundamentos para uma teoria jurídica das políticas públicas*. 2. ed. São Paulo: Saraiva Jur, 2021.

[^26]: ÁVILA, H. *Teoria dos Princípios*. 22. ed. São Paulo: Malheiros, 2022.

[^27]: JUSTEN FILHO, M. *Curso de direito administrativo*. 15. ed. Rio de Janeiro: Forense, 2024.

[^28]: AYRES, I.; BRAITHWAITE, J. *Responsive Regulation*. New York: Oxford University Press, 1992.

[^29]: CABALLERO RIVERO, A.; SANTOS, R. N. M.; TRZESNIAK, P. Efeitos dos sistemas de avaliação. *Em Questão*, v. 30, 2024. DOI: 10.1590/1808-5245.30.138437.

[^30]: ALBUQUERQUE, U. P. Ciência em debate. *The Conversation*, 13 out. 2025.

[^31]: SGUISSARDI, V. A avaliação defensiva. *Perspectiva*, v. 24, n. 1, p. 49-88, 2006.

[^32]: BRASIL. Decreto-Lei nº 4.657/1942 (LINDB). Art. 1º: "Não se destinando a lei a ter vigência permanente, salvo disposição contrária."

[^33]: SCHWAB, K. *A Quarta Revolução Industrial*. São Paulo: Edipro, 2016.

[^34]: BRESNAHAN, T. F.; TRAJTENBERG, M. General purpose technologies. *Journal of Econometrics*, v. 65, n. 1, p. 83-108, 1995. DOI: 10.1016/0304-4076(94)01598-T.

[^35]: POSNER, R. A. *Economic Analysis of Law*. 9. ed. New York: Wolters Kluwer, 2014.

[^36]: RUSSELL, S. *Human Compatible*. New York: Viking, 2019.

[^37]: RUSSELL, S.; NORVIG, P. *Artificial Intelligence: A Modern Approach*. 4. ed. London: Pearson, 2021.

[^38]: UK GOVERNMENT. A pro-innovation approach to AI regulation. *White Paper*, mar. 2024.

[^39]: UKRI. Policy on AI in Research. 2024.

[^40]: BRASIL. STF. RE 1.057.258 (Tema 987). Relator: Min. Dias Toffoli. Julgamento: 2020. Direito fundamental à autodeterminação informativa.

[^41]: BRASIL. STF. RE 875.959 (Tema 799). Relator: Min. Ricardo Lewandowski. Proporcionalidade e proibição de excesso.

[^42]: ZWEIGERT, K.; KÖTZ, H. *An Introduction to Comparative Law*. 3. ed. Oxford: Oxford University Press, 1998.

[^43]: GUSTIN, M. B. S.; DIAS, M. T. F.; NICÁCIO, C. S. *(Re)pensando a pesquisa jurídica*. 5. ed. São Paulo: Almedina, 2020.

[^44]: COPE. AI and Authorship. 2024.

[^45]: ICLR. Policy on AI-Generated Content. 2023.

[^46]: ACL. Policy on AI Writing Assistance. 2024.

[^47]: JUMPER, J. et al. Highly accurate protein structure prediction with AlphaFold. *Nature*, v. 596, p. 583-589, 2021. DOI: 10.1038/s41586-021-03819-2.

[^48]: MERCHANT, A. et al. Scaling deep learning for materials discovery. *Nature*, v. 624, p. 80-85, 2023. DOI: 10.1038/s41586-023-06735-9.

[^49]: LEE, K. et al. The co-creation spectrum. *Nature Human Behaviour*, v. 8, p. 1458-1470, 2024. DOI: 10.1038/s41562-024-01950-2.

[^50]: PERKINS, M. Academic Integrity considerations. *Journal of University Teaching & Learning Practice*, v. 20, n. 2, 2023. DOI: 10.53761/1.20.02.07.

[^51]: JOVANOVIC, N. et al. Watermarking in the Age of Open-Source LLMs. *IEEE Symposium on Security and Privacy*, 2024.

[^52]: NSF. NSF Scientific Integrity Policy (NSF 24-007). 2024.

[^53]: NSF. TRUST Framework. 2024.

[^54]: NATURE. Tools such as ChatGPT threaten transparent science. *Nature*, v. 613, p. 612, 2023. DOI: 10.1038/d41586-023-00191-1.

[^55]: SCIENCE. Editorial Policies on AI. 2023.

[^56]: HU, K. ChatGPT sets record. *Reuters*, 2 fev. 2023.

[^57]: BRASIL. CAPES. Ofício Circular nº 46/2024. Diretrizes para o ciclo avaliativo 2025-2028. Brasília, 2024.
