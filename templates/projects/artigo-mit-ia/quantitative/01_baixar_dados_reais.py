import wbgapi as wb
import pandas as pd
import numpy as np
import time, warnings
from pathlib import Path
warnings.filterwarnings("ignore")

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

print("=" * 70)
print("DOWNLOAD DADOS REAIS - World Bank WDI API (v2)")
print("=" * 70)
tm_ini = time.time()

# 1. Listar paises
print("\n[1/6] Listando economias...")
eco_list = list(wb.economy.list())
print(f"  Total: {len(eco_list)} economias")

regiao_map = {r["code"]: r["name"] for r in wb.region.list()}
income_map = {r["id"]: r["value"] for r in wb.income.list()}
income_classe = {"High income": "alta_renda", "Upper middle income": "renda_media_alta",
                 "Lower middle income": "renda_media_baixa", "Low income": "renda_baixa"}

countries_info = []
for e in eco_list:
    rc = e.get("region", "")
    rn = regiao_map.get(rc, "")
    if rn and rc not in ("", "NA") and not e.get("aggregate", False):
        ic = e.get("incomeLevel", "")
        countries_info.append({
            "id": e["id"], "name": e["value"],
            "region": rn,
            "income_code": ic,
            "income_name": income_map.get(ic, ""),
            "renda": income_classe.get(income_map.get(ic, ""), "outros"),
        })
print(f"  Paises: {len(countries_info)}")

# 2. Baixar WDI (batch para eficiencia)
print("\n[2/6] Baixando WDI...")
INDICATORS = {
    "NY.GDP.PCAP.PP.KD": "pib_pc_ppc",
    "NY.GDP.MKTP.KD.ZG": "cresc_pib_anual",
    "NV.IND.MANF.ZS": "manufatura_pib_pct",
    "NV.SRV.TOTL.ZS": "servicos_pib_pct",
    "NV.AGR.TOTL.ZS": "agricultura_pib_pct",
    "TX.VAL.TECH.MF.ZS": "export_tech_pct",
    "SE.TER.ENRR": "educ_superior_pct",
    "SE.SEC.ENRR": "educ_secundaria_pct",
    "IT.NET.USER.ZS": "internet_pop_pct",
    "GB.XPD.RSDV.GD.ZS": "gerd_pib_pct",
    "IP.PAT.RESD": "patentes_residentes",
    "SL.UEM.TOTL.ZS": "desemprego_pct",
    "SI.POV.GINI": "gini",
    "EN.POP.DNST": "densidade_pop_km2",
    "SP.POP.TOTL": "populacao_total",
}

years = [f"YR{yr}" for yr in range(2015, 2026)]
pais_ids = [c["id"] for c in countries_info]

# Download em lotes
all_data = {}
for wdi_code, col_name in INDICATORS.items():
    print(f"  {col_name}...", end=" ", flush=True)
    try:
        df_wdi = wb.data.DataFrame(wdi_code, economy=pais_ids, time=years, skipBlanks=True)
        all_data[col_name] = df_wdi
        print(f"OK ({df_wdi.shape[0]} paises)")
    except Exception as e:
        print(f"ERRO: {e}")

# 3. Montar corte transversal (ano mais recente)
print("\n[3/6] Montando corte transversal...")
df_cross = pd.DataFrame({
    "pais_id": [c["id"] for c in countries_info],
    "pais": [c["name"] for c in countries_info],
    "regiao": [c["region"] for c in countries_info],
    "renda": [c["renda"] for c in countries_info],
})

for col_name in INDICATORS.values():
    if col_name in all_data:
        df_raw = all_data[col_name]
        # Most recent year per country
        vals = {}
        for idx in df_raw.index:
            row_vals = df_raw.loc[idx]
            valid = row_vals.dropna()
            if len(valid) > 0:
                vals[idx] = valid.iloc[-1]
        if vals:
            s = pd.Series(vals, name=col_name)
            df_cross = df_cross.merge(s, left_on="pais_id", right_index=True, how="left")
            print(f"  {col_name}: {s.notna().sum()} paises")
    else:
        print(f"  {col_name}: SEM DADOS")

# 4. Variaveis compostas
print("\n[4/6] Variaveis compostas...")

# Complexidade economica
eci_v = [c for c in ["export_tech_pct", "manufatura_pib_pct", "patentes_residentes", "gerd_pib_pct", "educ_superior_pct"] if c in df_cross.columns]
if eci_v:
    eci = df_cross[eci_v].copy()
    for c in eci_v:
        mx = eci[c].max()
        if mx > 0: eci[c] = eci[c] / mx
    df_cross["complexidade_economica"] = eci.mean(axis=1).round(3)

