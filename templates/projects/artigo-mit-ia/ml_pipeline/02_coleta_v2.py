import wbgapi as wb
import pandas as pd
import numpy as np
import os

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1) Main WDI indicators
ids = [
    "NY.GDP.PCAP.KD", "NY.GDP.MKTP.KD.ZG", "SE.TER.ENRR",
    "GB.XPD.RSDV.GD.ZS", "IP.PAT.RESD", "TX.VAL.TECH.MF.ZS",
    "IT.NET.USER.ZS", "BX.KLT.DINV.WD.GD.ZS", "SL.UEM.TOTL.ZS",
    "SI.POV.GINI", "SL.SRV.EMPL.ZS",
]
print("Downloading WDI indicators 2000-2025...")
d = wb.data.DataFrame(ids, time=range(2000, 2026), labels=True, skipBlanks=False)
print(f"Main: {d.shape}")

df = d.reset_index()
yr = [c for c in df.columns if c.startswith("YR")]
df_m = df.melt(id_vars=["economy", "series"], value_vars=yr, var_name="year", value_name="value")
df_m["year"] = df_m["year"].str.replace("YR", "").astype(int)
df_p = df_m.pivot_table(index=["economy", "year"], columns="series", values="value").reset_index()

ren = {
    "NY.GDP.PCAP.KD": "gdp_per_capita", "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "SE.TER.ENRR": "tertiary_enrollment", "GB.XPD.RSDV.GD.ZS": "rd_spending",
    "IP.PAT.RESD": "patent_apps", "TX.VAL.TECH.MF.ZS": "high_tech_exp",
    "IT.NET.USER.ZS": "internet_users", "BX.KLT.DINV.WD.GD.ZS": "fdi_inflows",
    "SL.UEM.TOTL.ZS": "unemployment", "SI.POV.GINI": "gini",
    "SL.SRV.EMPL.ZS": "services_emp",
}
for old, new in ren.items():
    if old in df_p.columns:
        df_p.rename(columns={old: new}, inplace=True)

# 2) GDP historical for ARM
print("Downloading GDP historical 1990-2025...")
gdp_h = wb.data.DataFrame(["NY.GDP.PCAP.KD", "NY.GDP.MKTP.KD.ZG"], time=range(1990, 2026), labels=True, skipBlanks=False)
gdp2 = gdp_h.reset_index()
gdp_yr = [c for c in gdp2.columns if c.startswith("YR")]
gdp_m2 = gdp2.melt(id_vars=["economy", "series"], value_vars=gdp_yr, var_name="year", value_name="value")
gdp_m2["year"] = gdp_m2["year"].str.replace("YR", "").astype(int)
gdp_w = gdp_m2.pivot_table(index=["economy", "year"], columns="series", values="value").reset_index()
gdp_w.columns = ["economy", "year", "gdp_growth_hist", "gdp_pc_hist"]
print(f"GDP hist: {gdp_w.shape}")

# 3) ARM classification
print("Classifying ARM...")
def classify_arm(group):
    g = group.dropna(subset=["gdp_pc_hist", "gdp_growth_hist"]).copy()
    if len(g) < 10:
        return None
    mid = g[(g["gdp_pc_hist"] >= 1136) & (g["gdp_pc_hist"] <= 13845)]
    if len(mid) < 8:
        return None
    modern = mid[mid["year"] >= 2000]
    if len(modern) >= 8:
        return int(modern["gdp_growth_hist"].mean() < 0.02)
    recent = mid.nlargest(max(8, len(mid) // 2), "year")
    return int(recent["gdp_growth_hist"].mean() < 0.02)

arm = gdp_w.groupby("economy").apply(classify_arm).reset_index()
arm.columns = ["economy", "arm_trapped"]
arm = arm.dropna()
arm["arm_trapped"] = arm["arm_trapped"].astype(int)
print(f"ARM: {int(arm['arm_trapped'].sum())} trapped / {len(arm)} total")

df_p = df_p.merge(arm, on="economy", how="left")

# 4) Features
def inc_level(gdp):
    if pd.isna(gdp):
        return None
    if gdp < 1136:
        return "low"
    elif gdp <= 13845:
        return "middle"
    else:
        return "high"

df_p["income_level"] = df_p["gdp_per_capita"].apply(inc_level)

def ai_readiness(row):
    s, n = 0, 0
    if pd.notna(row.get("internet_users")): s += row["internet_users"]; n += 1
    if pd.notna(row.get("tertiary_enrollment")): s += row["tertiary_enrollment"] * 0.5; n += 1
    if pd.notna(row.get("rd_spending")): s += row["rd_spending"] * 15; n += 1
    if pd.notna(row.get("high_tech_exp")): s += row["high_tech_exp"] * 0.3; n += 1
    return s / max(n, 1)

df_p["ai_readiness"] = df_p.apply(ai_readiness, axis=1)

# 5) Save
df_p.to_csv(os.path.join(OUTPUT_DIR, "dataset_completo.csv"), index=False)
print(f"Completo: {df_p.shape}")

df_lt = df_p.sort_values("year").groupby("economy").last().reset_index()
df_lt.to_csv(os.path.join(OUTPUT_DIR, "dataset_latest.csv"), index=False)
print(f"Latest: {df_lt.shape}")

df_ml = df_lt.dropna(subset=["arm_trapped", "gdp_per_capita"]).copy()
df_ml.to_csv(os.path.join(OUTPUT_DIR, "dataset_ml.csv"), index=False)
print(f"ML clean: {df_ml.shape}")

print(f"\n=== RESUMO ===")
print(f"Paises unicos: {df_p['economy'].nunique()}")
print(f"ARM trapped: {int(arm['arm_trapped'].sum())}")
print(f"Fora ARM: {int(len(arm)-arm['arm_trapped'].sum())}")
print(f"ML samples: {len(df_ml)}")
arm_list = arm[arm["arm_trapped"] == 1]["economy"].tolist()
print(f"ARM countries: {arm_list}")

import json
meta = {"n_countries": int(df_p["economy"].nunique()), "n_arm": int(arm["arm_trapped"].sum()), "seed": 42}
with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w") as f:
    json.dump(meta, f)

print("\nFASE 1 CONCLUIDA!")
