# evo-48 — R414: Auditoria de submissão (scanners + consistência + correções)

## Objetivo

Auditar o manuscrito RBEP para submissão com os scanners do ecossistema,
buscar gaps, inconsistências, redundâncias e contradições, e corrigir.

## Mudanças

1. **Contradição corrigida (4.5 vs 3.2c)**: "matrícula terciária defasada em
   cinco anos" → "log do PIB per capita defasado em cinco anos como
   regressor" (MD + TeX). A especificação implementada usa PIB defasado;
   a matrícula é a variável dependente.
2. **Imprecisão removida (3.1)**: "135 países (mais de 20 países)" → "135
   países" (resquício do R409; o critério é ≥ 20 observações por país).
3. **Falsificabilidade explícita (3.2a)**: critérios de invalidação
   pré-definidos (se FD ≈ níveis, leitura de diferenças permanentes é
   refutada; se FE estável e distinto de zero, leitura de não
   discernibilidade é refutada) — MD + TeX.
4. **Gap fechado**: seção **4.7 "Canais associativos da educação terciária"**
   com números fechados por `provenance_r413.json` (etapas 0,701→0,358→0,105;
   parcial saúde 0,684; canais FE 0,535/−0,104/0,836; interação WGI 0,054,
   p = 0,005) + Tabela 7 + parágrafo na Discussão — MD + TeX, PDF recompilado.
5. **Guarda de regressão EvolutionRegistry**: R413 gravado fora do formato
   canônico derrubava o carregamento de todos os ciclos via `except`
   silencioso (0/230); R413 convertido para `round_id/objective/changes/
   score/lessons/timestamp` (230/230; total 1418,54; next R414) e novos
   testes garantem formato + carregamento 100%.
6. **Refinamento anti-overclaim nos testes R410/R411/R412**: "causa"/"prova"
   como substring bloqueavam "mecanismos causais" (negação explícita) e
   "provavelmente" (incerteza); refinado para word-boundary (alinhado ao
   gate do R413). Intenção preservada: "causa" como palavra continua
   bloqueado; "prova que" literal continua bloqueado.
7. **Tabelas dentro das margens** (pedido do usuário): Tabela 1 (nomes de
   variáveis longos, overfull 9–15pt) → colunas `p{3.9cm}`/`p{4.4cm}` com
   `\raggedright`; Tabela 5 (especificação longa, overfull 230pt) →
   `\resizebox{\textwidth}{!}` + pacote `graphicx`; Tabela 7 (no limite) →
   primeira coluna `p{5.2cm}` com quebra de linha. Log final: **zero
   Overfull**. Guarda de regressão `test_log_sem_overfull`.

## Evidências de validação

- Suíte R408–R414: **247/247 passed** (R414: 23; R410–R413 sem regressão).
- `doctor`: 10/12 pass, 0 failed (2 warns pré-existentes: loop_specs, scihub-cli).
- PDF recompilado: 12 páginas, **0 Overfull no log** (Tabelas 1, 5 e 7
  enquadradas nas margens ABNT: esquerda 3cm, direita 2cm).
- Scanners (heurísticos, sobre o corpo atualizado):
  - `scientific_reasoning_scan` (seção 3.2): SRI 20→**45**, falsif. 50→**75**,
    status low_rigor→**moderate_rigor**; sem falácias.
  - `super_rigor_audit` (corpo): excellence 42.5→**57.5**, SRI 35→**65**,
    methodology 25→**75**, falácias [], recomendação positiva.
- Sem redundâncias: nenhuma sentença repetida literalmente (verificação
  programática).

## Lições registradas

1. Testes anti-overclaim com substring ingênuo geram falsos positivos
   ("causa" ⊂ "causais"; "prova" ⊂ "provavelmente"); usar word-boundary e
   permitir adjetivação em negação explícita.
2. A gravação de ciclos fora do formato canônico derruba o EvolutionRegistry
   inteiro silenciosamente (except amplo em `_load`); guarda de formato +
   contagem mínima são obrigatórias.
3. Scanners de rigor são heurísticos: recomendações estruturais (ex. grupo de
   controle) podem ser inexistentes por desenho (observacional); registrar a
   decisão em vez de inflar o texto.
4. Auditoria programática de números MD vs provenance gera muitos falsos
   positivos (cabeçalhos de seção, DOIs); filtrar por regex e comparar
   arredondamento a 3 casas.
5. Tabelas longas em colunas `l` estouram as margens ABNT (Tabela 5:
   230pt); usar `p{}` com `\raggedright` para quebra e `\resizebox` para
   casos extremos (exige `graphicx`); verificar `Overfull` no log como
   guarda automática.

## Pendência humana

- Revisão humana do texto das seções 3.2a/4.7 e da Tabela 7 antes da
  submissão efetiva à RBEP.
- Submissão à revista permanece ação humana (fora do escopo do ecossistema).