# PTF relativa
if "pib_pc_ppc" in df_cross.columns:
    lp = np.log(df_cross["pib_pc_ppc"].fillna(1).clip(lower=100))
    df_cross["ptf_relativa"] = ((lp - lp.min()) / (lp.max() - lp.min()) * 100).round(1) if lp.max() > lp.min() else 50.0

# Escape ARM
tgt = {}
for v, w in [("ptf_relativa", 0.25), ("educ_superior_pct", 0.20), ("gerd_pib_pct", 0.10),
             ("complexidade_economica", 0.10), ("internet_pop_pct", 0.10)]:
    if v in df_cross.columns: tgt[v] = w
if "gini" in df_cross.columns: tgt["gini"] = -0.10

score = pd.Series(0.0, index=df_cross.index)
for v, w in tgt.items():
    col = df_cross[v].fillna(0)
    mx = col.max()
    if mx > 0:
        if w > 0: score += w * (col / mx)
        else: score += abs(w) * (1 - col / mx)
df_cross["escape_arm"] = (score / score.max()).round(4) if score.max() > 0 else score.round(4)

# AIPI proxy - versao melhorada
aipi_parts = []
if "internet_pop_pct" in df_cross.columns:
    df_cross["aipi_digital"] = (df_cross["internet_pop_pct"].fillna(0) / 100 * 100).round(1)
    aipi_parts.append("aipi_digital")
if "educ_superior_pct" in df_cross.columns:
    df_cross["aipi_humano"] = (df_cross["educ_superior_pct"].fillna(0) / 100 * 100).round(1)
    aipi_parts.append("aipi_humano")

inov = df_cross.get("gerd_pib_pct", pd.Series(0, index=df_cross.index)).fillna(0)
mx = inov.max()
inov_norm = inov / mx if mx > 0 else inov
et = df_cross.get("export_tech_pct", pd.Series(0, index=df_cross.index)).fillna(0)
mx2 = et.max()
et_norm = et / mx2 if mx2 > 0 else et
df_cross["aipi_inovacao"] = ((0.5 + inov_norm * 0.25 + et_norm * 0.25) * 100).round(1)
aipi_parts.append("aipi_inovacao")

df_cross["aipi_regulacao"] = 50.0
df_cross["aipi_total"] = df_cross[aipi_parts].mean(axis=1).round(1) if aipi_parts else 50.0

print(f"  Feito: escape_arm [{df_cross['escape_arm'].min():.3f}-{df_cross['escape_arm'].max():.3f}], aipi [{df_cross['aipi_total'].min():.0f}-{df_cross['aipi_total'].max():.0f}]")

# 5. Painel
print("\n[5/6] Painel...")
panel_cols = [c for c in ["pib_pc_ppc", "cresc_pib_anual", "internet_pop_pct",
              "educ_superior_pct", "gerd_pib_pct", "gini", "manufatura_pib_pct"]
              if c in df_cross.columns]

rows = []
for _, r in df_cross.iterrows():
    for a in range(2016, 2026):
        e = {"pais_id": r["pais_id"], "pais": r["pais"], "regiao": r["regiao"], "ano": a}
        for c in panel_cols:
            if pd.notna(r.get(c)):
                e[c] = r[c]
        rows.append(e)

df_painel = pd.DataFrame(rows)
if "aipi_total" in df_cross.columns:
    df_painel["aipi_total"] = df_painel["pais_id"].map(dict(zip(df_cross["pais_id"], df_cross["aipi_total"])))
if "internet_pop_pct" in df_cross.columns:
    df_painel["exposicao_ia"] = df_painel["pais_id"].map(dict(zip(df_cross["pais_id"], df_cross["internet_pop_pct"]))).fillna(0)
print(f"  Painel: {df_painel.shape[0]} obs, {df_painel['pais_id'].nunique()} paises")

# 6. Export
print("\n[6/6] Exportando...")
df_cross.to_csv(OUT / "dataset_corte_transversal.csv", index=False)
df_painel.to_csv(OUT / "dataset_painel_2016_2025.csv", index=False)
print(f"  Tempo: {(time.time()-tm_ini)/60:.1f} min")
print(f"\nCOBERTURA:")
for c in df_cross.columns:
    if c not in ("pais_id", "pais", "regiao", "renda", "income_code", "income_name"):
        nv = df_cross[c].notna().sum()
        print(f"  {c}: {nv}/{len(df_cross)} ({nv/len(df_cross)*100:.0f}%)")
