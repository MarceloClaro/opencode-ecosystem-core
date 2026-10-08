# SPEC-935-R712 — Superfícies do pesquisador polímata: MCPs, agentes, skill, hooks e scanners

**Status:** `em implementação`
**Ciclo:** R712
**Data:** 2026-10-07
**Base:** SPEC-935-R711 (allowlist 21 labs + `integrations/github_polymath_labs.py`)

## 1. Problema

A curadoria R711 existe como módulo Python, mas sem superfícies operáveis:
sem MCP para o orquestrador invocar com validação, sem agentes com
responsabilidades delimitadas, sem skill que mapeie tipo de raciocínio ao lab,
sem hooks fail-closed que barrem clone fora da allowlist e overclaim causal,
sem scanners que auditem cobertura de raciocínio, licenças e reprodutibilidade.
Sem essas superfícies, o polímata improvisa e importa risco de terceiros.

## 2. Objetivo

Expor a allowlist R711 em 5 superfícies testadas, todas sem rede/subprocesso/LLM
no gate hermético, todas com rótulo `candidato_a_inspecao`:

1. **MCP** `integrations/polymath_labs_mcp.py` (5 ferramentas sobre R711)
2. **Agentes** `agents/catalog/46..48` (polímata, laboratório, auditoria)
3. **Skill** `.opencode/skills/pesquisador-polimata-labs/SKILL.md`
4. **Hooks** `hooks/polymath_labs_guards.py` sobre `hooks/engine.py`
5. **Scanners** `scanners/polymath_labs_scanner.py` (cobertura + licença + repro)

## 3. Critérios de aceitação

- [ ] AC1 — MCP: `listar_labs`, `validar_lab`, `manifesto_labs`, `auditar_clones`, `rotulo_polimata`; schemas JSON fechados; `validar_lab` rejeita fora da allowlist; `manifesto_labs`/`auditar_clones` operam em diretório explícito fail-closed; sem clone/build/execução.
- [ ] AC2 — Agentes: 46 pesquisador-polímata (roteia tipo→lab, nunca executa terceiro), 47 laboratório-reproduzível (issues+versão+contêiner, modelo rasilab), 48 auditoria-reprodutibilidade (repro_audit + ReproRepo + checklists PRISMA-trAIce); cada .md com frontmatter `name/description/skills/tags/examples` e corpo que cita R711/R712 e proíbe frases causais sem desenho.
- [ ] AC3 — Skill: mapa método→lab por tipo (tabela dedutivo/indutivo/abdutivo/causal/bayesiano/contrafactual/síntese/autônomo/auditoria), bloqueadores (F<10, prior oculto, claim causal, licença_undeclared), ferramentas MCP e agentes 46-48; sem promessa de nota/Qualis/aceite.
- [ ] AC4 — Hooks: `guard_clone_url(url)` deny fora da allowlist/HTTPS-GitHub; `guard_claim(text)` deny em causal absoluto sem mitigador (`causa|prova|eficaz|cura` sem `associado|limitação|suposição` próxima); `guard_third_party_exec(cmd)` deny em `pip install|git clone|docker run|npm install` quando origem fora da allowlist; integrados via `HookMatcher` sem rede.
- [ ] AC5 — Scanners: `PolymathLabsScanner.varrer(config)` retorna `cobertura_tipos` (7 tipos exigidos), `licencas_ok vs undeclared`, `reprodutibilidade` (manifesto+HEAD+hash), `riscos[]`, `recomendacoes[]`, `status` (`pronto|parcial|bloqueado`); `license_undeclared` nunca é `pronto`.
- [ ] AC6 — Testes herméticos `tests/test_r712_polimata_superficies.py`: MCP schemas + fail-closed, agentes com frontmatter válido, skill com tabela e bloqueadores, hooks deny/allow, scanner com fixtures pronta/parcial/bloqueada; sem rede/subprocesso/LLM.
- [ ] AC7 — Anti-overclaim global: nenhuma superfície retorna `verificado|Qualis A1|superhumano|aprovado`; `rotulo_polimata` e scanner repetem `candidato_a_inspecao + exige_validacao_externa`.

## 4. Fora de escopo (declarado)

- Clone/build/instalação/execução de terceiros; pinagem viva de commits/stars; federação automática; MCMC/HMC, McCrary, Sargan; qualquer frase de cura/eficácia/aceite.

## 5. Verificação

- `pytest tests/test_r712_polimata_superficies.py tests/test_r711_pesquisador_polimata_github.py -q` verde.
- `python3 -m marceloclaro.cli doctor` sem novos falhos.
- Orquestração permanece ao `marceloclaro`; MCP é ferramenta/contexto; A2A é colaboração; importados inertes.
