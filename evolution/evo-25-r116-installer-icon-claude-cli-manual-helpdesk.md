# R116 — Instalação Multiplataforma, Ícone Próprio, Claude CLI e Manual/Helpdesk

## Objetivo

Melhorar a instalação do OpenCode CLI, Antigravity CLI e (novo) Claude Code CLI em todas as plataformas, personalizar os ícones dos atalhos com identidade visual própria, e tornar o `marceloclaro` CLI mais intuitivo com um manual e um helpdesk.

## Mudanças Entregues

1. **5 bugs reais corrigidos**
   - `AntigravityBridge`: binário real é `agy`, não `antigravity` — a ponte nunca detectava disponibilidade
   - `OpenCodeCLIIntegration` (nova classe): `provision.sh` já chamava essa API, que não existia — regeneração do `opencode.json` falhava silenciosamente
   - `AGENTS.md` criado (referenciado por `opencode.json.instructions`, mas ausente)
   - `build_livro_tritemo.py::copy_to_desktop`: path hardcoded `/mnt/c/Users/marce/Desktop` substituído por detecção dinâmica (`_detect_desktop_path`, agora com detecção real de usuário Windows a partir do WSL via `cmd.exe`)
   - Catálogo de agentes: 75/160 agentes tinham a descrição truncada em `"<!--"` (comentário HTML antes do frontmatter quebrava o parser) — corrigido para preferir o campo `description:` autoral do frontmatter

2. **Ícone próprio** (`assets/generate_icon.py`) — monograma "M" com 4 nós satélite (Pillow, sem depender de arte externa), exportado em `.png`/`.ico` + iconset para conversão futura em `.icns` num Mac real. Usado nos 4 atalhos de desktop do instalador Windows.

3. **Claude Code CLI como opção de primeira classe**
   - `installer/common/install_clis.sh`: lógica compartilhada de instalação (OpenCode, Antigravity, Claude Code via npm, Ollama), reutilizada por Windows (WSL)/Linux/macOS
   - 4º atalho de desktop no Windows: "Claude Code (Ecosystem)"
   - `doctor()` ganhou check `external_clis` (sempre `warn`, nunca `fail`, já que são opcionais)
   - `CLAUDE.md` reescrito como manual real (comandos, disciplina SDD/TDD, onde encontrar cada coisa)

4. **Instaladores nativos Linux + macOS best-effort**
   - `installer/linux/install.sh`: detecta apt/dnf/pacman, cria launcher `.desktop`
   - `installer/macos/install.sh`: Homebrew, launcher `.command`, best-effort declarado
   - `installer/README.md`: substitui o link quebrado "Guia Manual" que apontava para `ARCHITECTURE.md`

5. **Desinstaladores nas 3 plataformas** — removem por padrão apenas o que é seguro reverter (atalhos, regras de firewall/aliases); ações destrutivas (remover distro WSL inteira, desativar o WSL do Windows, remover CLIs compartilhadas, apagar o repositório clonado) exigem a flag específica **e** confirmação explícita (`CONFIRMO`), nunca silenciosas.

6. **Manual + Helpdesk**
   - `MANUAL.md`: linguagem simples, traduz cada opção do menu do CLI, FAQ, troubleshooting cruzado com `doctor()`
   - `marceloclaro/helpdesk.py`: roda `doctor()` e anexa sugestão de correção em linguagem simples por check `warn`/`fail`
   - `marceloclaro/cli.py`: itens `[7] Ajuda`/`[8] Helpdesk` e comandos diretos `ajuda`/`helpdesk`

7. **Cobertura de testes**: `tests/test_r116_installer_platform_upgrade.py` (32 testes).

## Verificação

- `python3 -m pytest tests/test_r116_installer_platform_upgrade.py -v` → **32 passed**
- `bash -n` em todos os 7 scripts de instalação/desinstalação → sintaxe válida
- `python3 -m marceloclaro.cli doctor` / `helpdesk` / `ajuda` executados manualmente com sucesso
- `python3 assets/generate_icon.py` gera `icon.png`/`icon.ico`/`icon.iconset/` reais

## Lições

1. Uma classe referenciada por um script (`provision.sh`) mas nunca criada é um bug silencioso difícil de notar sem rodar o fluxo fim-a-fim — vale `grep` por chamadas a classes/funções antes de assumir que existem.
2. Quase metade (75/160) das descrições do catálogo de agentes estava quebrada por um bug de parsing simples — vale auditar os *dados gerados*, não só o código que os gera.
3. Path hardcoded a um usuário específico é um antipadrão recorrente neste projeto; detecção dinâmica via WSL tem sua própria armadilha (`cmd.exe` responde em code page do Windows, não UTF-8 — decodificação precisa de fallback).
4. Desinstaladores são parte responsável de qualquer instalador — confirmação explícita para ações destrutivas evita desastres irreversíveis (remover o WSL inteiro afeta todas as distros, não só a do projeto).

## Score

**9.2/10**

- Resolve 5 bugs reais encontrados por investigação direta, não hipotéticos
- Primeira integração de identidade visual própria do projeto
- Claude Code CLI elevado a CLI de primeira classe, com o mesmo tratamento das demais
- Manual/helpdesk fecham uma lacuna real de usabilidade para quem não conhece o jargão interno
- Desinstalação seguindo o mesmo padrão de responsabilidade do resto do projeto (nunca destrutivo sem confirmação)
