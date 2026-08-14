# Carta ao Editor — Revista Brasileira de Estudos Pedagógicos (RBEP/INEP)

**Data:** 13 de agosto de 2026
**Manuscrito:** "Educação terciária e trajetórias de renda: evidência associativa de painel com validação cruzada agrupada por país (135 economias, 1960–2023)"

---

Prezado(a) Editor(a),

Submetemos à consideração da Revista Brasileira de Estudos Pedagógicos o manuscrito acima, um estudo empírico associativo sobre a relação entre educação terciária e nível de renda per capita em 135 economias (1960–2023), com base exclusivamente em dados oficiais do World Development Indicators e do Worldwide Governance Indicators (Banco Mundial).

## Contribuição

O manuscrito contribui em três frentes. Primeiro, apresenta evidência descritiva transparente sobre uma questão de política educacional relevante para o Brasil e para a agenda da renda média. Segundo, submete as estimativas a validações cruzadas por país (leave-one-country-out) e por tempo, quantificando explicitamente a limitação de generalização de amostras com poucos países — um ponto metodológico raramente reportado na literatura de educação e crescimento. Terceiro, a ciência aberta é integral: dados, código e arquivo de proveniência numérica (SHA-256) estão disponíveis para verificação independente.

## Ciência aberta e reprodutibilidade

- Fonte de dados: World Development Indicators e Worldwide Governance Indicators (World Bank API), download em 13/08/2026, cache imutável com URL, timestamp UTC, status HTTP e hash SHA-256 por arquivo.
- Código: `scripts/download_expanded_data.py` e `scripts/analyze_expanded.py` (Python, offline, sementes fixas).
- Resultados: `outputs/expanded/` com proveniência numérica completa em `provenance_expanded.json` (painel de 135 países, controles de governança WGI, erros padrão clusterizados por país); cada número citado no manuscrito tem entrada correspondente.
- Repositório de auditoria: `academic/papers/arm_education_audit/`.

## Declarações

- **Ineditismo:** este manuscrito não foi publicado e não está sob consideração em outro periódico no momento da submissão; comprometemo-nos a comunicar qualquer alteração dessa condição.
- **Conflitos de interesse:** não há conflitos de interesse a declarar.
- **Financiamento:** o estudo não contou com financiamento externo.
- **Autoria:** todos os autores contribuíram substancialmente para a concepção, análise e redação, e aprovam a versão submetida.

## Nota de conduta

Este documento é um **candidato a submissão**: nenhuma alegação de aceite, de classificação Qualis ou de prontidão editorial é feita. A adequação às normas ABNT (NBR 10520 e NBR 6023) foi verificada por testes automatizados, mas a decisão final de publicação pertence exclusivamente ao corpo editorial da RBEP.

Agradecemos a oportunidade de submeter este trabalho.

Atenciosamente,

**Equipe de pesquisa — OpenCode Ecosystem Core**
(Manuscrito preparado com apoio de ferramentas de IA; a revisão final e a decisão de submissão permanecem sob responsabilidade humana.)
