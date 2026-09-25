# Protocolo OSF — Scoping Review Brasil-comparado
## IA Generativa na Educação Jurídica Brasileira entre a Regulação e a Sala de Aula: revisão de escopo Brasil-comparado sobre ética, governança algorítmica e equidade (2020-2025)

**SPEC:** SPEC-935-R522  
**Registro OSF (a criar):** `https://osf.io/[A GERAR]` — Pré-registro antes da execução  
**Revista-alvo:** Educação Por Escrito (PUCRS), Chamada 799, fluxo contínuo, e-ISSN 2179-8435, Qualis A4 (Ensino, 2021-2024) — Meta de rigor Qualis A1 (meta, não garantia)  
**Data do protocolo:** 17 de setembro de 2026  
**Versão:** 2.0 (atualizada 17/09/2026 — execução real iniciada: DOAJ + busca web; Scopus/WoS/SciELO/Educ@/CAPES pendentes)  
**Autores:** [A CONFIRMAR — Nome, ORCID, PPGEDU/PPGD, Instituição, e-mail]  
**Contato:** [e-mail do autor correspondente]  
**Licença:** CC BY 4.0  
**Financiamento:** [A CONFIRMAR]  
**Conflitos:** Declarar / Nenhum  
**Palavras-chave:** Inteligência artificial generativa; Ensino jurídico; Ética; Governança algorítmica; Equidade; Revisão de escopo; Brasil comparado

---

### 1. Justificativa e GAP

A literatura sentinela (VALENCIA & BELTRÁN, 2025, PRISMA 136→19, DOI 10.59659/revistatribunal.v5i12.235) demonstra: 57,89% dos estudos focam marcos regulatórios, 42,11% comparação internacional, 42,11% responsabilidade — enquanto **acesso à justiça/equidade** é sub-representado e **justiça social/governança algorítmica/direitos humanos** são vácuo. Triangulação BR (PAULA 2026 DOI 10.5281/zenodo.19966396; CARMO & ALVES 2025; ABAL & PILATI 2025 DOI 10.47975/ijdl.v.6.1302) confirma: falta síntese que traduza LGPD + PL 2.338/2023 (art.14 II alto risco educacional) + CNJ 615/2025 (arts.14, 19-25, Sinapses) + AI Act UE 2024/1689 + UNESCO 2023 (DOI 10.54675/EWZM9535) em **diretrizes pedagógicas operacionais equitativas**. Este protocolo fecha o descompasso norma-pedagogia por scoping review.

### 2. Pergunta e objetivos

**PICo comparada:**
- **P:** Educação jurídica superior brasileira (graduação, pós, educação judicial) comparada a UE/Portugal/Alemanha/EUA
- **I:** Uso de IA Generativa/LLMs no ensino-aprendizagem
- **Co:** Marcos ético-normativos 2020-2025, foco governança/equidade/direitos humanos

**Pergunta principal:**
> Que evidências, princípios e lacunas a literatura científica (2020-2025) apresenta sobre a implementação ética, transparente e equitativa de IAGen na educação jurídica brasileira em perspectiva comparada?

**Subperguntas (GAPs 1-4):**
- S1: Como equidade/acesso à justiça é operacionalizada (BR vs comparados)?
- S2: Que modelos de governança/transparência hermenêutica são propostos/avaliados?
- S3: Que estratégias didático-pedagógicas foram testadas empiricamente (BR vs comparados)?
- S4: Que convergências/divergências UNESCO/AI Act vs BR para educação?

**Objetivo geral:** Mapear/sintetizar literatura BR comparada 2020-2025 para mapa de evidências + agenda + princípios de Transparência Hermenêutica.

**Objetivos específicos:**
- OE1: Caracterizar volume, desenho, qualidade
- OE2: Codificar 6 dimensões Valencia + 4 eixos Carmo
- OE3: Extrair barreiras/facilitadores equitativos
- OE4: Propor agenda e Transparência Hermenêutica

### 3. Critérios de elegibilidade

