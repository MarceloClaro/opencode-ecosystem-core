# research_lab — laboratório isolado R1049

File-first, sem rede, sem LLM e sem execução de experimento. Cria manifesto,
plano, budget e review; a finalização exige revisor humano.

```bash
python3 -m research_lab.run --objective "Hipótese falsificável..." \
  --out /tmp/opencode/research-lab --dry-run --max-steps 8 --max-cost 0
```

Inspirado em Co-Scientist (Apache-2.0) e ARIS (MIT), sem cópia de código.
Status máximo: `completed_pending_external_validation`; nunca "descoberta".
