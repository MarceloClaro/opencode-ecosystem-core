# SPEC-935-R425 — Pacote final de submissão RBEP

**Estado:** Implementado
**Data:** 2026-08-15
**Objetivo:** Gerar, por script, um pacote ZIP organizado e auditável com
todos os artefatos necessários à submissão humana do manuscrito na Revista
Brasileira de Estudos Pedagógicos (RBEP/INEP).

## Critérios de aceitação

1. `scripts/empacotar_submissao.py` (offline, sem rede) gera
   `outputs/submission/ARTIGO_RBEP_SUBMISSAO_submissao_<DATA>.zip`.
2. O ZIP contém, no mínimo:
   - `01_manuscrito/ARTIGO_RBEP_SUBMISSAO.docx` (16 tabelas, autoria+ORCID)
   - `01_manuscrito/ARTIGO_RBEP_SUBMISSAO.pdf` (20 páginas, 0 Overfull)
   - `01_manuscrito/ARTIGO_RBEP_SUBMISSAO.md` (canônico)
   - `02_carta/CARTA_AO_EDITOR.md` (autor+ORCID, sem overclaim)
   - `03_revisao/peer_review_r422.md` (relatório do blind peer review)
   - `04_dados/provenance_*.json` (todos os JSONs de proveniência R412–R423)
   - `README_SUBMISSAO.md` (instruções, checklist, notas)
   - `MANIFEST_SUBMISSAO.json` (sha256 de cada arquivo + data)
3. O manifest SHA-256 é verificado na leitura (o teste reabre o ZIP e confere
   hashes de pelo menos 5 arquivos).
4. Nenhum arquivo temporário (`*.aux`, `*.log`, `__pycache__`) entra no ZIP.
5. Testes: `tests/test_r425_pacote_submissao.py` (≥ 5 testes) na suíte R408–R425.
6. EvolutionRegistry: ciclo R425 registrado; evo-56 documentado.

## Fora de escopo

- Submissão de fato no portal da RBEP (ação humana).
- Conferência editorial do ID 12 (resumo em espanhol) — permanece humana.
- Alteração de conteúdo do manuscrito.

## Verificação

- `python3 scripts/empacotar_submissao.py`
- `python3 -m pytest tests/test_r425_pacote_submissao.py -q`
- Suíte R408–R425 completa sem regressões.
