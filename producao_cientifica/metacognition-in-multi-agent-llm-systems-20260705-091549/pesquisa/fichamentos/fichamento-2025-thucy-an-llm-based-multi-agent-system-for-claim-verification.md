# Fichamento — Thucy: An LLM-based Multi-Agent System for Claim Verification across Relational Databases

**Tema de pesquisa:** metacognition in multi-agent LLM systems
**Aderência ao tema:** 8.0/10 — LEITURA PRIORITÁRIA — alta aderência ao tema; candidato a referência central na revisão de literatura.

## 1. Referência

**ABNT (NBR 6023:2018):** THEOLOGITIS, M.; SUCIU, D. Thucy: An LLM-based Multi-Agent System for Claim Verification across Relational Databases. **arXiv**, 2025. Disponível em: http://arxiv.org/abs/2512.03278v2. Acesso em: 5 jul. 2026.

**APA (7ª ed.):** Theologitis, M., & Suciu, D. (2025). Thucy: An LLM-based Multi-Agent System for Claim Verification across Relational Databases. *arXiv*. http://arxiv.org/abs/2512.03278v2

**Formato de citação no texto (NBR 10520:2023):** (Theologitis; Suciu, 2025, p. N)

## 2. Identificação

| Campo | Valor |
| --- | --- |
| Autores | Michael Theologitis; Dan Suciu |
| Ano | 2025 |
| Veículo | arXiv |
| DOI | — |
| Plataforma de origem | arxiv |
| Citações | — |
| Texto integral (MD) | [2025] - thucy-an-llm-based-multi-agent-system-for-claim-verification-across-re.md |

## 3. Fichamento bibliográfico (resumo objetivo)

In today's age, it is becoming increasingly difficult to decipher truth from lies. Every day, politicians, media outlets, and public figures make conflicting claims -- often about topics that can, in principle, be verified against structured data. For instance, statements about crime rates, economic growth or healthcare can all be verified against official public records and structured datasets. Building a system that can automatically do that would have sounded like science fiction just a few years ago. Yet, with the extraordinary progress in LLMs and agentic AI, this is now within reach. Still, there remains a striking gap between what is technically possible and what is being demonstrated by recent work. Most existing verification systems operate only on small, single-table databases -- typically a few hundred rows -- that conveniently fit within an LLM's context window. In this paper we report our progress on Thucy, the first cross-database, cross-table multi-agent claim verification system that also provides concrete evidence for each verification verdict. Thucy remains completely agnostic to the underlying data sources before deployment and must therefore autonomously discover, inspect, and reason over all available relational databases to verify claims. Importantly, Thucy also reports the exact SQL queries that support its verdict (whether the claim is accurate or not) offering full transparency to expert users familiar with SQL. When evaluated on the TabFact dataset [...]

## 4. Fichamento de citação (trechos literais)

> "In this work, we present a multi-agent system called In this paper we report our progress on T HUCY, the first T HUCY that takes over the verification process once the user cross-database, cross-table multi-agent claim verification sys- has obtained the structured data and imported it into a re- tem that also provides concrete evidence for each verification lational database." (Theologitis; Suciu, 2025, p. N)

> "We had downloaded this data from the In this section, we present the experimental evaluation of Seattle Police Department (2025b) in the form of a CSV T HUCY." (Theologitis; Suciu, 2025, p. N)

> "To test the robust- returned the following report (excerpted verbatim): ness of T HUCY, we also swapped the models of our three Conclusion expert agents for GPT-4o-mini, aligning them to those used – The Seattle crime data do not support the claim that in the baseline systems (e.g., we match POS)." (Theologitis; Suciu, 2025, p. N)

## 5. Fichamento crítico (análise vinculada ao tema)

**Termos compartilhados com o tema:** agent, llm, multi, systems

**Pontos fortes:**

- Fundamentação empírica com experimentos ou benchmarks, favorecendo a verificabilidade dos resultados.
- Preocupação explícita com reprodutibilidade ou disponibilização de código, critério valorizado em avaliações Qualis A1.

**Limitações e riscos de viés:**

- Ausência de menção a validação estatística (p-valores, intervalos de confiança, tamanhos de efeito) no material analisado.
- O texto não declara limitações explícitas, o que exige leitura cética das conclusões.

**Lacunas em relação ao tema de pesquisa:**

- O artigo não esgota o tema; identificar se aborda as variáveis específicas do problema de pesquisa antes de citá-lo como evidência central.

---
_Fichamento gerado pelo subsistema research do opencode-ecosystem-core (ABNT NBR 6023:2018 / NBR 10520:2023 / APA 7)._