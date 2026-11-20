---
spec_id: SPEC-935-R1235
title: Integrar Claude-BugHunter como referência de segurança defensiva com escopo limitado
component: .opencode/skills/claude-bughunter-safe
status: implemented
test_file: tests/test_r1235_claude_bughunter_safe.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1235-PROVENANCE:
      - tests/test_r1235_claude_bughunter_safe.py::test_manifest_pins_observed_snapshot_and_separates_license_claims
    R1235-REFERENCE-ONLY:
      - tests/test_r1235_claude_bughunter_safe.py::test_manifest_forbids_upstream_import_install_execution_and_mcp
    R1235-SAFE-SCOPE:
      - tests/test_r1235_claude_bughunter_safe.py::test_skill_requires_explicit_authority_and_bounded_scope
      - tests/test_r1235_claude_bughunter_safe.py::test_skill_limits_assistance_to_defensive_non_intrusive_work
---

# SPEC-935-R1235 — Claude-BugHunter como referência defensiva limitada

## Objetivo

Integrar `elementalsouls/Claude-BugHunter` ao Core somente como referência de
proveniência e uma skill local original para preparação de avaliação autorizada,
revisão defensiva de código e documentação responsável de achados. A autorização
para integrar o repositório não autoriza testar nenhum ativo externo.

## Evidência observada (2026-11-20)

- Repositório: <https://github.com/elementalsouls/Claude-BugHunter>.
- README e `SECURITY.md` descrevem material de bug bounty/red team e condicionam
  avaliação dinâmica a ativos próprios ou autorização escrita; o README anuncia
  83 skills, 15 comandos e integração Burp MCP. Esses números são declarações
  upstream, não auditoria do Core.
- O feed Atom de commits da branch `main` apresentou o commit
  `0e70a021e59d6875004e7a563f8511aca2ba3bc1`, em 2026-11-19. A API de commits
  respondeu 403 nesta consulta; assinatura e estado atual do branch não foram
  confirmados. O pin é somente o último commit observado no feed.
- `LICENSE` declara MIT para código; `LICENSE-CONTENT` e `NOTICE` declaram
  CC BY 4.0 para conteúdo documental/skills. Materiais upstream de terceiros
  mantêm licenças próprias. Estas declarações foram lidas, sem parecer jurídico.
- A integração não redistribuirá conteúdo/código upstream nem as skills,
  comandos, payloads, scripts, dados de relatórios ou servidor Burp MCP.

## Contrato

1. Adicionar `federation/claude-bughunter.json`, fixando URL, commit observado,
   data, URLs de evidência e os limites de licença/proveniência; registrar
   assinatura e estado do branch como não verificados.
2. Adicionar `.opencode/skills/claude-bughunter-safe/SKILL.md` com orientação
   original, explícita e conservadora para definir autorização e escopo,
   revisar código defensivamente e documentar achados sem exploração.
3. A skill deve exigir autorização explícita e escopo escrito antes de qualquer
   sugestão de avaliação dinâmica. Sem isso, limitar a orientação geral,
   revisão de código fornecido pelo usuário e recomendações de correção.
4. Mesmo com autorização, esta integração não executa testes: não inclui
   instruções operacionais de exploração, payloads, bypass, enumeração, varredura
   ativa, pós-exploração, persistência, exfiltração, DoS ou acesso a dados de
   terceiros. Uma tarefa dinâmica posterior exige autorização específica,
   método permitido e revisão independente antes de qualquer ferramenta.
5. Não copiar/adaptar material upstream, importar as 83 skills ou 15 comandos,
   executar bootstrap, instalar dependências, registrar/iniciar Burp MCP, ler
   credenciais, nem habilitar comandos ou agentes globais.
6. A adoção e os estados runtime permanecem `reference_only`, `installed=false`,
   `executed=false`, `enabled=false`, `mcp_enabled=false` e
   `content_imported=false`. O manifesto deve tornar esses estados testáveis.
7. Testes devem ser offline, determinísticos e limitados ao manifesto e à skill;
   nenhum alvo externo ou pacote upstream será acessado ou testado.

## Critérios de aceitação executáveis

- `R1235-PROVENANCE` O manifesto fixa o snapshot observado e distingue licença
  declarada para código, licença declarada para conteúdo e licenças independentes
  de material upstream; não afirma assinatura ou atualização verificada.
- `R1235-REFERENCE-ONLY` A integração não contém artefatos importados nem
  executáveis upstream, permanece sem instalação/execução/ativação/MCP e não
  altera ferramentas globais.
- `R1235-SAFE-SCOPE` A skill exige autoridade e escopo delimitado, falha de modo
  conservador quando ausentes e limita a assistência a preparação defensiva,
  revisão de código e documentação responsável não intrusiva.

## Verificação

- Registrar RED válido antes de criar manifesto e skill; depois executar os
  testes por critério, validar o par RED/GREEN e rodar SpecVerifier.
- Executar `git diff --check` e o diagnóstico local do Core. Manter todas as
  alterações concorrentes preexistentes sem sobrescrever ou descartar arquivos.
- A integração não é auditoria de segurança do upstream, não confirma licença
  por parecer jurídico e não habilita o Tunnel do ChatGPT.

## Fora de escopo

- Importar ou ativar o pacote completo Claude-BugHunter, skills, comandos ou MCP.
- Testar, escanear, enumerar ou explorar qualquer alvo, inclusive plataformas de
  treinamento públicas, bug bounty ou ativos mencionados no README upstream.
- Instalar Burp Suite/extensões, configurar contas, tokens, credenciais,
  proxies, agentes globais ou integrações no workspace ChatGPT.
- Reproduzir técnicas, payloads, bypasses, código, templates ou relatórios
  upstream; emitir parecer jurídico sobre as licenças.
