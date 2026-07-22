# SPEC-950: Livro "Odontologia & Inteligência Artificial — Da História aos Gêmeos Digitais"

## Metadados

| Campo | Valor |
|---|---|
| **SPEC ID** | SPEC-950 |
| **Título** | Odontologia & Inteligência Artificial: Da História aos Gêmeos Digitais |
| **Autor** | marceloclaro (Orquestrador Central) |
| **Versão** | 1.0.0 |
| **Data** | 2026-07-09 |
| **Status** | `em_especificacao` |
| **Gate** | SDD+TDD+RigorQualisA1 |
| **Público-alvo** | Cirurgiões-dentistas, estudantes de odontologia, cientistas da computação, pesquisadores IA, nível 0 (leigo) até PhD |
| **Idioma** | Português (BR) + códigos Python comentados em português |

---

## 1. Escopo e Justificativa

### 1.1 Problema
Não existe na literatura um livro **autodidático, progressivo e prático** que:
- Una odontologia clínica E programação Python/Google Colab
- Use metodologia **SDD + TDD** (Spec-Driven & Test-Driven Development)
- Tenha nível de dificuldade explícito 🟢🟡🔴 em cada seção
- Cite artigos **reais com DOI/links ativos**
- Use imagens reais de artigos com permissão de citação acadêmica
- Passe por **banca Qualis A1** rigorosa

### 1.2 Solução Proposta
Um livro-texto de ~800-1200 páginas (formato LaTeX → PDF) dividido em **15 capítulos** + apêndices, cobrindo:

```
Parte I —  FUNDAMENTOS (Cap 1-3)   🟢 Nível 0-3
Parte II —  TEORIA & MODELOS (Cap 4-7)   🟡 Nível 4-7
Parte III — PRÁTICA SDD/TDD (Cap 8-11)   🔴 Nível 6-9
Parte IV —  APLICAÇÕES AVANÇADAS (Cap 12-15)   🔴 Nível 8-PhD
```

---

## 2. Sumário Detalhado com Níveis de Dificuldade

### 🟢 PARTE I — FUNDAMENTOS (Nível 0 a 3)

#### Capítulo 1: A Jornada da Odontologia Digital
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 1.1 A odontologia antes dos computadores | 🟢 | História clínica, anotações manuais, radiografia analógica |
| 1.2 A revolução da informática odontológica | 🟢 | Schleyer (2001, 2003) — informática odontológica como disciplina |
| 1.3 Primeiros sistemas especialistas | 🟡 | Hammond (1993), Brickley (1998) — regras vs redes neurais |
| 1.4 A transição para o aprendizado de máquina | 🟡 | Khanagar (2021) — revisão sistemática de 20 anos |
| 1.5 Big data e odontologia baseada em evidências | 🟢 | Conceito, importância, exemplos clínicos |
| 1.6 O estado da arte em 2026 | 🟡 | González Herrera (2025) — bibliometria VOSviewer |
| 🧪 **Prática 1.1** — Setup do Google Colab | 🟢 | Primeiro notebook: "Oi Odontologia + IA" |

**Citações chave:** Schleyer (2001, 2003), Brickley (1998), Hammond (1993), Khanagar (2021), González Herrera (2025)

#### Capítulo 2 — Introdução à Inteligência Artificial
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 2.1 O que é inteligência? Definições históricas | 🟢 | Turing, McCarthy, Minsky |
| 2.2 Machine Learning: a arte de aprender com dados | 🟡 | Definição formal (Mitchell, 1997) |
| 2.3 Tipos de aprendizado | 🟡 | Supervisionado, não-supervisionado, por reforço |
| 2.4 Deep Learning: redes neurais profundas | 🟡 | Perceptron → MLP → CNN → Transformer |
| 2.5 A matemática por trás: álgebra linear essencial | 🟡 | Vetores, matrizes, gradiente descendente |
| 2.6 Métricas de avaliação | 🟢 | Acurácia, sensibilidade, especificidade, AUC-ROC |
| 🧪 **Prática 2.1** — Primeira rede neural no Colab | 🟡 | MLP para classificação simples (Keras) |
| 🧪 **Prática 2.2** — Testes com Pytest no Colab | 🟡 | TDD: testar acurácia mínima |

