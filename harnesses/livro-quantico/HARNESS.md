# Harness — fábrica do livro quântico {#harness-livro-quantico}

> **Contrato:** execução determinística, sem LLM no caminho crítico. Cada etapa
> tem entrada, comando, artefato e gate. Falha de gate interrompe a etapa; não
> há “aprovação por otimismo”.

## Etapas

| # | Etapa | Entrada | Comando | Artefato | Gate |
|---:|---|---|---|---|---|
| 1 | Spec | tema, escopo, critérios | editar `specs/SPEC-935-R1099-*.md` | spec versionada | critérios verificáveis |
| 2 | Fonte | fichas, DOIs, dados | `verificar_dois.py` | `RELATORIO_DOIS.md` | 0 falhas; 5 URLs declaradas |
| 3 | Geração | base de conceitos | `gerar_secoes.py` | 3000 laudas + 100 fichas | 3000/100 arquivos |
| 4 | Repetição | laudas | `scripts/auditar_repeticoes.py` | `RELATORIO_REPETICOES.md` | palavras < 500k; repetidos < 22k |
| 5 | Testes | código + laudas | `pytest` | relatório | 0 falhas |
| 6 | Build | HTML + CSS | `build_pixel_fast.py` | PDF único | páginas ≥ 3000; rodapés únicos |
| 7 | Links | PDF | `pypdf` | auditoria | 0 links quebrados |
| 8 | Lean | `QuantumTrails.lean` | `lake env lean` | compilação | exit 0; sem sorry/admit |
| 9 | Publicação | pacote | checklist | `PACOTE_PEER_REVIEW.md` | pendências declaradas |

## Comandos canônicos

```bash
python3 -m marceloclaro.cli doctor
python3 scripts/auditar_repeticoes.py
.venv-quantum/bin/python -m pytest educacao_quantica_bohm/tests/test_pixel_book.py -q
.venv-quantum/bin/python educacao_quantica_bohm/livro_pixel/build_pixel_fast.py
cd livro-core/lean && lake env lean QuantumTrails.lean
```

## Condições de parada

- Spec sem critério de aceitação.
- Teste falhando.
- Lean com `sorry`/`admit`.
- Link interno quebrado.
- Chave literal encontrada.
- Claim de eficácia/peer review sem evidência externa.

## Artefatos de saída

- `LIVRO_3000_LAUDAS.pdf` (volume único).
- `RELATORIO_REPETICOES.md`.
- `LEAN_QUANTUM.md` + `QuantumTrails.lean`.
- `LEDGER_AFIRMACOES.md`.
- `AVALIACAO_EFICACIA.md` + `PILOTO_SINTETICO.md`.
- `PACOTE_PEER_REVIEW.md`.
- `LICENCA.md` e metadados.

## Limite

O harness prova que o processo rodou e que os gates passaram. Ele não prova
eficácia pedagógica, peer review ou originalidade científica.
