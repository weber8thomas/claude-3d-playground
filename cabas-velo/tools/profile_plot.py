#!/usr/bin/env python3
"""Trace le profil 2D du crochet avec le tube en place, cotes CIBLE superposees.

Une image vaut trois allers-retours. Les deux plus grosses erreurs de ce
projet (l'anneau massif, puis le berceau qu'on ne pouvait pas engager)
auraient saute aux yeux sur ce trace. Fais-le tourner avant d'imprimer.

Deux sources, jamais melangees :
  - les cotes REELLES sont derivees des parametres lus dans le .scad ;
  - les cotes CIBLE (le croquis) sont lues dans docs/target_hook.json.
On ne recopie aucune valeur : on les met cote a cote pour voir l'ecart.
"""
import json, math, pathlib, re, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

ROOT   = pathlib.Path(__file__).resolve().parent.parent
SRC    = ROOT / "src" / "cabas_velo.scad"
TARGET = ROOT / "docs" / "target_hook.json"

def scad_params():
    """Lit les cotes directement dans le .scad : jamais de valeur recopiee."""
    txt = SRC.read_text()
    def v(name):
        m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)\s*;", txt, re.M)
        if not m: sys.exit(f"parametre '{name}' introuvable dans {SRC}")
        return float(m.group(1))
    return {k: v(k) for k in ("bar_h","bar_t","tube_d","rib_t","clr","hook_depth",
                              "wrap_end","lang_l","lang_ang","col_wall","col_clr")}

def targets():
    """Cotes du croquis (verite externe). Absent -> pas de superposition."""
    if not TARGET.exists(): return {}
    return {k: c["val"] for k, c in json.loads(TARGET.read_text())["cotes"].items()}

def build(p, wrap_end=None):
    we = p["wrap_end"] if wrap_end is None else wrap_end
    la = p["lang_ang"]
    ci_u0, ci_u1 = -p["bar_t"]-p["col_clr"], p["col_clr"]
    co_u0, co_u1 = ci_u0-p["col_wall"], ci_u1+p["col_wall"]
    ci_v0, ci_v1 = -p["col_clr"], p["bar_h"]+p["col_clr"]
    co_v0, co_v1 = ci_v0-p["col_wall"], ci_v1+p["col_wall"]
    Rc = p["tube_d"]/2 + p["clr"] + p["rib_t"]/2
    cu = co_u1 + p["hook_depth"] - p["rib_t"]/2 - Rc
    v_top = co_v1 - p["rib_t"]/2
    cv = v_top - Rc
    lipe = (cu + Rc*math.cos(math.radians(we)), cv + Rc*math.sin(math.radians(we)))
    u_tip = lipe[0] + p["lang_l"]*math.cos(math.radians(la))
    v_tip = lipe[1] + p["lang_l"]*math.sin(math.radians(la))
    arc = [(cu+Rc*math.cos(math.radians(a)), cv+Rc*math.sin(math.radians(a)))
           for a in range(90, int(we)-1, -5)]
    arc_low = min(cv - Rc, cv + Rc*math.sin(math.radians(we)))
    real = dict(
        hook_depth = cu + Rc + p["rib_t"]/2 - co_u1,
        back_h     = (v_top + p["rib_t"]/2) - (v_tip - p["rib_t"]/2),
        bowl_h     = (cv + Rc) - arc_low + p["rib_t"],
        arm_top    = cu - co_u1,
        lang_l     = p["lang_l"],
        tube_d     = p["tube_d"],
    )
    return dict(collar=(co_u0,co_v0,co_u1,co_v1,ci_u0,ci_v0,ci_u1,ci_v1),
                Rc=Rc, cu=cu, cv=cv, v_top=v_top, tip=(u_tip,v_tip),
                path=[(0,v_top)]+arc+[(u_tip,v_tip)],
                mouth=(u_tip - p["rib_t"]/2) - co_u1, real=real)

def dim(ax, p0, p1, text, color="#3161c9", off=0.0):
    """Petite cote a double fleche."""
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.1))
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    ax.text(mx, my+off, text, color=color, fontsize=7.5, ha="center", va="center",
            bbox=dict(fc="white", ec="none", alpha=.75, pad=.4))