**Notas de rodapé:** ²¹Turing Test; ²²Função de ativação sigmoide; ²³Gradiente descendente: ∂L/∂w

#### Capítulo 3 — Python para Odontólogos
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 3.1 Por que Python na odontologia? | 🟢 | Ecossistema científico |
| 3.2 Variáveis, tipos e estruturas de dados | 🟢 | listas, dicts, arrays NumPy |
| 3.3 NumPy e operações matriciais | 🟡 | Tensores para imagens |
| 3.4 Pandas para dados clínicos | 🟡 | DataFrames de pacientes |
| 3.5 Matplotlib e Seaborn: visualização | 🟡 | Gráficos ROC, curvas de perda |
| 3.6 Google Colab: GPU grátis na nuvem | 🟢 | Drive, runtime, células |
| 🧪 **Prática 3.1** — SDD: spec de função de IMC odontológico | 🟢 | Spec → Test → Code |
| 🧪 **Prática 3.2** — TDD: validação de idade gestacional odontológica | 🟡 | RED → GREEN → REFACTOR |

---

### 🟡 PARTE II — TEORIA E MODELOS (Nível 4 a 7)

#### Capítulo 4 — Processamento de Imagens Odontológicas
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 4.1 Fundamentos de imagens digitais | 🟡 | Pixels, canais, resolução, DICOM |
| 4.2 Radiografias odontológicas e seus formatos | 🟡 | Panorâmica, periapical, bitewing, CBCT |
| 4.3 Pré-processamento: equalização, normalização, augmentação | 🟡 | CLAHE, histogram matching, GANs |
| 4.4 Segmentação de imagens: fundamentos | 🟡 | Thresholding, watershed, regiões |
| 4.5 Aumento de dados com GANs em odontologia | 🔴 | Kwak et al. (2024) — GANs para aumento de radiografias |
| 🧪 **Prática 4.1** — SDD: pipeline de pré-processamento | 🟡 | Spec → Test → Code → Refactor |
| 🧪 **Prática 4.2** — Visualização Grad-CAM | 🔴 | XAI em radiografia panorâmica |

**Imagens:** Figuras de Schleyer (2003), Schwendicke (2020), Kwak et al. (2024)

#### Capítulo 5 — Redes Neurais Convolucionais (CNNs) para Diagnóstico Bucal
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 5.1 A arquitetura da visão computacional | 🟡 | Convolução, pooling, ReLU, camadas densas |
| 5.2 Aritmética de convoluções | 🟡 | Kernel, stride, padding, mapas de ativação |
| 5.3 Arquiteturas clássicas | 🟡 | LeNet, AlexNet, VGG, ResNet, Inception |
| 5.4 Transfer Learning em odontologia | 🟡 | Modelos pré-treinados, fine-tuning |
| 5.5 Classificação de cáries com CNNs | 🔴 | Rohban (2024) — meta-análise 87 estudos |
| 5.6 Detecção de lesões bucais malignas | 🔴 | CNNs para carcinoma oral |
| 5.7 Explainable AI (XAI) em radiografias | 🔴 | Grad-CAM, LIME, SHAP na prática clínica |
| 🧪 **Prática 5.1** — TDD: CNN para classificação de cáries | 🟡 | Spec → RED → GREEN → REFACTOR |
| 🧪 **Prática 5.2** — Fine-tuning ResNet50 | 🔴 | Transfer learning + testes de acurácia |

**Citações chave:** Rohban (2024), Bayrakdar (2024), Golkarieh (2025), arch. originais ResNet

