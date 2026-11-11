# Pacote de validação externa — R1151

**Objetivo:** permitir que um revisor independente reproduza os testes, leia os
certificados e classifique cada claim como suportada, insuficiente,
contradita ou overclaim.

**Importante:** este pacote **não** é peer review, validação clínica ou
validação em hardware. Ele separa:

| Tipo | Status real |
|---|---|
| Provas complexas e de correlação | kernel-checked em Lean 4 + Mathlib |
| Runtime, N-of-1, claims graph e auditoria de catálogo | testados localmente |
| Classificação quântica e QAOA | sintéticos; sem vantagem demonstrada |
| EMA e N-of-1 com participantes | não executados; sem ética/consentimento operacional |
| Hardware e calibração | não executados |

## Como reproduzir

```bash
bash validation/external_r1151/reproduce.sh
# ou, incluindo Lean:
bash validation/external_r1151/reproduce.sh --lean
```

O script executa o gate local (`scripts/local_ci.sh`), os testes dos gates Lean
(sem recompilar quando o job pesado está skipado), a auditoria de catálogo e
grava hashes em `/tmp/opencode/`.

## Arquivos

- `claims.json`: claims, status, evidência e limites.
- `review_request.md`: perguntas para o revisor independente.
- `reproduce.sh`: reprodução delimitada.
- `verify_claims.py`: verificação automatizada de certificados, hashes e testes.
- `verification_result.json`: veredito por claim.
- `review_result.md`: síntese legível da verificação.
- `manifest.json`: SHA-256 dos arquivos do pacote.

**Revisão externa:** os executores Codex/Antigravity foram tentados, mas o
roteador não atribuiu agente interno elegível; a revisão por subagente foi
bloqueada por assinatura de modelo. A verificação automatizada é independente
do meu contexto, mas **não é peer review humano**.

## Critério de aceite

Um revisor independente deve:

1. executar `reproduce.sh` e confirmar os resultados;
2. verificar os certificados Lean e o relatório de catálogo;
3. recusar tratar prova formal como validação empírica;
4. registrar claims não suportadas e riscos de overclaim;
5. não promover confiança sem validação humana/institucional.

O resultado da revisão fica em `review_result.md`; ele não altera
`externally_validated` para `true`.
