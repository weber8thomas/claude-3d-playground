#!/usr/bin/env python3
"""Trace le profil 2D du crochet (modele v15) avec le tube en place, cotes CIBLE.

Meme geometrie que src/cabas_velo.scad et que l'editeur tools/web/designer.html :
dos -> bras du haut -> ventre (arc a trois points) -> languette.

Deux sources, jamais melangees :
  - REEL : cotes derivees des parametres lus dans le .scad ;
  - CIBLE : le croquis, dans docs/target_hook.json.
"""
import json, math, pathlib, re, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

ROOT   = pathlib.Path(__file__).resolve().parent.parent
SRC    = ROOT / "src" / "cabas_velo.scad"
TARGET = ROOT / "docs" / "target_hook.json"

def scad_params():
    txt = SRC.read_text()
    def v(name):
        m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)\s*;", txt, re.M)
        if not m: sys.exit(f"parametre '{name}' introuvable dans {SRC}")
        return float(m.group(1))
    keys = ("bar_h","bar_t","tube_d","rib_t","clr","arm_top","depth","bowl_h",
            "arm_bot","back_h","leg_l","leg_ang","col_wall","col_clr")
    return {k: v(k) for k in keys}

def targets():
    if not TARGET.exists(): return {}
    return {k: c["val"] for k, c in json.loads(TARGET.read_text())["cotes"].items()}

def circ3(A,Q,B):
    d = 2*(A[0]*(Q[1]-B[1]) + Q[0]*(B[1]-A[1]) + B[0]*(A[1]-Q[1]))
    if abs(d) < 1e-9: return None
    ux = ((A[0]**2+A[1]**2)*(Q[1]-B[1]) + (Q[0]**2+Q[1]**2)*(B[1]-A[1]) + (B[0]**2+B[1]**2)*(A[1]-Q[1]))/d
    uy = ((A[0]**2+A[1]**2)*(B[0]-Q[0]) + (Q[0]**2+Q[1]**2)*(A[0]-B[0]) + (B[0]**2+B[1]**2)*(Q[0]-A[0]))/d
    return (ux,uy)

def build(p):
    rib=p["rib_t"]
    # collier
    co_u1 = rib/2
    co_u0 = co_u1 - (p["bar_t"] + 2*p["col_clr"] + 2*p["col_wall"])
    co_v1 = 0
    co_v0 = co_v1 - (p["bar_h"] + 2*p["col_clr"] + 2*p["col_wall"])
    ci = (co_u0+p["col_wall"], co_v0+p["col_wall"], co_u1-p["col_wall"], co_v1-p["col_wall"])
    # ruban
    spineTop=(0,0); spineBot=(0,-p["back_h"])
    armEnd=(p["arm_top"],0); bowlBot=(p["arm_bot"],-p["bowl_h"]); apex=(p["depth"],-p["bowl_h"]/2)
    cc=circ3(armEnd,apex,bowlBot)
    if cc is None: bowl=[armEnd,bowlBot]
    else:
        r=math.hypot(armEnd[0]-cc[0],armEnd[1]-cc[1])
        a0=math.degrees(math.atan2(armEnd[1]-cc[1],armEnd[0]-cc[0]))
        a1=math.degrees(math.atan2(bowlBot[1]-cc[1],bowlBot[0]-cc[0]))
        am=math.degrees(math.atan2(apex[1]-cc[1],apex[0]-cc[0]))
        n360=lambda x:x-360*math.floor(x/360)
        sweep=n360(a1-a0); span=sweep if n360(am-a0)<=sweep else sweep-360
        bowl=[(cc[0]+r*math.cos(math.radians(a0+span*i/48)),
               cc[1]+r*math.sin(math.radians(a0+span*i/48))) for i in range(49)]
    legEnd=(bowlBot[0]+p["leg_l"]*math.cos(math.radians(p["leg_ang"])),
            bowlBot[1]+p["leg_l"]*math.sin(math.radians(p["leg_ang"])))
    path=[spineBot,spineTop]+bowl+[legEnd]
    maxx=max(q[0] for q in path)
    tube=(maxx - rib/2 - p["clr"] - p["tube_d"]/2, -p["bowl_h"]/2)
    real=dict(arm_top=p["arm_top"], depth=p["depth"], bowl_h=p["bowl_h"],
              arm_bot=p["arm_bot"], back_h=p["back_h"], leg_l=p["leg_l"], tube_d=p["tube_d"])
    return dict(collar=(co_u0,co_v0,co_u1,co_v1), ci=ci, path=path, maxx=maxx,
                tube=tube, legEnd=legEnd, bowlBot=bowlBot, real=real,
                fits=(tube[0]-p["tube_d"]/2 > co_u1) and (maxx-tube[0] >= rib/2+p["tube_d"]/2+p["clr"]-0.35))

