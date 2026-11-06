# odontoia — Odontologia & Inteligência Artificial

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v1.json)](https://python-poetry.org/)

**odontoia** é o pacote Python central do livro *"Odontologia & Inteligência Artificial"*, de Edson Laranjeiras. Ele reúne implementações didáticas e reprodutíveis de modelos de aprendizado de máquina e deep learning aplicados ao diagnóstico bucal, segmentação de radiografias, detecção de lesões, métricas clínicas, explicação de modelos (Grad-CAM), gêmeos digitais e muito mais.

## 🦷 Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| `odontoia.data` | Carregamento de datasets odontológicos (DNS, UFBA, OdontoAI), DICOM e radiografias panorâmicas |
| `odontoia.preprocessing` | Pré-processamento de imagens: normalização, CLAHE, redimensionamento, tensorização |
| `odontoia.augment` | Aumento de dados odontológico (rotação, espelhamento, ruído, corte adaptativo) |
| `odontoia.models` | CNNs didáticas, U-Net para segmentação, YOLO simplificado, ML clássico para periodontia, gêmeos digitais |
| `odontoia.metrics` | Métricas clínicas: acurácia, sensibilidade, especificidade, F1, Dice, IoU, Kappa, AUC |
| `odontoia.visualization` | Grad-CAM, curvas ROC, matrizes de confusão, relatórios clínicos |
| `odontoia.sdd` | Specification-Driven Development: decorador `@spec` e validador formal |
| `odontoia.tdd` | Helpers para TDD odontológico: pacientes mockados, radiografias sintéticas, asserções clínicas |

## 📦 Instalação

### Via pip (recomendado para uso)

```bash
pip install git+https://github.com/marceloclaro/opencode-ecosystem-core.git#subdirectory=livro-odontologia-ia/odontoia-pkg
```

### Modo desenvolvimento

```bash
git clone https://github.com/marceloclaro/opencode-ecosystem-core.git
cd opencode-ecosystem-core/livro-odontologia-ia/odontoia-pkg
pip install -e ".[dev,notebooks]"
```

### Via Poetry

```bash
poetry install --with dev,notebooks
```

## 🚀 Exemplo rápido

```python
from odontoia.data import load_panoramic
from odontoia.preprocessing import clahe_equalization, resize_with_aspect
from odontoia.models.cnn import build_simple_cnn

# Carrega e processa uma radiografia panorâmica
img = load_panoramic("exemplo.dcm")
img = clahe_equalization(img)
img = resize_with_aspect(img, (256, 256))

# Constrói e treina uma CNN didática
model = build_simple_cnn(input_shape=(256, 256, 1), n_classes=3)
model.summary()
```

## 🧪 Testes

```bash
pytest tests/ -v --cov=src/odontoia
```

## 📓 Notebooks

Os notebooks no diretório `notebooks/` acompanham os capítulos do livro:

| Notebook | Capítulo | Tema |
|----------|----------|------|
| `01_intro_colab.ipynb` | 1 | Configuração Google Colab |
| `02_classificacao_lesoes.ipynb` | 5 | CNN para classificação de lesões |
| `03_segmentacao_dental.ipynb` | 6 | U-Net para segmentação |
| `04_periodontia_ml.ipynb` | 12 | ML clássico em periodontia |
| `05_gradcam.ipynb` | 11 | Explicabilidade com Grad-CAM |
| `06_gemeo_digital.ipynb` | 13 | Gêmeos digitais |
| `07_rag_odontologico.ipynb` | 14 | RAG odontológico |

## 📄 Licença

MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Este pacote segue os princípios de **Specification-Driven Development (SDD)** e **Test-Driven Development (TDD)**. Veja o capítulo 8 do livro para detalhes sobre SDD.

---

*"A tecnologia não substitui o cirurgião-dentista — amplia sua visão, precisão e capacidade de cuidar."* — Edson Laranjeiras