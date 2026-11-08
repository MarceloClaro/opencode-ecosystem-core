# Handoff — livro quântico {#handoff-livro-quantico}

## Estado

```yaml
production: "Do Bit ao Todo — 3000 Laudas de Física Quântica"
version: "1.0"
pdf: "educacao_quantica_bohm/livro_pixel/LIVRO_3000_LAUDAS.pdf"
pages: 3550
tests: 58
links_internos: "todos resolvidos"
lean: "compila; CHSH quântico e ruído fenomenológico"
```

## Artefatos

| Artefato | Caminho | Hash/estado |
|---|---|---|
| PDF | `livro_pixel/LIVRO_3000_LAUDAS.pdf` | gerado |
| Laudas | `livro_pixel/secoes/` | 3000 |
| Fichas | `livro_pixel/fichas/` | 100 |
| Repetição | `livro_pixel/RELATORIO_REPETICOES.md` | 451.411 palavras; 21.031 repetidos |
| Lean | `livro-core/lean/QuantumTrails.lean` | compila |
| Ledger | `livro_pixel/LEDGER_AFIRMACOES.md` | atualizado |
| Eficácia | `livro_pixel/AVALIACAO_EFICACIA.md` | protocolo, não resultado |
| Peer review | `livro_pixel/PACOTE_PEER_REVIEW.md` | convite, não parecer |

## O que o próximo agente deve fazer

1. Ler `LEDGER_AFIRMACOES.md` antes de qualquer claim.
2. Rodar `pytest` e o build; não confiar em estado anterior.
3. Verificar links e Lean.
4. Se for publicar, atualizar metadados e checklist.
5. Se for medir eficácia, seguir o protocolo e o CEP.

## Perguntas abertas

- Estudo com estudantes ainda não executado.
- Peer review externo ainda não recebido.
- Edição enxuta impressa ainda não produzida.
- Tradução inglesa ainda não publicada.
- Limite de Tsirelson geral não formalizado no Lean.

## Limite

Handoff não é aprovação. O próximo agente herda estado, não confiança.
