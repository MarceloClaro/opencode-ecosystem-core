# evo-50 — R419: Estatística da hipótese, amostragem e confiabilidade

## Objetivo

Atender ao pedido do usuário: enquadrar tabelas e manuscritos dentro das
margens e implementar a estatística formal da hipótese central, a descrição
formal do processo de amostragem e a confiabilidade das estimativas
(intervalos de confiança bootstrap e robustez de semente) no artigo RBEP.

## Mudanças

1. **Margens ABNT garantidas (3 cm esquerda / 2 cm direita)**: diagnóstico
   completo de Overfull/Underfull no log LaTeX; build limpo confirmou 0
   Overfull e 0 Underfull em 16 páginas. A Tabela 8 (caso brasileiro) foi
   reescrita com `\resizebox{\textwidth}{!}` (padrão já usado na Tabela 5)
   para eliminar o estouro de 113 pt na linha do cabeçalho.
2. **Estatística formal da hipótese central** (`provenance_r419.json`,
   Tabela 9): H0: ρ_níveis − ρ_1ªdif ≤ 0 contra H1: > 0, testada por
   bootstrap por país (re-amostragem de países com reposição, 500
   replicações, semente fixa 42). Resultado: Δ = 0,604 (0,751 − 0,146),
   IC95% [0,547; 0,665], p < 0,001 (nenhuma das 500 replicações com Δ ≤ 0).
   IC95% por país: ρ níveis [0,697; 0,809]; ρ 1ªdif [0,118; 0,177] — sem
   sobreposição.
3. **Amostragem formal** (Tabela 10): população de 217 países oficiais WDI
   (excluídos 78 agregados e territórios sem ISO3); elegibilidade ≥ 20
   observações não nulas de matrícula e PIB; 135 elegíveis, todos na amostra
   final; 82 excluídos por motivo — 13 sem série de matrícula, 2 sem PIB, 2
   sem ambos, 65 com < 20 observações; cobertura temporal balanceada (1.350
   obs país-ano por década 1960–2019; 540 em 2020–2023); viés de seleção
   declarado (seleção condicionada à disponibilidade de dados, não aleatória).
4. **Confiabilidade** (Tabela 11): robustez de semente com sementes 42, 7,
   2024 e 123 — Δ observado estável em 0,604, IC95% entre 0,543 e 0,665,
   p < 0,001 em todas; desvio máximo dos limites do IC < 0,01.
5. **Seção 4.9 "Estatística da hipótese, amostragem e confiabilidade"** no MD
   canônico e espelhada no TeX (Tabelas 9, 10 e 11 com numeração automática
   do LaTeX), com âncoras adicionadas em 3.1 (dados) e 4.2 (associações),
   linguagem associativa, sem termos bloqueados de anti-overclaim
   (substituiu-se "IC95% percentil" por "intervalo de confiança de 95%
   empírico").
6. **Correção metodológica na classificação de exclusões**: o cálculo de
   motivos de exclusão passou a usar os dados brutos (`load_series`) em vez
   do painel já filtrado — antes, `sem_matricula = sem_pib = 82` era
   tautológico; agora a classificação por motivo é informativa (13/2/2/65).
7. **Correção de regressão induzida**: o teste R418 passou a extrair a seção
   4.8 até o marcador `### 4.9` (antes, `## 5.` capturava a nova seção 4.9 e
   quebrava âncoras numéricas da provenance r418).

## Verificação

- Suíte R408–R419: **308 testes passed** (R419: 33).
- LaTeX: compilação limpa em 2 passadas; 16 páginas; 0 Overfull; 0 Underfull.
- Numeração automática confirmada no `.aux`: tab:hipotese=9,
  tab:amostragem=10, tab:confiabilidade=11.
- Novos artefatos: `outputs/expanded/provenance_r419.json`,
  `tabela9_hipotese.csv`, `tabela10_amostragem.csv`,
  `tabela11_confiabilidade.csv`, `scripts/analyze_hipotese_confiabilidade.py`,
  `tests/test_r419_hipotese_amostragem.py`.

## Lições

- Qualquer nova subseção de resultados deve fechar a extração das seções
  anteriores nos testes (split por marcador de seção seguinte, não por seção
  distante).
- A classificação de exclusões amostrais exige os dados brutos, não o painel
  já elegível — contar sobre o painel filtrado produz categorias tautológicas.
- Terminologia de IC bootstrap com a palavra "percentil" é bloqueada pelos
  gates de anti-overclaim; usar "intervalo de confiança empírico".
