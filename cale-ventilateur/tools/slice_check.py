#!/usr/bin/env python3
"""Garde 8 : trancher pour de vrai, au lieu d'estimer.

`cabas-velo` traine ce TODO dans son verify.py depuis le debut :

    garde n.4, des que prusaslicer est disponible : trancher et exiger
    qu'aucun support ne soit genere. C'est la formulation forte de zmin = 0.

Le voici -- mais PAS sous cette forme, parce que cette forme-la ne garde rien.

CE QUI NE MARCHE PAS, ET POURQUOI
---------------------------------
« Trancher et exiger qu'aucun support ne soit genere » est **circulaire** :
le profil de production a `support_material = 0`, donc PrusaSlicer n'en
genere jamais, quelle que soit la piece. Une etagere en porte-a-faux passe
cette garde-la sans broncher. Verifie.

« Exiger que l'auto-detecteur n'en reclame aucun » ne marche pas non plus,
en sens inverse : trop severe. Il signale TOUTE face horizontale, quelle que
soit la portee. Sur la cale, il veut remplir les trois puits Ø14 sur 27 mm
de haut -- 3,2 g qu'on ne pourrait jamais aller curer au fond d'un trou
borgne -- pour un annulaire de 1,8 mm qui se ponte sans difficulte.

« Tout porte-a-faux doit etre ponte » (Overhang perimeter sans Bridge infill)
ne mord pas davantage : PrusaSlicer ponte a peu pres tout ce qu'il peut, y
compris ce qui pendrait vraiment. Teste sur la cale retournee : zero
detection.

CE QUI MARCHE
-------------
La PART de support, rapportee au poids de la piece. Mesure :

    cale              3,22 g / 190,06 g  ->   1,7 %
    gabarit           0,00 g /  43,08 g  ->   0,0 %
    etagere temoin    1,89 g /   6,05 g  ->  31,2 %   <- temoin, doit echouer

La masse absolue ne discriminerait rien : l'etagere temoin, minuscule,
demande MOINS de support que la cale. C'est le rapport qui parle.

Ce n'est pas une garde parfaite -- c'est un canari. Elle tolere les plafonds
de lamage, qu'on ponte deliberement, et elle crie si une vraie surface en
porte-a-faux apparait.

VERIFICATION DU PROFIL, avant toute mesure
------------------------------------------
Un .ini PrusaSlicer est PLAT. Avec des en-tetes [print]/[filament]/[printer]
il est silencieusement ignore : le trancheur retombe sur ses defauts (couche
0,3, buse 200, plateau 0, plateau 200x200) sans rien signaler. On croit
mesurer, on ne mesure rien -- c'est arrive, et ca a produit un « 3h36 pour le
gabarit » qui ne voulait rien dire. On relit donc l'en-tete du G-code avant
de croire quoi que ce soit.

CE QUE LES TEMPS NE SONT PAS
----------------------------
L'utilisateur imprime sous **Cura + Klipper**. PrusaSlicer n'est ici que
parce qu'il est le seul trancheur pilotable en ligne de commande (CuraEngine
n'est pas empaquetable). Un temps sorti d'ici est un ORDRE DE GRANDEUR : sous
Klipper le temps reel depend surtout de `max_accel` et de l'input shaper. La
garde sur les supports, elle, porte sur la geometrie et pas sur la machine.
"""
import json, pathlib, re, subprocess, sys

ROOT  = pathlib.Path(__file__).resolve().parent.parent
SRC   = ROOT / "src" / "cale_ventilateur.scad"
INI   = ROOT / "slicer" / "ender3v3se_petg.ini"
SPEC  = json.loads((ROOT / "tools" / "expected.json").read_text())
BUILD = ROOT / "build"

# Ø1,75 -> 2,405 mm3 par mm de filament ; PETG a 1,27 g/cm3.
MM_EN_G = 2.405 / 1000 * 1.27

# Les valeurs qui DOIVENT arriver jusqu'au trancheur (voir le docstring).
ATTENDU = {"layer_height": "0.2", "temperature": "235", "bed_temperature": "70",
           "max_volumetric_speed": "10", "external_perimeter_speed": "50",
           "bed_shape": "0x0,220x0,220x220,0x220"}


def render(part):
    BUILD.mkdir(exist_ok=True)
    stl = BUILD / f"{part}.stl"
    subprocess.run(["openscad", "-o", str(stl), "-D", f'part="{part}"', str(SRC)],
                   capture_output=True, text=True)
    return str(stl)


def slice_to(stl, out, extra):
    p = subprocess.run(["prusa-slicer", "--export-gcode", "--load", str(INI)]
                       + list(extra) + ["-o", out, stl],
                       capture_output=True, text=True)
    f = pathlib.Path(out)
    return f.read_text(errors="ignore") if f.exists() else None, p.stderr


