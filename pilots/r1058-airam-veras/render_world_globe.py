#!/usr/bin/env python3
"""Globo ortográfico centrado na América do Sul, com Brasil e Ceará."""
from __future__ import annotations
import json, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Circle
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TOPO = Path("/tmp/opencode/maps/countries-110m.json")
OUT = ROOT / "editor-workspace/remotion-smoke/public/r1058-world-map.png"
COPY = ROOT / "pilots/r1058-airam-veras/assets/map-world-globe.png"
W, H = 1920, 1080
CX, CY, R = W/2, H/2, 430
LAT0, LON0 = math.radians(-15), math.radians(-60)


def decode_arcs(topo):
    scale, translate = topo["transform"]["scale"], topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x=y=0; pts=[]
        for dx,dy in arc:
            x+=dx; y+=dy; pts.append((x*scale[0]+translate[0], y*scale[1]+translate[1]))
        arcs.append(pts)
    return arcs


def ring_points(ring, arcs):
    pts=[]
    for i in ring:
        seg = arcs[i] if i>=0 else list(reversed(arcs[~i]))
        if pts and seg and pts[-1]==seg[0]: pts.extend(seg[1:])
        else: pts.extend(seg)
    return pts


def project(lon, lat):
    lam=math.radians(lon)-LON0; phi=math.radians(lat)
    x=math.cos(phi)*math.sin(lam)
    y=math.cos(LAT0)*math.sin(phi)-math.sin(LAT0)*math.cos(phi)*math.cos(lam)
    z=math.sin(LAT0)*math.sin(phi)+math.cos(LAT0)*math.cos(phi)*math.cos(lam)
    return CX+R*x, CY-R*y, z


def visible_runs(points):
    runs=[]; current=[]
    for p in points:
        if p[2] >= 0:
            current.append((p[0],p[1]))
        else:
            if len(current)>=3: runs.append(current)
            current=[]
    if len(current)>=3: runs.append(current)
    return runs


def main():
    topo=json.loads(TOPO.read_text())
    arcs=decode_arcs(topo)
    fig=plt.figure(figsize=(W/100,H/100),dpi=100,frameon=False)
    fig.patch.set_facecolor("#07111f")
    ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis("off")
    ax.set_facecolor("#07111f")
    ax.add_patch(Circle((CX,CY),R,facecolor="#0a1a2a",edgecolor="#2dd4bf",linewidth=2,zorder=1))
    # graticula
    for lon in range(-180,181,30):
        pts=[project(lon,lat) for lat in np.linspace(-80,80,161)]
        for run in visible_runs(pts):
            ax.plot([p[0] for p in run],[p[1] for p in run],color="#4c6c8c",alpha=.12,lw=.6,zorder=2)
    for lat in range(-60,61,30):
        pts=[project(lon,lat) for lon in np.linspace(-180,180,241)]
        for run in visible_runs(pts):
            ax.plot([p[0] for p in run],[p[1] for p in run],color="#4c6c8c",alpha=.12,lw=.6,zorder=2)
    for feature in topo["objects"]["countries"]["geometries"]:
        polys=[feature["arcs"]] if feature["type"]=="Polygon" else feature["arcs"]
        brazil=str(feature.get("id","")) in {"076","76"}
        for poly in polys:
            for ring in poly:
                pts=[project(lon,lat) for lon,lat in ring_points(ring,arcs)]
                for run in visible_runs(pts):
                    ax.add_patch(MplPolygon(run,closed=True,
                        facecolor="#2b6f5e" if brazil else "#163247",
                        edgecolor="#4f7892",linewidth=.6,
                        alpha=.98 if brazil else .96,zorder=3))
    # Ceará marker static
    px,py,pz=project(-40.6628,-5.1873)
    if pz>=0:
        ax.scatter([px],[py],s=120,color="#f4b942",edgecolor="#fff",linewidth=1.5,zorder=6)
        ax.scatter([px],[py],s=600,color="none",edgecolor="#f4b942",linewidth=1.0,alpha=.5,zorder=5)
        ax.text(px+18,py-14,"Ceará",color="#f8fafc",fontsize=15,fontweight="bold",zorder=7)
    ax.text(CX,CY-R-28,"AMÉRICA DO SUL",color="#2dd4bf",fontsize=20,fontweight="bold",ha="center")
    ax.text(CX,CY+R+38,"Ceará · Nordeste do Brasil",color="#a8b8cc",fontsize=15,ha="center")
    fig.savefig(OUT,dpi=100,facecolor="#07111f"); fig.savefig(COPY,dpi=100,facecolor="#07111f"); plt.close(fig)
    x=px/W; y=py/H
    meta=json.loads((ROOT/"pilots/r1058-airam-veras/assets/map-meta.json").read_text())
    meta["world"]={"marker":[round(x,5),round(y,5)]}
    (ROOT/"pilots/r1058-airam-veras/assets/map-meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
    print({"marker":[round(x,5),round(y,5)],"px":[round(px,1),round(py,1)],"visible":pz>=0})


if __name__=="__main__": main()
