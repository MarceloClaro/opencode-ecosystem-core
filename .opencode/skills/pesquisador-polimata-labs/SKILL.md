---
name: pesquisador-polimata-labs
description: Roteia tipo de raciocínio ao lab R711, ancora laboratório reproduzível e auditoria, com bloqueadores fail-closed. Use para pergunta polímata que exija lab externo curado; nunca executa clone/build/install de terceiros; nunca promete nota, Qualis ou aceite.
---

# Pesquisador Polímata Labs — R711/R712/R713

Orquestração pertence ao `marceloclaro` via Blackboard; MCP é ferramenta/contexto; A2A é colaboração.
Importados inertes. Recuperação lexical não é treinamento nem melhoria medida.

## Quando acionar

Pergunta que exija raciocínio tipado + lab curado + artigo auditável. Sem lab curado: produzir
protocolo, nunca número. Sem desenho causal: nunca frase causal.

## Mapa tipo → lab R711 → uso

| Tipo | Labs R711 | Uso polímata |
|---|---|---|
| dedutivo | Z3Prover/z3, sympy/sympy | prova, SMT, derivação simbólica |
| indutivo | InternScience/SciReason, Irving-Feng/CoT-Evo | régua multidisciplinar, CoT evolutiva |
| abdutivo | kmineshima/abduction-syllogism-llm, Aswinesag/research-reasoning-engine | hipótese vs prova, grafo esparso |
| causal | pgmpy/pgmpy, py-why/dowhy, mckinsey/causalnex | DAG, identificação, what-if |
| bayesiano | pymc-labs/CausalPy, pgmpy/pgmpy | HDI, posterior com prior explícito |
| contrafactual | py-why/dowhy, pymc-labs/CausalPy | do(X), sintético, placebos |
| sintese | Proportione/prisma, cqh4046/PRISMA-trAIce, OHDSI/EvidenceSynthesis | PRISMA 2020, trAIce, meta-análise |
| autonomo | SakanaAI/AI-Scientist, AweAI-Team/AiScientist, SamuelSchmidgall/AgentLaboratory | ideia-experimento-escrita sob supervisão |
| auditoria | aqibrahimbt/repro_audit, rasilab/github_demo, rasilab/github_template | seeds, splits, manifesto, HEAD, hash |
| laboratorio | rasilab/github_demo, rasilab/github_template | issues + versão + contêiner |

## Bloqueadores

- `validar_lab` fail-closed: fora da allowlist ou fora de `https://github.com/org/repo` é deny.
- Palavras `causa|prova|eficaz|cura` só com desenho + diagnósticos ok + mitigador próximo; verificado por `hooks/polymath_labs_guards.py`.
- `F<10` no primeiro estágio = instrumento fraco: sem frase causal.
- Prior nunca oculto: `mu0/tau0` registrados.
- `license_undeclared` não federa; `tem_manifesto+HEAD+hash` exigidos para `pronto`.
- `pip install|git clone|docker run|npm install|curl|bash` de terceiros exige consentimento do operador.

## Ferramentas

MCP `polymath-labs-mcp`: `listar_labs`, `validar_lab`, `manifesto_labs`, `auditar_clones`, `rotulo_polimata`, `pinar_lab`, `revalidar_federacao` (R713 exige consentimento=true).
Agentes: `46_agente_pesquisador_polimata`, `47_agente_laboratorio_reproduzivel`, `48_agente_auditoria_reprodutibilidade`.
Scanner: `scanners/polymath_labs_scanner.py` (+ sinal `pin_fresco` R713, sem mudar vereditos R712). Hooks: `hooks/polymath_labs_guards.py`.
Pinagem: `integrations/polymath_pinagem.py` — `pinar_lab`, `revalidar_todos`, `emitir_pins` com fetcher injetável; gate hermético com falso, viva com operador.

## Pinagem viva e federação (R713)

- `pinar_lab`/`revalidar_federacao` exigem `consentimento=true`; sem consentimento é deny.
- Federável sse commit 40 hex + push dentro de 90d + licença viva + não arquivado.
- Emite `labs_pins.json` + `federacao_gate.json` via `emitir_pins`; decisão humana exigida.

## Classes e federação (R715)

| Classe | Janela | Labs |
|---|---|---|
| ativo | 90d | SciReason, SciR, CoT-Evo, abduction-syllogism, research-engine, pgmpy, dowhy, CausalPy, causalnex |
| formal-estavel | 730d | z3, sympy, reasonkit-core |
| sintese-referencia | 730d | prisma, PRISMA-trAIce, EvidenceSynthesis, AiScientist-filebus, AI-Scientist |
| laboratorio-estavel | 1095d | AgentLaboratory, github_demo, github_template, repro_audit |

Override manual exige `licenca+url_license+sha256_license+confirmado_por`; `SakanaAI/AI-Scientist` é custom restritiva com AI Scientist Clause — retido sem revisão jurídica.

## Lote piloto (R717, exemplo ratificável)

Em `/tmp/polymath_intencoes_piloto`: aprovadas `pgmpy, sympy, prisma`; rejeitada `reasonkit-core` por licença a confirmar; 12 aguardando. Original `/tmp/polymath_intencoes` intacto com 16 aguardando. Ratificação titular pendente antes de R621.
