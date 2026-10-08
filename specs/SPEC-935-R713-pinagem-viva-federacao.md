# SPEC-935-R713 — Pinagem viva e revalidação 90 dias para federação polímata

**Status:** `em implementação`
**Ciclo:** R713→R714
**Data:** 2026-10-07
**Base:** R711 (allowlist 21), R712 (MCP/agentes/skill/hooks/scanners)

## 1. Problema

A allowlist R711 registra URLs sem pin de commit, sem data de manutenção e sem
licença viva confirmada. Federar sem pinagem permite deriva silenciosa:
HEAD muda, licença muda, repo arquiva, manutenção cessa. O gate hermético
R711/R712 proíbe rede por desenho; a pinagem viva exige rotina operacional com
rede, consentimento explícito do operador e trilha auditável, sem executar
código de terceiros.

## 2. Objetivo

Módulo operacional `integrations/polymath_pinagem.py` com fetcher injetável que:

1. Resolve `HEAD` vivo por lab via GitHub API ou `git ls-remote` (operador autoriza rede/subprocesso fora do gate).
2. Revalida manutenção 90 dias (`pushed_at` vs agora, tolerância UTC) e licença viva.
3. Emite `labs_pins.json` + `federacao_gate.json` com decisão `federavel|bloqueado` por lab e motivo.
4. Nunca clona, instala, constrói ou executa; nunca declara qualidade sem validação externa.

Testes herméticos usam fetcher falso determinístico; nenhuma chamada real no gate.

## 3. Critérios de aceitação

- [ ] AC1 — `pinar_lab(url, fetcher)` fail-closed: URL fora da allowlist rejeitada antes de qualquer rede; fetcher recebe apenas `org/repo`; retorna `url, org, repo, commit, pushed_at, license, federavel, motivo, auditado_em, sha256_registro`.
- [ ] AC2 — `revalidar_todos(fetcher, dias=90)` percorre allowlist, tolera falha isolada por lab (um lab fora do ar não aborta os demais), registra `total, federaveis, bloqueados, gerado_em, janela_dias`.
- [ ] AC3 — Regra de federação: `federavel=true` sse `commit` com 40 hex + `pushed_at` dentro de 90 dias + `license_ok=true` + `arquivado=false`; `license_undeclared` R711 exige `license_ok` viva para virar `ok`, senão `bloqueado` com motivo explícito.
- [ ] AC4 — `emitir_pins(destino_dir, resultado)` escreve `labs_pins.json` e `federacao_gate.json` com `spec_id, gerador=marceloclaro, janela_dias, pins[]`; leitura posterior reproduz `sha256_registro`.
- [ ] AC5 — Fiação sem quebra: MCP `polymath_labs_mcp` ganha `pinar_lab` e `revalidar_federacao` como extensões documentadas que delegam ao módulo (rede só com `consentimento=true` explícito); skill ganha seção Pinagem viva; scanner considera `pin_fresco` como sinal adicional sem mudar vereditos R712 existentes.
- [ ] AC6 — Testes herméticos `tests/test_r713_pinagem_federacao.py`: fetcher falso com 4 cenários (fresco+licença ok→federável; desatualizado 120d→bloqueado; licença ausente→bloqueado; arquivado→bloqueado); fora da allowlist sem chamar fetcher; tolerância a falha isolada; manifesto em tmp com schema; rótulo sempre candidato.
- [ ] AC7 — Anti-overclaim: nenhum retorno contém `verificado|Qualis|superhumano|aprovado`; decisão é `federavel|bloqueado` + motivo, nunca qualidade atestada.

## 4. Fora de escopo (declarado)

- Clone/build/install/execução de terceiros; execução de suíte de testes do lab; checagem de CI; avaliação de qualidade científica; federação automática no `ecosystem_network` sem decisão humana.

## 5. Verificação

- `pytest tests/test_r713_pinagem_federacao.py tests/test_r712_polimata_superficies.py tests/test_r711_pesquisador_polimata_github.py -q` verde.
- `python3 -m marceloclaro.cli doctor` sem novos falhos.
- Demo hermética em /tmp com fetcher falso; rotina viva documentada com `consentimento` explícito e exemplo `git ls-remote https://github.com/<org>/<repo> HEAD`.
