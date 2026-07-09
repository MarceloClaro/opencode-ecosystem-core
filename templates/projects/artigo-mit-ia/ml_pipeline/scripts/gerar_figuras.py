"""
Gera todas as figuras do artigo ARM+IAG:
1. Feature Importance (RF + Permutation)
2. Classificacao (Logistic Regression vs Random Forest)
3. Clusters (GDP per capita vs AI Readiness)
4. Anomalias (Isolation Forest)
5. Matriz de Correlacao
6. Fluxograma da Metodologia
7. Mapa-mundi dos paises com ARM
"""

import json, os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.lines as mlines
import seaborn as sns

warnings.filterwarnings('ignore')

BASE = r"C:\Users\marce\.config\opencode\artigo-mit-ia"
OUTPUT = os.path.join(BASE, "ml_pipeline", "outputs", "figuras")
os.makedirs(OUTPUT, exist_ok=True)

JSON_PATH = os.path.join(BASE, "ml_pipeline", "outputs", "resultados_ml_v2.json")
CSV_PATH  = os.path.join(BASE, "ml_pipeline", "outputs", "dataset_ml_v2.csv")
CLUSTER_PATH = os.path.join(BASE, "ml_pipeline", "outputs", "clusters_v2.csv")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.read_csv(CSV_PATH)

COR1, COR2, COR3, COR4 = "#1B2A4A", "#C9A84C", "#3A6B8C", "#8B4513"
CINZA = "#D3D3D3"

sns.set_style("whitegrid")
plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "#FAFAFA",
    "font.family": "serif", "font.size": 11, "axes.titlesize": 14, "axes.labelsize": 12})

FEAT_LAB = {"gdp_per_capita":"PIB per capita","rd_spending":"Gastos em P&D",
    "internet_users":"Usuarios Internet","fdi_inflows":"Invest. Estrangeiro (FDI)",
    "services_emp":"Emprego Servicos","gini":"Indice Gini",
    "high_tech_exp":"Export. Alta Tecnologia","unemployment":"Desemprego",
    "tertiary_enrollment":"Ensino Superior","patent_apps":"Pedidos Patente",
    "ai_readiness":"Prontidao para IA"}
FEAT_ORDER = ["gdp_per_capita","rd_spending","internet_users","fdi_inflows",
    "services_emp","gini","high_tech_exp","unemployment",
    "tertiary_enrollment","patent_apps","ai_readiness"]

# --- FIG 1: Feature Importance ---
def fig1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fi_rf = {f["feature"]: f["importance_rf"] for f in data["feature_importance"]}
    fi_p = {f["feature"]: f["importance_perm"] for f in data["feature_importance"]}
    fi_s = {f["feature"]: f["importance_perm_std"] for f in data["feature_importance"]}
    labs = [FEAT_LAB.get(k,k) for k in FEAT_ORDER]
    vr = [fi_rf.get(k,0)*100 for k in FEAT_ORDER]
    vp = [fi_p.get(k,0)*100 for k in FEAT_ORDER]
    ep = [fi_s.get(k,0)*100 for k in FEAT_ORDER]
    cr = [COR2 if k=="ai_readiness" else COR1 for k in FEAT_ORDER]
    cp = [COR4 if k=="ai_readiness" else COR3 for k in FEAT_ORDER]
    ax1.barh(range(len(vr)), vr, color=cr, edgecolor="white", height=0.7)
    ax1.set_yticks(range(len(labs))); ax1.set_yticklabels(labs)
    ax1.set_xlabel("Importancia Relativa (%)")
    ax1.set_title("A - Random Forest", fontweight="bold", loc="left"); ax1.invert_yaxis()
    ax2.barh(range(len(vp)), vp, xerr=ep, color=cp, edgecolor="white", height=0.7, capsize=3, ecolor="gray")
    ax2.set_yticks(range(len(labs))); ax2.set_yticklabels([])
    ax2.set_xlabel("Importancia por Permutacao (%)")
    ax2.set_title("B - Permutation Importance", fontweight="bold", loc="left"); ax2.invert_yaxis()
    L = [mpatches.Patch(color=COR1, label="Demais"), mpatches.Patch(color=COR2, label="Pront. IA")]
    fig.legend(handles=L, loc="lower center", ncol=2, frameon=True, fancybox=True, fontsize=10)
    plt.tight_layout(rect=[0,0.08,1,1])
    plt.savefig(os.path.join(OUTPUT, "fig1_feature_importance.png"), dpi=300, bbox_inches="tight")
    plt.close(); print("  OK Fig 1")

