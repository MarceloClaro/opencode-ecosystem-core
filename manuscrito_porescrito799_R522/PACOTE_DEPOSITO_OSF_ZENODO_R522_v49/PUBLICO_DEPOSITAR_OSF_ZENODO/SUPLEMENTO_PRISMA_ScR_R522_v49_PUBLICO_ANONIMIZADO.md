# Suplemento PRISMA-ScR — R522 v49

**Manuscrito:** IA generativa na educação jurídica brasileira entre a regulação e a sala de aula.  
**Versão do suplemento:** v49 — 20/09/2026.  
**Função:** reunir, em um único arquivo, checklist PRISMA-ScR, strings disponíveis, log de execução, matriz de extração, razões de exclusão e trilha RH1/RH2.  
**Nota de integridade:** este suplemento consolida apenas informações já disponíveis nos artefatos locais. Strings não recuperadas textualmente não foram reconstruídas por memória.

## 1. Arquivos-fonte e integridade

| Artefato | Caminho local | SHA-256 |
|---|---|---|
| Matriz de extração | `matriz_extracao_R522.xlsx` | `d6390dcb351d31fedb27ddab0ed0e177bc185c1c3080f6a8fd6874482b7a2ddc` |
| Log de execução real | `execucao_real/LOG_EXECUCAO_REAL_R522.md` | `bf512e4bc1a320c9be1a12bc5d222f7a26457dcfeb45eec5690b22c983e0065d` |
| Consolidação DOAJ | `execucao_real/consolidacao_doaj.md` | `bbfedd2a8a45a93650768b7160395d0be2bd5de32bce0235481e136009bd1eb4` |
| OpenAlex O1 | `execucao_real/openalex_legal_genai.json` | `8168cb650a000a45996529b2e92041b47bbcece3bea5876ed73e0bf403b0419c` |
| OpenAlex O2 | `execucao_real/oa1.json` | `99b07850a92551a9ed73d652ee975d8f281453a63a5c3fe32772f5bfd40eb93c` |
| OpenAlex O3 | `execucao_real/oa2.json` | `f2d0aa15a82201df16b9d99e37a4aee7d1351eb09f4ca91a0309ca23da3b499b` |
| OpenAlex atualização 2026 | `execucao_real/openalex_2026_update.json` | `f505cc526439829b88f99198da91c6a6ce911c94078af64a037edd83bf91eccc` |
| RH1 humano | instrumento RH1 preservado na pasta sensível | não público |
| RH2 humano | instrumento RH2 preservado na pasta sensível | não público |
| Errata RH2/κ | `ERRATA_RH2_KAPPA_R522_v49.md` | calcular após fechamento do pacote |

## 2. Checklist PRISMA-ScR consolidado

O checklist oficial PRISMA-ScR contém 20 itens essenciais e 2 opcionais. A tabela abaixo registra o estado de atendimento na v49.

| Item PRISMA-ScR | Status v49 | Evidência/localização |
|---|---|---|
| Título identifica revisão de escopo | Atende | Título/subtítulo do manuscrito. |
| Resumo estruturado | Atende com microcorreção v49 | Resumo e abstract corrigidos para D6 < D5. |
| Racional | Atende | Introdução e referencial teórico. |
| Objetivos/pergunta | Atende | Método, pergunta PICo comparada. |
| Protocolo/registro | Atende parcialmente | Protocolo retrospectivo; OSF/DOI ainda pendente antes de submissão. |
| Critérios de elegibilidade | Atende | Seção 3.5 do manuscrito e log. |
| Fontes de informação | Atende com limitação explícita | OpenAlex e DOAJ executadas; SciELO/Educ@/Google Scholar formal/Scopus/WoS/CAPES limitadas ou não auditáveis. |
| Busca | Atende para OpenAlex/DOAJ; pendente para fontes não executadas | Strings D1-D11 e O1-O3 registradas neste suplemento. |
| Seleção de fontes de evidência | Atende | RH1/RH2 humanos documentados; errata v49. |
| Processo de extração | Atende | Matriz de extração versionada. |
| Itens dos dados | Atende | Matriz: metadados, desenho, método, achados, limitações, dimensões/eixos. |
| Avaliação crítica individual | Não aplicável/limitado | Scoping review; não se agregou risco de viés como metanálise. |
| Síntese dos resultados | Atende | Síntese descritiva e temática; tabelas D1-D6/E1-E4. |
| Seleção de evidências — resultados | Atende | Fluxograma PRISMA-ScR e razões de exclusão. |
| Características das evidências | Atende parcialmente | Caracterização nominal do corpus; matriz suplementar contém detalhes. |
| Avaliação crítica — resultados | Não aplicável/limitado | Ver nota de limites inferenciais e ausência de eficácia causal. |
| Resultados de fontes individuais | Atende no suplemento | Matriz de extração. |
| Síntese dos resultados — resultados | Atende | Seção 4.2/4.3. |
| Sumário da evidência | Atende | Discussão e conclusão. |
| Limitações | Atende | Bases abertas, paywalls, protocolo retrospectivo, ausência de mensuração causal. |
| Conclusões | Atende com linguagem proporcional | v49 troca “confirma-se” por “os achados indicam/sugerem”. |
| Financiamento/conflitos | Atende | Declarações finais. |

## 3. Strings de busca registradas

### 3.1 DOAJ — API aberta, 17/09/2026

