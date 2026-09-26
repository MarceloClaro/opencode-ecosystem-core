# Quickstart — OpenCode Ecosystem Core

Guia rápido para começar a usar o **OpenCode Ecosystem Core** (ecossistema de
orquestração multi‑agente para pesquisa científica, automação e metacognição).

> Os comandos produzem saídas operacionais locais. Elas não constituem
> certificação externa, garantia de resultado ou aconselhamento profissional.

## 1. Requisitos

- Python 3.10+
- Git
- Linux, macOS ou WSL2 (Windows 10/11)

## 2. Clonar e preparar

```bash
git clone https://github.com/MarceloClaro/opencode-ecosystem-core.git
cd opencode-ecosystem-core
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 3. Conferir a saúde do ambiente

```bash
.venv/bin/python -m marceloclaro.cli doctor
```

O `doctor` executa os checks estruturais do checkout (specs carregando,
registro de evolução íntegro, memória metacognitiva acessível).

## 4. Ajuda e primeiros passos

```bash
.venv/bin/python -m marceloclaro.cli helpdesk
```

O helpdesk lê o diagnóstico e sugere próximos passos.

## 5. Exemplos de uso

```bash
# Menu interativo principal
.venv/bin/python -m marceloclaro.cli

# Pesquisa científica (fontes OpenAlex, Crossref, EuropePMC, arXiv)
.venv/bin/python -m marceloclaro.cli pesquisa "seu tema"

# Regenerar a configuração do OpenCode CLI (após editar o catálogo)
.venv/bin/python -m integrations.opencode_cli
```

## 6. Onde aprofundar

- [MANUAL.md](MANUAL.md) — uso completo da CLI, em linguagem simples
- [ARCHITECTURE.md](ARCHITECTURE.md) — arquitetura técnica, camadas e fluxos
- [README.md](README.md) — visão geral, capacidades e procedência
- [installer/README.md](installer/README.md) — instalação detalhada por plataforma

## Limites

- Métricas internas (contagens do `doctor`, scores de evolução) **não são
  certificação externa**; reavalie no seu checkout.
- Domínios sensíveis (clínico, jurídico, científico): o Core é **apoio
  computacional**, não decisor; **não substitui revisão humana**.
- Instalação **sem pipe de rede**: versão imutável + commit Git + SHA-256
  conferível (ver "Instalação segura e procedência" no README).