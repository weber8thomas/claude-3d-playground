#!/usr/bin/env python3
"""Harnais de verification de la cale de ventilateur.

Meme doctrine que `cabas-velo` : on ne conclut pas sur une relecture de code,
on rend et on mesure le maillage. Six gardes, chacune pour une classe de bug :

  1. Variable perdue    -> OpenSCAD emet un WARNING et rend quand meme, un
                           maillage irreprochable de la MAUVAISE piece.
                           TOUT WARNING EST FATAL. Aucun outil de maillage
                           ne remplace cette garde.
  2. Corps flottant     -> trimesh compte les corps, verifie l'etancheite et
                           l'orientation des faces.
  3. Piece imprimable ? -> zmin = 0 (sinon supports) et encombrement plateau.
  4. Cotes hors-tout    -> bornes sur x, y, z.
  5. Volume             -> le .scad ANNONCE son volume analytique par echo ;
                           on confronte le maillage a cette annonce (0,5 %).
                           Ce n'est pas une mesure supposee : c'est de la
                           coherence interne entre ce que le modele dit et
                           ce qu'il produit.
  6. Percages           -> coupe a mi-hauteur : nombre de trous traversants,
                           et leurs centres compares a l'echo VIS_XY.
  7. CIBLE vs REEL      -> le maillage mesure, confronte a docs/target.json.

La garde 7 n'est pas un luxe. Un `bolt_r` faux ne bouge NI le volume (un trou
deplace occupe le meme volume), NI la boite englobante, NI aucun echo -- ils
en derivent tous. Teste : le harnais sans la garde 7 declarait vert une cale
dont le cercle de percage etait a 40 mm au lieu de 47. Il faut une source
qui ne vienne pas du .scad : c'est docs/target.json, la demande elle-meme.
C'est le meme dispositif que docs/target_hook.json dans `cabas-velo`.
"""
import json, pathlib, re, subprocess, sys, tempfile, warnings

warnings.filterwarnings("ignore")           # to_planar deprecation, trimesh 5
import trimesh
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / "src" / "cale_ventilateur.scad"
SPEC = json.loads((ROOT / "tools" / "expected.json").read_text())
TGT  = json.loads((ROOT / "docs" / "target.json").read_text())
BED  = SPEC["bed"]


