# Model Card — Template (FUTURE-AI)

> **Baseado em:** Mitchell M, et al. *Model Cards for Model Reporting.* Proceedings of FAT*, 2019.*
> **Estendido com:** Princípios FUTURE-AI (Lekadir et al. 2025)

---

## 1. Model Details

- **Nome do modelo:**
- **Versão:**
- **Data de lançamento:**
- **Tipo de modelo:** (CNN, transformer, random forest, etc.)
- **Framework:** (PyTorch, TensorFlow, scikit-learn, etc.)
- **Linguagem:**
- **Licença:**
- **Autores/Owners:**
- **Contato:**
- **Dataset usado no treino:** (DOI ou link)

## 2. Intended Use

### 2.1 Primary Use
- **Aplicação clínica:**
- **População-alvo:**
- **Setting:** (primário, secundário, ambulatório, hospitalar)
- **Usuários:** (dentistas, radiologistas, assistentes)

### 2.2 Out-of-Scope Use
- ❌ **Não usar para:** (decisão final sem revisão humana, diagnóstico autônomo)
- ❌ **Não validado para:** (populações fora do dataset de treino)

## 3. Training Data

- **Fonte:** (hospital, banco, ensaio)
- **Tamanho:** (número de imagens, número de classes)
- **Período:** (datas de coleta)
- **Demografia:** (idade, sexo, etnia)
- **Pré-processamento:**
- **Data augmentation:**
- **Split:** (treino/validação/teste, %)
- **Ground truth:** (histopatologia, especialistas, etc.)
- **DOI dataset:** 

## 4. Evaluation Results

### 4.1 Overall Performance
- **AUC-ROC:**
- **Accuracy:**
- **Sensitivity:**
- **Specificity:**
- **F1-Score:**
- **Confidence Interval (95%):**

### 4.2 Performance by Subgroup
| Subgrupo | AUC | Sens | Spec | F1 | n |
|----------|-----|------|------|-----|---|
| Idade < 18 |  |  |  |  |  |
| Idade 18-65 |  |  |  |  |  |
| Idade > 65 |  |  |  |  |  |
| Feminino |  |  |  |  |  |
| Masculino |  |  |  |  |  |
| Etnia A |  |  |  |  |  |
| Etnia B |  |  |  |  |  |

### 4.3 Confusion Matrix
```
                Predito
              Neg   Pos
Real  Neg    [TN]  [FP]
Real  Pos    [FN]  [TP]
```

### 4.4 Calibration
- **Brier Score:**
- **Hosmer-Lemeshow p-value:**
- **Calibration plot:** [anexar]

## 5. Ethical Considerations

### 5.1 Privacy
- **LGPD/GDPR compliance:**
- **Anonymization:** (sim/não, técnica)
- **Consent:**

### 5.2 Bias and Fairness
- **Bias audit:** (sim/não)
- **Disparate impact ratio:** (por subgrupo)
- **Mitigation strategies:**

### 5.3 Risks
- **Falso negativo:** (consequências clínicas)
- **Falso positivo:** (consequências clínicas)
- **Mitigation:** (revisão humana, threshold ajustado)

## 6. Model Lineage (FUTURE-AI — Traceability)

- **Versão anterior:** (v1.0, etc.)
- **Mudanças nesta versão:**
- **Data de treinamento:**
- **Hardware usado:** (GPU model, memory, training time)
- **Software:** (versão exata, dependencies)
- **Seed:** (random seed para reprodutibilidade)
- **Hyperparâmetros finais:**

## 7. Caveats and Recommendations

### 7.1 Limitações Conhecidas
- **Dataset limitado a:** (população X, equipamento Y)
- **Performance pode variar em:** (outras populações)
- **Não recomendado para:** (casos raros, etc.)

### 7.2 Recomendações de Uso
- ✅ Usar com revisão humana
- ✅ Atualizar periodicamente
- ❌ Não usar como única fonte de decisão

## 8. How to Cite

```bibtex
@model{odontoia_carie_v1,
  author = {Laranjeiras, Edson},
  title = {ODONTOIA: CNN for Caries Detection in Panoramic Radiographs},
  year = {2026},
  url = {https://github.com/edsonlaranjeiras/odontoia-book}
}
```

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
**Versão:** 1.0
