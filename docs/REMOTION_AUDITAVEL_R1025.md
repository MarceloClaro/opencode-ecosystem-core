# Remotion auditável — R1025

## O que foi criado

Três camadas originais, sem copiar código do Remotion:

| Camada | Arquivo | Função |
|---|---|---|
| Skill | `.opencode/skills/remotion-auditavel/` | licença, inspeção, prévia, render e QC |
| MCP local | `integrations/remotion_mcp.py` | 4 ferramentas read-only |
| Plugin | `.opencode/plugins/remotion-guard.ts` | bloqueia render sem aprovação e instalação sem ciência da licença |
| Núcleo | `integrations/remotion_guard.py` | regras puras, scanner e pré-checagem |

## Licença

Remotion usa a **Remotion License**, não uma licença OSI. O `LICENSE.md` do
commit `1e55bdc62fb2a9e828060b9728a767f27816f762` permite uso gratuito por
indivíduos, organizações sem fins lucrativos e empresas com até 3 funcionários;
empresas for-profit maiores precisam de licença comercial. Não é permitido
vender, alugar ou relicenciar derivado do Remotion.

O Core faz um resumo operacional. **Não é parecer jurídico.** O texto oficial
e a licença comercial prevalecem.

## Skill

`remotion-auditavel` cobre:

1. checagem de elegibilidade antes de instalar;
2. inspeção read-only do projeto;
3. prévia (`remotion studio`) antes de render;
4. render apenas com aprovação explícita;
5. validação do plano R1024 e conferência de metadados;
6. limites: regex não compila TypeScript, metadados não provam qualidade.

## MCP `remotion-audit`

Ferramentas read-only:

| Ferramenta | Entrada | Saída |
|---|---|---|
| `license_scope` | entidade, funcionários, revenda | `eligible_free`, `company_license_required` ou `blocked` |
| `project_scan` | caminho local | dependências, licença, configs, composições, avisos |
| `render_preflight` | plano R1024, composição, saída | `ready` ou `blocked`; nunca renderiza |
| `command_policy` | comando, aprovação, ciência | `allow` ou `block`; nunca executa |

O servidor não abre navegador, não roda Node/Remotion e não acessa a rede.

## Plugin `remotion-guard`

O hook `execute.before` intercepta apenas `shell`/`bash`:

- `remotion studio` → permite prévia;
- `remotion render|still|bundle` → bloqueia sem `REMOTION_RENDER_APPROVED=1`;
- `npm/pnpm/yarn/bun install|add` de Remotion → bloqueia sem
  `REMOTION_LICENSE_ACK=1`;
- `remotion upgrade` → bloqueia para revisão;
- demais comandos → passam.

A aprovação é uma decisão do operador. Ela não valida licença, direitos de
mídia ou qualidade do vídeo.

## Uso

```bash
# Inspecionar (MCP remotion-audit, ferramenta project_scan)
python3 - <<'PY'
from integrations.remotion_guard import scan_project
print(scan_project("caminho/do/projeto"))
PY

# Prévia
npx remotion studio --no-open

# Render explícito
REMOTION_RENDER_APPROVED=1 npx remotion render Intro out/video.mp4

# Plano e QC
python3 -m integrations.video_edit_plan validate plano.json
python3 -m integrations.video_edit_plan verify plano.json relatorio.json
```

## Verificação

- `tests/test_r1025_remotion_integration.py`: 21 testes.
- RED/GREEN e `SpecVerifier` 5/5 em worktree isolada.
- Teste Node da política JS em `tests/remotion_policy_test.mjs`.
- Regressão dos componentes afetados e `doctor`.

## Limites

- Nenhum projeto Remotion foi instalado, executado ou renderizado.
- O scanner não compila TypeScript; composições dinâmicas podem não aparecer.
- O pré-render valida o plano, não o vídeo.
- O plugin reduz acidente; não impede uso comercial indevido.
- Nenhum código do Remotion foi copiado.

## Lacuna conhecida no guard (piloto R1026)

O guard bloqueia `npm install remotion` e `npx remotion render`, mas não
inspeciona `npm run <script>` cujo `package.json` invoca Remotion. No piloto
autorizado, a instalação foi feita por manifesto e o render por script npm.
Isso foi possível porque a aprovação por ambiente não está disponível no
processo do servidor. Correção recomendada: aprovação por arquivo com escopo e
expiração, além de leitura dos scripts do `package.json`. Enquanto isso, o
guard é uma barreira contra comando direto, não uma fronteira de segurança.

