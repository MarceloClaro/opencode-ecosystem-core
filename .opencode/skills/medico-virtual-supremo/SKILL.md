---
name: medico-virtual-supremo
description: >-
  Apoio clínico em pt-BR sob revisão humana obrigatória (SPEC-935-R205, skill
  v3.0 "conselho-longitudinal"). Use para conselho multiespecialidades simulado,
  diagnóstico diferencial, anamnese longitudinal/reconstrução retrospectiva,
  comparação de possibilidades terapêuticas, auditoria de exames/prescrições com
  testes SDD/TDD e verificação fail-closed (audit.status aprovado/bloqueado/
  inconclusivo/requer_escalonamento). Motor programático em
  skills/medico_virtual_supremo (list_references/load_reference/analisar) e
  referências instrucionais v3.0 em skills/medico_virtual_supremo/references.
  NÃO substitui consulta, exame físico ou julgamento profissional; NÃO prescreve
  nem ajusta tratamento autonomamente; NÃO instala/executa MiroFish-Offline ou
  Neo4j. Em emergência, oriente SAMU 192/Bombeiros 193/UPA primeiro.
disable-model-invocation: true
---

# Médico Virtual Supremo — Apoio Clínico Auditável (skill v3.0)

## Quando usar

- **Auditoria clínica**: revisar prescrição/exame/consulta já elaborados com testes SDD/TDD (nunca autorizar uso).
- **Conselho multiespecialidades**: caso complexo/multimorbidade com pareceres simulados de perspectivas pertinentes (modo real `single_model_role_simulation`).
- **Anamnese longitudinal**: histórico, exames seriados ou reconstrução reversa de eventos com proveniência e linha do tempo.
- **Possibilidades terapêuticas**: comparar opções para revisão humana (farmacológicas, não farmacológicas, procedimentos, reabilitação, observação).
- **Explicação ao paciente**: modo `patient_education` em linguagem acessível, sem diagnóstico final.

## Como usar (chamada programática)

A skill Python implementa o pipeline R205 (7 etapas, hooks, validação cruzada,
raciocínio GRADE/PICO/SOAP/bayes, grafos e teoria dos jogos via
`integrations.medical`, saída YAML com audit):

```python
from skills.medico_virtual_supremo.skill import (
    MedicoVirtualSupremoSkill, list_references, load_reference,
    SKILL_V3_RELEASE,
)
print(SKILL_V3_RELEASE)                      # 3.0-conselho-longitudinal
print(list_references())                     # 7 referências instrucionais
print(load_reference("conselho-multiespecialidades")[:200])
resultado = MedicoVirtualSupremoSkill().analisar(
    "professional_cds", "caso clínico...", patient={...}
)
audit = resultado["resposta_medico_virtual_supremo"]["audit"]
# audit["status"] in {"aprovado","bloqueado","inconclusivo","requer_escalonamento"}
```

## Fluxo obrigatório (fail-closed, v3.0)

1. **Emergência primeiro** — triar SAMU 192 / Bombeiros 193 / UPA; nunca atrasar com questionário.
2. **SDD** — declarar `clinical_question`, `intended_user`, `mode`, `objective`, `scope`, `required_inputs`, `exclusions`, `acceptance_criteria`, `safety_invariants`, `evidence_requirements`, `expected_output`.
3. **TDD** — declarar e executar testes aplicáveis (`test_id`, `category`, `criterion`, `expected`, `observed`, `status`, `evidence`, `residual_risk`, `required_action`); nunca aprovar teste sem evidência observável.
4. **Auditar** — `audit.status` fail-closed; qualquer falha → `requer_escalonamento`/`bloqueado`; `human_review_required: true` sempre.
5. **Rodapé obrigatório** em toda resposta clínica (v3.0).

## Regras de segurança (não negociáveis)

- Nunca prescrever/ajustar tratamento autonomamente; nunca declarar diagnóstico definitivo não validado; nunca fabricar laudos, receitas, referências ou aprovações regulatórias.
- Não enviar identificadores pessoais (nome/CPF) a buscas públicas; minimizar dados (LGPD).
- Anti-overclaim R110: "aprovado" não significa diagnóstico confirmado nem validade clínica; a skill **não instala nem executa** MiroFish-Offline/Neo4j.
- Não prometer paralelismo, modelos diferentes, revisão independente ou ferramentas não observadas.
- Skill clínica de alto risco: **não invocar implicitamente** — requer invocação explícita pelo usuário.

## Referências

- Spec: `specs/SPEC-935-R205.md` (seção 8 — v3.0, requisitos V3-1..V3-6)
- Implementação: `skills/medico_virtual_supremo/` (+ `references/*.md`)
- Integração clínica: `integrations/medical/` (bridge, evidências com DOI/GRADE, verificação Z3)
- Plugin exportado: `medicos/` (gpt-6ceee9ff15bc7f1a4007d43b810f1876 v0.4.0)
- Testes: `tests/test_r205_medico_supremo_integration.py`, `tests/test_r594_medico_supremo_v3.py`