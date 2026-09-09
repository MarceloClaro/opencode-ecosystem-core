# Guia Rápido para Iniciantes

> **Este guia é para quem nunca usou o OpenCode Ecosystem Core.**
> Siga os passos na ordem listed.

---

## O que é o OpenCode Ecosystem Core?

É um ecossistema de inteligência artificial que ajuda você a:

- 🔬 **Pesquisar** — Encontrar artigos científicos e fontes confiáveis
- 🤖 **Orquestrar** — Coordenar 205 agentes especializados
- 📝 **Especificar** — Criar contratos formais para garantir qualidade
- 🎯 **Executar** — Rodar tarefas com validação automática
- 📊 **Apresentar** — Gerar apresentações profissionais

**Não substitui profissionais** — é uma ferramenta de apoio.

---

## Instalação (3 Passos)

### Passo 1: Instale o WSL (Windows Apenas)

Se você usa **Windows**, primeiro instale o WSL:

1. Abra o **PowerShell como Administrador**
2. Digite: `wsl --install -d Ubuntu`
3. Reinicie o computador
4. Abra o **Ubuntu** no menu Iniciar
5. Crie um usuário e senha quando solicitado

**Se você usa Linux ou macOS**, pule para o Passo 2.

### Passo 2: Execute o Instalador

No terminal (Ubuntu, Linux ou macOS), copie e cole:

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

Aguarde a instalação terminar. Pode demorar alguns minutos.

### Passo 3: Comece a Usar

Após a instalação:

```bash
# Ative o ambiente virtual
source ~/opencode-ecosystem-core/.venv/bin/activate

# Veja o que pode fazer
python3 -m marceloclaro.cli helpdesk
```

---

## Comandos Mais Usados

| Comando | O que faz |
|---|---|
| `python3 -m marceloclaro.cli` | Abre o menu principal |
| `python3 -m marceloclaro.cli doctor` | Verifica se tudo está funcionando |
| `python3 -m marceloclaro.cli helpdesk` | Mostra ajuda guiada |
| `python3 -m marceloclaro.cli pesquisa "inteligência artificial"` | Pesquisa sobre um tema |

---

## Exemplo: Pesquisa Científica

```bash
# Ative o ambiente
source ~/opencode-ecosystem-core/.venv/bin/activate

# Pesquise sobre um tema
python3 -m marceloclaro.cli pesquisa "governança de inteligência artificial" --max-papers 5

# Veja os resultados
python3 -m marceloclaro.cli status
```

---

## Problemas Comuns

### "Comando não encontrado"

```bash
# Verifique se o ambiente virtual está ativo
source ~/opencode-ecosystem-core/.venv/bin/activate

# Tente novamente
python3 -m marceloclaro.cli doctor
```

### "Erro de permissão"

```bash
# Não execute como root/sudo
# Execute como usuário normal
```

### "Python não encontrado"

```bash
# No Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# No macOS
brew install python3
```

---

## Desinstalação

### Remover apenas o ecossistema

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/uninstall.sh | bash
```

### Remover WSL do Windows

**No PowerShell (como Administrador):**

```powershell
wsl --unregister Ubuntu
dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux
dism.exe /online /disable-feature /featurename:VirtualMachinePlatform
```

---

## Links Úteis

| Recurso | URL |
|---|---|
| **GitHub** | https://github.com/MarceloClaro/opencode-ecosystem-core |
| **Documentação** | https://github.com/MarceloClaro/opencode-ecosystem-core/blob/main/MANUAL.md |
| **Problemas** | https://github.com/MarceloClaro/opencode-ecosystem-core/issues |

---

## Precisa de Ajuda?

1. Consulte o [MANUAL.md](MANUAL.md)
2. Abra uma issue no [GitHub](https://github.com/MarceloClaro/opencode-ecosystem-core/issues)
3. Execute `python3 -m marceloclaro.cli helpdesk` no terminal

---

<div align="center">

**Voltar ao [README Principal](README.md)**

</div>