| ID | String executada | Total recuperado | Exportação |
|---|---|---:|---|
| D1 | `"legal education" AND "artificial intelligence" AND Brazil` | 2 | `doaj_legal_edu_ai_brazil.json` |
| D2 | `"ensino juridico" AND "inteligencia artificial"` | 1 | `doaj_ensino_jur_ia.json` |
| D3 | `"generative AI" AND "legal education"` | 10 | `doaj_genai_legal_edu.json` |
| D4 | `"legal education" AND "generative artificial intelligence"` | 7 | `doaj_*.json` |
| D5 | `"law school" AND ChatGPT AND assessment` | 2 | `doaj_*.json` |
| D6 | `"educacao juridica" AND "inteligencia artificial"` | 0 | `doaj_*.json` |
| D7 | `"legal education" AND "AI Act"` | 1 | `doaj_*.json` |
| D8 | `"IA generativa" AND "ensino juridico"` | 0 | `doaj_*.json` |
| D9 | `"ChatGPT" AND "law school" AND ethics` | 4 | `doaj_*.json` |
| D10 | `"generative AI" AND "higher education" AND ethics AND law` | 5 | `doaj_*.json` |
| D11 | `"legal education" AND equity AND AI` | 1 | `doaj_*.json` |

Total bruto DOAJ: 33 registros; consolidação por título registrada em `execucao_real/consolidacao_doaj.md`.

### 3.2 OpenAlex — API aberta, 17/09/2026

| ID | String/filtro registrado | Total recuperado | Exportação |
|---|---|---:|---|
| O1 | `search=legal education generative AI (2020-2025)` | 42.671 na API; amostra top-25 exportada | `openalex_legal_genai.json` |
| O2 | `title_and_abstract:"legal education" AND "generative AI" (2020-2025, artigo)` | 25 | `oa1.json` |
| O3 | `title_and_abstract:"ensino juridico" OR "educacao juridica" (2020-2025, artigo)` | 25 | `oa2.json` |

### 3.3 Atualização 2026 — OpenAlex, 18/09/2026

Arquivo: `execucao_real/openalex_2026_update.json`. Candidatos identificados: Lorteau & Sarro (2026), Schrepel (2026) e Fruehwald (2026). Lorteau & Sarro e Schrepel foram mantidos como literatura contextual por paywall/ausência de texto completo recuperado; Fruehwald ficou fora do corpus por tipo documental (preprint SSRN).

### 3.4 Fontes não executadas integralmente

SciELO teve tentativa bloqueada por anti-bot; Educ@ e Google Acadêmico foram acessados apenas de modo exploratório por índice web; Scopus, Web of Science e Portal CAPES não foram executados por ausência de credenciais institucionais. Nenhum número dessas fontes foi usado como denominador final.

## 4. Razões de exclusão registradas

| Registro | Decisão final | Código | Razão |
|---|---|---|---|
| A01 | Excluído | E2 | Foco educacional insuficientemente central para o corpus final. |
| B02 | Excluído | E4 | Introdução/editorial sem método próprio compatível. |
| N03 | Excluído | E4 | Ausência de método próprio/compatível com critérios finais. |
| N12 | Excluído | E4 | Estratégias gerais sem método próprio/compatível para o corpus final. |
| C07 | Excluído/não analisável | E6 | Texto completo não recuperado por rota legítima; subscription/paywall. |
| N06 | Excluído/não analisável | E6 | Texto completo não recuperado por rota legítima; paywall. |
| N09 | Excluído/não analisável | E6 | Texto completo não recuperado por rota legítima; paywall. |
| N10 | Excluído/não analisável | E6 | Texto completo não recuperado por rota legítima; sem PDF direto confiável. |
| N16 | Excluído/não analisável | E6 | Texto completo não recuperado por rota legítima; paywall. |

## 5. Concordância RH1/RH2

A série humana documentada de 19/09/2026 é a documentação vigente para o manuscrito v49. Ver `ERRATA_RH2_KAPPA_R522_v49.md`.

| | RH2 incluir | RH2 excluir | Total RH1 |
|---|---:|---:|---:|
| RH1 incluir | 21 | 0 | 21 |
| RH1 excluir | 0 | 9 | 9 |
| Total RH2 | 21 | 9 | 30 |

Po=1,000; Pe=0,580; κ=1,000. Interpretação: concordância perfeita entre registros humanos documentados; não implica validade perfeita das decisões.

## 6. Corpus final v49

O corpus analítico final permanece em **n = 21**, conforme manuscrito v49. As frequências v49 são:

- D1 Marcos normativos: 20/21 = 95,2%.
- D2 Comparação internacional: 11/21 = 52,4%.
- D3 Letramento/competências: 11/21 = 52,4%.
- D4 Ética e responsabilidade: 16/21 = 76,2%.
- D5 Abordagens pedagógicas (IA como método): 9/21 = 42,9%.
- D6 Equidade/Acesso: 8/21 = 38,1%.
- E1 Fundamentos éticos: 20/21 = 95,2%.
- E2 Transparência/explicabilidade: 15/21 = 71,4%.
- E3 Proteção de dados/privacidade: 12/21 = 57,1%.
- E4 Competências humanísticas: 18/21 = 85,7%.

## 7. Pendências antes de depósito externo

1. Depositar este suplemento, a matriz `.xlsx`, o log e os instrumentos RH1/RH2 em repositório persistente (OSF/Zenodo ou equivalente).
2. Inserir DOI/URL persistente apenas após o depósito real.
3. Manter todas as versões antigas com status histórico, mas usar a errata v49 para orientar a leitura do pacote atual.
