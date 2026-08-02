#!/usr/bin/env python3
"""Comparaison de buses : 0,4 / 0,6 / 0,8 -- MESUREE, pas raisonnee.

Pourquoi cet outil existe
-------------------------
"Une buse plus grosse va plus vite" est vrai, mais pas partout, et le
raisonnement de coin de table se trompe de facteur. Deux regimes coexistent
dans ce projet, et ils ne repondent pas du tout pareil :

  - `gabarit` est un disque Ø150 de 2 mm : QUE des couches pleines. Le temps
    y est gouverne par le DEBIT (mm3/s), pas par les vitesses affichees.
    Grossir la buse n'aide que dans la mesure ou la hotend suit.
  - `cale` fait 30 mm de haut a 20 % de remplissage : le temps y est
    gouverne par le NOMBRE DE COUCHES et de perimetres. Grossir la buse
    divise les deux.

D'ou la regle de lecture de la table : regarder l'ecart entre le temps
tranche et le PLANCHER DE DEBIT (volume / debit). Quand les deux se
rejoignent, la piece est limitee par la hotend et il n'y a plus rien a
gagner ailleurs que sur le debit -- ou sur la geometrie.

LE DEBIT EST UNE HYPOTHESE, PAS UNE MESURE
------------------------------------------
`max_volumetric_speed` par buse ci-dessous est une estimation pour une
hotend d'origine d'Ender 3 V3 SE en PETG. C'est la seule valeur de ce
fichier qui ne soit pas verifiable ici : elle depend de la longueur de zone
de fusion, pas de la geometrie. Si la hotend ne tient pas 18 mm3/s en 0,8,
le gain annonce pour la 0,8 fond d'autant. Un test de debit (extrusion en
l'air a debit croissant jusqu'a sous-extrusion) le tranche en 10 minutes,
et c'est LA mesure a faire avant de croire la derniere ligne.

Ce que cet outil ne dit pas
---------------------------
Rien sur la PRECISION. Une buse de 0,8 ne rend pas un Ø6,4 comme une 0,4 :
le jeu de percage (`clr`) et le logement d'ecrou doivent etre reverifies
par une impression de `essai` A LA MEME BUSE. Le temps est ici ; la cote
se mesure sur la piece.
"""
import json, pathlib, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import slice_check as S

ROOT  = pathlib.Path(__file__).resolve().parent.parent
SPEC  = json.loads((ROOT / "tools" / "expected.json").read_text())
BUILD = ROOT / "build"

# Chaque config garde constantes les EPAISSEURS, pas les comptages :
#   parois  ~1,25 mm (3x0,42 / 2x0,62)      dessus-dessous  ~1,0 a 1,2 mm
# Sinon on comparerait des pieces differentes, pas des buses.
CONFIGS = [
    ("0,4 mm  couche 0,20", ["--nozzle-diameter", "0.4", "--layer-height", "0.2",
      "--first-layer-height", "0.2", "--extrusion-width", "0.42",
      "--first-layer-extrusion-width", "0.42", "--perimeters", "3",
      "--top-solid-layers", "5", "--bottom-solid-layers", "5",
      "--max-volumetric-speed", "10"], 10.0),
    ("0,6 mm  couche 0,30", ["--nozzle-diameter", "0.6", "--layer-height", "0.3",
      "--first-layer-height", "0.3", "--extrusion-width", "0.62",
      "--first-layer-extrusion-width", "0.62", "--perimeters", "2",
      "--top-solid-layers", "4", "--bottom-solid-layers", "4",
      "--max-volumetric-speed", "14"], 14.0),
    ("0,6 mm  + infill x2", ["--nozzle-diameter", "0.6", "--layer-height", "0.3",
      "--first-layer-height", "0.3", "--extrusion-width", "0.62",
      "--first-layer-extrusion-width", "0.62", "--perimeters", "2",
      "--top-solid-layers", "4", "--bottom-solid-layers", "4",
      "--infill-every-layers", "2", "--max-volumetric-speed", "14"], 14.0),
    ("0,8 mm  couche 0,40", ["--nozzle-diameter", "0.8", "--layer-height", "0.4",
      "--first-layer-height", "0.4", "--extrusion-width", "0.84",
      "--first-layer-extrusion-width", "0.84", "--perimeters", "2",
      "--top-solid-layers", "3", "--bottom-solid-layers", "3",
      "--max-volumetric-speed", "18"], 18.0),
]

# Ø1,75 -> mm3 par mm de filament ; sert a retrouver le volume extrude.
MM3_PAR_MM = 2.405


def secondes(t):
    """'11h 2m 32s' -> 39752. Le G-code n'expose que le texte."""
    s, n = 0, ""
    for c in t:
        if c.isdigit():
            n += c
        elif c in "hms" and n:
            s += int(n) * {"h": 3600, "m": 60, "s": 1}[c]
            n = ""
    return s


def hms(s):
    return f"{int(s)//3600}h{int(s)%3600//60:02d}" if s >= 3600 else f"{int(s)//60} min"


def main():
    parts = [p for p, s in SPEC["parts"].items() if s.get("printable", True)]
    if len(sys.argv) > 1:
        parts = [p for p in parts if p in sys.argv[1:]]

    print("  tranche par PrusaSlicer. Les debits par buse sont des HYPOTHESES")
    print("  de hotend d'origine (10 / 14 / 18 mm3/s) -- a confirmer par un")
    print("  test de debit. Le plancher = volume extrude / debit : c'est le")
    print("  temps incompressible si la hotend etait le seul frein.\n")

    for part in parts:
        stl = S.render(part)
        base = SPEC["parts"][part].get("slice_args", [])
        print(f"  {part}")
        ref = None
        for nom, args, flow in CONFIGS:
            g, err = S.slice_to(stl, str(BUILD / f"{part}_b.gcode"), args + base)
            if g is None:
                print(f"    {nom:<22} ECHEC : {err.strip()[:70]}")
                continue
            a = S.analyse(g)
            t = secondes(a["temps"])
            ref = ref if ref is not None else t
            vol = a["g_total"] / S.MM_EN_G * MM3_PAR_MM      # mm3 extrudes
            plancher = vol / flow
            print(f"    {nom:<22} {hms(t):>7}  {a['poids']:>5.1f} g   "
                  f"x{ref/t if t else 0:.2f}   plancher debit {hms(plancher):>7}"
                  f"  ({100*plancher/t if t else 0:.0f} % du temps)")
        print()


if __name__ == "__main__":
    main()