#### Capítulo 6 — Segmentação Semântica e Instance-Level
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 6.1 O problema da segmentação em imagens médicas | 🟡 | Pixel-wise classification |
| 6.2 U-Net: a arquitetura encoder-decoder | 🔴 | Ronneberger (2015), U-Net para bioimagens |
| 6.3 Atenção e gates em segmentação | 🔴 | Deb (2023) — grid-aware attention, DNS dataset |
| 6.4 Mask R-CNN e detecção instance-level | 🔴 | He et al. (2017), detecção de dentes |
| 6.5 YOLO para detecção em tempo real | 🔴 | YOLOv8 + OralBBNet (Budagam 2024) |
| 6.6 Transformers em segmentação odontológica | 🔴 | Swin Transformer, ViT para CBCT |
| 🧪 **Prática 6.1** — TDD: U-Net para segmentação de dentes | 🔴 | Dataset DNS, Dice Loss, IoU |
| 🧪 **Prática 6.2** — Avaliação: Dice Score + IoU | 🔴 | Testes de métricas de segmentação |

**Citações:** Ronneberger (2015), Deb (2023), Budagam (2024), He (2017), Yang (2025 DE-KAN)

#### Capítulo 7 — Radiologia Odontológica com Deep Learning
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 7.1 Radiografia panorâmica: o padrão ouro populacional | 🟡 | Técnica, indicações, limitações |
| 7.2 CBCT e tomografia computadorizada | 🟡 | Aplicações, dose de radiação, voxels |
| 7.3 Detecção de cáries e restaurações | 🔴 | Rohban (2024), Bayrakdar (2024) |
| 7.4 Classificação de qualidade óssea | 🔴 | Lee (2024), Pornvoranant (2024) |
| 7.5 Lesões periapicais e cistos | 🔴 | DL em radiografias periapicais |
| 7.6 Anomalias dentárias e patologias | 🔴 | CNN em condições raras |
| 🧪 **Prática 7.1** — TDD: classificador de qualidade óssea | 🔴 | Spec → Treino → Teste |
| 🧪 **Prática 7.2** — Comparação humano vs IA | 🔴 | Métricas estatísticas, Kappa de Cohen |

---

### 🔴 PARTE III — PRÁTICA SDD/TDD (Nível 6 a 9)

#### Capítulo 8 — Metodologia Spec-Driven Development (SDD)
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 8.1 O que é SDD? | 🟡 | Especificação formal antes da implementação |
| 8.2 Specs para odontologia | 🟡 | "Spec-driven oral diagnosis" |
| 8.3 Escrevendo specs: critérios de aceitação | 🟡 | Given-When-Then |
| 8.4 O ciclo SDD | 🟡 | Spec → Implement → Verify → Deploy |
| 8.5 SDD vs metodologias ágeis | 🟡 | Diferenças e complementaridades |
| 🧪 **Prática 8.1** — SDD: spec para detector de cáries | 🟡 | MSC: "detectar_carie(img) → (x,y,w,h,confiança)" |

#### Capítulo 9 — Test-Driven Development (TDD) em Python Odontológico
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 9.1 Filosofia RED-GREEN-REFACTOR | 🟡 | O ciclo TDD completo |
| 9.2 Pytest e unittest no Colab | 🟡 | Setup, asserts, fixtures |
| 9.3 Testes para pré-processamento | 🟡 | TDD em pipelines de imagem |
| 9.4 Testes para modelos de ML | 🔴 | Mocking, fixtures, tolerâncias |
| 9.5 Testes de integração | 🔴 | Pipeline completo |
| 9.6 CI/CD para odontologia IA | 🔴 | GitHub Actions, test coverage |
| 🧪 **Prática 9.1** — TDD: função "avaliar_perda_ossea()" | 🟡 | RED → GREEN → REFACTOR |
| 🧪 **Prática 9.2** — TDD: pipeline de segmentação | 🔴 | Spec → Test → Code → Refactor |

#### Capítulo 10 — Projetos Guiados (SDD+TDD)
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 10.1 Projeto 1: Classificador de lesões bucais | 🔴 | Spec → Test → CNN Treino → Validação |
| 10.2 Projeto 2: Segmentador de dentes CBCT | 🔴 | U-Net do zero com TDD |
| 10.3 Projeto 3: Detector de cáries em bitewing | 🔴 | YOLOv8 customizado, spec-driven |
| 10.4 Projeto 4: Analisador de perda óssea periodontal | 🔴 | ML clássico + CNN, pipeline testado |
| 10.5 Publicação no Hugging Face Hub | 🟡 | Modelo + demo Gradio + testes |

