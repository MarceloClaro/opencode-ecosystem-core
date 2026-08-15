# SPEC-935-R418 — Análise do caso brasileiro em perspectiva comparada (R418)

## Objetivo

Melhorar o manuscrito `ARTIGO_RBEP_SUBMISSAO` adicionando uma análise do
**Brasil em perspectiva comparada internacional**: posição do país na
associação educação terciária–renda documentada no artigo, comparação com
emergentes asiáticos (China, Indonésia, Malásia, Tailândia, Vietnã), Estados
Unidos e Europa Ocidental (Alemanha, França, Reino Unido, Itália, Espanha,
Portugal).

## Justificativa (gaps do diagnóstico R417)

- G3 (LLMICs/estratificação por faixa de renda) e G2 (heterogeneidade
  regional) apontam que o artigo trata apenas a dimensão país agregada. Um
  estudo de caso do Brasil — economia de renda média-alta citada no WDR 2024
  — ancorado nos mesmos dados e proveniência, aumenta a relevância para o
  periódico-alvo (RBEP) sem mudar o desenho observacional nem as alegações
  do artigo.
- A introdução já cita o WDR 2024 e o caso brasileiro; a nova seção fecha a
  ponte entre o resultado agregado e o país do leitor, com a mesma
  linguagem estritamente associativa.

## Análises (todas com números fechados por proveniência)

1. **Perfil atual do Brasil no painel** (último ano com matrícula e PIB):
   matrícula terciária bruta, log-PIB per capita e posição percentual em
   ambas as distribuições.
2. **Trajetória 2000 → último ano**: matrícula terciária (Δ p.p.) e
   crescimento médio anual do PIB per capita.
3. **Comparação por grupo**: emergentes asiáticos, EUA, Europa Ocidental —
   matrícula (último ano), Δ matrícula, crescimento médio anual do PIB pc.
4. **Associação intra-Brasil**: correlação de Spearman em primeiras
   diferenças (matrícula × PIB) apenas para o Brasil.
5. **Resíduo do Brasil na relação de níveis global** (regressão simples
   ln_matrícula ~ ln_PIB): matrícula observada vs prevista.

## Entregáveis

- `scripts/analyze_brasil_comparativo.py` → `outputs/expanded/provenance_r418.json`
  + `outputs/expanded/tabela8_brasil_comparado.csv`
- Nova subseção **4.8 "O caso brasileiro em perspectiva comparada"** (MD + TeX)
  + Tabela 8 (grupos comparativos) + parágrafo na Discussão.
- Testes `tests/test_r418_analise_brasil.py` (gate TDD).

## Critérios de aceitação

1. Cada número citado na seção 4.8 tem entrada em `provenance_r418.json`
   (arredondamento a 3 casas; aceita vírgula decimal).
2. Linguagem estritamente associativa: sem "causa", "efeito", "gera",
   "efetiva", sem termos bloqueados (gate R410/R413).
3. Seção 4.8 antes da Discussão; Tabela 8 com grupos e variáveis.
4. Sem números que contradigam o provenance R412/R416 (0,751; 0,146; 0,073;
   etc.) — os números novos são país-específicos e não substituem os globais.
5. Suíte R408–R418 100% verde; PDF recompilado com 0 Overfull.
6. Ciclo R418 registrado no EvolutionRegistry (formato canônico).

## Fora de escopo

- Qualquer alegação causal sobre o Brasil; inferência com modelos
  econométricos adicionais; alteração da especificação principal (3.2).
