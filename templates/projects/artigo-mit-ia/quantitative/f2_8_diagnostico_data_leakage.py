"""
Fase 2.8 — Diagnóstico de Data Leakage
========================================
O target `escape_arm` é composto por 6 componentes que também figuram como features.
Este script quantifica o vazamento em 3 cenários:

Cenário A: Todas as features (leakage máximo) → R² artificialmente alto
Cenário B: Apenas features NÃO componentes do target (R² realista baixo)
Cenário C: Componentes isolados (quanto cada um explica isoladamente)

Saída: JSON + console para o relatório final.
"""

import pandas as pd
import numpy as np
import json
import warnings
import sys
from pathlib import Path
import io

# Forçar UTF-8 no stdout do Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# ── 0. Caminhos ──────────────────────────────────────────────────────────────
BASE = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia\quantitative')
DATA = BASE / 'output' / 'dataset_corte_transversal.csv'
OUT  = BASE / 'output' / 'diagnostico_data_leakage.json'

# ── 1. Carga ─────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA)
print(f"Dataset: {df.shape[0]} países, {df.shape[1]} colunas")

# ── 2. Componentes do target ────────────────────────────────────────────────
COMPONENTES_TARGET = [
    'ptf_relativa', 'educ_superior_pct', 'gerd_pib_pct',
    'complexidade_economica', 'internet_pop_pct', 'gini'
]

TARGET = 'escape_arm'
FEATURES_ESTRUTURAIS = [
    'pib_pc_ppc', 'manufatura_pib_pct', 'agricultura_pib_pct',
    'export_tech_pct', 'densidade_pop_km2'
]
FEATURES_AIPI = ['aipi_digital', 'aipi_humano', 'aipi_inovacao', 'aipi_regulacao']
FEATURES_TOTAIS = COMPONENTES_TARGET + FEATURES_ESTRUTURAIS + FEATURES_AIPI

print(f"\nComponentes do target: {COMPONENTES_TARGET}")
print(f"Features estruturais: {FEATURES_ESTRUTURAIS}")
print(f"Features AIPI: {FEATURES_AIPI}")

# ── 3. Verificar correlação target ↔ componentes ────────────────────────────
print("\n── Correlação target ↔ componentes ──")
corr_target = {}
for col in COMPONENTES_TARGET + ['aipi_total']:
    if col in df.columns:
        r = df[col].corr(df[TARGET])
        corr_target[col] = round(r, 4)
        print(f"  {col:30s}  r = {r:+.4f}")

# ── 4. Modelagem comparativa ────────────────────────────────────────────────
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import r2_score
from sklearn.impute import SimpleImputer

def preparar_dados(features_list, label):
    """Prepara X, y com imputação de mediana."""
    X = df[features_list].copy()
    y = df[TARGET].values
    # Remove linhas sem target
    mask = ~np.isnan(y)
    X, y = X[mask], y[mask]
    # Imputação
    imp = SimpleImputer(strategy='median')
    X_imp = pd.DataFrame(imp.fit_transform(X), columns=X.columns)
    print(f"  {label:40s} → {X_imp.shape[0]} obs, {X_imp.shape[1]} features")
    return X_imp, y

def avaliar_modelo(X, y, label):
    """R² treino, teste e CV 5-fold."""
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    r2_tr = r2_score(y_tr, rf.predict(X_tr))
    r2_te = r2_score(y_te, rf.predict(X_te))
    cv_scores = cross_val_score(rf, X, y, cv=5, scoring='r2')
    print(f"  {label:40s} R² treino={r2_tr:.4f}  teste={r2_te:.4f}  CV={cv_scores.mean():.4f}±{cv_scores.std():.4f}")
    return {
        'r2_treino': round(r2_tr, 4),
        'r2_teste': round(r2_te, 4),
        'cv_r2_medio': round(cv_scores.mean(), 4),
        'cv_r2_std': round(cv_scores.std(), 4)
    }

resultados = {}