#### Capítulo 11 — Interpretação de Modelos e Resultados
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 11.1 Matriz de confusão: interpretação odontológica | 🟡 | FN = cárie não detectada, FP = alarme falso |
| 11.2 Curvas ROC e AUC | 🟡 | Significado clínico |
| 11.3 Grad-CAM na prática | 🔴 | "Onde a CNN está olhando?" |
| 11.4 SHAP para features não-imagem | 🔴 | Importância de cada preditor clínico |
| 11.5 Viés e fairness em IA odontológica | 🔴 | Dados desbalanceados, etnias |
| 11.6 Escrevendo relatórios de resultados | 🟡 | Tabelas, figuras, interpretação |
| 🧪 **Prática 11.1** — Grad-CAM visual + testes | 🔴 | XAI testável |

---

### 🟣 PARTE IV — APLICAÇÕES AVANÇADAS (Nível 8-PhD)

**Legenda:** 🟣 PhD-level — requer domínio de programação e odontologia

#### Capítulo 12 — IA em Periodontia
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 12.1 Periodontite: classificação 2018 | 🟡 | Novos critérios de estágio e grau |
| 12.2 Detecção de perda óssea em radiografias | 🔴 | Chang et al. (2024), DL em periodontia |
| 12.3 Deep Learning para recessão gengival | 🔴 | Segmentação de margem gengival |
| 12.4 Predição de progressão da doença | 🟣 | Modelos longitudinais, séries temporais |
| 12.5 Periodontia de precisão com IA | 🟣 | Biomarcadores, microbioma, aprendizado multimodal |
| 🧪 **Prática 12.1** — TDD: perda óssea alveolar | 🔴 | U-Net + métricas periodontais |
| 🧪 **Prática 12.2** — SDD: spec de predição de risco | 🟣 | Dados clínicos, tabagismo, DM, PCR |

#### Capítulo 13 — Gêmeos Digitais em Odontologia
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 13.1 Conceito de Digital Twin | 🟡 | Gêmeo digital vs modelo 3D vs simulação |
| 13.2 O gêmeo digital do paciente odontológico | 🔴 | Integração CBCT + scanner intraoral + fotos |
| 13.3 Planejamento virtual de implantes | 🟣 | Dinâmica de fluidos, FEM, osseointegração |
| 13.4 Gêmeos digitais de restaurações | 🟣 | Simulação mastigatória, FEM |
| 13.5 Simulação de tratamento ortodôntico | 🟣 | Predição de movimento dentário |
| 13.6 O futuro: hospitais odontológicos virtuais | 🟣 | Integração multiescala, IoT, IA no loop |
| 🧪 **Prática 13.1** — TDD: modelo simplificado de gêmeo digital | 🟣 | Spec → Simulação → Teste |
| 🧪 **Prática 13.2** — SDD: arquitetura de Digital Twin | 🟣 | Spec formal de integração de dados |

#### Capítulo 14 — Large Language Models (LLM) na Odontologia
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 14.1 O que são LLMs? | 🟡 | GPT, LLaMA, Claude — arquitetura transformer |
| 14.2 Aplicações clínicas de LLMs | 🟡 | Documentação, prontuários, laudos |
| 14.3 RAG em odontologia | 🔴 | Retrieval-Augmented Generation para literatura |
| 14.4 LLMs multilingues em odontologia | 🟣 | Avaliação de respostas odontológicas |
| 14.5 Agentes autônomos odontológicos | 🟣 | Planejamento de tratamento automático |
| 14.6 Limitações e alucinações | 🟣 | Verificação de fontes, riscos clínicos |
| 🧪 **Prática 14.1** — LLM + RAG + TDD no Colab | 🟣 | Pipeline de QA odontológico |

#### Capítulo 15 — O Futuro da Odontologia com IA
| Seção | Nível | Descrição |
|-------|-------|-----------|
| 15.1 Bioimpressão 3D e IA generativa | 🟣 | Tecidos, biomateriais, desenho generativo |
| 15.2 IA na educação odontológica | 🟣 | Simuladores inteligentes, feedback |
| 15.3 Ética, regulamentação e privacidade | 🟡 | LGPD, FDA, CFM/CFO |
| 15.4 O dentista na era da IA | 🟢 | Nova definição de papéis |
| 15.5 Linhagem de progressão do leitor | 🟢 | De onde você veio, aonde pode chegar |

