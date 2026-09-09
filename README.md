# OpenCode Ecosystem Core

> **Ecossistema completo de orquestração multi-agente, pesquisa científica e automação.**
> 205 agentes · 303 specs · 160 propostas de pesquisa · Auto-score 97/100

---

## 🚀 Instalação One-Click (Para Iniciantes)

### Windows (WSL2)

**Um único comando no PowerShell (como Administrador):**

```powershell
wsl --install -d Ubuntu
```

Após o WSL instalar e pedir para reiniciar, abra o **Ubuntu** no menu Iniciar e cole:

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

**Pronto!** O ecossistema está instalado. 🎉

### Linux (Ubuntu/Debian)

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

### macOS

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

### Como usar após instalação

```bash
# Ative o ambiente virtual
source ~/opencode-ecosystem-core/.venv/bin/activate

# Veja o menu de ajuda
python3 -m marceloclaro.cli helpdesk

# Execute o diagnóstico
python3 -m marceloclaro.cli doctor

# Use o ecossistema
python3 -m marceloclaro.cli
```

---

## 🗑️ Desinstalação Total (Um Clique)

### Desinstalar apenas o ecossistema

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/uninstall.sh | bash
```

### Remover WSL do Windows (Tudo)

**No PowerShell (como Administrador):**

```powershell
# Remover distribuição Ubuntu
wsl --unregister Ubuntu

# Remover WSL do Windows
dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux
dism.exe /online /disable-feature /featurename:VirtualMachinePlatform
```

---

## 📋 O que está incluído

| Componente | Descrição | Quantidade |
|---|---|---|
| **Agentes** | Especialistas por domínio | 205 |
| **Especificações** | Contratos formais SDD/TDD | 303 |
| **Propostas de pesquisa** | Artigos acadêmicos prontos | 160 |
| **MCPs** | Integrações de memória | 6 |
| **Scanners** | Análise literária e científica | 8 |
| **Modelos** | LiteRT-LM, Colibri, Z3, SymPy | Vários |

---

## 🏗️ Arquitetura (Resumida)

```
┌─────────────────────────────────────────────────────────┐
│                    OpenCode Ecosystem                    │
├─────────────────────────────────────────────────────────┤
│  CLI (marceloclaro)  →  Orquestrador  →  205 Agentes    │
│       ↓                   ↓                  ↓           │
│   Comandos          SDD/TDD Gate        Blackboard A2A  │
│       ↓                   ↓                  ↓           │
│   Saída com         Specs + Testes     MetaBus Memória  │
│   estado e          Formal             Compartilhada    │
│   ressalvas                                              │
└─────────────────────────────────────────────────────────┘
```

**Ciclo de vida:**
1. **Perceber** → Consulta memória e contexto
2. **Especificar** → Cria ou recupera especificação formal
3. **Delegar** → Roteia para agente mais adequado
4. **Executar** → Ciclo RED → GREEN → REFACTOR
5. **Verificar** → Gate SDD e validações
6. **Refletir** → Registra lições e atualiza confiança

---

## 🛠️ Comandos Úteis

| Comando | O que faz |
|---|---|
| `python3 -m marceloclaro.cli` | Menu interativo principal |
| `python3 -m marceloclaro.cli doctor` | Diagnóstico do sistema |
| `python3 -m marceloclaro.cli helpdesk` | Ajuda guiada |
| `python3 -m marceloclaro.cli status` | Status do ecossistema |
| `python3 -m marceloclaro.cli pesquisa "tema"` | Pesquisa científica |

---

## 📚 Documentação

| Documento | Para quem |
|---|---|
| [MANUAL.md](MANUAL.md) | Todos os usuários |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Desenvolvedores |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribuidores |
| [SECURITY.md](SECURITY.md) | Segurança |
| [CORRIGENDUM.md](CORRIGENDUM.md) | Histórico |
| [CHANGELOG.md](CHANGELOG.md) | Mudanças |

---

## 🔗 Links Importantes

| Recurso | URL |
|---|---|
| **GitHub** | https://github.com/MarceloClaro/opencode-ecosystem-core |
| **HuggingFace Hub** | https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core |
| **Pesquisa** | https://huggingface.co/datasets/marceloclaro/opencode-research |

---

## ⚠️ Limites Importantes

- **Não é certificação externa** — resultados são observados no checkout
- **Revisão humana necessária** — agentes são ferramentas, não decisores
- **Domínios sensíveis** — clínico, jurídico e científico são apoio computacional
- **Serviços externos** — MCPs e modelos podem falhar ou estar indisponíveis

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

---

## 📄 Licença

Este projeto é licenciado sob a [Licença MIT](LICENSE).

---

## 🙏 Agradecimentos

- **Anthropic** — Claude, Antigravity
- **Google** — LiteRT-LM, Gemma
- **HuggingFace** — Modelos e infraestrutura
- **Comunidade Open Source** — Todas as dependências

---

<div align="center">

**Feito com ❤️ para a comunidade de pesquisa e desenvolvimento**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MarceloClaro/opencode-ecosystem-core)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>
