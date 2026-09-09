---
name: pesquisador-universal-marcelo-claro
description: >
  Use para pesquisa científica rigorosa e auditável: busca/download open access,
  revisão sistemática e living review, Evidence Graph, meta-análise, GRADE,
  inferência causal, Agent Mesh, Mission Control, replicação federada e release
  reproduzível. MarceloClaro permanece o orquestrador primário do Core.
---

# Pesquisador Universal Marcelo Claro v4.1 — Core Native Bridge

Esta skill registra no OpenCode Ecosystem Core a supercamada científica v4.1.
O Core permanece o kernel/runtime; a supercamada não substitui MetaBus,
Blackboard, AttentionRouter ou SDD/TDD.

## Entrada nativa

```bash
python -m marceloclaro.scientific_lab doctor
python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
python -m marceloclaro.scientific_lab review --help
python -m marceloclaro.scientific_lab synthesis --help
python -m marceloclaro.scientific_lab grade --help
python -m marceloclaro.scientific_lab causal --help
python -m marceloclaro.scientific_lab federation --help
python -m marceloclaro.scientific_lab production --help
```

## Discovery

A bridge procura a instalação completa nesta ordem:

1. `PESQUISADOR_UNIVERSAL_HOME`;
2. `PU_PREFIX/skill`;
3. `~/.local/share/pesquisador-universal/skill`.

A instalação completa continua sendo responsável pelos 88 schemas e 87 testes
da v4.1. A integração Core adiciona apenas a fachada e os testes de contrato da
ponte.

## Invariantes

- `marceloclaro` é o único orquestrador primário.
- ausência da supercamada instalada é reportada como `not_installed`, não sucesso.
- o commit `a5478054...` é baseline auditada, não HEAD obrigatório após merge.
- nenhum score, consenso computacional, GRADE ou estimativa causal possui
  autoridade epistêmica automática.
- `scihub-cli` não faz parte desta integração.

Veja `docs/SCIENTIFIC_LAB_V41.md` e `specs/SPEC-935-R468-pesquisador-universal-v41-core-integration.md`.

## Nota R470 — opt-in restrito desabilitado por omissão

O padrão é `open_science_only`; o resolvedor restrito nasce desligado
(fail-closed) e exige autorização, base legal e evidência com recibo auditável.
Sem opt-in explícito, toda tentativa é negada sem rede nem execução.
