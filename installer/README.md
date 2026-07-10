# Instalação — OpenCode Ecosystem Core

Instala o OpenCode CLI, o Antigravity CLI (`agy`), o Claude Code CLI, o Ollama e o próprio ecossistema, com atalhos de área de trabalho usando o ícone próprio do projeto (`assets/icon.png`/`.ico`).

## Windows 10/11 (1-clique)

Configura WSL2 + Ubuntu automaticamente, depois provisiona tudo dentro dele.

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; irm https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/windows/Install-OpenCodeEcosystem.ps1 | iex
```

Detalhes: [`windows/README.md`](windows/README.md). Desinstalar: `Uninstall-OpenCodeEcosystem.ps1` (mesma pasta).

## Linux (nativo, sem WSL)

Caminho principal testado: distros baseadas em Debian/Ubuntu (`apt-get`). Fedora/Arch são suportados best-effort.

```bash
curl -fsSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/linux/install.sh | bash
```

Cria um launcher `.desktop` em `~/.local/share/applications/` (e copia para `~/Desktop` se existir). Desinstalar: `bash installer/linux/uninstall.sh`.

## macOS (best-effort — não testado em hardware real)

```bash
curl -fsSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/macos/install.sh | bash
```

Usa Homebrew para dependências e cria um launcher `.command` na Área de Trabalho (duplo-clique). Para gerar o ícone `.icns` nativo do macOS, rode `bash installer/macos/build_icns.sh` num Mac real após a instalação. Desinstalar: `bash installer/macos/uninstall.sh`.

## Depois de instalar

- Diagnóstico de saúde: `python3 -m marceloclaro.cli doctor`
- Ajuda guiada: `python3 -m marceloclaro.cli helpdesk`
- Manual de uso: [`../MANUAL.md`](../MANUAL.md)
- Manual técnico: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

## Reinstalar / atualizar

Todos os instaladores são idempotentes — rodar de novo atualiza o que já está instalado em vez de duplicar.