# ── Cenário A: Todas as features (LEAKAGE) ──────────────────────────────────
print("\n═══ Cenário A — Todas as features (com leakage) ═══")
Xa, y = preparar_dados(FEATURES_TOTAIS, "Todas as features (leakage)")
resultados['A_todas_features'] = avaliar_modelo(Xa, y, "RF com todas features")

# ── Cenário B: Apenas features NÃO componentes ──────────────────────────────
print("\n═══ Cenário B — SEM componentes do target ═══")
Xb, _ = preparar_dados(FEATURES_ESTRUTURAIS + FEATURES_AIPI, "Apenas estruturais + AIPI")
resultados['B_sem_leakage'] = avaliar_modelo(Xb, y, "RF sem leakage")

# ── Cenário C1: Apenas AIPI (puramente estrutural) ─────────────────────────
print("\n═══ Cenário C1 — Apenas AIPI ═══")
Xc1, _ = preparar_dados(FEATURES_AIPI, "Apenas 4 pilares AIPI")
resultados['C1_apenas_AIPI'] = avaliar_modelo(Xc1, y, "RF apenas AIPI")

# ── Cenário C2: Apenas componentes (leakage puro) ──────────────────────────
print("\n═══ Cenário C2 — Apenas componentes do target ═══")
Xc2, _ = preparar_dados(COMPONENTES_TARGET, "Apenas componentes do target")
resultados['C2_apenas_componentes'] = avaliar_modelo(Xc2, y, "RF apenas componentes")

# ── Cenário C3: Apenas estruturais (sem AIPI, sem leakage) ─────────────────
print("\n═══ Cenário C3 — Apenas estruturais (controle) ═══")
Xc3, _ = preparar_dados(FEATURES_ESTRUTURAIS, "Apenas estruturais")
resultados['C3_apenas_estruturais'] = avaliar_modelo(Xc3, y, "RF apenas estruturais")

# ── 5. Feature importance do modelo SEM leakage (Cenário B) ─────────────────
print("\n═══ Feature Importance — Modelo SEM leakage ═══")
Xb_imp, y_imp = Xb, y
X_tr, X_te, y_tr, y_te = train_test_split(Xb_imp, y_imp, test_size=0.2, random_state=42)
rf_clean = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
rf_clean.fit(X_tr, y_tr)
fi = sorted(zip(Xb.columns, rf_clean.feature_importances_), key=lambda x: -x[1])
resultados['feature_importance_sem_leakage'] = {v: round(r, 4) for v, r in fi}
for v, r in fi:
    print(f"  {v:30s}  {r:.4f}")

# ── 6. Resumo ───────────────────────────────────────────────────────────────
print("\n═══ RESUMO — Inflação por Data Leakage ═══")
r2_leak = resultados['A_todas_features']['r2_teste']
r2_clean = resultados['B_sem_leakage']['r2_teste']
inflacao = (r2_leak - r2_clean) / max(r2_clean, 0.001) * 100
print(f"  R² com leakage (Cenário A):       {r2_leak:.4f}")
print(f"  R² sem leakage (Cenário B):       {r2_clean:.4f}")
print(f"  Inflação relativa:                {inflacao:+.1f}%")
print(f"  R² dos componentes isolados (C2): {resultados['C2_apenas_componentes']['r2_teste']:.4f}")
print(f"  R² apenas AIPI (C1):              {resultados['C1_apenas_AIPI']['r2_teste']:.4f}")
print(f"  R² apenas estruturais (C3):       {resultados['C3_apenas_estruturais']['r2_teste']:.4f}")

resultados['resumo'] = {
    'r2_com_leakage': r2_leak,
    'r2_sem_leakage': r2_clean,
    'inflacao_percentual': round(inflacao, 1),
    'diagnostico': 'CRÍTICO — target composto por features' if inflacao > 50 else 'MODERADO'
}

# ── 7. Salvar ────────────────────────────────────────────────────────────────
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)
print(f"\nResultados salvos em: {OUT}")