def draw(ax, p, g, tgt, title):
    co_u0,co_v0,co_u1,co_v1,ci_u0,ci_v0,ci_u1,ci_v1 = g["collar"]
    ax.add_patch(plt.Rectangle((co_u0,co_v0),co_u1-co_u0,co_v1-co_v0,fc="#ddd",ec="k",lw=.8))
    ax.add_patch(plt.Rectangle((ci_u0,ci_v0),ci_u1-ci_u0,ci_v1-ci_v0,fc="w",ec="k",lw=.8))
    ax.text(co_u0+.5, p["bar_h"]/2, "JONC", fontsize=8, va="center", rotation=90)
    ax.add_patch(Circle((g["cu"],g["cv"]), p["tube_d"]/2, fc="#F0997B", ec="#993C1D", lw=1.3))
    ax.text(g["cu"], g["cv"], "tube\nØ%.2f"%p["tube_d"], ha="center", va="center", fontsize=8, zorder=3)
    xs=[q[0] for q in g["path"]]; ys=[q[1] for q in g["path"]]
    ax.plot(xs, ys, "-", color="#1D9E75", lw=p["rib_t"]*3.6, solid_capstyle="round", alpha=.9, zorder=2)
    ax.plot(*g["tip"], "rv", ms=10, zorder=4)
    ax.plot([co_u1, g["tip"][0]-p["rib_t"]/2],[g["tip"][1]]*2, "r-", lw=1.2)
    ax.text((co_u1+g["tip"][0])/2-4, g["tip"][1]-2.6,
            "bouche %.2f  (tube %.2f)"%(g["mouth"], p["tube_d"]), color="r", fontsize=9)

    r = g["real"]; top = g["v_top"]+p["rib_t"]/2; bot = g["tip"][1]-p["rib_t"]/2
    # --- cotes CIBLE (tirets) vs REEL, superposees
    if tgt:
        yD = top + 3.5   # profondeur, en haut, depuis la face du collier
        ax.plot([co_u1, co_u1+tgt["hook_depth"]], [yD, yD], "--", color="#3161c9", lw=.8)
        dim(ax, (co_u1, yD), (co_u1+tgt["hook_depth"], yD),
            "profondeur  cible %g / reel %.1f"%(tgt["hook_depth"], r["hook_depth"]), off=.9)
        xH = co_u0 - 4.0  # hauteur du dos, a gauche
        dim(ax, (xH, top), (xH, top-tgt["back_h"]),
            "dos  cible %g / reel %.1f"%(tgt["back_h"], r["back_h"]))
        ax.plot([xH-1, co_u0], [top, top], ":", color="#3161c9", lw=.6)
        ax.plot([xH-1, co_u0], [top-tgt["back_h"]]*2, ":", color="#3161c9", lw=.6)
        dim(ax, (co_u1, top+1.4), (co_u1+tgt["arm_top"], top+1.4),  # bras du haut
            "bras %g / %.1f"%(tgt["arm_top"], r["arm_top"]), off=.8)
        xB = g["cu"] + g["Rc"] + 3.2  # ventre (hauteur), a droite du tube
        dim(ax, (xB, g["cv"]+tgt["bowl_h"]/2), (xB, g["cv"]-tgt["bowl_h"]/2),
            "ventre %g / %.1f"%(tgt["bowl_h"], r["bowl_h"]))
        dim(ax, g["tip"], (g["tip"][0], g["tip"][1]+tgt["lang_l"]),  # languette
            "lang %g / %.1f"%(tgt["lang_l"], r["lang_l"]), color="#993C1D")

    ax.set_aspect("equal"); ax.grid(alpha=.3)
    ax.set_xlim(co_u0-9, g["cu"]+g["Rc"]+11); ax.set_ylim(bot-4, top+7)
    ax.set_xlabel("u : vers le porte-bagages →"); ax.set_title(title)

def main():
    p = scad_params(); tgt = targets()
    fig, ax = plt.subplots(figsize=(8.5,7.5))
    g = build(p)
    draw(ax, p, g, tgt,
         "wrap_end=%g°  lang=%g@%g°   interference bouche %+.2f mm"
         % (p["wrap_end"], p["lang_l"], p["lang_ang"], p["tube_d"]-g["mouth"]))
    ax.set_ylabel("v : hauteur")
    out = ROOT/"build"/"profil.png"; out.parent.mkdir(exist_ok=True)
    plt.tight_layout(); plt.savefig(out, dpi=110)
    print(f"  -> {out}")
    print("  bouche %.2f mm, tube %.2f mm, interference %+.2f mm"
          % (g["mouth"], p["tube_d"], p["tube_d"]-g["mouth"]))
    if tgt:
        print("  cible-vs-reel :")
        for k in ("hook_depth","back_h","bowl_h","arm_top","lang_l"):
            print("    %-11s cible %6.2f   reel %6.2f   ecart %+5.2f"
                  % (k, tgt[k], g["real"][k], g["real"][k]-tgt[k]))

if __name__ == "__main__":
    main()
