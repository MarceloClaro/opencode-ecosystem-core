# Relatório dos cinco scanners (`/diagnose`)

**Entrada:** `02_ARTIGO_QUALIS_A1.md`
**SHA-256 da entrada:** `5d5e1b4c718da88f1305d645d3913ade77ed8a81a77e132fbc1f26bff945d079`
**Comando:** `python3 -m scanners.cli --format json diagnose 02_ARTIGO_QUALIS_A1.md --social`
**Data:** 5 de novembro de 2026
**Duração:** 0,277 s
**Saída bruta:** `dados/scanners.json` e `dados/scanners_raw.txt`

> **Ressalva central.** O pipeline `/diagnose` foi calibrado para **artefatos do ecossistema** (agentes, módulos, capacidades, metas). Aplicado a um artigo em prosa, ele produz uma leitura **lexical e estrutural**, não uma avaliação editorial, metodológica ou de qualidade científica. Os resultados abaixo são **candidato_a_inspecao** e **exigem_validação_externa**. O campo `measurement` registra `functional_validation: false`, `externally_validated: false` e `confidence_calibrated: false`.

---

## 1. Quadro dos cinco scanners

| Scanner | Resultado | O que mede | Aplicabilidade ao artigo |
|---|---|---|---|
| **Noológico** | Cobertura 34% (31 de 92 categorias; 10 dimensões; grau C) | Menção lexical a categorias epistemológicas | Baixa: mede vocabulário, não profundidade argumentativa |
| **Teleológico** | Ignorado: "sem metas definidas" | Distância entre metas declaradas e capacidades | Nula: o artigo não declara metas de ecossistema |
| **Potencialidade** | 2 candidatos latentes (hipóteses de ecossistema) | Capacidades latentes e lacunas de inovação | Nula: os candidatos tratam de auto-evolução e avaliação do ecossistema |
| **Evolutivo** | 61 lacunas (todas noológicas) | Roadmap de fechamento de lacunas | Baixa: recomenda "fechar lacunas" como se o artigo fosse um sistema |
| **Impacto social** | `sroi_ratio: null`; objeto padrão de ecossistema com SROI 2,55 | SROI, teoria da mudança, ODS | Nula: o relatório não foi derivado do artigo |

Scanner opcional **Engenharia Reversa**: score 3,0; nenhum código estruturado detectado. Não se aplica a um texto.

---

## 2. Leitura de cada resultado

### 2.1 Noológico

O scanner analisou 10 dimensões e 92 categorias, das quais 31 foram mencionadas e 61 não. O grau atribuído foi **C — Cobertura Limitada**. O campo `gaps` veio vazio; o número 61 aparece em `summary.categories_absent` e é reutilizado pelo scanner evolutivo.

O que isso significa: o artigo usa vocabulário associado a algumas dimensões (provavelmente políticas, formação, práticas e métodos), mas não a outras (teoria dos jogos, níveis de análise, dados). Em um artigo de educação, a ausência de vocabulário de "teoria dos jogos" não é uma falha. **A cobertura de 34% não deve ser lida como "o artigo cobre apenas 34% do conhecimento relevante".** Ela mede apenas a presença de palavras-chave predefinidas.

### 2.2 Teleológico

O scanner foi ignorado porque não há "metas definidas" no artefato. Ele espera um sistema com objetivos declarados e capacidades correspondentes. Um artigo não é um sistema desse tipo. A ausência de resultado não indica falha do artigo; indica incompatibilidade de modelo.

### 2.3 Potencialidade

Foram retornados 2 candidatos, ambos com `hypothesis_only: true` e `probability_calibrated: false`. O principal é "evidence-oriented-evolution", que descreve uma hipótese de evolução do ecossistema baseada em auto-evolução, avaliação e memória compartilhada. Nada disso se refere ao artigo. O resultado é ruído para este contexto.

### 2.4 Evolutivo

O scanner reutiliza as 61 categorias ausentes do noológico e recomenda "priorizar o fechamento de lacunas críticas antes de novas features". A recomendação é própria para desenvolvimento de software, não para um manuscrito. Não deve ser seguida como orientação editorial.

### 2.5 Impacto social

O campo `sroi_ratio` veio `null`. O objeto `summary` contém um `SocialImpactReport` padrão, com título "Diagnóstico do Ecossistema", investimento de R$ 200.000, valor social bruto de R$ 230.000 e SROI de 2,5548. Esses números **não foram calculados a partir do artigo**; são parâmetros default do scanner. **Não devem ser citados, reproduzidos ou atribuídos ao estudo.**

---

## 3. O que os scanners não dizem

- Não dizem se o artigo é bom, publicável ou "Qualis A1".
- Não avaliam a qualidade da revisão, a adequação das referências ou a consistência argumentativa.
- Não leem o conteúdo semântico; contam menções lexicais.
- Não substituem leitura humana, parecer ad hoc ou revisão por pares.
- Não validam a metodologia declarada.

## 4. O que os scanners sugerem

- A cobertura lexical de 34% é compatível com um texto de ciências humanas que não mobiliza vocabulário de dados, teoria dos jogos ou modelagem formal. Não há, aqui, sinal de problema.
- O campo `measurement.kind = provided_input_lexical` confirma que a medição é lexical.
- A ausência de metas e de componentes de ecossistema confirma que o pipeline não foi desenhado para prosa.

## 5. Recomendação de uso

1. Usar este relatório apenas como **registro de execução** do comando `/diagnose`, não como parecer editorial.
2. Para decisões sobre o artigo, usar `RELATORIO_AUDITORIA.md` e `RELATORIO_REFERENCIAS.md`.
3. Se o objetivo for uma avaliação acadêmica, submeter o texto a leitura humana especializada ou a um revisor do periódico-alvo.
4. Não citar o SROI de 2,55 nem a cobertura de 34% como evidência de qualidade ou de impacto.

---

## 6. Ressalva formal

Os resultados dos cinco scanners são **candidato_a_inspecao** e **exigem_validacao_externa**. Nenhum deles foi validado funcionalmente (`functional_validation: false`), calibrado (`confidence_calibrated: false`) ou verificado por terceiros (`externally_validated: false`). A execução é local (`verification: local_operation`).