def render(part, defines=None):
    out = tempfile.NamedTemporaryFile(suffix=".stl", delete=False).name
    cmd = ["openscad", "-o", out, "-D", f'part="{part}"', str(SRC)]
    for k, v in (defines or {}).items():
        cmd[-1:-1] = ["-D", f"{k}={v}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return out, p.stderr


def echoes(err):
    """Les valeurs derivees, telles que le modele les annonce. Rien n'est
    recopie depuis le .scad : on lit ce qu'il dit."""
    return {k.strip(): v.strip()
            for k, v in re.findall(r'ECHO: "([^=]+?)\s*=\s*([^"]*)"', err)}


def ring(r):
    """Centre et rayon moyen d'un contour circulaire, mesures sur ses points."""
    p = np.asarray(r.coords)[:-1]
    c = p.mean(axis=0)
    return c, float(np.hypot(*(p - c).T).mean())


def holes_at(m, z):
    """Trous traversants vus dans une coupe horizontale.

    Retourne (nb de contours exterieurs, [(cx, cy, rayon), ...], rayon ext).
    Un percage qui ne traverse pas, un percage de trop, un triangle mal
    oriente : tout se voit ici et nulle part ailleurs."""
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return 0, [], 0.0
    planar, _ = sec.to_planar()
    shells = planar.polygons_full
    holes = [(*ring(r)[0], ring(r)[1]) for g in shells for r in g.interiors]
    r_out = max((ring(g.exterior)[1] for g in shells), default=0.0)
    return len(shells), holes, r_out


def cible_vs_reel(holes, r_out, thickness):
    """Garde 7 : le maillage MESURE, confronte a docs/target.json.

    Aucune valeur ne vient du .scad. Si le modele se trompe de cercle de
    percage, c'est ici -- et seulement ici -- que ca se voit."""
    fails, tol = [], TGT["tol"]
    L, A = tol["longueur"], tol["angle"]
    jmin, jmax = tol["jeu_percage"]

    def cmp(label, got, want, t=L):
        if abs(got - want) > t:
            fails.append(f"CIBLE {label} : {got:.2f} mesure vs {want:g} demande")

    cmp("epaisseur", thickness, TGT["disc_t"]) if thickness else None
    cmp("Ø disque", 2 * r_out, TGT["disc_d"])

    if not holes:
        return fails + ["CIBLE : aucun percage traversant"]

    # le trou du cable est celui qui est sur l'axe ; les autres sont les vis
    cable = min(holes, key=lambda h: np.hypot(h[0], h[1]))
    vis = [h for h in holes if h is not cable]
    cmp("Ø passage cable", 2 * cable[2], TGT["cable_d"])
    cmp("centrage du passage cable", np.hypot(cable[0], cable[1]), 0.0, 0.2)

    if len(vis) != TGT["n_holes"]:
        return fails + [f"CIBLE : {len(vis)} percage(s) de vis, "
                        f"attendu {TGT['n_holes']}"]

    # jeu de percage : voulu, mais jamais negatif (la vis doit passer)
    for _, _, r in vis:
        j = 2 * r - TGT["hole_d"]
        if not (jmin - 1e-6 <= j <= jmax + 1e-6):
            fails.append(f"CIBLE jeu de percage : {j:+.2f} mm "
                         f"(Ø{2*r:.2f} pour une vis Ø{TGT['hole_d']:g}), "
                         f"attendu dans [{jmin:g} ; {jmax:g}]")

    # triangle equilateral : meme rayon, 120 deg entre chaque
    rayons = sorted(np.hypot(x, y) for x, y, _ in vis)
    if rayons[-1] - rayons[0] > L:
        fails.append(f"CIBLE triangle : rayons inegaux {rayons[0]:.2f} "
                     f"a {rayons[-1]:.2f} mm")
    angs = sorted(np.degrees(np.arctan2(y, x)) % 360 for x, y, _ in vis)
    ecarts = [(angs[(i + 1) % 3] - angs[i]) % 360 for i in range(3)]
    if max(abs(e - 120) for e in ecarts) > A:
        fails.append("CIBLE triangle non equilateral : ecarts angulaires "
                     + ", ".join(f"{e:.1f}deg" for e in ecarts))

    # LA cote de la demande : du BORD DU TROU au bord du disque.
    # Mesuree sur le maillage, comparee au diametre NOMINAL de la vis --
    # le jeu de percage est deja controle plus haut, il ne doit pas la fausser.
    marge = r_out - np.mean(rayons) - TGT["hole_d"] / 2
    cmp("marge bord du trou -> bord", marge, TGT["edge_margin"])
    return fails


def check(part, spec):
    stl, err = render(part, spec.get("defines"))
    fails, ech = [], echoes(err)

    if "ERROR" in err:
        for l in err.splitlines():
            if "ERROR" in l:
                fails.append(f"ERROR OpenSCAD: {l.strip()}")
        return fails, ech

    # -- 1. LA garde qu'aucun outil de maillage ne peut remplacer.
    warns = [l.strip() for l in err.splitlines() if l.startswith("WARNING")]
    if warns:
        fails.append(f"{len(warns)} WARNING(s), le premier : {warns[0][:90]}")

    m = trimesh.load(stl)
    lo, hi = m.bounds
    dims = [hi[i] - lo[i] for i in range(3)]

    # -- 2. maillage
    n = len(m.split(only_watertight=False))
    if n != spec.get("bodies", 1):
        fails.append(f"{n} corps, attendu {spec.get('bodies', 1)}")
    if not m.is_watertight:
        fails.append("maillage non etanche : le trancheur produira n'importe quoi")
    if not m.is_winding_consistent:
        fails.append("orientation des faces incoherente")

    # -- 3. imprimabilite
    if spec.get("printable", True):
        if abs(lo[2]) > 1e-3:
            fails.append(f"zmin = {lo[2]:.3f}, doit valoir 0 (support requis)")
        if dims[0] > BED[0] or dims[1] > BED[1] or dims[2] > BED[2]:
            fails.append(f"hors plateau : {dims[0]:.1f}x{dims[1]:.1f}x{dims[2]:.1f}")

    # -- 4. cotes hors-tout
    for k, (lo_b, hi_b) in spec.get("dims", {}).items():
        i = "xyz".index(k)
        if not (lo_b <= dims[i] <= hi_b):
            fails.append(f"dim {k} = {dims[i]:.2f}, attendu [{lo_b}, {hi_b}]")

    # -- 5. volume annonce vs volume mesure
    key = spec.get("volume_echo")
    if key:
        if key not in ech:
            fails.append(f"echo {key} absent : le modele n'annonce plus son volume")
        else:
            want, got = float(ech[key]), m.volume
            d = (got - want) / want
            if abs(d) > spec.get("volume_tol", 0.005):
                fails.append(f"volume {got:.0f} mm3 vs {want:.0f} annonce "
                             f"({d*100:+.2f} %)")

    # -- 6. percages traversants, au bon endroit
    sec = spec.get("section")
    if sec:
        shells, holes, r_out = holes_at(m, sec["z"])
        if shells != sec["shells"]:
            fails.append(f"coupe z={sec['z']} : {shells} contour(s), "
                         f"attendu {sec['shells']}")
        if len(holes) != sec["holes"]:
            fails.append(f"coupe z={sec['z']} : {len(holes)} trou(s) "
                         f"traversant(s), attendu {sec['holes']}")
        else:
            if sec.get("match_vis_xy"):
                want = json.loads(ech.get("VIS_XY", "[]")) + [[0, 0]]
                for wx, wy in want:
                    d = min(np.hypot(cx - wx, cy - wy) for cx, cy, _ in holes)
                    if d > 0.15:
                        fails.append(f"aucun trou en ({wx:.2f}, {wy:.2f}) : "
                                     f"le plus proche est a {d:.2f} mm")
            # -- 7. cible vs reel. `epaisseur` n'a de sens que pour la cale :
            #    le gabarit est volontairement fin, il ne porte que le plan.
            if sec.get("target"):
                fails += cible_vs_reel(holes, r_out,
                                       dims[2] if sec["target"] == "full" else 0)

    return fails, ech


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    bad, last = 0, {}
    for part, spec in SPEC["parts"].items():
        if only and part != only:
            continue
        fails, ech = check(part, spec)
        last = ech or last
        if fails:
            bad += 1
            print(f"  FAIL  {part}")
            for f in fails:
                print(f"          {f}")
        else:
            print(f"  ok    {part}")

    if not only and last:
        print("\n  cotes derivees (annoncees par le modele) :")
        for k, v in last.items():
            if not k.startswith("V_"):
                print(f"    {k:<28} = {v}")

    # -- balayage : le modele doit rester sain sur la plage utile. Le jeu de
    #    percage et l'epaisseur sont les deux parametres qu'on retouchera.
    if not only:
        print("\n  balayage (le jeu de percage et l'epaisseur ne sont pas figes) :")
        for var, vals in SPEC["sweep"].items():
            for v in vals:
                _, err = render("cale", {var: v})
                ko = "ERROR" in err or "WARNING" in err
                bad += ko
                note = next((l.strip()[:70] for l in err.splitlines()
                             if "ERROR" in l or "WARNING" in l), "")
                e = echoes(err)
                info = note if ko else f"web_e {e.get('web_e (trou -> bord)', '?')}"
                print(f"    {'FAIL' if ko else 'ok  '}  {var}={v:<6} {info}")

    print()
    if bad:
        print(f"{bad} verification(s) en echec.")
        sys.exit(1)
    print("Tout est vert.")


if __name__ == "__main__":
    main()
