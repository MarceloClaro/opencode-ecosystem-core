# Gêmeos Digitais Periodontais — Framework SUS-Twin

> **Volume 2 — Práticas de Validação do Framework SUS-Twin**
> Ecossistema de validação, qualidade e implementação de Gêmeos Digitais Periodontais no SUS

[![TDD](https://img.shields.io/badge/TDD-85%2F85%20PASS-brightgreen)](.tdd_validate_v2.py)
[![LaTeX](https://img.shields.io/badge/LaTeX-0%20errors%2C%200%20overfull-brightgreen)](light.tex)
[![BibTeX](https://img.shields.io/badge/BibTeX-0%20warnings-brightgreen)](referencias.bib)
[![Pages](https://img.shields.io/badge/Pages-184-lightgrey)](light.pdf)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-blue)](LICENSE)

---

## 📖 Sobre a Obra

Este repositório contém os fontes LaTeX do **Volume 2 — Gêmeos Digitais Periodontais**, uma continuação direta e didática do Volume 1, com foco em **Práticas de Validação do Framework SUS-Twin**.

Diferentemente do Volume 1 (que estabelece os fundamentos conceituais), o Volume 2 é uma **jornada prática N0→N3** que ensina o leitor a implementar, validar e orquestrar pipelines completos de Gêmeos Digitais Periodontais usando ferramentas open-source e o ecossistema OpenCode.

### Estrutura da Obra

| Parte | Capítulos | Tema |
|:------|:---------:|:-----|
| **I — Fundamentos** | 3 | Ferramentas, arquitetura 6 camadas, pipeline DICOM→malha |
| **II — Aplicações Práticas** | 5 | PySUS, FEM/Open3D, Periomod/K-Fold, DentalSegmentator, laboratório virtual |
| **III — Validação** | 5 | OpenCode MCP, pipeline 3D, K-Fold temporal, IoT/Gateway, práticas integradas |
| **IV — Implementação no SUS** | 4 | Plano piloto, ética/LGPD, guia N0→N3, roadmap tecnológico |

### Níveis de Maturidade (N0–N3)

| Nível | Perfil | Descrição |
|:-----:|:-------|:----------|
| **N0** | Curioso Digital | Visualizar DT sem programação (3D Slicer, DentalSegmentator) |
| **N1** | Implementador Guiado | Reproduzir pipelines com tutoriais passo a passo |
| **N2** | Pesquisador Reprodutível | Executar TDD, modificar pipelines, validar métricas |
| **N3** | Inovador/PhD | Propor novos métodos, publicar, integrar ao SUS |

---

## 📊 Estado do Projeto

| Métrica | Resultado |
|:--------|:----------|
| **Capítulos** | **17/17** — 100% V2 standalone |
| **Sub-arquivos V1 deletados** | **97** |
| **TDD** | **85/85 — PASS ALL** ✅ |
| **Erros LaTeX** | **0** |
| **Overfull boxes** | **0** |
| **BibTeX warnings** | **0** |
| **Páginas (light)** | **184** (~2,8 MB) |
| **Páginas (dark)** | **184** (~2,8 MB) |
| **Footnotes** | **~290** para leitores leigos |
| **Códigos Python** | **46** blocos executáveis |
| **Tabelas** | **32** |
| **Referências** | **86** entradas BibTeX |
| **Ciclo Evolutivo** | **R23** — Trust Engine + N3.5 Completo |

---

## 🚀 Como Compilar

### Pré-requisitos

- Distribuição LaTeX completa (TeX Live 2024+ ou MiKTeX)
- Python 3.11+ (para scripts de validação)

### Comandos

```bash
# Tema Claro
pdflatex -interaction=nonstopmode light.tex
bibtex light
pdflatex -interaction=nonstopmode light.tex
pdflatex -interaction=nonstopmode light.tex

# Tema Escuro
pdflatex -interaction=nonstopmode dark.tex
bibtex dark
pdflatex -interaction=nonstopmode dark.tex
pdflatex -interaction=nonstopmode dark.tex
```

### Validação TDD

```bash
python .tdd_validate_v2.py
```

---

## 🛠️ Arquitetura do Volume 2

```
livro-volume2/
├── light.tex              # Tema Claro (entrada principal)
├── dark.tex               # Tema Escuro
├── preamble-common.tex    # Preâmbulo compartilhado
├── referencias.bib        # Base bibliográfica (86 entradas)
├── .tdd_validate_v2.py    # Validador TDD (85 testes)
├── .sdd_v2_specs.md       # Especificações SDD
│
├── sections/
│   ├── part1/             # Fundamentos (3 caps)
│   ├── part2/             # Aplicações Práticas (5 caps)
│   ├── part3/             # Ecossistema de Validação (5 caps)
│   └── part4/             # Implementação no SUS (4 caps)
│
├── appendices/
│   ├── glossario.tex
│   ├── referencias.tex
│   └── repositorios.tex
│
└── evolution/             # Skills geradas por evolução
```

### Ferramentas Open-Source Referenciadas

| Ferramenta | Aplicação | Capítulo |
|:-----------|:----------|:--------:|
| 3D Slicer + DentalSegmentator | Segmentação CBCT | 1, 10, 16 |
| PySUS | Dados DATASUS | 4, 11, 13 |
| Open3D | Reconstrução 3D | 5, 10, 13 |
| MONAI | Segmentação profunda | 10, 13 |
| Periomod | Predição periodontal | 6, 11, 13 |
| FEniCS / Gmsh | Elementos Finitos | 2, 5 |
| Paho-MQTT + InfluxDB | IoT/Telemetria | 12 |
| OpenCode Ecosystem | Orquestração | 9 |

---

## 🔬 Metodologia de Qualidade

O Volume 2 foi desenvolvido seguindo os princípios de **SDD (Spec-Driven Development)** e **TDD (Test-Driven Development)** do OpenCode Ecosystem:

1. **SDD**: Especificações formais documentadas em `.sdd_v2_specs.md`
2. **TDD**: 85 testes automatizados validando badges, encoding, citações, labels, exercícios
3. **AutoEvolve**: Pipeline autônomo SENSE→DISCOVER→INSTALL→VERIFY→EVOLVE→LEARN
4. **Cross-Validation**: Verificação cruzada de 17 capítulos, 137 labels, 25 citações

### Testes TDD (85/85 PASS)

| Suite | Testes | Descrição |
|:------|:------:|:----------|
| S1 | 34 | Badge de nível + referência SUS-Twin |
| S2 | 2 | Prefácio alinhado (N0-N3 + SUS-Twin) |
| S3 | 17 | Exercícios práticos |
| S4 | 17 | Seções listadas no cabeçalho |
| S5 | 1 | Zero arquivos órfãos |
| S6 | 4 | Metadados da capa |
| **S7** | **1** | **Todos os .tex UTF-8 válidos** |
| **S8** | **1** | **Todas as citações no .bib** |
| **S9** | **1** | **Labels únicos (sem duplicatas)** |
| W1 | 1 | Blocos de código Python (info) |
| W2 | 1 | Tabelas de métricas (info) |
| W3 | 7 | Ferramentas referenciadas |

---

## 📄 Licença

Este trabalho está licenciado sob **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International** (CC BY-NC-SA 4.0).

---

## 🤝 Como Contribuir

1. Faça um fork do repositório
2. Crie uma branch (`git checkout -b feature/nova-contribuicao`)
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

### Diretrizes

- Todos os arquivos .tex devem ser UTF-8 válidos
- Execute `.tdd_validate_v2.py` antes de submeter
- Mantenha o padrão V2 (standalone, badges, footnotes, exercícios)
- Respeite o `.gitignore` (`.evolve/` não é commitado)

---

## 📬 Contato

**Marcelo Claro** — Arquiteto do OpenCode Ecosystem

- GitHub: [@MarceloClaro](https://github.com/MarceloClaro)
- Trabalho original: [OpenCode Ecosystem](https://github.com/MarceloClaro/OpenCode_Ecosystem)

---

> *"O gêmeo digital não é uma fotografia tridimensional; é um sistema cibernético vivo que evolui simbioticamente com o estado fisiológico do paciente."*
