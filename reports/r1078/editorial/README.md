# R1078 — Editorial: LanguageTool 6.6 + Vale 3.26 nos 84 fragmentos

**Status:** diagnóstico executado; **nenhuma correção automática aplicada**.
**Não é aprovação editorial, não é nota literária e não é validação externa.**

## 1. Corpus e método

- 84 fragmentos ativos da edição R1075 (o epílogo foi excluído).
- 48.767 palavras no texto plano extraído dos fragmentos.
- LaTeX convertido para texto plano com Pandoc 3.7.0.2; o Markdown equivalente
  foi usado no Vale.
- LanguageTool 6.6 em pt-BR, via servidor local.
- Vale 3.26.0 com estilo PT-BR próprio: repetição, muletas, advérbios em
  `-mente`, pleonasmos e clichês.

A conversão de LaTeX para texto plano introduz artefatos de espaçamento e
checkboxes. Eles foram separados dos problemas de prosa.

## 2. LanguageTool — 650 ocorrências

| Categoria | Ocorrências |
|---|---:|
| Estilo | 216 |
| Tipografia | 138 |
| Erro de escrita | 73 |
| Linguagem formal | 68 |
| Redundância | 38 |
| Pontuação | 26 |
| Gramática geral | 23 |
| Maiúsculo/minúsculo | 21 |
| Remoção de pronomes | 14 |
| Clareza | 8 |
| Linguagem concisa | 7 |
| Outras | 18 |
| **Total** | **650** |

### 2.1 Regras mais frequentes

| Regra | Ocorrências | Leitura |
|---|---:|---|
| `PORTUGUESE_WORD_REPEAT_BEGINNING_RULE` | 207 | inícios de frase repetidos; provável anáfora/ritmo |
| `MORFOLOGIK_RULE_PT_BR` | 73 | termos de domínio, nomes, CIDs e símbolos |
| `FORMAL_PRA_PARA` | 49 | “pra” em registro oral; provável escolha de voz |
| `COMMA_PARENTHESIS_WHITESPACE` | 44 | checkboxes `( )` e conversão |
| `PARENTESESE_AND_QUOTES_SPACING` | 38 | conversão de LaTeX |
| `UNPAIRED_BRACKET_SUGGESTIONS` | 22 | conversão de LaTeX |
| `UPPERCASE_SENTENCE_START` | 21 | fragmentos e rótulos |
| `VERB_COMMA_CONJUNCTION` | 17 | 6 candidatos reais antes de “mas” |
| `REMOVER_EU_NÓS` | 14 | estilo de primeira pessoa |
| `DEPOIS_DE_APÓS` | 12 | preferência lexical |
| `SENTENCE_WHITESPACE` | 11 | conversão |
| `SPACE_BEFORE_PUNCTUATION2` | 10 | conversão |
| `REDUNDANCY_JUNTO_COM` | 6 | falso positivo (“junto com a tinta”) |
| `CRASE_CONFUSION_2` | 5 | falso positivo (“próximo a Fortaleza”) |
| `GENERAL_VERB_AGREEMENT_ERRORS` | 5 | dialeto “tu” intencional em diálogo |

### 2.2 Triagem

| Grupo | Volume | Interpretação | Ação |
|---|---:|---|---|
| Repetições de início | 207 | anáfora, litania, voz fragmentária | revisar só se soar involuntário |
| Termos de domínio/CIDs | ~70 | `F43.10`, `TEPT`, `ECT`, `Konvulsator`, `Strigiformes`, `transorbital` | não corrigir |
| “Pra” | 49 | registro oral/rural | manter, salvo decisão de voz |
| Espaçamento/checkboxes | ~125 | conversão de LaTeX e formulários | ignorar no texto final |
| “Tu” + verbo | 5 | dialeto intencional | manter |
| Crase “próximo a” | 5 | falso positivo | ignorar |
| “Junto com” | 6 | falso positivo | ignorar |
| Concussão “que ele visse” | 3 | falso positivo | ignorar |
| “Ter vindo/ter deixado” | 2 | falso positivo | ignorar |
| **Vírgula antes de “mas”** | **6** | candidato real | revisar |
| **Grafia “circumferencial”** | **1** | candidato real | corrigir para “circunferencial” |
| **“Paranóide”** | **2+1** | histórico (1979) vs contemporâneo (2026) | decidir por norma/época |

