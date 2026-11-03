---
spec_id: SPEC-935-R1025
title: Skill, MCP e plugin de guarda para Remotion
component: integrations.remotion_guard
status: implemented
test_file: tests/test_r1025_remotion_integration.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1025-1:
      - "tests/test_r1025_remotion_integration.py::test_license_free_eligibility"
      - "tests/test_r1025_remotion_integration.py::test_license_company_or_blocked"
      - "tests/test_r1025_remotion_integration.py::test_license_never_gives_legal_clearance"
    R1025-2:
      - "tests/test_r1025_remotion_integration.py::test_project_scan_detects_remotion_project"
      - "tests/test_r1025_remotion_integration.py::test_project_scan_rejects_symlink"
      - "tests/test_r1025_remotion_integration.py::test_project_scan_skips_node_modules_and_limits"
      - "tests/test_r1025_remotion_integration.py::test_project_scan_is_read_only"
    R1025-3:
      - "tests/test_r1025_remotion_integration.py::test_render_preflight_accepts_valid_plan"
      - "tests/test_r1025_remotion_integration.py::test_render_preflight_blocks_invalid_plan"
      - "tests/test_r1025_remotion_integration.py::test_render_preflight_checks_composition_and_output"
    R1025-4:
      - "tests/test_r1025_remotion_integration.py::test_command_policy_preview_and_unrelated"
      - "tests/test_r1025_remotion_integration.py::test_command_policy_render_requires_approval"
      - "tests/test_r1025_remotion_integration.py::test_command_policy_install_requires_license_ack"
      - "tests/test_r1025_remotion_integration.py::test_plugin_policy_matches_python"
      - "tests/test_r1025_remotion_integration.py::test_plugin_blocks_render_in_source"
    R1025-5:
      - "tests/test_r1025_remotion_integration.py::test_skill_structure_and_discovery"
      - "tests/test_r1025_remotion_integration.py::test_skill_references_resolve"
      - "tests/test_r1025_remotion_integration.py::test_mcp_server_exposes_tools"
      - "tests/test_r1025_remotion_integration.py::test_opencode_config_registers_mcp"
      - "tests/test_r1025_remotion_integration.py::test_no_remotion_code_copied_or_network"
      - "tests/test_r1025_remotion_integration.py::test_plugin_and_skill_are_text_only"
---

# SPEC-935-R1025 — Remotion auditável

## Solicitação

O usuário autorizou criar skills, MCPs e plugins que melhorem o uso de
`remotion-dev/remotion`. A entrega é **original** e não copia código do
Remotion. Ela adiciona três camadas:

1. skill `remotion-auditavel`, com licença, inspeção, prévia, render e QC;
2. MCP local `remotion-audit`, somente leitura, com quatro ferramentas;
3. plugin `remotion-guard`, que bloqueia render sem aprovação explícita e
   instalação do Remotion sem ciência da licença.

## Licença de referência

Remotion usa a **Remotion License**, não uma licença OSI. O `LICENSE.md` do
commit `1e55bdc62fb2a9e828060b9728a767f27816f762` permite uso gratuito por
indivíduos, organizações sem fins lucrativos e empresas com até 3 funcionários;
empresas maiores precisam de licença comercial. Não é permitido vender, alugar
ou relicenciar derivado do Remotion. O Core não faz parecer jurídico e não
copia o código.

## Entregáveis

- `integrations/remotion_guard.py`: regras puras, inspeção local e pré-checagem.
- `integrations/remotion_mcp.py`: servidor FastMCP local, read-only.
- `.opencode/skills/remotion-auditavel/`: skill e referências originais.
- `.opencode/plugins/remotion_policy.mjs` e `.opencode/plugins/remotion-guard.ts`.
- Registro do MCP em `integrations/opencode_cli.py` e `opencode.json`.
- `docs/REMOTION_AUDITAVEL_R1025.md` e teste determinístico.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1025-1` — Licença: elegibilidade gratuita, exigência de licença empresarial,
  bloqueios por entidade desconhecida, funcionários ausentes e revenda; nunca
  declara aprovação jurídica.
- `R1025-2` — Inspeção: detecta dependências, versões fixadas, licença,
  configuração e composições; recusa symlink; ignora `node_modules`; respeita
  limites; não modifica o projeto.
- `R1025-3` — Pré-render: aceita plano R1024 válido, bloqueia plano inválido e
  confere composição e caminho de saída; não renderiza.
- `R1025-4` — Comando: prévia permitida; render/still/bundle exigem aprovação;
  instalação exige ciência da licença; política JS e Python coincidem; plugin
  bloqueia no hook `execute.before`.
- `R1025-5` — Integração: skill descoberta, links válidos, MCP com quatro
  ferramentas, config gerada, nenhum código do Remotion copiado, nenhuma rede
  ou execução no módulo puro, arquivos textuais.

## Contrato

1. Nenhuma função baixa, instala, renderiza ou executa Remotion/Node.
2. A inspeção lê apenas arquivos locais e não segue symlink na raiz.
3. O MCP é read-only e não abre navegador nem servidor Remotion.
4. O plugin só intercepta `shell`/`bash`; comandos não relacionados passam.
5. A aprovação de render é explícita por ambiente (`REMOTION_RENDER_APPROVED=1`);
   a ciência da licença é explícita (`REMOTION_LICENSE_ACK=1`).
6. Nenhum arquivo do Remotion é copiado para o Core.

## Limites

O scanner usa regex para composições; não avalia TypeScript, não executa o
projeto e pode não reconhecer composições geradas dinamicamente. O pré-render
verifica o plano, não o vídeo. A política de licença é um resumo operacional,
não parecer jurídico. A aprovação do plugin não autoriza uso comercial; ela só
confirma que o operador decidiu renderizar.