# --- FIG 2: Classification ---
def fig2():
    fig, ax = plt.subplots(figsize=(10, 6))
    clf = data["classification"]; mods = list(clf.keys())
    mets = ["accuracy","f1","roc_auc","recall"]
    labs = ["Acuracia","F1-Score","ROC-AUC","Recall"]
    cols = [COR1, COR2, COR3, COR4]
    x = np.arange(len(mods)); w = 0.18
    for i,(m,l) in enumerate(zip(mets,labs)):
        v = [clf[mo][m] for mo in mods]
        sk = m+"_std"; e = [clf[mo].get(sk,0) for mo in mods] if m!="recall" else None
        ax.bar(x+i*w-1.5*w, v, w, label=l, color=cols[i], edgecolor="white", yerr=e, capsize=3, error_kw={"ecolor":"gray"})
    ax.set_xticks(x); ax.set_xticklabels(["Regr. Logistica","Random Forest"], fontsize=11)
    ax.set_ylabel("Score"); ax.set_ylim(0,1.0)
    ax.axhline(0.5, color="gray", ls="--", lw=0.8, alpha=0.6, label="Chance")
    ax.legend(loc="lower right", frameon=True, fancybox=True, ncol=2, fontsize=9)
    ax.set_title("Comparacao de Modelos - Classificacao ARM", fontweight="bold", loc="left")
    for im,mo in enumerate(mods):
        roc = clf[mo]["roc_auc"]; rs = clf[mo].get("roc_auc_std",0)
        ax.annotate(f"ROC-AUC={roc:.3f}\261{rs:.3f}", xy=(im,roc), xytext=(im,roc+0.08),
            ha="center", fontsize=9, fontweight="bold", color=COR1,
            arrowprops=dict(arrowstyle="->", color=COR1, lw=1.2))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, "fig2_classificacao.png"), dpi=300, bbox_inches="tight")
    plt.close(); print("  OK Fig 2")

# --- FIG 3: Clusters ---
def fig3():
    fig, ax = plt.subplots(figsize=(12, 8))
    cl = data["cluster_profiles"]
    ec = {}
    if os.path.exists(CLUSTER_PATH):
        cd = pd.read_csv(CLUSTER_PATH)
        if "cluster" in cd.columns: ec = dict(zip(cd["economy"],cd["cluster"]))
    cc = {0:"#2E86AB",1:"#A23B72",2:"#F18F01",3:"#C73E1D"}
    for _,r in df.iterrows():
        eco = r["economy"]
        if eco in ec: c = ec[eco]
        else:
            g = r["gdp_per_capita"]
            if pd.isna(g): continue
            c = 1 if g>60000 else (0 if g>2500 else 2)
        arm = r.get("arm_relative",0)
        if pd.isna(arm): arm=0
        ax.scatter(r["gdp_per_capita"], r["ai_readiness"], c=cc.get(c,"#666"),
            s=30 if arm==0 else 80, marker="o" if arm==0 else "D",
            alpha=0.6 if arm==0 else 0.9, edgecolors="black" if arm==1 else "none",
            linewidths=0.5 if arm==1 else 0, zorder=2 if arm==1 else 1)
    a = df[df["arm_relative"]==1].dropna(subset=["gdp_per_capita","ai_readiness"])
    for _,r in a.iterrows():
        ax.annotate(r["economy"], (r["gdp_per_capita"],r["ai_readiness"]), xytext=(8,5),
            textcoords="offset points", fontsize=7, alpha=0.8, color=COR1)
    le = [mlines.Line2D([],[],color=cc[i],marker="o",lw=0,
        label=f"C{i}: {'R.Media' if i==0 else 'Alta' if i==1 else 'Baixa' if i==2 else 'Outlier'} (n={cl[str(i)]['n']},ARM={cl[str(i)]['arm_count']})")
        for i in range(4)]
    le.append(mlines.Line2D([],[],color="black",marker="D",lw=0,markersize=8,
        markeredgecolor="black",markerfacecolor="white",label="ARM (relativa)"))
    ax.legend(handles=le, loc="upper left", frameon=True, fancybox=True, fontsize=8)
    ax.set_xlabel("PIB per capita (USD)"); ax.set_ylabel("Prontidao para IA")
    ax.set_title("Clusters de Desenvolvimento x Prontidao para IA", fontweight="bold", loc="left")
    ax.set_xscale("symlog", linthresh=1000)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, "fig3_clusters.png"), dpi=300, bbox_inches="tight")
    plt.close(); print("  OK Fig 3")

