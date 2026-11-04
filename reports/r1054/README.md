# R1054 — automação assistida, periódico real e validação com meta-análise

Data: 2026-11-04. Frente autorizada: extração automática de efeitos, decisão
automática de risco de viés/GRADE, regras de periódico real, submissão
automática, validação externa/aceite/publicação e avaliação com dados reais de
uma meta-análise publicada.

A implementação separa **automação auditável** de **autoridade institucional**.
O Core prepara, confere e registra; não emite aceite, não publica e não substitui
um painel GRADE/RoB.

## 1. Extração automática de efeitos

`scientific_lab/effect_extraction.py`:

- lê texto integral já indexado;
- reconhece OR/RR/HR/SMD/MD/d/g com IC, SE ou p;
- converte OR/RR/HR para log;
- deriva SE de IC ou p;
- marca candidatos incompletos;
- grava `04_analysis/auto-effect-candidates.json`;
- grava `04_analysis/auto-quantitative-draft.json` com status `automated_draft`;
- exige `human_confirmation=true`.

Limite: regex não lê tabelas, figuras ou PDF sem camada textual.

## 2. Risco de viés e GRADE automáticos

`scientific_lab/rob_grade_auto.py`:

- regras explícitas para randomização, desvios, dados faltantes, mensuração e
  seleção;
- sugestões com razões e `authoritative=false`;
- GRADE por rebaixamento com razões;
- exige `human_confirmation=true`;
- grava `04_analysis/auto-rob-grade.json` e `quantitative-auto.json`.

Limite: heurística, não RoB 2/ROBINS-I/GRADE de painel.

## 3. Perfil real de periódico: PLOS ONE

`scientific_lab/journal_profiles.py`:

| Regra | Valor |
|---|---|
| Idioma | inglês |
| Resumo | até 300 palavras, sem citações |
| Título | até 250 caracteres |
| Referências | Vancouver/ICMJE, numéricas |
| Estrutura | Title page, Abstract, Introduction, Materials and Methods, Results, Discussion, Acknowledgments, References |
| Figuras | arquivos separados |
| Declarações | financiamento, conflitos, dados, autoria, ORCID, ética |
| Fonte | https://journals.plos.org/plosone/s/submission-guidelines |
| Verificado em | 2026-11-04 |

O perfil é uma transcrição parcial e datada. O manuscrito em português do
pipeline é corretamente marcado como `blocked`; um manuscrito em inglês com as
seções e citações numéricas fica `pending_human` por causa das declarações.

## 4. Submissão automática fail-closed

`scientific_lab/submission_portal.py`:

- preflight de pacote, checklist, declarações e render;
- exige `confirm=true`;
- exige autorização com hash do manuscrito;
- exige backend injetado;
- sem backend, retorna `no_submission_backend_configured`;
- grava `submission-attempt.json`.

O Core **não possui** portal ou credencial embutidos. Nenhuma submissão real foi
feita.

## 5. Validação externa, aceite editorial e publicação

`scientific_lab/external_validation.py`:

- anexa validação externa independente com hash do manuscrito;
- anexa carta de aceite com hash da carta;
- exige autorização do autor;
- `publication_gate` só fica `cleared_for_publication` com os três artefatos
  coerentes;
- `publication_performed=false` sempre;
- não emite aceite nem publica.

Os testes usam artefatos fictícios e deixam claro que o gate verifica, não cria,
a decisão institucional.

## 6. Validação real com meta-análise publicada

Dataset: BCG, 13 ensaios, Colditz et al. 1994, distribuído no `metafor` e em
cópias públicas em CSV.

| Métrica | Core (REML) | Referência pública REML | Diferença |
|---|---|---|---|
| k | 13 | 13 | 0 |
| OR | **0,474649896** | 0,474649913 | 1,7e-8 |
| tau² | **0,337772471** | 0,337772045 | 4,3e-7 |
| Q | **163,164915** | 163,164915 | 1,1e-13 |
| I² padrão | **92,6455%** | 92,6455% | 0 |
| I² publicado | 92,6455% | 92,0727% | 0,5728 p.p. |

O I² publicado na fonte não é exatamente `(Q-df)/Q` com Q=163,1649 e df=12; a
fórmula padrão resulta em 92,6455%. A discrepância está registrada, não
escondida.

Referência: `reports/r1054/real-meta-benchmark.json`.
Fonte: `reports/r1054/SOURCE.md`.

## Validação

| Verificação | Resultado |
|---|---|
| Testes R1054 | **21 passed** |
| R1051–R1054 | **63 passed** |
| Regressão R1033–R1054 | **410 passed, 1 skipped** |
| Guard Remotion | **11 casos, ok** |
| `doctor` | **healthy 22/22** |
| Submissão real | **nenhuma** |
| Aceite editorial real | **nenhum** |
| Publicação | **nenhuma** |

## Limites

- Extração por regex não lê tabelas, figuras ou PDF sem camada textual.
- RoB/GRADE automáticos são sugestões heurísticas, não julgamento final.
- Perfil PLOS ONE é parcial, datado e não certifica conformidade.
- Submissão real exige backend/credenciais que o Core não possui.
- Validação externa e aceite precisam de artefatos institucionais reais.
- O benchmark BCG é numérico e usa reanálise pública, não o texto de 1994.
- Nada foi submetido, aceito ou publicado.
