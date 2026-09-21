# SPEC-971: Integração da CLI Gemini Notebook (`nlm`) no doctor

**Round**: R548 (evolution registry)
**Data**: 2026-09-21
**Status**: Implementado — 7 testes TDD verdes
**Score**: 1.0 (gate SDD pass; regressão completa verde)

## Objetivo

Integrar a CLI `nlm` (pacote PyPI `notebooklm-mcp-cli`, do projeto
`jacob-bd/gemini-notebook-mcp-cli` — MIT, v0.11.6) ao monitoramento de CLIs
externas de primeira classe do ecossistema (`EXTERNAL_CLIS` do `doctor.py`),
como 9ª ferramenta opt-in, de modo que:

1. O `doctor` reconheça a presença/ausência do binário `nlm` no PATH
   (mesmo tratamento `warn`-nunca-`fail` das demais CLIs opcionais).
2. A sugestão de instalação exata (`pip install notebooklm-mcp-cli`)
   apareça no detalhe do check e no helpdesk quando o binário estiver ausente.
3. **Não** haja acoplamento ao pipeline automático de pesquisa/publicação:
   APIs internas não documentadas do NotebookLM + autenticação por cookies
   tornam a ferramenta instável — uso exclusivo do operador (veredito
   ADOTAR-opt-in da lição R474).

## Contexto

- Projeto upstream real e ativo: 6.126★ / 932 forks, licença MIT,
  atualizado em 2026-09-21; PyPI `notebooklm-mcp-cli` v0.11.6
  (score 7.83 — saúde 9.5, compatibilidade 9.0; Beta).
- Capacidades: notebooks, sources (URL/Drive/arquivo), queries
  cross-notebook, pesquisa web/Drive, Studio (áudio/vídeo/slides/
  infográficos), pipelines, tags, batches, share; servidor MCP com 43 tools.
- Decisão estratégica: **metacognição não é afetada** (MetaBus/Trust/
  Reflexion permanecem como estão); benefício concentrado na camada de
  produto/pesquisa do operador.

## Critérios de aceitação

- CA1: `nlm` presente em `marceloclaro.doctor.EXTERNAL_CLIS` com comando
  exato `pip install notebooklm-mcp-cli`.
- CA2: `_check_external_clis()` retorna `warn` (nunca `fail`) com sugestão
  do nlm quando o binário está ausente; `pass` citando o nlm quando presente.
- CA3: ausência isolada do nlm produz detail `1/N` com apenas a sugestão do
  nlm.
- CA4: `helpdesk` inclui o nlm na sugestão de CLIs ausentes.
- CA5: regressão completa das suítes que tocam o doctor (r116, r120, r473,
  r212, runai, r547) permanece verde.

## Arquivos tocados

- `marceloclaro/doctor.py` — entrada em `EXTERNAL_CLIS` + docstring.
- `marceloclaro/helpdesk.py` — mensagem de sugestão citando Gemini Notebook.
- `tests/test_r548_notebooklm_cli.py` — 7 testes RED/GREEN herméticos.

## Verificação

- `python3 -m pytest tests/test_r548_notebooklm_cli.py` → 7 passed.
- Regressão das suítes do doctor → verde.
- `nlm` detectado como presente/ausente no `doctor` conforme o ambiente.