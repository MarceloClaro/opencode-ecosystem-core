# -*- coding: utf-8 -*-
"""
Gera figuras (PNG, 200 dpi) do artigo "Armadilha da Renda Média e IDEB —
Sertão de Crateús/Ceará". Fontes: academic/papers/crateus_ideb/data/processed/*.json
(dados oficiais INEP/IBGE) e outputs/expanded/resultados_r428.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[3]
PROC = BASE / "academic/papers/crateus_ideb/data/processed"
FIGS = Path(__file__).resolve().parents[1] / "figuras"
FIGS.mkdir(parents=True, exist_ok=True)

def jload(rel):
    return json.loads((BASE / rel).read_text(encoding="utf-8"))

micro = jload("academic/papers/crateus_ideb/data/processed/ideb_microrregiao.json")
ce = jload("academic/papers/crateus_ideb/data/processed/ideb_ce.json")
br = jload("academic/papers/crateus_ideb/data/processed/ideb_br.json")
renda = {r["cod_mun"]: r for r in jload("academic/papers/crateus_ideb/data/processed/renda_microrregiao.json")}
res = jload("academic/papers/crateus_ideb/outputs/expanded/resultados_r428.json")
ANOS = ["2005","2007","2009","2011","2013","2015","2017","2019","2021","2023","2025"]

def num(v):
    try: return float(v)
    except (TypeError, ValueError): return None

ai_micro = [r for r in micro if r["etapa"]=="anos_iniciais" and r["rede"]=="Municipal"]
ai_ce = [r for r in ce if r["etapa"]=="anos_iniciais" and r["rede"]=="Municipal"]
ai_br = [r for r in br if r.get("etapa")=="anos_iniciais" and r.get("rede")=="Municipal"]

def serie_media(rows):
    out={}
    for a in ANOS:
        vals=[num(r[a]) for r in rows]; vals=[v for v in vals if v is not None]
        if vals: out[int(a)] = sum(vals)/len(vals)
    return out

ser_micro, ser_ce, ser_br = serie_media(ai_micro), serie_media(ai_ce), serie_media(ai_br)

plt.figure(figsize=(7.6,4.0))
plt.plot(list(ser_br), list(ser_br.values()), marker="o", lw=1.8, label="Brasil (média municipal)")
plt.plot(list(ser_ce), list(ser_ce.values()), marker="s", lw=1.8, label="Ceará (média municipal)")
plt.plot(list(ser_micro), list(ser_micro.values()), marker="^", lw=2.4, label="Sertão de Crateús (média, 9 mun.)")
for x,y in ser_micro.items():
    plt.annotate(f"{y:.1f}".replace(".",","),(x,y),textcoords="offset points",xytext=(0,7),ha="center",fontsize=7)
plt.xticks(range(2005,2026,2)); plt.ylim(3,10.4)
plt.ylabel("IDEB — anos iniciais (rede municipal)"); plt.xlabel("Ano de avaliação")
plt.grid(alpha=0.3); plt.legend(loc="upper left",fontsize=8); plt.tight_layout()
plt.savefig(FIGS/"fig01_evolucao_ideb.png",dpi=200); plt.close()

plt.figure(figsize=(7.6,4.2))
for r in sorted(ai_micro,key=lambda z:z["nome_mun"]):
    xs=[int(a) for a in ANOS if num(r[a]) is not None]; ys=[num(r[a]) for a in ANOS if num(r[a]) is not None]
    plt.plot(xs,ys,marker=".",lw=1.4,label=r["nome_mun"])
plt.xticks(range(2005,2026,2)); plt.ylabel("IDEB — anos iniciais (rede municipal)")
plt.xlabel("Ano de avaliação"); plt.grid(alpha=0.3)
plt.legend(ncol=3,fontsize=7,loc="upper left"); plt.tight_layout()
plt.savefig(FIGS/"fig02_spaghetti_municipios.png",dpi=200); plt.close()

fator = jload("academic/papers/crateus_ideb/data/processed/ipca_medias_anuais.json")["fator_deflator_para_2021"]
pib_rec={}
for row in jload("academic/papers/crateus_ideb/data/processed/pib_microrregiao.json"):
    pib_rec[(row["cod_mun"],row["ano"])]=row["pib_per_capita"]
anos_painel=[2013,2015,2017,2019,2021,2023]
pairs=[]
for etapa in ("anos_iniciais","anos_finais"):
    rows=[r for r in micro if r["etapa"]==etapa and r["rede"]=="Municipal"]
    for r in rows:
        for t in anos_painel:
            y=num(r[str(t)]); pv=pib_rec.get((r["cod_mun"],t-2))
            if y is None or pv is None: continue
            pairs.append((r["cod_mun"],r["nome_mun"],y,math.log(pv*fator[str(t-2)])))
muns=sorted({p[0] for p in pairs})
xm=[sum(p[3] for p in pairs if p[0]==c)/6 for c in muns]
ym=[sum(p[2] for p in pairs if p[0]==c)/6 for c in muns]
labels=[renda[c]["nome_mun"] for c in muns]

import numpy as np
plt.figure(figsize=(6.4,4.2))
plt.scatter(xm,ym,s=55,color="#1a55a0")
for x,y,lab in zip(xm,ym,labels):
    plt.annotate(lab,(x,y),textcoords="offset points",xytext=(4,4),fontsize=7)
c=np.polyfit(xm,ym,1); xs=[min(xm)-0.02,max(xm)+0.02]
plt.plot(xs,[c[0]*v+c[1] for v in xs],ls="--",lw=1.2,color="#888")
plt.xlabel("log do PIB per capita real (R$ de 2021; médias do painel, defasagem 2 anos)")
plt.ylabel("IDEB médio no painel (2013–2023)"); plt.grid(alpha=0.3); plt.tight_layout()
plt.savefig(FIGS/"fig03_scatter_between.png",dpi=200); plt.close()

gd=res["h3_metas_por_ano"]["ganho_2007_2025_ai"]["detalhe"]
gx=[d["renda_media_resp"] for d in gd]; gy=[d["ganho"] for d in gd]
plt.figure(figsize=(6.4,4.2))
plt.scatter(gx,gy,s=60,color="#2e7d32")
for d in gd: plt.annotate(d["nome"],(d["renda_media_resp"],d["ganho"]),textcoords="offset points",xytext=(4,4),fontsize=7)
c2=np.polyfit(gx,gy,1); xs2=[min(gx)-20,max(gx)+20]
plt.plot(xs2,[c2[0]*v+c2[1] for v in xs2],ls="--",lw=1.2,color="#888")
plt.xlabel("Renda média mensal do responsável — Censo 2022 (R$)")
plt.ylabel("Ganho IDEB anos iniciais (2007→2025)"); plt.grid(alpha=0.3); plt.tight_layout()
plt.savefig(FIGS/"fig05_ganho_vs_renda.png",dpi=200); plt.close()

por=res["h3_metas_por_ano"]["por_ano"]; am=sorted(por)
vals=[por[a]["pct_atingiu"] for a in am]
plt.figure(figsize=(6.4,3.6))
bars=plt.bar([str(a) for a in am],vals,color="#ef6c00",alpha=0.85)
for b,v in zip(bars,vals):
    plt.annotate(f"{v:.1f}%".replace(".",","),(b.get_x()+b.get_width()/2,v),textcoords="offset points",xytext=(0,3),ha="center",fontsize=8)
plt.axhline(res["h3_metas_por_ano"]["pct_atingiu_geral"],ls="--",lw=1.2,color="#444",
            label=f"Geral: {res['h3_metas_por_ano']['pct_atingiu_geral']:.1f}%".replace(".",","))
plt.ylim(90,101); plt.ylabel("% de metas INEP cumpridas (mesmo ano)"); plt.xlabel("Ano de referência")
plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(FIGS/"fig04_metas_por_ano.png",dpi=200); plt.close()

lags=res["robustez_lags"]["perfil_lags"]; lx=[l["lag"] for l in lags]
plt.figure(figsize=(6.4,3.6))
plt.plot(lx,[l["r_niveis_pooled"] for l in lags],marker="o",label="r níveis (pooled)")
plt.plot(lx,[l["r_primeiras_diferencas"] for l in lags],marker="s",label="r primeiras diferenças")
plt.axhline(0,color="#666",lw=0.8); plt.xticks(lx)
plt.xlabel("Defasagem do PIB real (anos)"); plt.ylabel("Coeficiente de Pearson")
plt.grid(alpha=0.3); plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(FIGS/"fig06_perfil_lags.png",dpi=200); plt.close()
print("figuras ok:", sorted(p.name for p in FIGS.glob("*.png")))
