---
language:
  - pt
  - en
license: mit
tags:
  - multi-agent
  - orchestration
  - scientific-research
  - ai
  - python
  - opencode
  - maswos
  - sdd-tdd
  - qualis-a1
  - open-science
  - research-automation
  - metacognitive-memory
  - formal-verification
  - click-uninstall
task_categories:
  - other
task_ids:
  - other
---

# OpenCode Ecosystem Core

> **Ecossistema completo de orquestração multi-agente, pesquisa científica e automação.**
> 205 agentes · 303 specs · 160 propostas de pesquisa · Auto-score 97/100

---

## 🚀 Instalação One-Click (Para Iniciantes)

### Um único comando no terminal:

**Linux / macOS / WSL (Ubuntu):**

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

**Windows (PowerShell como Administrador):**

```powershell
wsl --install -d Ubuntu
```

Após o WSL instalar, abra o **Ubuntu** e cole o comando acima.

**Pronto!** O ecossistema está instalado. 🎉

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
wsl --unregister Ubuntu
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

## 📊 Dados Científicos

| Dataset | Descrição | Itens |
|---|---|---|
| `research_proposals.json` | Propostas de pesquisa por domínio | 160 |
| `scientific_datasets_catalog.json` | Datasets científicos reais | 243 |
| `phd_agents.json` | Agentes PhD especializados | 8 |

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

| Documento | Descrição |
|---|---|
| [MANUAL.md](MANUAL.md) | Uso da CLI e comandos |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arquitetura técnica |
| [SCIENTIFIC_LAB_V41.md](docs/SCIENTIFIC_LAB_V41.md) | Lab científico v4.1 |
| [HF_HUB_PROFILE_SETUP.md](docs/HF_HUB_PROFILE_SETUP.md) | Configuração do profile |

---

## 🔗 Links

| Recurso | URL |
|---|---|
| **GitHub** | https://github.com/MarceloClaro/opencode-ecosystem-core |
| **HuggingFace Core** | https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core |
| **HuggingFace Research** | https://huggingface.co/datasets/marceloclaro/opencode-research |

---

## ⚠️ Limites

- **Não é certificação externa** — resultados são observados no checkout
- **Revisão humana necessária** — agentes são ferramentas, não decisores
- **Serviços externos** — MCPs e modelos podem falhar ou estar indisponíveis

---

## 📄 Licença

MIT License — Veja [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**Feito com ❤️ para a comunidade de pesquisa e desenvolvimento**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MarceloClaro/opencode-ecosystem-core)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>