**Inclusão:**
- Artigo original, revisão ou análise documental com foco **educação jurídica + IA**
- Período 2020-2025, texto completo, peer-reviewed ou Qualis/CAPES
- Idiomas PT, EN, ES
- Para bloco comparado: traz lição transferível ao BR (UE/PT/DE/EUA/UNESCO)

**Exclusão:**
- Duplicatas, anais, teses/dissertações, resumos, opinião sem método
- Foco exclusivo em automação judiciária sem dimensão educacional
- <2020, idioma fora escopo

### 4. Fontes e estratégia de busca

**Bases:** Scopus, Web of Science, SciELO, Educ@, Portal CAPES, DOAJ, Google Acadêmico (complementar).

**Período/idiomas:** 2020-2025; PT, EN, ES.

**Strings reprodutíveis:**

```sql
-- BLOCO A — BR (Scopus/WoS)
("artificial intelligence" OR "generative AI" OR "large language model*" OR "ChatGPT" OR "LLM" OR "IA generativa")
AND
("legal education" OR "law school" OR "ensino jurídico" OR "educação jurídica" OR "formação jurídica")
AND
(Brasil OR Brazil OR "PL 2338" OR "CNJ 615" OR LGPD)
AND
(ethic* OR governance OR transparency OR accountability OR equity OR "access to justice" OR "direitos humanos" OR "transparência hermenêutica")

-- BLOCO B — Comparados (Scopus/WoS)
("generative AI" OR "LLM") AND ("legal education") AND ("EU AI Act" OR UNESCO OR Portugal OR Germany OR "United States" OR "OAP")

-- BLOCO C — PT (SciELO/Educ@/DOAJ)
("inteligência artificial" OR "IA generativa") AND ("ensino jurídico" OR "educação jurídica") AND (ética OR governança OR equidade OR LGPD OR "PL 2338" OR "CNJ 615")
```

**Busca complementar:** Lista de referências dos incluídos + busca por citações (forward).

**Gestão:** Rayyan para deduplicação e triagem duplo-cega.

### 5. Seleção

1. Importação para Rayyan + deduplicação
2. Triagem duplo-cega título/resumo (2 revisores)
3. Leitura integral dos elegíveis (2 revisores)
4. Terceiro revisor em conflito
5. Fluxograma PRISMA 2020 (identificação → triagem → elegibilidade → incluídos) com motivos de exclusão

**Estimativa:** 800-1.200 recuperados → 600-900 após dedup → 60-90 textos completos → 25-40 incluídos (base sentinela 136→19).

### 6. Extração

**Ficha por estudo (planilha Excel, ver matriz_extracao_R522.xlsx):**
`ID | Referência ABNT | DOI/URL auditada | Data acesso | Ano | País comparado | Desenho | Amostra/Contexto | Pergunta | Método | Achados | Limitações | Conflitos/Financiamento | Dimensões Valencia (6) | Eixos Carmo (4) | GAP (1-4) | Lição para BR (transferibilidade) | Notas`

**Processo:** Duplo independente + reconciliação; contato com autores se dado ausente.

### 7. Avaliação de qualidade

Scoping: mapeia sem exclusão por qualidade. Se migrar para sistemática: JBI Checklist ou MMAT, sem excluir, mas estratificando síntese por qualidade.

### 8. Síntese

- **(1) Frequência:** Gráfico radar das 6 dimensões Valencia (+2 emergentes) — Tabela 1 do manuscrito
- **(2) Temática:** Síntese Braun & Clarke (2006) nos 4 eixos Carmo (fundamentos éticos, transparência, dados/privacidade, competências humanísticas)
- **(3) Matriz comparativa:** BR (PL/CNJ/LGPD) vs UE/AI Act vs PT/OAP vs DE vs EUA vs UNESCO — Tabela 2 do manuscrito
- **(4) Gap map:** Matriz dimensões × país × nível evidência + agenda PICO para primários

**Software:** Rayyan, Excel, R/Python para gráficos, NVivo opcional para codificação.

### 9. Ética, transparência e reprodutibilidade