### 2.3 Candidatos reais (para revisão humana)

**Vírgula antes de “mas”:**

| Arquivo | Trecho |
|---|---|
| `cont/CONT-01.tex` | “Como carne que passou do ponto mas ainda não estragou.” |
| `doc/DOC-02.tex` | “indicada em 1948 mas não realizada” |
| `doc/DOC-10.tex` | “ouviu o osso quebrar mas não doeu” |
| `luc/LUC-12.tex` | “Joaquim sabia mas não escreveu” |
| `mem/MEM-04.tex` | “que não era parente mas caminhava junto” |
| `mem/MEM-05.tex` | “mexia a boca mas não saía som” |

**Grafia:**

- `doc/DOC-03.tex`: “hiperpigmentação circumferencial” → norma atual:
  **circunferencial**.
- `doc/DOC-04.tex`, `doc/DOC-07.tex`: “Esquizofrenia Paranóide” — forma histórica
  do laudo de 1979; pode ser mantida como registro de época.
- `luc/LUC-13.tex`: “ideação paranóide” — em contexto contemporâneo, a forma
  corrente é **paranoide**; decidir se a grafia é escolha de voz ou descuido.

## 3. Vale — 95 alertas

| Regra | Alertas | Severidade |
|---|---:|---|
| `PTBR.AdverbiosMente` | 91 | sugestão |
| `PTBR.Muletas` | 3 | aviso |
| `PTBR.Repeticao` | 1 | erro |
| **Total** | **95** | — |

- 40 dos 84 fragmentos tiveram ao menos um alerta; 44 não tiveram.
- A única repetição literal é `mem/MEM-04.tex`: “o não não saía” — provável
  escolha de voz infantil; revisar, não corrigir automaticamente.
- Termos mais frequentes: `completamente` (6), `simplesmente` (6), `fisicamente`
  (3), `exatamente` (3), `novamente` (3), `pessoalmente` (3), `mentalmente` (2).
- Os advérbios em `-mente` são, em grande parte, escolha de ritmo e de voz. O
  relatório serve para revisar densidade, não para eliminar a classe inteira.

## 4. Limites

- LanguageTool e Vale são **diagnósticos**, não aprovadores.
- A conversão de LaTeX para texto plano altera espaçamento, checkboxes e
  posições; os números são do texto convertido.
- Repetições, fragmentos, “pra” e “tu” podem ser escolhas estéticas deliberadas.
- Nenhuma correção foi aplicada ao manuscrito.
- Nenhuma nota 10/10, Qualis ou aceite editorial é declarada.

## 5. Próximo passo editorial

1. Revisar apenas os 6 candidatos de vírgula antes de “mas”.
2. Corrigir “circumferencial” → “circunferencial”.
3. Decidir, com o autor, se “paranóide” é registro histórico ou erro contemporâneo.
4. Revisar a densidade de advérbios em `-mente` nos fragmentos com mais alertas.
5. Rodar novamente LanguageTool/Vale depois das decisões, sem auto-fix em massa.

## 6. Arquivos

| Caminho | Conteúdo |
|---|---|
| `languagetool/matches.jsonl` | 84 resultados completos |
| `languagetool/summary.json` | agregados, amostras e limites |
| `vale/vale.json` | alertas do Vale |
| `vale/summary.json` | agregados por regra e severidade |
| `vale/.vale.ini` e `vale/styles/PTBR/` | configuração e regras PT-BR |