---

## 3. Metodologia Pedagógica

### 3.1 Sistema de Marcação de Dificuldade

| Símbolo | Nível | Pré-requisito | Descrição |
|---------|-------|---------------|-----------|
| 🟢 | 0-3 | Nenhum | Odontologia básica, sem programação |
| 🟡 | 4-7 | Python básico, conceitos de ML | Teoria com prática guiada |
| 🔴 | 6-9 | Python intermediário, ML | Implementação completa, TDD |
| 🟣 | 8-PhD | Programação avançada, álgebra linear | Pesquisa de ponta, arquiteturas |

### 3.2 Estrutura de Cada Seção

```
┌─────────────────────────────────────────┐
│ [Título da Seção]           🟢/🟡/🔴/🟣 │
├─────────────────────────────────────────┤
│ Texto principal com citações [ref]      │
│                                         │
│ 📝 Nota de Rodapé: explicação extra     │
│                                         │
│ 🖼️ Figura X: [descrição] (Fonte: autor) │
│                                         │
│ 💻 Código: (Colab link)                 │
│ 🔬 Teste TDD: assert modelo.output...   │
│ 📊 Resultado: SAÍDA DO TESTE            │
│ ─────────────────────────────────────── │
│ Nível atual: 2 → 3 (você está aqui)     │
└─────────────────────────────────────────┘
```

### 3.3 Trilha de Aprendizagem

```
Módulo 0 (🟢 Cap 1-3):  "Nunca programei, sei o que é cárie" → "Rodo Python no Colab"
Módulo 1 (🟡 Cap 4-5):  "Entendo CNNs" → "Faço fine-tuning"
Módulo 2 (🟡🔴 Cap 6-7): "Segmento dentes" → "Classifico lesões"
Módulo 3 (🔴 Cap 8-11):  "Escrevo specs" → "TDD em pipeline completo"
Módulo 4 (🟣 Cap 12-15): "Pesquiso periodontia IA" → "Crio gêmeo digital"
```

---

## 4. Especificação Técnica de Código

## 4.1 Template de Cada Notebook (Colab)

```python
# ========================================
# Capítulo X — Seção Y
# Nível: 🟢/🟡/🔴/🟣
# Spec: SPEC-LIVRO-ODT-CAPX-SECY
# ========================================

# SDD: Especificação formal da função/projeto
"""
SPEC: detectar_caries(img: np.ndarray) -> List[BoundingBox]
- Given: radiografia panorâmica 512x512
- When: executada
- Then: retorna lista de (x, y, w, h, confidence) para cáries detectadas
- Acceptance: confidence > 0.5, IoU com ground truth > 0.5
"""

# TDD: Testes antes da implementação
import pytest
import numpy as np

def test_detectar_caries_saida_valida():
    """Teste falha (RED) inicial"""
    img = np.zeros((512, 512), dtype=np.uint8)
    resultado = detectar_caries(img)
    assert isinstance(resultado, list), "Deve retornar lista"
    assert len(resultado) >= 0

# Implementação (GREEN)
def detectar_caries(img):
    # Placeholder: implementação real no capítulo
    return []

# Refatoração (REFACTOR)
# Será refinada ao longo do capítulo

# Execução dos testes
pytest.main(["-v", "test_capX_secaoY.py"])
```

### 4.2 Template de Testes (pytest)

```python
# test_livro_capX.py
import pytest
import numpy as np
from models.segmentador import SegmentadorDental

class TestSegmentadorDental:
    @pytest.fixture
    def img_mock(self):
        return np.random.rand(512, 512, 3).astype(np.float32)
    
    def test_segmentacao_dice_minimo(self, img_mock):
        seg = SegmentadorDental()
        pred = seg.predict(img_mock)
        # Dice mínimo contra baseline
        assert seg.dice_score(pred, img_mock) > 0.5
```

---

## 5. Critérios de Aceitação (Gate SDD)