# --- FIG 4: Anomalies ---
def fig4():
    fig, ax = plt.subplots(figsize=(12, 8))
    an = {a["economy"] for a in data["anomalies"]["top_anomalies"]}
    ax.scatter(df["gdp_per_capita"], df["ai_readiness"], c=CINZA, s=20, alpha=0.5, label="Demais")
    ad = df[df["economy"].isin(an)].dropna(subset=["gdp_per_capita","ai_readiness"])
    ax.scatter(ad["gdp_per_capita"], ad["ai_readiness"], c=COR4, s=60, alpha=0.8,
        edgecolors="black", linewidths=0.5, label=f"Outliers ({len(ad)})", zorder=3)
    for _,r in ad.iterrows():
        ax.annotate(r["economy"], (r["gdp_per_capita"],r["ai_readiness"]),
            xytext=(6,4), textcoords="offset points", fontsize=7, color=COR4, fontweight="bold")
    ax.set_xlabel("PIB per capita (USD)"); ax.set_ylabel("Prontidao para IA")
    ax.set_title("Deteccao de Anomalias - Isolation Forest", fontweight="bold", loc="left")
    ax.set_xscale("symlog", linthresh=1000); ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, "fig4_anomalias.png"), dpi=300, bbox_inches="tight")
    plt.close(); print("  OK Fig 4")

# --- FIG 5: Correlation Matrix ---
def fig5():
    cc = ["gdp_per_capita","ai_readiness","gdp_growth","rd_spending","internet_users",
        "fdi_inflows","high_tech_exp","services_emp","tertiary_enrollment","unemployment","gini","patent_apps"]
    cm = df[cc].dropna().corr()
    labs = ["PIB per cap","Pront.IA","Cresc.PIB","P&D","Internet","FDI","AltaTec",
        "Servicos","EnsSup","Desemprego","Gini","Patentes"]
    m = np.triu(np.ones_like(cm,dtype=bool),k=1)
    fig, ax = plt.subplots(figsize=(12,10))
    sns.heatmap(cm, mask=m, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
        square=True, linewidths=0.5, cbar_kws={"shrink":0.75,"label":"Pearson r"},
        xticklabels=labs, yticklabels=labs, ax=ax)
    ax.set_title("Matriz de Correlacao", fontweight="bold", loc="left", pad=15)
    plt.xticks(rotation=45, ha="right"); plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, "fig5_correlacao.png"), dpi=300, bbox_inches="tight")
    plt.close(); print("  OK Fig 5")

