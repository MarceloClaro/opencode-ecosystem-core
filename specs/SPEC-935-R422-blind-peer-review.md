# SPEC-935-R422 — Blind Peer Review emulado do manuscrito final (RBEP)

## Objetivo

Submeter o manuscrito final de submissão
(`academic/papers/arm_education_audit/ARTIGO_RBEP_SUBMISSAO.md`, versão
R410–R421) a um **blind peer review emulado** de alta severidade (Reviewers
1, 2 e 3), antes da revisão humana e decisão de submissão à RBEP/INEP.

O review deve cobrir o manuscrito **completo**, incluindo as seções
adicionadas nos ciclos recentes: seção 4.8 (caso brasileiro comparado,
R418), seção 4.9 (teste formal da hipótese, amostragem e confiabilidade,
R419), Apêndice A (glossário de símbolos, códigos e abreviaturas, R420) e
o artefato DOCX (R421).

## Escopo

- Fonte única de verdade: `ARTIGO_RBEP_SUBMISSAO.md` (canônico).
- Cruzamento com `latex/ARTIGO_RBEP_SUBMISSAO.tex` e PDF (19 páginas) e
  `outputs/docx/ARTIGO_RBEP_SUBMISSAO.docx`.
- Números críticos a conferir: ρ_níveis 0,751 (IC95% [0,697; 0,809]),
  ρ_1ªdif 0,146 (IC95% [0,118; 0,177]), Δ = 0,604 (IC95% [0,547; 0,665],
  p < 0,001, 500 replicações bootstrap por país), Brasil 43,834 → 61,000
  (+17,166 p.p.), amostra 135/217 países, 8.640 observações país-ano.

## Critérios de aceitação

1. Três revisores emulados (R1 = econometria de painel, R2 = economia da
   educação, R3 = metodologia/rigor de submissão) produzem pareceres
   independentes com severidade (crítico/menor/informativo), localização
   exata (seção/linha/tabela) e recomendação concreta.
2. Cada parecer responde explicitamente: (a) pergunta de pesquisa é
   respondida? (b) inferência é válida? (c) há alegação sem suporte?
   (d) os números do texto batem com as tabelas? (e) o apêndice é útil?
3. Achados críticos = bloqueio; menores = recomendações; nenhum número do
   texto pode divergir das tabelas sem flag.
4. Registro dos achados em `outputs/review/peer_review_r422.md` (ou
   similar) com tabela de triagem: id, severidade, seção, problema,
   recomendação, resolução (sim/não/aplicável).
5. Ciclo SDD/TDD: testes novos em `tests/test_r422_peer_review.py`
   verificam que o relatório existe, tem 3 pareceres e a triagem cobre os
   achados críticos com resolução.
6. Anti-overclaim: o relatório NÃO pode afirmar "aprovado", "validado" ou
   "pronto para publicação" — o gate final é humano.

## Não escopo

- Reexecutar análises empíricas (R408–R419 já fecham proveniência).
- Corrigir achados críticos neste ciclo (será ciclo posterior, se houver).
- Avaliação de adequação a Qualis A1 (vedada sem validação externa).

## Verificação

- Suíte R408–R422 verde (334 + novos).
- Doctor 10/12 pass, 0 failed.
- Registro do ciclo R422 no EvolutionRegistry e evo-53.
