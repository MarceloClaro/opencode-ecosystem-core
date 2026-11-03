---
name: laboratorio-pesquisa-isolado
description: Execute um laboratório de pesquisa file-first com orçamento de passos,
  tempo, custo e chamadas externas, manifesto, retomada e revisão humana obrigatória.
  Use para hipóteses e protocolos; não executa LLM, rede ou experimento e não declara
  descoberta científica.
metadata:
  round: R1049
  source: https://github.com/panjose/Co-Scientist
  license: MIT
  adaptation: Adaptação textual e implementação original do Core inspirada em Co-Scientist
    (Apache-2.0, commit 31240805f7bcb3652765a008dd2eae36a638e398) e ARIS (MIT, commit
    f76ec8d6b77792e2242cca049e08d0cbb7d54e19); sem código copiado.
---

# Laboratório de pesquisa isolado

## Princípio

Hipótese não é descoberta. O laboratório registra objetivo, hipóteses, passos,
orçamento, evidências e revisão humana em arquivos. Ele **não** chama LLM, não
usa rede e não executa experimento.

## Uso

```bash
python3 -m research_lab.run --objective "Hipótese falsificável..."   --out /tmp/opencode/research-lab --dry-run --max-steps 8 --max-cost 0
```

O `--dry-run` cria plano/manifesto e não executa. Para registrar um passo
manual, use a API `record_step`; a finalização exige `reviewer` e veredito.

## Gates

- Orçamento de passos, segundos, custo e chamadas externas.
- Nenhuma chamada de rede; nenhum LLM.
- `external_validation=false` até auditoria independente.
- `human_review_required=true`; finalização sem revisor falha.
- Artefatos com hash e status; retomada por `manifest.json`.

## Limites

Esta skill não copia código, scripts ou hooks do repositório original.

O laboratório não prova hipótese, não substitui estatística, ética ou revisão
por pares. Co-Scientist/ARIS são referências; nenhum código deles foi copiado.