# --- FIG 6: Flowchart ---
def fig6():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0,14); ax.set_ylim(0,10); ax.axis("off")
    ax.set_facecolor("#F5F0EB"); fig.patch.set_facecolor("#F5F0EB")

    def bx(x,y,w,h,t,cf="#1B2A4A",ct="white",fs=10,s=None):
        p = FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.15,rounding_size=0.3",
            facecolor=cf,edgecolor="white",linewidth=1.5,alpha=0.95)
        ax.add_patch(p)
        ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,fontweight="bold",color=ct)
        if s: ax.text(x+w/2,y+h*0.2,s,ha="center",va="center",fontsize=8,color=ct,alpha=0.8)

    def ar(x1,y1,x2,y2,c="#888"):
        ax.annotate("",xy=(x2,y2),xytext=(x1,y1),
            arrowprops=dict(arrowstyle="->",color=c,lw=1.8,connectionstyle="arc3,rad=0.2"))

    bx(0.3,8.0,4.0,1.2,"WDI\n(262 paises x 11 features)",COR1,"white",10)
    bx(5.0,8.0,4.0,1.2,"Pront. IA\n(Oxford Insights AIPI)",COR3,"white",10)
    bx(9.7,8.0,4.0,1.2,"ARM\n(Armadilha Renda Media)",COR4,"white",10,"Strict:3 | Relativa:29")
    for x in [2.3,7.0,11.7]: ar(x,8.0,x,6.5)
    bx(0.5,5.3,13.0,1.4,"Pre-processamento e Integracao",COR1,"white",11,"Imputacao mediana | Z-score | Merge")
    for x,y,(xb,yb,w,h,t,s) in [(2.3,5.3,(0.3,2.8,4.0,1.4,"Clusterizacao K-Means (k=4)","C0:Media | C1:Alta | C2:Baixa | C3:Outlier")),
        (7.0,5.3,(5.0,2.8,4.0,1.4,"Correlacoes Pearson+Parciais","Controle PIB per capita")),
        (11.7,5.3,(9.7,2.8,4.0,1.4,"Classificacao ARM\nLogistica+RF","ML Supervisionado"))]:
        ar(x,y,x,4.0); bx(xb,yb,w,h,t,COR3,"white",10,s)
    ar(11.7,2.8,11.7,1.3)
    bx(9.7,0.1,4.0,1.4,"Validacao Cruzada",COR4,"white",9,"Stratified K-Fold (k=5)\nPermutation Importance\nBootstrap 1000x\nseed=42")
    for x in [2.3,7.0]: ar(x,2.8,x,1.3)
    bx(0.5,0.1,6.0,1.0,"AI Readiness sem efeito significativo sobre ARM",COR1,"white",10,"r=-0,057 (p=0,36) | GDP lider (19,2%)")
    ax.text(7.0,9.5,"Fluxograma Metodologico - Pipeline ML ARM+IAG",ha="center",va="center",fontsize=16,fontweight="bold",color=COR1)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT, "fig6_fluxograma.png"), dpi=300, bbox_inches="tight")
    plt.close(); print("  OK Fig 6")

# --- FIG 7: Map ---
def fig7():
    import plotly.express as px
    dm = df[["economy","arm_relative","gdp_per_capita","income_level","ai_readiness","gdp_growth"]].copy()
    dm["status_arm"] = dm["arm_relative"].apply(lambda x: "ARM" if x==1 else "Sem ARM")
    dm["iso_alpha"] = dm["economy"]; dm = dm.dropna(subset=["economy"])
    fig = px.choropleth(dm, locations="iso_alpha", color="ai_readiness",
        hover_name="economy",
        hover_data={"iso_alpha":False,"ai_readiness":":.1f","gdp_per_capita":":,.0f","gdp_growth":":.2f","status_arm":True,"income_level":True},
        color_continuous_scale=px.colors.sequential.Blues, range_color=[0,100],
        projection="natural earth", title="Prontidao para IA x ARM (n=262)")
    am = dm[dm["arm_relative"]==1]
    fig.add_scattergeo(locations=am["iso_alpha"], text=am["economy"], mode="markers+text",
        marker=dict(symbol="diamond",size=10,color="#C73E1D",line=dict(width=1,color="black")),
        textfont=dict(size=8,color="#C73E1D"), textposition="top center", name="ARM",
        customdata=am[["ai_readiness"]].values)
    fig.update_layout(geo=dict(showframe=True,showcoastlines=True,coastlinecolor="gray",
        showland=True,landcolor="#F5F0EB",showocean=True,oceancolor="#E8F4F8",
        showcountries=True,countrycolor="gray",countrywidth=0.5,projection_scale=1.1),
        margin=dict(l=10,r=10,t=60,b=10))
    fig.write_html(os.path.join(OUTPUT, "fig7_mapa_arm.html"))
    print("  OK Fig 7 HTML")
    try: fig.write_image(os.path.join(OUTPUT, "fig7_mapa_arm.png"), width=1400, height=800, scale=2); print("  OK Fig 7 PNG")
    except Exception as e: print(f"  Fig 7 PNG: {e}")

if __name__ == "__main__":
    print("="*50); print("GERANDO FIGURAS ARM+IAG"); print("="*50)
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); fig7()
    print("\\nTodas as figuras geradas em:", OUTPUT)
