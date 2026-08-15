# SPEC-935-R430 — Marcadores socioeconômicos não convencionais no artigo Crateús-IDEB

## Objetivo

Ampliar o manuscrito Crateús-IDEB (R428/R429) com **indicadores/marcadores não
convencionais** por município (n = 9, microrregião do Sertão de Crateús),
cruzados com o desempenho escolar (IDEB 2025 AI/AF; ganho 2007–2025), nas
famílias: **saúde**, **gênero**, **trabalho**, **profissões/ocupações**,
**formação** e **conectividade** — tudo a partir de fontes oficiais auditáveis
(Censo Demográfico 2022 via IBGE SIDRA v3), com protocolo inferencial
exploratório honesto (bootstrap por cluster n=9 + correção de múltiplas
comparações) e sem alterar números já aprovados no R428.

## Critérios de aceitação

1. **Coleta (CA-1):** `scripts/baixar_indicadores_r430.py` obtém, para os 9
   municípios, ao menos 15 indicadores nas famílias pedidas, a partir do IBGE
   SIDRA (Censo 2022 — universo e resultados preliminares da amostra),
   salvando `data/processed/indicadores_r430.json` +
   `manifest_r430.json` (URL, tabela, variável, classificação, timestamp).
   **33 indicadores coletados (33/33 OK).**
2. **Análise (CA-2):** `scripts/analise_r430_marcadores.py` calcula correlações
   Pearson e Spearman de cada marcador com os desfechos IDEB 2025 AI
   (primário) e IDEB 2023 AI (sensibilidade), com IC95% bootstrap por cluster
   (seed 42, 5.000 réplicas), estabilidade de sinal, **FDR (Benjamini–Hochberg)
   e Bonferroni sobre as 66 hipóteses**, ranking agregado por |r|, e perfil de
   Crateús; saída em `outputs/expanded/resultados_r430.json` +
   `provenance_r430.json`.
3. **Manuscrito (CA-3):** nova subseção **§4.8 "Marcadores socioeconômicos não
   convencionais (análise exploratória)"** no MD e no TeX, com tabela-resumo
   (família, marcador, ρ com IDEB 2025 AI, sinal estável %, qBH), leitura
   substantiva anti-overclaim, e **nota explícita** sobre a
   indisponibilidade do indicador de docentes (INEP/Censo Escolar bloqueado na
   rede do ambiente) e o proxy oficial usado (profissionais das ciências e
   intelectuais entre ocupados; alfabetização 15+). Corpo permanece entre
   40.000 e 70.000 caracteres.
