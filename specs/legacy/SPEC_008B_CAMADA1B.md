# SPEC-008-B: Domain Shift Detection — Camada 1B
# Projeto: Antiprojeto UFC — PPGTE/UFC
# Extensão da Triangulação Anti-Circularidade
# Versão: 1.0 | Data: 2026-05-30

## Objetivo
Detectar e quantificar domain shift em corpora multi-institucionais,
distinguindo "padrao real que evoluiu" de "mudanca de fonte que
invalida a comparacao temporal".

## Quando Aplicar
- Corpus com campo `instituicao` nos metadados
- Multiplas instituicoes no mesmo periodo
- Nova instituicao entra apenas em T2 (ex: TRF-6 criado em 2024)

## Artefatos
- Script: `artigo/evaluations/domain_shift_audit.py` (725 linhas, seed=42)
- Output: `artigo/evaluations/domain_shift_audit_output.json`
- Documento: `artigo/jaccard_domain_shift_audit.pdf` (27 laudas, 25 refs DOI)
- Skill: `~/.config/opencode/skills/system/domain-shift-camada1b/SKILL.md`

## Limiares Jaccard (corpus simulado 5 instituições jurídicas)
- Moderado (P95): 0.215 — Publicação com ressalva
- Estrito (P99): 0.279 — Publicação científica
- Permissivo (μ+σ): 0.135 — Triagem inicial

⚠️ NÃO use limiar fixo 0.70 da SPEC-008 original em corpora multi-inst.

## Referências Principais
1. Jaccard, P. (1901). DOI: 10.5169/seals-266450
2. Efron, B. (1979). Bootstrap Methods. DOI: 10.1214/aos/1176344552
3. Hendrycks & Gimpel (2017). OOD Detection. DOI: 10.48550/arxiv.1610.02136
4. Ben-David et al. (2010). Learning from Different Domains. DOI: 10.1007/s10994-009-5152-4
5. Laranjeira, M.C. (2026). SPEC-008 Triangulação Anti-Circularidade.

## Dependências
- SPEC-008 (Triangulação Anti-Circularidade)
- INTEGRIDADE.md (Princípios de Integridade)
- Python 3.8+, numpy
