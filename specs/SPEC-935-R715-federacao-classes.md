# SPEC-935-R715 — Federação por classe com licença confirmada e decisão humana

**Status:** `em implementação`
**Ciclo:** R715→R716
**Data:** 2026-10-07
**Base:** R714 (gate real 8/21 sem token; 13 bloqueados por licença API e janela 90d única)

## 1. Problema

Janela única de 90 dias penaliza templates estáveis (`rasilab/*`, `AgentLaboratory`)
e a API sem token retorna `license NOASSERTION/nulo` para MIT/BSD reais
(`z3`, `sympy`). Sem classes de freshness e sem confirmação manual auditável de
`LICENSE`, a federação permanece subaproveitada ou arrisca licença não confirmada.

## 2. Objetivo

Camada de decisão `integrations/polymath_federacao.py` que, sem rede no gate e
sem auto-federar, aplica janelas por classe + overrides manuais de licença com
evidência (`url_license, sha256_license, confirmado_por, confirmado_em`) e emite
`federacao_proposta.json` com `proposto|retido + motivo` para decisão humana no
`ecosystem_network`. Rede viva de confirmação pertence ao operador.

## 3. Classes e janelas

- `ativo` (motor inferência, benchmark, causal): 90d — `pgmpy, dowhy, CausalPy, causalnex, SciReason, CoT-Evo, research-engine, scir, abduction`
- `laboratorio-estavel` (template/refs): 1095d (3 anos) — `rasilab/github_demo, rasilab/github_template, AgentLaboratory, repro_audit`
- `sintese-referencia` (checklists, meta): 730d (2 anos) — `prisma, PRISMA-trAIce, EvidenceSynthesis, AiScientist-filebus, AI-Scientist`
- `formal-estavel` (provers/CAS consolidados): 730d — `z3, sympy, reasonkit-core`

`license_undeclared` R711 só vira `proposto` com override manual com evidência;
sem evidência permanece `retido`.

## 4. Critérios de aceitação

- [ ] AC1 — `classificar(url)` mapeia 21 URLs a `ativo|laboratorio-estavel|sintese-referencia|formal-estavel`; fora da allowlist levanta `ValueError` sem rede.
- [ ] AC2 — `propor(pins, overrides, dias_por_classe)` recebe pins R713/R714 e dict `{url: {licenca, url_license, sha256_license, confirmado_por}}`; aplica janela da classe sobre `idade_dias`, exige commit 40 hex + não arquivado + (license_ok viva ou override com 4 campos + sha64); tolera pin ausente como `retido`.
- [ ] AC3 — `emitir_proposta(destino_dir, proposta)` escreve `federacao_proposta.json` com `spec_id, gerador, classes, total, propostos, retidos, decisoes[]`; decisão é `proposto|retido + motivo`, nunca `federado`.
- [ ] AC4 — Anti-segredo e anti-overclaim: overrides nunca contêm token; saída nunca contém `verificado|Qualis|superhumano|aprovado|federado`; rótulo `candidato_a_inspecao` preservado.
- [ ] AC5 — Testes herméticos `tests/test_r715_federacao_classes.py`: classe correta, estável antigo dentro de 1095d proposto com override, ativo 200d retido, sem override retido, fora da allowlist sem rede, proposta em tmp com schema.
- [ ] AC6 — Skill ganha tabela de classes; MCP documenta `propor_federacao` como orientação sem rede no gate.

## 4. Fora de escopo (declarado)

- Escrita no `ecosystem_network`/federação automática; execução de testes do lab; avaliação científica; token em disco.

## 5. Verificação

- `pytest tests/test_r715_federacao_classes.py tests/test_r714_pinagem_viva.py tests/test_r713_pinagem_federacao.py -q` verde.
- Proposta seca em /tmp com pins R714 + overrides manuais auditados; `doctor` sem novos falhos.
