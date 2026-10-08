# SPEC-935-R711 — Pesquisador polímata GitHub: raciocínio científico + laboratórios auditáveis

**Status:** `em implementação`
**Ciclo:** R711
**Data:** 2026-10-07
**Base:** R708 (descoberta auditável), R710 (Fase B causal/bayesiana/mista), R217 (integração de repos externos), R706 (produção em escala)

## 1. Problema

O Core dispõe de motores locais de inferência (R708/R710), mas não de mapa
curado e auditável de repositórios GitHub que colaborem com os diversos tipos
de raciocínio científico (dedutivo, indutivo, abdutivo, causal, bayesiano,
contrafactual, síntese de evidências) para construção de pesquisador polímata
investigativo capaz de erguer laboratórios reproduzíveis e artigos reais
auditáveis. Sem allowlist + manifesto com hashes, a integração importa risco:
execução inadvertida de hooks/scripts de terceiros, overclaim de qualidade e
confusão entre orquestração (orquestrador), ferramentas/contexto (MCP) e
colaboração entre agentes (A2A/Blackboard).

## 2. Objetivo

Módulo `integrations/github_polymath_labs.py` que registra curadoria fechada
de repositórios GitHub por tipo de raciocínio, emite roteiro de clonagem
auditada com hashes e ancora laboratórios/artigos sem executar código de
terceiros. Nenhum score, consenso ou GRADE possui autoridade epistêmica
automática. Recuperação lexical não equivale a treinamento nem a melhoria
cognitiva medida.

## 3. Curadoria fechada (allowlist v1, 21 alvos)

- **Dedutivo/formal:** `Z3Prover/z3` (MIT), `sympy/sympy` (BSD), `reasonkit/reasonkit-core` (Apache-2.0, a confirmar)
- **Indutivo/abdutivo/benchmark:** `InternScience/SciReason` (Apache-2.0), `idiap/SciR` (a confirmar), `Irving-Feng/CoT-Evo` (MIT), `kmineshima/abduction-syllogism-llm` (a confirmar), `Aswinesag/research-reasoning-engine` (a confirmar)
- **Causal/bayesiano/contrafactual:** `pgmpy/pgmpy` (MIT), `py-why/dowhy` (MIT), `pymc-labs/CausalPy` (Apache-2.0), `mckinsey/causalnex` (Apache-2.0)
- **Síntese/evidências:** `Proportione/prisma` (MIT), `cqh4046/PRISMA-trAIce` (MIT), `OHDSI/EvidenceSynthesis` (Apache-2.0)
- **Laboratório autônomo:** `SakanaAI/AI-Scientist` (Apache-2.0), `AweAI-Team/AiScientist` (MIT), `SamuelSchmidgall/AgentLaboratory` (a confirmar)
- **Reprodutibilidade/auditoria:** `rasilab/github_demo` + `rasilab/github_template` (a confirmar, ref. DOI 10.1371/journal.pbio.3003029), `aqibrahimbt/repro_audit` (MIT)

Licenças e stars são instantâneo de curadoria em 2026-10-07 e exigem
revalidação viva antes de federar. Entradas `a confirmar` nascem como
`license_undeclared` e não federam até confirmação.

## 4. Critérios de aceitação

- [ ] AC1 — `listar_labs()` retorna apenas entradas da allowlist, cada uma com `id`, `url`, `tipo_raciocinio[]`, `uso_polimata`, `licenca`, `status_licenca` (`ok`|`license_undeclared`); nenhuma URL fora da allowlist é retornada.
- [ ] AC2 — `validar_url(url)` fail-closed: aceita apenas `https://github.com/<org>/<repo>` presente na allowlist (normaliza case e sufixo `.git`); rejeita `http`, SSH, fora do GitHub ou fora da allowlist com `ValueError` explícito.
- [ ] AC3 — `gerar_manifesto(destino_dir)` escreve `labs_manifest.json` com `spec_id`, `gerado_em`, `gerador=marceloclaro`, `total`, `entradas[]` (url+commit_pin esperado vazio até pinagem viva+sha256_url), sem rede; nunca executa clone, hook ou script de terceiro.
- [ ] AC4 — `verificar_clones(base_dir)` audita diretório local: para cada subdiretório correspondente a lab, registra `existe`, `HEAD` (se `.git` presente, via leitura de arquivo, sem subprocesso), `sha256_gitignore_ou_readme` quando disponível; ausentes são `existe=false`, nunca erro fatal; relatório inclui `audit_trail` quem/quando/o quê.
- [ ] AC5 — Guarda anti-overclaim: módulo nunca retorna `verificado`, `Qualis A1`, `superhumano` ou `aprovado`; função `rotulo_epistemico()` retorna sempre `candidato_a_inspecao` + `exige_validacao_externa=true`.
- [ ] AC6 — Separação arquitetural documentada em docstring: orquestração pertence ao orquestrador via Blackboard; MCP fornece ferramentas/contexto; A2A trata colaboração entre agentes; artefatos importados são inertes.
- [ ] AC7 — Testes herméticos `tests/test_r711_pesquisador_polimata_github.py` (sem rede/subprocesso/LLM, sementes fixas): allowlist fechada, fail-closed de URL, manifesto em tmp com schema válido, verificação de clones em fixtures sintéticas, rótulo epistêmico constante.

## 5. Fora de escopo (declarado)

- Clone, build, pip install ou execução de código de terceiros: pertence ao operador com consentimento explícito, fora do teste hermético.
- Pinagem viva de commits/stars e checagem de manutenção 90 dias: rotina operacional com rede, fora do gate TDD.
- Federação automática no `ecosystem_network`: exige licença confirmada + testes do lab + decisão do orquestrador.
- Qualquer alegação causal, de eficácia, cura ou aceite editorial a partir da presença do repo.

## 6. Verificação

- `pytest tests/test_r711_pesquisador_polimata_github.py -q` verde.
- `python3 -m marceloclaro.cli doctor` sem novos falhos (avisos pré-existentes tolerados).
- Demo em /tmp: `gerar_manifesto()` + `verificar_clones()` sobre fixtures sintéticas, sem rede.