| Critério | Descrição | Métrica |
|----------|-----------|---------|
| **CA-1** | Cada capítulo possui ≥10 referências com DOI | Verificação de links |
| **CA-2** | Cada seção prática tem SDD → TDD | RED → GREEN → REFACTOR |
| **CA-3** | Nível de dificuldade claramente marcado | Marcador 🟢🟡🔴🟣 |
| **CA-4** | Imagens reais de artigos com fonte | Referência à figura original |
| **CA-5** | Notas de rodapé explicativas | ≥3 notas por seção |
| **CA-6** | Código executável e testado | pytest passando |
| **CA-7** | Banca Qualis A1: revisão por pares emulada | Checklist de 50 itens |
| **CA-8** | Leitores nível 0 entendem | Termo de compromisso |

---

## 6. Pipeline de Produção

```
Fase 1: PESQUISA E REFERÊNCIAS
   ├── Busca PubMed (65 artigos) ✓
   ├── Busca arXiv (35 artigos técnicos) ✓
   ├── Curadoria de imagens
   └── Validação de DOIs ativos

Fase 2: SDD + ESCRITA (Especificação formal)
   ├── SPEC-950 (este doc) → Revisado
   ├── Criação de diretório /livro-odontologia-ia
   ├── Template LaTeX principal (book class)
   ├── Template .tex para cada capítulo
   └── Makefile de compilação xelatex

Fase 3: IMPLEMENTAÇÃO DE CÓDIGO
   ├── Notebooks Python/Colab
   ├── Testes TDD (pytest)
   ├── Scripts de treinamento
   └── Integração com dados públicos (DNS, UFBA)

Fase 4: REVISÃO (Banca Qualis A1)
   ├── 42 agentes MASWOS para revisão
   ├── Correção textual Qualis
   ├── Consistência interna
   └── Blind review

Fase 5: EXPORTAÇÃO
   ├── LaTeX → PDF (xelatex)
   ├── ePub opcional
   ├── Repositório GitHub público
   └── Publicação DOI
```

---

## 7. Fontes de Dados e Datasets

### Datasets Públicos Identificados

| Dataset | Descrição | Artigos |
|---------|-----------|---------|
| DNS Dataset | 543 radiografias panorâmicas | Deb (2023) |
| UFBA-425 | 425 panorâmicas com bounding boxes | Budagam (2024) |
| Dental Condition Dataset | 1.512 panorâmicas, 11.137 anotações | Golkarieh (2025) |
| CBCT slices (Tailandês) | 1100 slices cross-section | Pornvoranant (2024) |
| TUEG Dataset | Radiografias periapicais | Diversos |

---

## 8. Agendamento

| Etapa | Prazo | Responsável |
|-------|-------|-------------|
| Base de referências (100 artigos) | Concluído ✓ | Researcher |
| SDD do livro | Concluído ✓ | marceloclaro |
| Template LaTeX | Dia 1-2 | Technical Writer |
| Capítulos 1-5 | Dia 3-7 | Academic Writer |
| Capítulos 6-10 | Dia 8-14 | Academic Writer + Coder |
| Capítulos 11-15 | Dia 15-21 | Academic Writer |
| Códigos e testes | Dia 10-21 | Coder + Test Engineer |
| Revisão MASWOS | Dia 22-25 | 39 agentes MASWOS |
| Banca Qualis A1 | Dia 25-28 | Auditor + Reviewer |
| Correções finais | Dia 29-30 | Corrector + Integrator |
| PDF final | Dia 30 | Technical Writer |
| Publicação | Dia 31 | Publishing Agent |

---

## 9. Aprovação

| Gate | Status | Observação |
|------|--------|------------|
| SDD Spec | ✅ Aprovado | Critérios de aceitação definidos |
| Base de referências | ✅ Aprovado | 100 artigos com DOI |
| Template | ⏳ Pendente | Criar estrutura LaTeX |
| Códigos de exemplo | ⏳ Pendente | Implementar notebooks |

---

**SPEC-950 aprovada em 2026-07-09 por marceloclaro (Orquestrador Central)**

*Próximo passo: Criar estrutura de diretórios e template LaTeX principal*