def analyse(g):
    """Par hauteur : types d'extrusion. Plus l'en-tete, le temps, les masses."""
    z = t = None
    e_prev = None
    par_z, e_sup, e_tot = {}, 0.0, 0.0
    for l in g.splitlines():
        if l.startswith(";TYPE:"):
            t = l[6:].strip()
            continue
        if not l.startswith("G1"):
            continue
        m = re.search(r"\bZ([\d.]+)", l)
        if m:
            z = round(float(m.group(1)), 2)
        m = re.search(r"\bE([-\d.]+)", l)
        if m:
            e = float(m.group(1))
            if e_prev is not None and e > e_prev:
                e_tot += e - e_prev
                if t and t.startswith("Support"):
                    e_sup += e - e_prev
                if z is not None and t:
                    par_z.setdefault(z, set()).add(t)
            e_prev = e
    tps = re.search(r"estimated printing time \(normal mode\) = (.+)", g)
    gr = re.search(r"total filament used \[g\] = ([\d.]+)", g)
    return {"par_z": par_z,
            "entete": dict(re.findall(r"^; (\w+) = (.*)$", g, re.M)),
            "temps": tps.group(1).strip() if tps else "?",
            "poids": float(gr.group(1)) if gr else 0.0,
            "g_support": e_sup * MM_EN_G,
            "g_total": e_tot * MM_EN_G}


def check(part, spec, seuil):
    extra = spec.get("slice_args", [])
    stl = render(part)

    # -- tranche de PRODUCTION : temps, poids, ponts
    g, err = slice_to(stl, str(BUILD / f"{part}.gcode"), extra)
    if g is None:
        return [f"PrusaSlicer a echoue : {err.strip()[:120]}"], None
    a = analyse(g)

    fails = [f"profil non applique : {k} = {a['entete'].get(k)!r}, attendu "
             f"{v!r} -- le .ini n'a pas ete lu"
             for k, v in ATTENDU.items() if a["entete"].get(k) != v]
    if fails:
        return fails, None

    # -- tranche de DIAGNOSTIC : supports en auto, pour mesurer ce que la
    #    geometrie reclamerait vraiment.
    gs, err = slice_to(stl, str(BUILD / f"{part}_sup.gcode"),
                       extra + ["--support-material", "--support-material-auto"])
    if gs is None:
        return [f"PrusaSlicer (auto-support) a echoue : {err.strip()[:120]}"], None
    s = analyse(gs)
    part_sup = 100 * s["g_support"] / s["g_total"] if s["g_total"] else 0.0
    if part_sup > seuil:
        fails.append(f"{part_sup:.1f} % de support reclame ({s['g_support']:.2f} g "
                     f"sur {s['g_total']:.1f} g), seuil {seuil:g} % : ce n'est "
                     f"plus un plafond de lamage, c'est du porte-a-faux")

    ponts = sorted(z for z, ts in a["par_z"].items() if "Bridge infill" in ts)
    return fails, (a["temps"], a["poids"], part_sup, ponts)


def main():
    seuil = SPEC.get("support_max_pct", 10)
    print("  tranche par PrusaSlicer avec slicer/ender3v3se_petg.ini")
    print("  temps = ordre de grandeur (l'utilisateur imprime sous Cura + Klipper) ;")
    print("  la part de support, elle, porte sur la geometrie.\n")
    print(f"  {'piece':<14} {'temps':>12} {'poids':>8} {'support':>9}   ponts (z)")
    bad = 0
    for part, spec in SPEC["parts"].items():
        if not spec.get("printable", True):
            continue
        fails, res = check(part, spec, seuil)
        if fails:
            bad += 1
            print(f"  FAIL  {part}")
            for f in fails:
                print(f"          {f}")
            continue
        tps, gr, pct, ponts = res
        z = ", ".join(f"{x:g}" for x in ponts[:4]) + ("…" if len(ponts) > 4 else "")
        print(f"  {part:<14} {tps:>12} {gr:>6.1f} g {pct:>8.1f} %   {z or 'aucun'}")

    # -- LE TEMOIN. Une garde qui n'a jamais echoue ne garde rien : on rejoue
    #    a chaque fois la piece qui DOIT etre rejetee. Si elle passe, ce n'est
    #    pas elle qui est en cause, c'est la garde.
    temoin = BUILD / "temoin.stl"
    subprocess.run(["openscad", "-o", str(temoin),
                    str(ROOT / "tools" / "temoin_porte_a_faux.scad")],
                   capture_output=True, text=True)
    gs, _ = slice_to(str(temoin), str(BUILD / "temoin.gcode"),
                     ["--support-material", "--support-material-auto"])
    t = analyse(gs) if gs else None
    pct = 100 * t["g_support"] / t["g_total"] if t and t["g_total"] else 0.0
    if pct > seuil:
        print(f"\n  {'temoin':<14} porte-a-faux pur      {pct:>8.1f} %   "
              f"rejete, la garde mord")
    else:
        bad += 1
        print(f"\n  FAIL  temoin : {pct:.1f} % seulement, sous le seuil de "
              f"{seuil:g} % -- la garde 8 ne mord plus")

    print()
    if bad:
        print(f"{bad} echec(s).")
        sys.exit(1)
    print(f"Aucune piece ne reclame plus de {seuil:g} % de support, "
          f"et le temoin est bien rejete.")


if __name__ == "__main__":
    main()
