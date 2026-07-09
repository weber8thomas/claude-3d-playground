#!/usr/bin/env python3
"""Harnais de verification du cabas velo.

Trois classes de bugs ont ete rencontrees sur ce projet. Chacune a sa garde :

  1. Corps flottant   -> `Volumes:` != attendu apres un rendu CGAL.
  2. Variable perdue  -> OpenSCAD emet un WARNING et rend quand meme.
                         Un `Volumes: 2` peut etre parfaitement faux.
  3. Piece imprimable ? -> zmin != 0, ou encombrement hors plateau.

Le point 2 est le plus vicieux : il ne leve aucune erreur. TOUT WARNING EST FATAL.
"""
import json, subprocess, sys, tempfile, pathlib, re
import trimesh

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / "src" / "cabas_velo.scad"
SPEC = json.loads((ROOT / "tools" / "expected.json").read_text())
BED  = SPEC["bed"]

def render(part, defines=None):
    out = tempfile.NamedTemporaryFile(suffix=".stl", delete=False).name
    cmd = ["openscad", "-o", out, "-D", f'part="{part}"', str(SRC)]
    for k, v in (defines or {}).items():
        cmd[-1:-1] = ["-D", f"{k}={v}"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return out, p.stderr

def mesh(stl):
    """trimesh remplace notre lecture STL maison ET la regle `Volumes:`.
    Il compte les corps sur n'importe quel STL -- y compris ceux qui ne
    passent pas par CGAL (hook, gauge) -- et donne l'etancheite en prime.
    Emprunte a claude-3d-playground (mesh.py)."""
    m = trimesh.load(stl)
    lo, hi = m.bounds
    return m, list(lo), list(hi)

def check(part, spec):
    stl, err = render(part, spec.get("defines"))
    fails = []

    if "ERROR" in err:
        for l in err.splitlines():
            if "ERROR" in l: fails.append(f"ERROR OpenSCAD: {l.strip()}")
        return fails, {}

    # -- LA garde que trimesh ne peut pas remplacer.
    # Une variable perdue produit un maillage irreprochable de la mauvaise
    # piece : etanche, un seul corps, meme bbox, 0,04 % d'ecart de volume.
    # Seul OpenSCAD le sait. Tout WARNING est fatal.
    warns = [l.strip() for l in err.splitlines() if l.startswith("WARNING")]
    if warns:
        fails.append(f"{len(warns)} WARNING(s), le premier : {warns[0][:90]}")

    m, lo, hi = mesh(stl)
    dims = [hi[i]-lo[i] for i in range(3)]

    # -- maillage
    n = len(m.split(only_watertight=False))
    if n != spec.get("bodies", 1):
        fails.append(f"{n} corps, attendu {spec.get('bodies', 1)}")
    if not m.is_watertight:
        fails.append("maillage non etanche : le trancheur produira n'importe quoi")
    if not m.is_winding_consistent:
        fails.append("orientation des faces incoherente")

    # -- imprimabilite
    if spec.get("printable", True):
        if abs(lo[2]) > 1e-3:
            fails.append(f"zmin = {lo[2]:.3f}, doit valoir 0 (support requis)")
        if dims[0] > BED[0] or dims[1] > BED[1] or dims[2] > BED[2]:
            fails.append(f"hors plateau : {dims[0]:.1f}x{dims[1]:.1f}x{dims[2]:.1f}")

    for k, (lo_b, hi_b) in spec.get("dims", {}).items():
        i = "xyz".index(k)
        if not (lo_b <= dims[i] <= hi_b):
            fails.append(f"dim {k} = {dims[i]:.2f}, attendu [{lo_b}, {hi_b}]")

    # TODO -- garde n.4, des que prusaslicer est disponible :
    #   trancher et exiger qu'aucun support ne soit genere. C'est la
    #   formulation forte de `zmin = 0`, celle qui a fait separer le
    #   crochet du jonc. `prusaslicer --slice --info` puis grep support.

    echoes = dict(re.findall(r'ECHO: "([^=]+?)\s*=\s*([^"]*)"', err))
    return fails, {k.strip(): v.strip() for k, v in echoes.items()}

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    bad = 0
    for part, spec in SPEC["parts"].items():
        if only and part != only: continue
        fails, echoes = check(part, spec)
        if fails:
            bad += 1
            print(f"  FAIL  {part}")
            for f in fails: print(f"          {f}")
        else:
            print(f"  ok    {part}")

    # -- balayage parametrique : le modele doit rester sain sur la plage utile
    if only:
        sys.exit(1 if bad else 0)
    print("\n  balayage tube_d (le porte-bagages n'est pas une constante) :")
    for td in SPEC["sweep"]["tube_d"]:
        _, err = render("hook", {"tube_d": td})
        st = "FAIL" if ("ERROR" in err or "WARNING" in err) else "ok  "
        mouth = re.search(r'Bouche de pose = ([\d.]+)', err)
        note = f"bouche {float(mouth.group(1)):.2f}" if mouth else ""
        interf = f"  interference {td - float(mouth.group(1)):+.2f}" if mouth else ""
        if st.strip() == "FAIL":
            bad += 1
            note = next((l for l in err.splitlines() if "ERROR" in l or "WARNING" in l), "")[:70]
        print(f"    {st}  tube_d={td:<6} {note}{interf if mouth else ''}")

    print()
    if bad:
        print(f"{bad} verification(s) en echec."); sys.exit(1)
    print("Tout est vert.")

if __name__ == "__main__":
    main()
