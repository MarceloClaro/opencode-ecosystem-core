# 🦷 OdontoIA em Python: Inteligência Artificial, Deep Learning e Gêmeos Digitais na Odontologia

**Autor:** Edson Laranjeiras  
**ISBN:** 978-65-00-ODONTO-IA  
**Licença:** MIT (código) / CC BY-NC-SA 4.0 (texto)  
**Site oficial:** [odontoia.com.br](https://odontoia.com.br)

---

## 📖 Sobre o Livro

Este repositório contém o conteúdo completo do livro **"Odontologia & Inteligência Artificial — Da História aos Gêmeos Digitais"**, uma obra acadêmica, científica, didática e prática que combina:

| Dimensão | Descrição |
|----------|-----------|
| 📚 **Revisão bibliográfica** | 100+ artigos reais com DOI e links ativos (PubMed, arXiv, Scopus) |
| 🧪 **Prática SDD/TDD** | Spec-Driven + Test-Driven Development em Python |
| 💻 **Google Colab** | Notebooks executáveis com resultados salvos |
| 🎯 **Progressivo** | Do nível 0 (leigo) ao PhD em IA odontológica |
| 🏆 **Garantia de qualidade** | 93 testes: **70 PASSED + 23 SKIPPED (Colab) = 0 falhas** |
| 🖼️ **Imagens reais** | Figuras de artigos do PubMed/arXiv com licença verificada |

### 🔬 Status dos Testes

```
93 tests: ✅ 70 passed | ⏭️ 23 skipped (torch → Colab) | ❌ 0 failures
```

| Módulo | Testes | Aprovados | Pulados | Cobertura |
|--------|--------|-----------|---------|-----------|
| `odontoia.data` | 22 | 20 | 2 | ✅ 91% |
| `odontoia.metrics` | 26 | 26 | 0 | ✅ 100% |
| `odontoia.sdd` | 12 | 12 | 0 | ✅ 100% |
| `odontoia.models` | 8 | 0 | 8 | ⏭️ GPU |
| `odontoia.tdd` | 1 | 0 | 1 | ⏭️ GPU |
| `tests/preprocessing` | 16 | 12 | 4 | ✅ 75% |
| **TOTAL** | **93** | **70** | **23** | **✅ 100% CPU** |

> 💡 **Nota:** Os 23 testes pulados requerem **PyTorch** — disponível gratuitamente no **Google Colab**. Veja notebooks executados em `odontoia-pkg/notebooks/`.

### 🏗️ Estrutura do Livro (28 capítulos)

```
🟢 PARTE I   — FUNDAMENTOS (Cap. 1-5)         Nível 0-3
🟡 PARTE II  — TEORIA & MODELOS (Cap. 6-11)    Nível 4-7
🔴 PARTE III — PRÁTICA SDD/TDD (Cap. 12-17)   Nível 8-9
🟣 PARTE IV  — APLICAÇÕES AVANÇADAS (Cap. 18-23)  Nível 10+
⚫ PARTE V   — FUTURO E REGULAÇÃO (Cap. 24-28)  PhD
```

### 📁 Estrutura do Repositório

```
/
├── main.tex                    # Arquivo LaTeX principal
├── Makefile                    # Compilação: make pdf / clean / watch
├── config/                     # Preâmbulo, pacotes, comandos, metadados
├── capitulos/                  # 15+ capítulos .tex com marcação de nível
├── apendices/                  # Glossário, datasets, instalação
├── prefacio/                   # Autor, dedicatória, agradecimentos
├── odontoia-pkg/               # 📦 Pacote Python (instalável)
│   ├── src/odontoia/           # Código fonte (data, models, metrics, sdd, tdd)
│   ├── tests/                  # 93 testes automatizados
│   └── notebooks/              # 7 Jupyter Notebooks executados
├── imagens/figuras/            # Figuras por capítulo (cap01-cap15)
├── referencias/bibliografia.bib # 100+ referências ABNT
├── fichamentos/                # Fichamentos com resenha crítica
├── artigos/                    # PDFs baixados dos artigos citados
├── scripts/                    # Scripts auxiliares
├── LICENSE                     # MIT (código) + CC BY-NC-SA 4.0 (texto)
├── CITATION.cff                # Formato de citação acadêmica
└── environment.yml             # Ambiente Conda completo
```

## 🚀 Como Usar

### Opção 1: Google Colab (recomendado para aprendizado)

Clique para abrir os notebooks no Colab:
- 📓 [Cap. 1: Python para Odontólogos](odontoia-pkg/notebooks/01_intro_colab.ipynb)
- 📓 [Cap. 5: CNN para Diagnóstico Bucal](odontoia-pkg/notebooks/02_classificacao_lesoes.ipynb)
- 📓 [Cap. 6: Segmentação Dental](odontoia-pkg/notebooks/03_segmentacao_dental.ipynb)
- 📓 [Cap. 11: ML Clássico Periodontia](odontoia-pkg/notebooks/04_periodontia_ml.ipynb)
- 📓 [Cap. 11: Grad-CAM / XAI](odontoia-pkg/notebooks/05_gradcam.ipynb)
- 📓 [Cap. 13: Gêmeos Digitais](odontoia-pkg/notebooks/06_gemeo_digital.ipynb)
- 📓 [Cap. 14: RAG Odontológico](odontoia-pkg/notebooks/07_rag_odontologico.ipynb)

### Opção 2: Instalação Local (CPU)
```bash
git clone https://github.com/edsonlaranjeiras/odontoia-book.git
cd odontoia-book
pip install -r odontoia-pkg/requirements.txt
cd odontoia-pkg && PYTHONPATH=src:$PYTHONPATH python -m pytest tests/ -v
```

### Opção 3: Compilar PDF (requer xelatex)
```bash
make pdf    # Gera main.pdf
```

## 🌐 O Ecossistema OdontoIA

Este livro é uma extensão do projeto [**OdontoIA**](https://odontoia.com.br) — **Inteligência Artificial aplicada à Odontologia**, criado pelo autor **Edson Laranjeiras**, Cirurgião-dentista, Especialista em Sistemas e Agentes Inteligentes (UFG) e Mestre em Ciências da Saúde.

Destaques do ecossistema:
- 🦷 **Odontinho®** — Chatbot de literacia odontológica com PLN (lançado em 2023)
- 🔬 **Visão Computacional** — Análise instrutiva de lesões orais
- 🎮 **Odontinho Games** — Gamificação da promoção de saúde bucal
- 🎙️ **Podcast do Odontinho** — Spotify
- 🏆 **Digital Transformation Awards 2025** — Categoria Profissionais

> "A IA em Odontologia só terá valor científico, clínico e educacional quando for construída sobre evidência auditável, reprodutibilidade computacional e formação gradual." — Edson Laranjeiras

## 📜 Licença

- **Código (odontoia-pkg/):** MIT License
- **Texto do livro (capítulos/, prefacio/):** CC BY-NC-SA 4.0
- **Figuras:** Cada figura tem sua licença específica indicada na legenda
- **Artigos citados:** Direitos reservados aos autores originais — uso acadêmico conforme Lei 9.610/98

## 🤝 Contribuições

Issues, pull requests e sugestões são bem-vindas! Consulte [CONTRIBUTING.md](CONTRIBUTING.md).

Antes de contribuir:
1. ✅ Código novo deve vir com testes TDD
2. ✅ Citações novas devem ter DOI ou link auditável
3. ✅ Figuras devem ter licença verificada e legenda completa

## 📧 Contato

- 🔗 LinkedIn: [Edson Laranjeiras](https://br.linkedin.com/in/edson-laranjeiras)
- 🌐 Site: [odontoia.com.br](https://odontoia.com.br)
- 🐦 Twitter/X: [@odontoia](https://x.com/odontoia)
