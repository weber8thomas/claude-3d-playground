#!/usr/bin/env python3
"""Harnais de verification de la cale de ventilateur.

Meme doctrine que `cabas-velo` : on ne conclut pas sur une relecture de code,
on rend et on mesure le maillage. Sept gardes, chacune pour une classe de bug :

  1. Variable perdue    -> OpenSCAD emet un WARNING et rend quand meme, un
                           maillage irreprochable de la MAUVAISE piece.
                           TOUT WARNING EST FATAL. Aucun outil de maillage
                           ne remplace cette garde.
  2. Corps flottant     -> trimesh compte les corps, verifie l'etancheite et
                           l'orientation des faces.
  3. Piece imprimable ? -> zmin = 0 (sinon supports) et encombrement plateau.
  4. Cotes hors-tout    -> bornes sur x, y, z.
  5. Volume             -> le .scad ANNONCE son volume analytique par echo ;
                           on confronte le maillage a cette annonce (0,5 a 1 %).
                           Ce n'est pas une mesure supposee : c'est de la
                           coherence interne entre ce que le modele dit et
                           ce qu'il produit.
  6. Percages           -> coupe horizontale : nombre de trous traversants,
                           et leurs centres compares aux echos VIS_*_XY.
  7. CIBLE vs REEL      -> le maillage mesure, confronte a docs/target.json :
                           les deux triangles, leur decalage, les jeux de
                           percage, la marge au bord, et l'ancrage qui reste
                           a une vis de 30 mm une fois le lamage creuse.

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
import shapely

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / "src" / "cale_ventilateur.scad"
SPEC = json.loads((ROOT / "tools" / "expected.json").read_text())
TGT  = json.loads((ROOT / "docs" / "target.json").read_text())
BED  = SPEC["bed"]

# Epsilon des comparaisons de tolerance. 1 micron : cent fois plus fin que
# ce qu'une imprimante FDM resout, et vingt fois plus grossier que le bruit
# du maillage. Un epsilon a 1e-6 comparait plus finement que la mesure
# elle-meme et sortait "hors plage" pour 5e-5 mm d'ecart a la borne.
EPS = 1e-3


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
    """Centre, rayon MOYEN et APOTHEME (rayon du cercle inscrit) d'un contour.

    Les deux rayons ne sont pas interchangeables, et confondre les deux a
    coute une garde a ce projet :

      Le rayon moyen n'a de sens que sur un cercle. Le logement d'ecrou est
      un hexagone dont le contour STL porte 12 points -- 6 sommets a 5,947 et
      6 nes de la triangulation des faces -- et sa moyenne tombe entre le
      sommet et le plat. La garde annoncait 9,78 mm sur plats pour un
      logement qui en mesure exactement 10,300. La piece etait bonne ; c'est
      la mesure qui etait fausse, et rien ne le signalait.

    L'apotheme est la distance du centre au SEGMENT le plus proche, pas au
    sommet le plus proche -- sur un hexagone les deux different de 13 %.
    C'est lui qu'il faut pour tout emboitement : c'est le cercle inscrit que
    la vis touche et que l'ecrou doit franchir. Sur les percages Ø6,4, le
    rayon moyen dit 3,195 quand la vis, elle, ne voit que 3,190.

    Le centre est le barycentre de la SURFACE, pas la moyenne des points : le
    contour porte des points supplementaires, nes de la triangulation et
    repartis sans symetrie, qui decalent la moyenne. L'ecart etait de 5e-5 mm
    -- physiquement nul, mais assez pour faire basculer une comparaison a la
    borne."""
    p = np.asarray(r.coords)[:-1]
    c = np.asarray(shapely.Polygon(r).centroid.coords[0])
    a, b = p, np.roll(p, -1, axis=0)
    ab = b - a
    t = np.clip(((c - a) * ab).sum(1) / (ab * ab).sum(1), 0, 1)
    apo = float(np.hypot(*(a + t[:, None] * ab - c).T).min())
    return c, float(np.hypot(*(p - c).T).mean()), apo


def holes_at(m, z):
    """Trous traversants vus dans une coupe horizontale.

    Retourne (nb de contours exterieurs, [(cx, cy, rayon, apotheme), ...],
    rayon ext). Un percage qui ne traverse pas, un percage de trop, un
    triangle mal oriente : tout se voit ici et nulle part ailleurs."""
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return 0, [], 0.0
    planar, _ = sec.to_planar()
    shells = planar.polygons_full
    holes = [(*c, r, a) for g in shells for c, r, a in map(ring, g.interiors)]
    r_out = max((ring(g.exterior)[1] for g in shells), default=0.0)
    return len(shells), holes, r_out


def triangle(holes):
    """Isole les trois percages de vis d'une coupe : ni le cable, ni la
    contre-forme (lamage ou logement d'ecrou) qui les accompagne.

    Regle unique aux deux hauteurs : le cable est le contour sur l'axe ; les
    percages de vis sont les trois plus petits de ce qui reste."""
    cable = min(holes, key=lambda h: np.hypot(h[0], h[1]))
    autres = sorted((h for h in holes if h is not cable), key=lambda h: h[2])
    return cable, autres[:3], autres[3:]


def z_transition(m, xy, z_large, z_etroit):
    """Hauteur ou le percage en (x, y) passe de la contre-forme (lamage ou
    logement d'ecrou) au simple trou de vis, trouvee par dichotomie.

    Deux cotes en dependent, et aucune des deux n'est visible autrement :
    l'epaisseur du plafond de percage -- c'est elle qui rend les vis de
    30 mm suffisantes -- et la profondeur du logement d'ecrou."""
    def large(z):
        _, holes, _ = holes_at(m, z)
        if not holes:
            return False
        r = min(holes, key=lambda h: np.hypot(h[0] - xy[0], h[1] - xy[1]))[2]
        return r > 5.0                      # Ø14 ou hexa Ø11,9  vs  Ø6,4
    if not large(z_large) or large(z_etroit):
        return None                         # pas de contre-forme du tout
    a, b = z_large, z_etroit
    for _ in range(14):
        mid = (a + b) / 2
        if large(mid):
            a = mid
        else:
            b = mid
    return (a + b) / 2


def cible_vs_reel(m, ech):
    """Garde 7 : le maillage MESURE, confronte a docs/target.json.

    Aucune valeur comparee ne vient du .scad. Les echos ne servent qu'a
    choisir OU couper -- jamais a fournir une reference. Si le modele se
    trompe de cercle de percage, c'est ici, et seulement ici, que ca se voit."""
    fails, tol = [], TGT["tol"]
    L, A = tol["longueur"], tol["angle"]
    jmin, jmax = tol["jeu_percage"]
    lo, hi = m.bounds
    ep = float(hi[2] - lo[2])

    def cmp(label, got, want, t=L):
        if abs(got - want) > t:
            fails.append(f"CIBLE {label} : {got:.2f} mesure vs {want:g} demande")

    cmp("epaisseur", ep, TGT["disc_t"])

    # -- deux coupes. En haut (dans le plafond de percage) les vis PLAFOND
    #    sont des trous nus ; a mi-hauteur ce sont les vis PLATINE.
    seat_t = float(ech.get("seat_t (plafond de percage)", "3").split()[0])
    plans = {"plafond": ep - seat_t / 2, "platine": ep / 2}

    familles, contre, r_out = {}, {}, 0.0
    for nom, z in plans.items():
        shells, holes, ro = holes_at(m, z)
        r_out = max(r_out, ro)
        if shells != 1:
            fails.append(f"coupe z={z:.1f} : {shells} contour(s), attendu 1")
            return fails
        cable, vis, reste = triangle(holes)
        if nom == "plafond":
            cmp("Ø passage cable", 2 * cable[2], TGT["cable_d"])
            cmp("centrage du passage cable",
                float(np.hypot(cable[0], cable[1])), 0.0, 0.2)
        if len(vis) != TGT["n_holes"] or len(reste) != TGT["n_holes"]:
            fails.append(f"coupe {nom} : {len(vis)} percage(s) + {len(reste)} "
                         f"contre-forme(s), attendu {TGT['n_holes']} + "
                         f"{TGT['n_holes']}")
            return fails
        familles[nom], contre[nom] = vis, reste

    cmp("Ø disque", 2 * r_out, TGT["disc_d"])

    for nom, vis in familles.items():
        # emboitement -> apotheme : c'est le cercle inscrit que la vis touche
        for *_, apo in vis:
            j = 2 * apo - TGT["hole_d"]
            if not (jmin - EPS <= j <= jmax + EPS):
                fails.append(f"CIBLE jeu de percage {nom} : {j:+.2f} mm "
                             f"(Ø utile {2*apo:.2f} pour une vis "
                             f"Ø{TGT['hole_d']:g}), "
                             f"attendu dans [{jmin:g} ; {jmax:g}]")
                break
        rayons = sorted(float(np.hypot(x, y)) for x, y, *_ in vis)
        if rayons[-1] - rayons[0] > L:
            fails.append(f"CIBLE triangle {nom} : rayons inegaux "
                         f"{rayons[0]:.2f} a {rayons[-1]:.2f} mm")
        angs = sorted(float(np.degrees(np.arctan2(y, x))) % 360 for x, y, *_ in vis)
        ecarts = [(angs[(i + 1) % 3] - angs[i]) % 360 for i in range(3)]
        if max(abs(e - 120) for e in ecarts) > A:
            fails.append(f"CIBLE triangle {nom} non equilateral : "
                         + ", ".join(f"{e:.1f}deg" for e in ecarts))
        # LA cote de la demande : du BORD DU TROU au bord du disque. Comparee
        # au Ø NOMINAL de la vis -- le jeu de percage est controle a part.
        cmp(f"marge bord du trou -> bord ({nom})",
            r_out - float(np.mean(rayons)) - TGT["hole_d"] / 2,
            TGT["edge_margin"])

    # -- les deux triangles doivent etre decales, sinon lamages et logements
    #    d'ecrous se rencontrent.
    def cap(vis):
        return sorted(float(np.degrees(np.arctan2(y, x))) % 360
                      for x, y, *_ in vis)[0]
    d = (cap(familles["platine"]) - cap(familles["plafond"])) % 120
    cmp("decalage plafond -> platine", min(d, 120 - d), TGT["offset_ang"], A)

    # -- LE LOGEMENT D'ECROU. Un six-pans trop serre ne se voit ni au volume,
    #    ni a la bbox, ni au comptage : l'ecrou n'entre simplement pas. La
    #    cote sur plats, c'est deux fois l'apotheme -- voir ring().
    jn, jx = tol["jeu_ecrou"]
    for *_, apo in contre["plafond"]:
        surplats = 2 * apo
        j = surplats - TGT["ecrou_s"]
        if not (jn - EPS <= j <= jx + EPS):
            fails.append(f"CIBLE jeu du logement d'ecrou : {j:+.2f} mm "
                         f"(sur plats {surplats:.2f} pour un "
                         f"{TGT['ecrou']} de {TGT['ecrou_s']:g}), "
                         f"attendu dans [{jn:g} ; {jx:g}]")
            break

    # -- les deux profondeurs qu'aucune coupe unique ne montre
    xc, yc, *_ = familles["plafond"][0]
    z = z_transition(m, (xc, yc), ep / 2, ep)          # lamage : large en bas
    seat = ep - z if z is not None else 0.0
    ancrage = TGT["vis_plafond_l"] - seat
    if ancrage < TGT["ancrage_mini"]:
        fails.append(f"CIBLE ancrage : plafond de percage {seat:.2f} mm, il ne "
                     f"reste que {ancrage:.2f} mm a une vis de "
                     f"{TGT['vis_plafond_l']:g} (mini {TGT['ancrage_mini']:g})")

    xb, yb, *_ = familles["platine"][0]
    z = z_transition(m, (xb, yb), ep - 1e-3, ep / 2)   # logement : large en haut
    prof = ep - z if z is not None else 0.0
    if prof <= TGT["ecrou_h"]:
        fails.append(f"CIBLE logement d'ecrou : {prof:.2f} mm de profondeur "
                     f"pour un ecrou de {TGT['ecrou_h']:g} -- il depasserait, "
                     f"la cale ne porterait plus a plat sur le plafond")
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
        shells, holes, _ = holes_at(m, sec["z"])
        if shells != sec["shells"]:
            fails.append(f"coupe z={sec['z']} : {shells} contour(s), "
                         f"attendu {sec['shells']}")
        if len(holes) != sec["holes"]:
            fails.append(f"coupe z={sec['z']} : {len(holes)} trou(s) "
                         f"traversant(s), attendu {sec['holes']}")
        elif sec.get("match_echo"):
            want = [xy for k in sec["match_echo"]
                    for xy in json.loads(ech.get(k, "[]"))] + [[0, 0]]
            for wx, wy in want:
                d = min(np.hypot(cx - wx, cy - wy) for cx, cy, *_ in holes)
                if d > 0.15:
                    fails.append(f"aucun trou en ({wx:.2f}, {wy:.2f}) : "
                                 f"le plus proche est a {d:.2f} mm")

    # -- 7. cible vs reel : uniquement sur la piece pleine, la seule qui
    #    porte toutes les cotes de la demande.
    if spec.get("target"):
        fails += cible_vs_reel(m, ech)

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

    # -- balayage. Ce sont les trois cotes que l'essai imprime fera bouger :
    #    on veut savoir OU la plage s'arrete, pas seulement que le modele
    #    rend. Chaque point passe donc par TOUTES les gardes -- un balayage
    #    qui ne verifie que l'absence de WARNING annoncerait `ok` pour un
    #    lamage qui ne laisse plus assez d'ancrage a une vis de 30.
    SUIVI = {"clr": "hd (Ø reellement perce)",
             "seat_t": "ancrage rendu a une vis de 30",
             "nut_clr": "hex_d (Ø circonscrit logement)"}
    if not only:
        print("\n  balayage (toutes les gardes, pour trouver ou la plage casse) :")
        spec = dict(SPEC["parts"]["cale"])
        for var, vals in SPEC["sweep"].items():
            for v in vals:
                s = dict(spec); s["defines"] = {var: v}
                fails, e = check("cale", s)
                key = SUIVI.get(var, "")
                info = (fails[0][:78] if fails else
                        f"{key.split(' (')[0]} = {e.get(key, '?')}")
                print(f"    {'hors plage' if fails else 'ok        '}  "
                      f"{var}={v:<6} {info}")

    print()
    if bad:
        print(f"{bad} verification(s) en echec.")
        sys.exit(1)
    print("Tout est vert.")


if __name__ == "__main__":
    main()
