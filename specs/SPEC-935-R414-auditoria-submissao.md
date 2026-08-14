# SPEC-935-R414 — Auditoria de submissão: scanners, consistência e correção de inconsistências

- **Ciclo**: R414
- **Data**: 2026-08-13
- **Status**: em implementação
- **Dependência**: R410–R413 (artigo RBEP, LaTeX, painel expandido, canais)

## Contexto

O usuário solicitou: "avalie com os scanners busque gaps, inconsistência e
redundancias, contradições e corrija para submissão". A auditoria combinou
scanners do ecossistema com verificação programática de consistência entre
o manuscrito (MD), o LaTeX, as proveniências e o registro evolutivo.

## Achados da auditoria

1. **Contradição real (4.5 vs 3.2c)**: a seção 4.5 afirma "matrícula
   terciária defasada em cinco anos", mas a especificação implementada
   (3.2c e `analyze_expanded.py`) usa **log-PIB per capita defasado** como
   regressor e matrícula como variável dependente. A Tabela 5 e o resumo
   usam a forma correta. **Corrigir 4.5.**
2. **Imprecisão (3.1)**: "135 países (mais de 20 países)" — resquício do
   R409 (7 países); o critério de amostra é "≥ 20 observações por país",
   descrito na frase seguinte. **Remover o parêntese.**
3. **Gap real**: a análise de canais (R413) não está no artigo. **Adicionar
   seção 4.7 "Canais associativos"** com números de `provenance_r413.json`,
   em linguagem associativa, sem alterar o resumo (preserva R410).
4. **Falsificabilidade implícita (recomendação scanner)**: explicitar na
   seção 3.2a os critérios de invalidação empírica (o que refutaria a
   leitura de dominância de diferenças permanentes).
5. **Bug no EvolutionRegistry (causado no R413)**: ciclo R413 gravado com
   chaves fora do formato canônico (`id/data/titulo/...` em vez de
   `round_id/objective/changes/score/lessons/timestamp`) derrubava o
   carregamento de TODOS os ciclos via `except` silencioso (0/230).
   **Corrigir o R413 e adicionar guarda de regressão.**
6. **Redundâncias**: nenhuma sentença repetida literalmente (n-gramas);
   tabelas descritivas com números sem proveniência numérica individual são
   cobertas por `tabela1_descr_expandido.csv` (sem mudança).

## Correções a implementar

1. MD `ARTIGO_RBEP_SUBMISSAO.md`:
   - 3.1: "135 países (mais de 20 países)" → "135 países".
   - 3.2a: adicionar critério de invalidação empírica.
   - 4.5: "matrícula terciária defasada em cinco anos" → "log do PIB per
     capita defasado em cinco anos".
   - Nova seção **4.7 Canais associativos da educação terciária** (números
     de provenance_r413.json; tabela; sem termos causais).
   - 5. Discussão: parágrafo conectando os canais ao painel principal.
2. LaTeX `latex/ARTIGO_RBEP_SUBMISSAO.tex`: mesmas mudanças (R411 exige
   identidade numérica MD↔TeX); recompilar PDF.
3. **Tabelas dentro das margens** (pedido do usuário): Tabela 1 (nomes de
   variáveis longos, overfull 9–15pt) → colunas `p{}` 3.9cm/4.4cm; Tabela 5
   (especificação longa, overfull 230pt) → `\resizebox{\textwidth}{!}`
   (pacote `graphicx`); Tabela 7 → primeira coluna `p{5.2cm}` com quebra.
   Guarda de regressão: `test_log_sem_overfull` (zero Overfull no log).
4. `evolution/cycles.json`: R413 convertido para formato canônico (feito).
5. Testes `tests/test_r414_auditoria_submissao.py` (RED→GREEN):
   - Guarda: todos os ciclos carregam; formato canônico; doctor evolution ok.
   - Artigo: ausência de "matrícula terciária defasada" e "(mais de 20
     países)"; presença da seção 4.7; números da 4.7 com proveniência
     r413; anti-overclaim na 4.7; critério de invalidação presente.
   - TeX: números da 4.7 presentes; PDF recompilado; log sem Overfull.
6. Rodar suíte R408–R414 completa.

## Critérios de aceitação

- Suíte R408–R414 **100% GREEN** (R414 novo; R410–R413 sem regressão).
- `doctor` com evolution_registry pass.
- PDF recompilado sem erros.
- Nenhum termo causal nas seções novas; nenhum número novo no resumo.

## Não escopo

- Não altera números/resultados das seções 1–6 existentes (exceto os dois
  erros textuais acima).
- Não adiciona alegação de Qualis ou validação externa.
