# Pedido de revisão independente — R1151

Você é um revisor independente. Não presuma que os artefatos estão corretos.
Leia `claims.json`, execute `reproduce.sh` e classifique cada claim.

## Perguntas obrigatórias

1. Alguma claim empírica está sendo apresentada como se fosse validada por
   prova formal, teste unitário ou auditoria textual?
2. Os certificados Lean são realmente `kernel_checked`? Há `sorryAx`, `axiom`
   ou `native_decide` não declarado?
3. O relatório de catálogo distingue duplicata real de legado preservado e de
   quase-duplicação revisada?
4. O N-of-1 está realmente unificado, ou ainda há duas políticas?
5. O runtime respeita `allow/ask/defer/block` e aprovação humana?
6. Os dados de classificação/cozinha/EMA são sintéticos? Alguma conclusão
   clínica, nutricional ou de vantagem quântica foi indevidamente sugerida?
7. O worktree e o CI estão limpos/ativos? Se não, isso está declarado?

## Formato da resposta

Para cada claim:

```json
{
  "id": "...",
  "verdict": "supported | insufficient | contradicted | overclaim",
  "evidence": ["arquivo:linha ou comando"],
  "reason": "...",
  "required_fix": "..."
}
```

No final:

- lista de overclaims;
- lista de claims sem evidência suficiente;
- se o pacote é reproduzível;
- declaração explícita de que esta revisão **não** é peer review, validação
  clínica ou validação em hardware.
