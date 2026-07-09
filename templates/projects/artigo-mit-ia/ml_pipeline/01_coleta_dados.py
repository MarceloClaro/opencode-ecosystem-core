import wbgapi as wb
import pandas as pd
import numpy as np
import os

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(42)

INDICATORS = {
    "NY.GDP.PCAP.KD": "gdp_per_capita",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "SE.TER.ENRR": "tertiary_enrollment",
    "GB.XPD.RSDV.GD.ZS": "rd_spending",
    "IP.PAT.RESD": "patent_applications",
    "TX.VAL.TECH.MF.ZS": "high_tech_exports",
    "IT.NET.USER.ZS": "internet_users",
    "BX.KLT.DINV.WD.GD.ZS": "fdi_net_inflows",
    "SL.UEM.TOTL.ZS": "unemployment",
    "SI.POV.GINI": "gini_index",
    "SL.SRV.EMPL.ZS": "services_employment",
    "CC.EST": "control_corruption",
    "GE.EST": "gov_effectiveness",
}

print("Coletando dados WDI 1990-2025...")
ids = list(INDICATORS.keys())
df_raw = wb.data.DataFrame(ids, time=range(1990, 2026), labels=True, skipBlanks=True)
print(f"Bruto: {df_raw.shape}")

df = df_raw.reset_index()
df_melted = df.melt(id_vars=["economy", "series"], var_name="year", value_name="value")
df_melted["year"] = df_melted["year"].astype(int)
df_pivot = df_melted.pivot_table(index=["economy", "year"], columns="series", values="value").reset_index()

for code, name in INDICATORS.items():
    if code in df_pivot.columns:
        df_pivot.rename(columns={code: name}, inplace=True)

print(f"Pivotado: {df_pivot.shape} | Paises: {df_pivot['economy'].nunique()} | Anos: {int(df_pivot['year'].min())}-{int(df_pivot['year'].max())}")
df_pivot.to_csv(os.path.join(OUTPUT_DIR, "dataset_completo.csv"), index=False, encoding="utf-8")
print("Dataset completo salvo.")

# Classificacao ARM
def classify_arm(group):
    g = group.dropna(subset=["gdp_per_capita", "gdp_growth"]).copy()
    if len(g) < 8:
        return None
    mid = g[(g["gdp_per_capita"] >= 1136) & (g["gdp_per_capita"] <= 13845)]
    if len(mid) < 8:
        return None
    recent = mid.nlargest(max(8, len(mid) // 2), "year")
    growth = recent["gdp_growth"].mean()
    modern = mid[mid["year"] >= 2000]
    if len(modern) >= 8:
        return int(modern["gdp_growth"].mean() < 0.02)
    return int(growth < 0.02)

arm = df_pivot.groupby("economy", group_keys=False).apply(classify_arm, include_groups=False).reset_index()
arm.columns = ["economy", "arm_trapped"]
arm = arm.dropna()
arm["arm_trapped"] = arm["arm_trapped"].astype(int)
print(f"ARM classification: {int(arm['arm_trapped'].sum())} trapped / {len(arm)} total")

# Income level
def income_level(gdp):
    if pd.isna(gdp): return None
    if gdp < 1136: return "low"
    elif gdp <= 13845: return "middle"
    else: return "high"

df_pivot["income_level"] = df_pivot["gdp_per_capita"].apply(income_level)

# AI Readiness
def ai_readiness(row):
    score, n = 0, 0
    if pd.notna(row.get("internet_users")): score += row["internet_users"]; n += 1
    if pd.notna(row.get("tertiary_enrollment")): score += row["tertiary_enrollment"] * 0.5; n += 1
    if pd.notna(row.get("rd_spending")): score += row["rd_spending"] * 15; n += 1
    if pd.notna(row.get("high_tech_exports")): score += row["high_tech_exports"] * 0.3; n += 1
    if pd.notna(row.get("gov_effectiveness")): score += (row["gov_effectiveness"] + 2.5) * 15; n += 1
    return score / max(n, 1)

df_pivot["ai_readiness"] = df_pivot.apply(ai_readiness, axis=1)
df_pivot = df_pivot.merge(arm, on="economy", how="left")

# Latest cross-section
df_latest = df_pivot.sort_values("year").groupby("economy").last().reset_index()
df_latest.to_csv(os.path.join(OUTPUT_DIR, "dataset_latest.csv"), index=False)
print(f"Dataset latest: {len(df_latest)} paises")

# ML ready
df_ml = df_pivot.dropna(subset=["arm_trapped", "gdp_growth"])
df_ml.to_csv(os.path.join(OUTPUT_DIR, "dataset_ml.csv"), index=False)
print(f"Dataset ML: {df_ml.shape}")

print("\nRESUMO:")
print(f"  Paises: {df_pivot['economy'].nunique()}")
print(f"  ARM trapped: {int(arm['arm_trapped'].sum())}")
print(f"  AI Readiness: {df_pivot['ai_readiness'].min():.1f} - {df_pivot['ai_readiness'].max():.1f}")
print("Fase 1 concluida.")
