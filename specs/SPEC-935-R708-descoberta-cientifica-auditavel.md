# SPEC-935-R708 — Descoberta científica auditável (dados → inferência → manuscrito)

**Status:** `em implementação`
**Ciclo:** R708
**Data:** 2026-10-07

## 1. Problema

O motor R706 produz *manuscritos*; não produz *descoberta*. Relevância
científica real exige elo auditável dados → desenho → inferência →
validação → resultados prontos para o manuscrito, com poder adequado,
controle de confundidores declarados, correção de múltiplas comparações e
pacote de replicação. Estatística corrobora, não prova (falsificacionismo):
"comprovável" = efeito quantificado + incerteza medida + trilha auditável.

## 2. Objetivo

Pacote `research/discovery/` que executa o elo quantitativo sobre CSV real,
reutilizando `mci/preregistration_protocol.py`, `mci/hypothesis_engine.py`
e `mci/statistical_validator.py` onde existirem, e emitindo seção de
resultados com linguagem calibrada + pacote de replicação.

## 3. Critérios de aceitação

- [ ] AC1 — `design.py`: formaliza PICO/PCC + registra H0/H1 + critério de falsificação por hipótese; poder/tamanho amostral por aproximação normal documentada (sem overclaim de exatidão).
- [ ] AC2 — `analysis.py`: descritiva, t de Welch, Pearson, d de Cohen e IC via scipy/pandas; saídas sempre com n, estatística, p, IC e tamanho de efeito — nunca só p.
- [ ] AC3 — `validate.py`: correção Holm-Bonferroni, checagem de normalidade (Shapiro/normaltest + assimetria/curtose) e relatório de suposições; fail-closed em coluna ausente ou n insuficiente.
- [ ] AC4 — `report.py`: seção de resultados com marcadores [RESULTADO] e bloco obrigatório de limitações; linguagem calibrada ("associado", nunca "prova"/"causa" sem desenho causal).
- [ ] AC5 — `pacote_replicacao()`: grava dados.csv (hash), methods.json e results.json — trilha auditável mínima.
- [ ] AC6 — Testes herméticos `tests/test_r708_descoberta_auditavel.py` com sementes fixas: grupos separados → p<0,05 e d>0,8; grupos idênticos → p>0,05; Holm rejeita o esperado; poder monotônico em n; fail-closed em coluna ausente.
- [ ] AC7 — Demo com dados **sintéticos rotulados** (SNAP-IV-like pré/pós, n=30, seed fixa): pipeline ponta a ponta sem apresentar número sintético como achado.

## 4. Fora de escopo (declarado)

- Inferência causal (DID/IV/RDD), Bayesiana e modelos mistos: Fase B.
- Coleta de dados reais e CEP: pertencem ao pesquisador/instituição.
- Qualquer alegação de "prova", "cura" ou "eficácia" a partir de saída do pacote.
