---
spec_id: SPEC-935-R267
title: Oito scanners literários rigorosos para análise, produção e estudo de obras
component: scanners/literary_scanners.py
status: verified
test_file: tests/test_r267_literary_scanners.py
---

# SPEC-935-R267 — Scanners Literários de Alto Rigor

## Objetivo

Criar um conjunto de **8 scanners exclusivamente literários**, com visões distintas, para complementar scanners científicos/ecossistêmicos que não são calibrados para romance, poesia, narrativa, ficção documental, estudo literário, comportamento leitor, teorias literárias, inovação formal e produção editorial.

## Scanners previstos

1. **NarrativeArchitectureScanner** — arquitetura narrativa, enredo, partes, tensão, temporalidade e coerência estrutural.
2. **CharacterPsychologyScanner** — personagens, agência, desejo, conflito, transformação e verossimilhança psicológica.
3. **StyleVoiceScanner** — estilo, voz, léxico, ritmo, repetição, variedade sintática e assinatura discursiva.
4. **SymbolicImageryScanner** — símbolos, imagens recorrentes, motivos, campos sensoriais e densidade metafórica.
5. **IntertextualTheoryScanner** — diálogos teóricos, paratextos, gêneros, tradição literária, metaficção e fundamentos interpretativos.
6. **ReaderResponseScanner** — comportamento do leitor, participação, imersão, instruções, rotas, pactos e efeitos de leitura.
7. **EthicalRepresentationScanner** — ética da representação, trauma, violência, alteridade, risco de exploração e advertências.
8. **LiteraryInnovationScanner** — inovação formal, híbridos de gênero, hipertexto impresso, experimentação material e contribuição potencial.

## Saídas esperadas

- Novo módulo `scanners/literary_scanners.py`.
- API pública com:
  - classe-base de resultado;
  - 8 classes de scanner;
  - função `run_literary_scanner_suite(text, metadata=None)`.
- Integração exportável em `scanners/__init__.py`.
- Testes em `tests/test_r267_literary_scanners.py`.

## Critérios de aceitação

1. Existem 8 scanners com nomes e escopos distintos.
2. Cada scanner retorna dicionário serializável com `scanner_id`, `score`, `grade`, `evidence`, `warnings`, `recommendations` e `dimensions`.
3. Scores são normalizados de 0 a 100.
4. Cada scanner possui pelo menos 3 dimensões avaliativas próprias.
5. A suíte agregadora retorna os 8 resultados e `literary_excellence_score`.
6. A suíte explicita `domain: literary` e `overclaim_guard`.
7. Nenhum scanner depende de LLM ou rede externa; a execução é determinística.
8. Texto vazio não quebra a execução e produz recomendações de insuficiência.
9. Texto literário rico em fragmentos, personagens, símbolos e metaleitura pontua melhor que texto mínimo.
10. Os scanners incluem recomendações acionáveis para produção/estudo literário.
11. Testes direcionados passam.
12. O doctor final permanece sem falhas críticas novas.

## Não escopo

- Não substituir crítica literária humana.
- Não declarar qualidade canônica, aprovação acadêmica ou validação externa.
- Não aplicar métricas de falsificabilidade científica a textos literários.

## Resultado — 2026-07-27

Implementado:

- `scanners/literary_scanners.py` com 8 scanners literários determinísticos.
- Exportação pública em `scanners/__init__.py`.
- Integração automática no `DiagnosticPipeline` para `domain="literary"`, `"literatura"`, `"fiction"`, `"ficcao"`, `"ficção"` e `"editorial_literary"`.
- Integração opcional via `include_literary=True`.
- Listagem/status resumido no CLI `python3 -m scanners.cli`.
- Ferramenta MCP futura `literary_scanner_suite` no servidor de scanners.
- Testes `tests/test_r267_literary_scanners.py`.

Validações:

- `pytest -q tests/test_r267_literary_scanners.py` → 8 passed.
- Regressão de scanners existentes (`test_legal_impact_scanner`, `test_r223_scientific_reasoning_scanner`, `test_r224_rigorous_scanners_pipeline`) → 21 passed no lote combinado.
- Smoke do MCP síncrono: `literary_scanner_suite` aparece em `get_tools()` e retorna 8 scanners.

Observação anti-overclaim: os scanners literários retornam índice exploratório e recomendações acionáveis, mas explicitam `overclaim_guard`: não substituem crítica literária humana, recepção especializada, comparação de corpus ou validação externa.