4. **Testes (CA-4):** `tests/test_r430_marcadores.py` verifica: nº de municípios
   = 9; nº de marcadores ≥ 15; valores reproduzem `resultados_r430.json`;
   correção FDR/Bonferroni aplicada e reportada (66 hipóteses); sem termos
   proibidos (R426) e sem alegações causais ("associação não discernível após
   correção" é o máximo permitido); consistência com `resultados_r428.json`
   intacta.
5. **Entregáveis (CA-5):** PDF e DOCX regenerados; evo-61; cycles.json (ciclo
   248); doctor sem falhas; commit + push.

## Fontes (efetivadas)

As tabelas clássicas de trabalho/saúde/renda do SIDRA v3 (9622, 9616, 9624,
9717, 9546, 9547, 9730, 9770, 9780, 9580, 9562) responderam HTTP 500
(seletivamente indisponíveis no ambiente). Solução auditável: usar as tabelas
da **amostra do Censo Demográfico 2022** (publicação IBGE "Resultados
preliminares da amostra", 2024–2025), que funcionam normalmente na API v3.

| Família | Marcador | Tabela SIDRA | Variável/classificação |
|---|---|---|---|
| Gênero | % mulheres | 9606 (universo) | 93, class 2 [5/6794] |
| Raça/etnia | % pretos e pardos | 9605 (universo) | 93, class 86 [2777+2779/95251] |
| Trabalho | Nível de ocupação 10+ (%) | 10268 (amostra) | 675 (direto) |
| Trabalho | % com carteira | 10261 (amostra) | 4090, class 11913 |
| Trabalho | % sem carteira | 10261 | 4090, class 11913 |
| Trabalho | % conta própria | 10261 | 4090, class 11913 |
| Trabalho | % empregador | 10261 | 4090, class 11913 |
| Trabalho | % doméstico | 10261 | 4090, class 11913 |
| Trabalho | % setor público | 10261 | 4090, class 11913 |
| Trabalho | % familiar auxiliar | 10261 | 4090, class 11913 |
| Trabalho | % contribuintes previdência | 10264 (amostra) | 4090, class 526 |
| Profissões | % diretores e gerentes | 10264 | 4090, class 12064 |
| Profissões | % profissionais ciências/intelectuais | 10264 | 4090, class 12064 |
| Profissões | % técnicos nível médio | 10264 | 4090, class 12064 |
| Profissões | % serviços/vendedores | 10264 | 4090, class 12064 |
| Profissões | % agropecuária | 10264 | 4090, class 12064 |
| Profissões | % ocupações elementares | 10264 | 4090, class 12064 |
| Atividade | % agropecuária | 10266 (amostra) | 4090, class 11805 |
| Atividade | % indústria | 10266 | 4090, class 11805 |
| Atividade | % construção | 10266 | 4090, class 11805 |
| Atividade | % comércio | 10266 | 4090, class 11805 |
| Atividade | % administração pública | 10266 | 4090, class 11805 |
| Atividade | % educação | 10266 | 4090, class 11805 |
| Atividade | % saúde | 10266 | 4090, class 11805 |
| Atividade | % serviços domésticos | 10266 | 4090, class 11805 |
| Renda | Rend. domiciliar per capita (R$) | 10295 (amostra) | 13431 (direto) |
| Renda | Rend. médio do trabalho (R$) | 10280 (amostra) | 13536 (direto) |
| Condições de vida | % renda per capita ≤ 1 SM | 10296 (amostra) | 13604, class 386 |
| Educação/formação | Anos de estudo 11+ | 10062 (amostra) | 13285 (direto) |
| Educação/formação | % 18+ com superior completo | 10061 (amostra) | 2667, class 1568 |
| Educação/formação | Taxa bruta de frequência escolar | 10056 (amostra) | 3795 (direto) |
| Habitação | % alvenaria | 9928 (universo) | 1000381, class 137 |
| Habitação | % moradores >3/dormitório | 9940 (universo) | 382, class 1975 |

**Indisponibilidades declaradas:** vacinação COVID-19 (9730), pobreza
multidimensional (9770), insegurança alimentar (9562), uso de internet por
pessoas (9780) e rendimento dos ocupados (9580) → HTTP 500 na API v3 no
ambiente. Proxies oficiais usados: pobreza via classes de rendimento domiciliar
per capita (10296) e formalidade via contribuintes de previdência (10264);
internet de domicílios reaproveitada da base R427 (9936).

**Limitação declarada:** indicador de docentes/formadores do INEP (Censo
Escolar, AFD) indisponível por bloqueio de rede do ambiente
(download.inep.gov.br → curl 60/000). Proxy oficial usado: % profissionais das
ciências e intelectuais entre ocupados e % alfabetizados 15+ (Censo 2022),
com nota no manuscrito. Ação futura registrada: rodar em ambiente com acesso
ao INEP.

## Resultado principal (R430)

- 33 marcadores × 9 municípios coletados; 66 hipóteses testadas
  (33 × IDEB 2025 AI e 33 × IDEB 2023 AI).
- **Nenhuma associação sobreviveu ao ajuste FDR (BH) nem a Bonferroni**
  (menor qBH = 0,49). Protocolo exploratório: associações crudas maiores em
  |ρ| (~0,65–0,73) não são interpretadas como evidência.
- Padrão descritivo (sem inferência): municípios com maior % de ocupados sem
  carteira e maior % de diretores tenderam a apresentar IDEB 2025 mais alto;
  municípios com maior % de nível superior completo, maior % de profissionais
  ciências/intelectuais e maior nível de ocupação tenderam a IDEB mais baixo —
  leitura contextualizada pelo perfil da sede (Crateús: maior escolaridade e
  renda da microrregião e IDEB abaixo dos municípios rurais vizinhos).
- Perfil Crateús: posição máxima (9/9) em renda domiciliar per capita,
  rendimento do trabalho, anos de estudo, nível de ocupação, carteira e
  contribuintes de previdência; posição mínima (1/9) em % sem carteira e em
  % renda per capita ≤ 1 SM.

## Decisões de rigor

- n=9 → **análise exploratória descritiva**; nenhuma hipótese formal nova.
- Bootstrap por cluster (5.000, seed 42) + IC95 percentil + estabilidade de sinal.
- FDR (BH) e Bonferroni sobre os p-valores empíricos; reportar sobrevivências.
- Anti-overclaim: "associação não discernível após correção" é o limite máximo;
  nunca "não existe associação" nem "efeito".
- Números R428 intocados; verificação de consistência deve continuar OK.

## Escopo

Inclui: coleta SIDRA, análise, manuscrito MD+TeX, testes, PDF/DOCX, evo-61,
cycles ciclo 248, commit+push. Exclui: downloads INEP (bloqueados), novas
figuras (tabela-texto é suficiente nesta rodada), alteração de números R428.