def dim(ax,p0,p1,txt,color="#3161c9",off=0.0):
    ax.annotate("",xy=p1,xytext=p0,arrowprops=dict(arrowstyle="<->",color=color,lw=1.1))
    mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    ax.text(mx,my+off,txt,color=color,fontsize=7.5,ha="center",va="center",
            bbox=dict(fc="white",ec="none",alpha=.75,pad=.4))

def draw(ax,p,g,tgt,title):
    co_u0,co_v0,co_u1,co_v1=g["collar"]; ci=g["ci"]
    ax.add_patch(plt.Rectangle((co_u0,co_v0),co_u1-co_u0,co_v1-co_v0,fc="#ddd",ec="k",lw=.8))
    ax.add_patch(plt.Rectangle((ci[0],ci[1]),ci[2]-ci[0],ci[3]-ci[1],fc="w",ec="k",lw=.8))
    ax.text(co_u0+1.2,(co_v0+co_v1)/2,"jonc",fontsize=8,va="center",rotation=90)
    # cible du croquis (pointilles)
    if tgt:
        gt=build({**p, **{k:tgt[k] for k in ("arm_top","depth","bowl_h","arm_bot","back_h","leg_l") if k in tgt},
                  "leg_ang":tgt.get("leg_ang",p["leg_ang"]), "tube_d":tgt.get("tube_d",p["tube_d"])})
        xs=[q[0] for q in gt["path"]]; ys=[q[1] for q in gt["path"]]
        ax.plot(xs,ys,"--",color="#a24be0",lw=p["rib_t"]*3.4,alpha=.35,solid_capstyle="round")
    # tube
    ax.add_patch(Circle(g["tube"],p["tube_d"]/2,fc="#F0997B",ec="#993C1D",lw=1.3))
    ax.text(*g["tube"],"tube\nØ%.2f"%p["tube_d"],ha="center",va="center",fontsize=8,zorder=3)
    # profil
    xs=[q[0] for q in g["path"]]; ys=[q[1] for q in g["path"]]
    ax.plot(xs,ys,"-",color="#1D9E75",lw=p["rib_t"]*3.6,solid_capstyle="round",alpha=.92,zorder=2)
    # cotes reel/cible
    r=g["real"]; t=tgt or {}
    def lab(k,base): return "%s %g/%.1f"%(base,t[k],r[k]) if k in t else "%s %.1f"%(base,r[k])
    dim(ax,(0,3.5),(p["arm_top"],3.5),lab("arm_top","bras"),off=.8)
    dim(ax,(0,7),(p["depth"],7),lab("depth","prof"),off=.8)
    dim(ax,(co_u0-4,0),(co_u0-4,-p["back_h"]),lab("back_h","dos"))
    dim(ax,(g["maxx"]+3,0),(g["maxx"]+3,-p["bowl_h"]),lab("bowl_h","ventre"),color="#c0392b")
    dim(ax,(0,-p["bowl_h"]),(p["arm_bot"],-p["bowl_h"]),lab("arm_bot","bas"),off=-1.4)
    dim(ax,g["bowlBot"],g["legEnd"],lab("leg_l","lang"),color="#993C1D")
    ax.set_aspect("equal"); ax.grid(alpha=.3)
    ax.set_xlim(co_u0-9,g["maxx"]+11); ax.set_ylim(-p["back_h"]-6,10)
    ax.set_xlabel("u : vers le porte-bagages →"); ax.set_ylabel("v : hauteur"); ax.set_title(title)

def main():
    p=scad_params(); tgt=targets()
    fig,ax=plt.subplots(figsize=(8.5,8))
    g=build(p)
    draw(ax,p,g,tgt,"crochet R v15  —  tube logé : %s"%("oui" if g["fits"] else "NON"))
    out=ROOT/"build"/"profil.png"; out.parent.mkdir(exist_ok=True)
    plt.tight_layout(); plt.savefig(out,dpi=110)
    print(f"  -> {out}")
    print("  tube logé :", "oui" if g["fits"] else "NON")
    if tgt:
        print("  cible-vs-reel :")
        for k in ("arm_top","depth","bowl_h","arm_bot","back_h","leg_l"):
            if k in tgt:
                print("    %-9s cible %6.2f   reel %6.2f   ecart %+5.2f"%(k,tgt[k],g["real"][k],g["real"][k]-tgt[k]))

if __name__=="__main__":
    main()
