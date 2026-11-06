"""
Prática 15.1 — Grad-CAM para interpretação de CNNs odontológicas
Usa odontoia.visualization.gradcam e odontoia.visualization.roc
"""
import numpy as np
import matplotlib.pyplot as plt


def demo_gradcam_application():
    """
    Demonstração conceitual do pipeline Grad-CAM para radiografias.
    
    Referências:
    - Selvaraju et al. (2017) 10.1109/ICCV.2017.74
    - Öztekin et al. (2023) 10.3390/diagnostics13152684
    """
    print("=" * 60)
    print("GRAD-CAM: Visualização de Ativação CNN")
    print("=" * 60)
    
    # Simula um heatmap Grad-CAM (em produção, usar plot_gradcam)
    heatmap = np.random.rand(224, 224) * 0.8
    heatmap[80:120, 100:140] = 1.0  # Região de interesse
    
    # Simula uma radiografia
    radiograph = np.zeros((224, 224))
    # Dente simulado
    for i in range(80, 120):
        for j in range(100, 140):
            dist = np.sqrt(((i-100)**2 + (j-120)**2) / 800)
            if dist < 1.2:
                radiograph[i, j] = 0.7 + 0.3 * (1 - dist/1.2)
    
    # Sobreposição
    overlay = np.zeros((224, 224, 3))
    overlay[..., 0] = radiograph * 0.7 + heatmap * 0.3
    overlay[..., 1] = radiograph * 0.7
    overlay[..., 2] = radiograph * 0.7
    
    print(f"✅ Heatmap Gerado: shape={heatmap.shape}")
    print(f"   Intensidade máxima: {heatmap.max():.3f}")
    print(f"   Intensidade média: {heatmap.mean():.3f}")
    print(f"   Região de maior ativação: [{80}:{120}, {100}:{140}]")
    return heatmap


def demo_roc_clinical():
    """
    Demonstração de curva ROC para avaliação diagnóstica.
    
    A métrica AUC é o padrão-ouro para avaliar classificadores
    binários em diagnóstico odontológico.
    """
    from sklearn.metrics import roc_auc_score
    
    print("\n" + "=" * 60)
    print("CURVA ROC: Avaliação Diagnóstica")
    print("=" * 60)
    
    np.random.seed(42)
    n = 200
    
    # Simula scores de 3 modelos
    y_true = np.random.randint(0, 2, n)
    
    # Modelo CNN (bom)
    y_score_cnn = np.where(
        y_true == 1,
        np.random.beta(8, 2, n),
        np.random.beta(2, 8, n),
    )
    
    # Modelo Random Forest (médio)
    y_score_rf = np.where(
        y_true == 1,
        np.random.beta(6, 3, n),
        np.random.beta(3, 6, n),
    )
    
    # Modelo baseline (ruim)
    y_score_base = np.random.rand(n)
    
    auc_cnn = roc_auc_score(y_true, y_score_cnn)
    auc_rf = roc_auc_score(y_true, y_score_rf)
    auc_base = roc_auc_score(y_true, y_score_base)
    
    print(f"\n📊 Resultados AUC:")
    print(f"   CNN (EfficientNet-B3):  AUC = {auc_cnn:.3f}")
    print(f"   Random Forest:          AUC = {auc_rf:.3f}")
    print(f"   Baseline (aleatório):   AUC = {auc_base:.3f}")
    
    return {
        "cnn": auc_cnn,
        "random_forest": auc_rf,
        "baseline": auc_base,
    }


if __name__ == "__main__":
    demo_gradcam_application()
    results = demo_roc_clinical()
    
    print("\n" + "=" * 60)
    print("✅ PRÁTICA XAI COMPLETA")
    print("=" * 60)
    print(f"Melhor modelo: CNN (AUC = {results['cnn']:.3f})")
    print(f"Ganho sobre baseline: +{results['cnn'] - results['baseline']:.3f} AUC")
