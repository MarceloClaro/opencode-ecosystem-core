---
spec_id: SPEC-1054
title: Automação assistida, perfil real de periódico, gate de publicação e validação com meta-análise publicada
version: 1.0.0
status: green
test_file: tests/test_r1054_real_meta.py, tests/test_r1054_journal_profile.py, tests/test_r1054_publication_gate.py, tests/test_r1054_submission_portal.py, tests/test_r1054_effect_extraction.py, tests/test_r1054_rob_grade.py
---

# SPEC-1054 — automação com rastro, não autoridade automática

## Problema

O R1053 entregou síntese quantitativa e submissão human-gated. O operador
autorizou avançar para:

- extração automática de efeitos de PDFs;
- decisão automática de risco de viés/GRADE;
- regras específicas de um periódico real;
- submissão automática;
- validação externa, aceite editorial ou publicação;
- avaliação com dados reais de uma meta-análise publicada.

Alguns desses itens são **atos institucionais**, não funções de software. O Core
pode preparar, conferir e registrar, mas não pode emitir aceite, publicar ou
substituir um painel GRADE/RoB. A implementação separa automação auditável de
autoridade científica.

## Escopo

### 1. Extração automática de efeitos

`effect_extraction.py`:

- lê texto integral já indexado;
- reconhece OR/RR/HR/SMD/MD/d/g com IC, SE ou p;
- converte OR/RR/HR para escala log;
- deriva SE de IC ou p;
- marca candidatos incompletos;
- gera `04_analysis/auto-effect-candidates.json`;
- gera `04_analysis/auto-quantitative-draft.json` como `automated_draft`;
- exige `human_confirmation=true` para gerar o rascunho.

### 2. Risco de viés e GRADE automáticos

`rob_grade_auto.py`:

- aplica regras explícitas de randomização, desvios, dados faltantes,
  mensuração e seleção;
- gera sugestões com razões e `authoritative=false`;
- gera GRADE por rebaixamento com razões;
- exige `human_confirmation=true`;
- grava `04_analysis/auto-rob-grade.json` e `quantitative-auto.json`.

### 3. Perfil real de periódico

`journal_profiles.py`:

- perfil **PLOS ONE** transcrito das diretrizes públicas em 2026-11-04;
- idioma inglês, resumo ≤ 300 palavras, título ≤ 250 caracteres;
- Vancouver/ICMJE, seções obrigatórias, figuras separadas, declarações;
- checagem objetiva com `pass`/`fail`/`pending_human`;
- `journal-compliance.json` e checklist específico;
- fonte e data de verificação registradas.

### 4. Submissão automática fail-closed

`submission_portal.py`:

- preflight de pacote, checklist, declarações e render;
- exige `confirm=true`, autorização com hash do manuscrito e backend injetado;
- sem backend, retorna `no_submission_backend_configured`;
- nenhum portal ou credencial embutido;
- grava `submission-attempt.json`;
- submissão não é aceite nem publicação.

### 5. Validação externa e aceite editorial

`external_validation.py`:

- anexa artefato externo independente com hash do manuscrito;
- anexa carta de aceite com hash da carta;
- exige autorização do autor;
- `publication_gate` só fica `cleared_for_publication` com os três artefatos
  coerentes;
- `publication_performed=false` sempre;
- não emite aceite nem publica.

### 6. Validação com meta-análise publicada

`real_benchmark.py`:

- dataset BCG (13 ensaios; Colditz et al. 1994);
- log OR e SE por estudo;
- REML do Core comparado a uma reanálise pública REML;
- checagens de OR, IC, tau², Q, I² e método;
- discrepância do I² publicado registrada;
- `reports/r1054/real-meta-benchmark.json`.

## Critérios de aceitação

1. Extração de OR com IC gera efeito log e SE correto.
2. Extração de SMD com IC e OR com p gera SE derivado.
3. Efeito sem SE/IC/p fica `incomplete`.
4. Rascunho automático exige humano, medida única e ≥ 2 estudos.
5. O resultado quantitativo preserva `extraction` e `automated_extraction=true`.
6. RoB automático produz domínios, razões, `authoritative=false`.
7. GRADE automático exige humano e razão para julgamento sério.
8. Perfil PLOS ONE tem fonte, data, idioma, limites e seções.
9. Manuscrito em português é `blocked` no PLOS ONE; inglês compatível fica
   `pending_human`.
10. Preflight bloqueia declarações/checklist pendentes.
11. Submissão exige confirmação, autorização e backend; sem backend, bloqueia.
12. Gate de publicação bloqueia artefatos ausentes ou hash divergente.
13. Gate só libera com validação externa `passed`, aceite `accepted` e
    autorização vinculada ao manuscrito.
14. BCG REML replica a referência dentro das tolerâncias.
15. Nenhuma submissão, aceite ou publicação real é executada nos testes.
16. CLI expõe `benchmark-meta`, `extract-effects`, `auto-rob-grade`,
    `publication-gate` e `submit`.

## RED/GREEN

RED: 21 testes novos falharam antes dos módulos e da integração.

GREEN: os seis arquivos de teste R1054 passam; R1051–R1054 ficam em
**63 passed**; a regressão focada R1033–R1054 fica em **410 passed, 1 skipped**.

## Evidência de execução

- Testes R1054: **21 passed**.
- R1051+R1052+R1053+R1054: **63 passed**.
- Regressão focada R1033–R1054: **410 passed, 1 skipped**.
- BCG REML: status **pass**, OR **0,47465**, tau² **0,33777**, Q **163,1649**,
  I² padrão **92,6455%**.
- I² publicado **92,0727%** difere **0,5728 p.p.** da fórmula (Q-df)/Q; a
  discrepância está registrada.
- `doctor`: **healthy 22/22**; guard Remotion: **11 casos, ok**.
- Nenhuma submissão, aceite ou publicação real.

## Limitações

- Extração por regex não lê tabelas, figuras ou PDF sem camada textual.
- RoB/GRADE automáticos são heurísticas, não RoB 2/ROBINS-I/GRADE de painel.
- O perfil PLOS ONE é uma transcrição parcial e datada, não certificação.
- Submissão real exige backend/credenciais que o Core não possui.
- Validação externa e aceite precisam ser artefatos institucionais reais.
- O benchmark BCG é numérico e usa uma reanálise pública, não o texto de 1994.
- Nada foi submetido ou publicado.
