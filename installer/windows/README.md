# Instalador Automático Windows (WSL + Ecossistema)

Este instalador (PowerShell) configura o ambiente completo do **OpenCode Ecosystem Core** em máquinas Windows, com apenas 1 comando.

## O que o instalador faz?

1. **Autorização Automática (Segurança):**
   - Adiciona exclusões no Windows Defender para o processo `wsl.exe` e para a unidade de rede do Ubuntu (`\\wsl.localhost\Ubuntu`).
   - Cria regras de Firewall para permitir o tráfego do WSL e portas de desenvolvimento (Ollama 11434, 3000, 8000).
   - Desativa temporariamente o SmartScreen para o download dos scripts (Zone.Identifier).
2. **WSL2 + Ubuntu:**
   - Instala o Windows Subsystem for Linux (WSL2) com a distribuição Ubuntu.
   - **Retomada Automática:** Se o Windows precisar reiniciar após instalar o WSL, o script usa o registro `RunOnce` para continuar a instalação automaticamente após o reboot.
3. **Provisionamento do Linux (CLIs):**
   - Instala dependências base (git, python3, pip, pandoc, nodejs).
   - Instala o **OpenCode CLI** (`opencode`).
   - Instala o **Antigravity CLI** (`agy`).
   - Instala o **Ollama CLI** e habilita seu serviço (systemd/nohup).
4. **Instalação do Ecossistema:**
   - Clona este repositório para `~/opencode-ecosystem-core`.
   - Instala todas as dependências Python (`requirements.txt`, `pymupdf`, `sympy`, etc).
   - Gera o `opencode.json` nativo (carregando os 134 agentes e o MCP metacognitivo).
5. **Atalhos (1 Clique):**
   - Cria 3 atalhos na sua Área de Trabalho do Windows:
     - **OpenCode Ecosystem**: Abre o OpenCode CLI já com todo o ecossistema carregado.
     - **Antigravity CLI**: Abre o terminal do Google Antigravity.
     - **Ecosystem (marceloclaro)**: Abre o menu interativo Python do orquestrador.

## Como Instalar

1. Abra o **PowerShell como Administrador** (clique com o botão direito no menu Iniciar > "Windows PowerShell (Admin)" ou "Terminal (Administrador)").
2. Cole o comando abaixo e pressione Enter:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; irm https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/windows/Install-OpenCodeEcosystem.ps1 | iex
```

3. Siga as instruções na tela. Se for a sua primeira vez instalando o WSL, o computador pode reiniciar. O script continuará sozinho.

> **Nota sobre repositórios privados:** Se o repositório no GitHub estiver privado, o script de provisionamento dentro do Ubuntu pode falhar no `git clone`. Nesse caso, abra o Ubuntu, rode `gh auth login` e execute `bash ~/provision.sh` manualmente.