- Revisão de literatura — dispensa CEP (CNS 510/2016); primários da agenda exigirão CEP
- Pré-registro OSF antes da execução, versionado
- Dados extraídos no Zenodo (DOI), strings e fluxograma suplementares
- Declaração de IA: apoio à revisão linguística/organização, sem geração de dados/análises/citações, revisão humana integral (COPE)
- Turnitin institucional (<15%)

### 10. Cronograma

| Semana | Atividade |
|--------|-----------|
| 1 | Registro OSF + importação Rayyan + teste strings |
| 2 | Triagem título/resumo duplo-cega |
| 3 | Leitura integral + extração |
| 4 | Síntese + matriz comparativa + gap map |
| 5 | Escrita discussão + checklist PRISMA-ScR + depósito Zenodo |
| 6 | Formatação ABNT + Turnitin + submissão Educação Por Escrito |

### 11. Financiamento e conflitos

[A CONFIRMAR]

### 12. Referências do protocolo

VALENCIA & BELTRÁN 2025 DOI 10.59659/revistatribunal.v5i12.235; PAULA 2026 DOI 10.5281/zenodo.19966396; CARMO & ALVES 2025; ABAL & PILATI 2025 DOI 10.47975/ijdl.v.6.1302; UNESCO 2023 DOI 10.54675/EWZM9535; AI Act 2024/1689; PL 2338/2023; CNJ 615/2025 DJe 14 mar 2025 p.2-17; ITS Rio 23 jun 2025; Juristech 18 abr 2026; PAGE et al. PRISMA 2020 BMJ 2021; PETERS et al. JBI scoping 2020; TRICCO et al. PRISMA-ScR 2018; BRAUN & CLARKE 2006.

### 13. Histórico de versões

- v1.0 — 17/09/2026 — Criação inicial R522

---

**Como registrar no OSF:**
1. Criar projeto em https://osf.io → “Register” → Template OSF Preregistration ou Prereg Challenge
2. Anexar este markdown + planilha vazia + strings
3. Gerar DOI e inserir no manuscrito + Zenodo
4. Tornar público após aprovação do registro


---

## Estado da execução real (17/09/2026 — rastreável)

**Número de buscas executadas até esta data:** 11 strings na DOAJ (API aberta) + 1 busca web acadêmica
complementar (Google Acadêmico/web). Exportações brutas e decisões de triagem registradas em
`execucao_real/LOG_EXECUCAO_REAL_R522.md` e em `execucao_real/doaj_*.json`.

**Bases ainda não executadas (pendentes):** Scopus, Web of Science, SciELO (bloqueio anti-bot em
tentativa direta), Educ@, Portal CAPES e Google Acadêmico formal. Nenhum número dessas bases é
reportado.

**Regra de integridade:** este pré-registro só será declarado "executado" quando todas as bases
planejadas tiverem exportações reais arquivadas e a triagem duplo-cega estiver concluída com a
matriz validada. Até lá, a Seção de Resultados do manuscrito permanece `[A CONFIRMAR]`.

**Alterações prospectivas que exigirão emenda formal:** incluir resultados de bases não previstas
ou ampliar a janela 2020-2025 para incluir 2026 (hoje permitido apenas como atualização contextual).


---

## Emendas ao protocolo

### EMENDA-2026-09-17-A1 — Fontes de informação em modalidade de acesso aberto

Aprovada de forma prospectiva em 17/09/2026 (ver `execucao_real/EMENDA_2026-09-17_A1_acesso_aberto.md`).

**Alteração:** as buscas passam a ser executadas em fontes de acesso aberto auditáveis — DOAJ,
OpenAlex, SciELO, Educ@, Google Acadêmico (promovido a fonte primária de varredura) e base de
preprints (SciELO Preprints/SSRN). Scopus, Web of Science e Portal CAPES tornam-se fontes opcionais
de validação a posteriori, sem bloquear a revisão.

**Não alterado:** pergunta PICo, critérios de elegibilidade, janela 2020-2025, desenho
JBI/PRISMA-ScR, regra anti-overclaim.

**Impacto declarado:** o fluxograma reportará somente fontes efetivamente executadas; a limitação
de cobertura será declarada na seção de limitações (PRISMA-ScR item 6).
