# Consolidação R1151 — CI local, worktree e validação externa

**Data:** 2026-11-11
**Depende de:** R1148, R1149, R1150

## 1. CI: patch remoto bloqueado, gate local ativo

O token OAuth continua sem escopo `workflow`; o GitHub recusa o patch
`docs/ci/r1149-ci-workflows.patch`. A tentativa foi feita, rejeitada e revertida
sem perda.

Como mitigação, `scripts/local_ci.sh` executa o equivalente local:

| Etapa | Conteúdo |
|---|---|
| 1 | testes R1148 + R1150 (59) |
| 2 | regressão metacognitiva (16) |
| 3 | `opencode_cli --check` |
| 4 | auditoria de catálogo com 0 duplicata não resolvida |
| 5 | `git diff --check` |
| 6 | Lean opcional (`--lean`): 3 arquivos |

Resultado:

```text
59 passed
16 passed
opencode.json OK: 374 agentes, 35 MCP servers, 35 comandos
catalog audit ok
GATE LOCAL OK
```

`--lean` também passou: `ComplexProofs`, `CorrelationCounterproof` e
`MathlibCounterproof` compilaram. O `MathlibCounterproof` usa `native_decide`
declarado, como já documentado.

## 2. Worktree limpo sem perda

- As 184 deleções históricas de `.backups/` e `pilots/` foram commitadas como
  remoção deliberada.
- Os 23 itens não rastreados foram guardados em
  `stash@{0}` (`R1151 local artifacts: ...`), incluindo book/video/promo,
  `mindquantum-master/` e `educacao_quantica/`.
- `mindquantum-master/` e demais artefatos locais foram adicionados ao
  `.gitignore`.
- `git status` fica limpo após o commit; o stash pode ser reaplicado com
  `git stash apply` quando necessário.

## 3. Validação externa: pacote + verificação automatizada

`validation/external_r1151/` contém:

- `README.md`: escopo e limites;
- `claims.json`: claims formais, testes, sintéticos e clínicos;
- `reproduce.sh`: reprodução delimitada;
- `review_request.md`: perguntas para revisor independente;
- `verify_claims.py`: verificação de certificados, hashes, catálogo e testes;
- `verification_result.json` e `review_result.md`.

Resultado da verificação:

| Claim | Veredito |
|---|---|
| `formal_complex` | supported (kernel-checked) |
| `formal_correlation` | supported (kernel-checked) |
| `runtime_adapter` | supported (testes) |
| `n_of_1_unified` | supported (teste de identidade) |
| `catalog_audit` | supported (0 duplicata não resolvida) |
| `classification_pilot` | **insufficient** (sintético) |
| `clinical_claims` | **insufficient** (sem participantes) |

`reproducible=true`, `overclaims=[]`.

Os executores Codex/Antigravity foram tentados, mas o roteador respondeu
“Nenhum agente interno elegível foi atribuído”; o subagente foi bloqueado por
assinatura de modelo. Portanto:

- **não** há peer review humano;
- **não** há validação clínica;
- **não** há validação em hardware.

A verificação automatizada é independente do contexto do autor, mas não
substitui revisão humana/institucional.

## 4. Limites e próximos passos

- Ativar o workflow exige token com escopo `workflow`.
- O stash não versiona os artefatos locais; se forem necessários no repositório,
  devem ser triados e commitados individualmente.
- A validação externa humana continua aberta.
- Nenhuma confiança foi promovida e nenhum hardware foi executado.
