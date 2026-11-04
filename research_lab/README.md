# research_lab — laboratório de pesquisa isolado

**File-first, sem rede, sem LLM e sem execução automática de experimento.**

O `research_lab` cria um workspace reproduzível com objetivo falsificável,
manifesto, plano, orçamento de passos/custo e revisão pendente. Ele é um
**laboratório de protocolo**, não um executor de descobertas.

[🏠 README principal](../README.md) ·
[🔬 Pipeline científico](../docs/SCIENTIFIC_RESEARCH_PIPELINE_R1054.md) ·
[📋 Spec R1053](../specs/SPEC-1053-sintese-quantitativa-e-submissao.md)

## Uso

```bash
python3 -m research_lab.run \
  --objective "Hipótese falsificável e critério de refutação" \
  --out /tmp/opencode/research-lab \
  --dry-run \
  --max-steps 8 \
  --max-cost 0
```

## O que ele entrega

| Artefato | Função |
|---|---|
| `manifest.json` | identidade, versão e hash do workspace |
| `plan.json` | etapas, dependências e orçamento |
| `budget.json` | limite de passos, tempo e custo |
| `review.json` | estado `pending_human` e critérios de aceite |

## Limites

- Não executa LLM, rede ou experimento.
- Não declara descoberta científica.
- `completed_pending_external_validation` é o estado máximo.
- A finalização exige revisor humano.

Inspirado em Co-Scientist (Apache-2.0) e ARIS (MIT), sem cópia de código.
