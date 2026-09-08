---
name: pesquisador-universal-marcelo-claro
description: >
  Laboratório científico nativo do OpenCode Core para busca/download open access,
  revisão sistemática e Evidence Graph; usa fallback v4.1 verificado apenas para
  módulos avançados ainda não internalizados. MarceloClaro é o orquestrador primário.
---
# Pesquisador Universal Marcelo Claro v4.2 — Native Scientific Runtime

## Nativo no Core

```bash
python -m marceloclaro.scientific_lab doctor
python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
python -m marceloclaro.scientific_lab review --help
python -m marceloclaro.scientific_lab evidence --help
```

`research/articles`, `review` e `evidence` não exigem a instalação externa da skill.

## Módulos avançados em transição

`mesh`, `mission`, `living`, `synthesis`, `grade`, `causal`, `federation` e `production` continuam delegados ao release v4.1 verificado enquanto são internalizados.

## Invariantes

- busca/download é open-science-only;
- PDF precisa validar `%PDF-` e SHA-256;
- screening final e evidência `verified` exigem humano;
- candidate não é evidência;
- nenhuma convergência ou score é verdade científica;
- o mecanismo de bypass removido não é executado pelo runtime científico v4.2.

Veja `docs/SCIENTIFIC_LAB_V42.md` e `specs/SPEC-935-R469-pesquisador-universal-v42-native-runtime.md`.
