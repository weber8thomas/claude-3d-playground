#!/usr/bin/env python3
"""Genere build/index.html : un viewer web autonome, une iteration a la fois.

Regle numero un du depot : on ne conclut pas sur une relecture de code. Cette
page permet de VOIR la piece -- disque plein, passage central centre, trois
percages a 120 degres, rien qui flotte -- en un coup d'oeil.

A cote du viewer, la table CIBLE vs REEL : la demande (docs/target.json) face
a ce qui a ete MESURE sur le maillage par verify.py. Jamais face a ce que le
.scad affirme -- ce serait circulaire, et c'est exactement le piege que la
garde 7 existe pour eviter.

Tout est inline (STL en base64, three.js vendorise) : la page marche
hors-ligne, meme ouverte en double-clic. La librairie est empruntee au projet
voisin `cabas-velo` (lue au build, pas au runtime : rien a installer, et on
ne duplique pas 640 Ko de JS dans le depot).
"""
import base64, datetime, html, json, pathlib, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import verify as V                                   # meme dossier tools/

ROOT   = pathlib.Path(__file__).resolve().parent.parent
SRC    = ROOT / "src" / "cale_ventilateur.scad"
BUILD  = ROOT / "build"
VENDOR = ROOT.parent / "cabas-velo" / "tools" / "web" / "vendor"
PARTS  = ["cale", "gabarit", "gabarit_fente", "essai", "mod_hubs"]


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def render_all():
    BUILD.mkdir(exist_ok=True)
    stls, warns = {}, {}
    for part in PARTS:
        out = BUILD / f"{part}.stl"
        p = sh(["openscad", "-o", str(out), "-D", f'part="{part}"', str(SRC)])
        w = [l.strip() for l in p.stderr.splitlines()
             if l.startswith("WARNING") or "ERROR" in l]
        if w:
            warns[part] = w
        if out.exists():
            stls[part] = out.read_bytes()
    return stls, warns


def measured():
    """CIBLE vs REEL. Le reel est MESURE sur le maillage, par le meme code que
    la garde 7 de verify.py -- jamais lu dans le .scad, ce serait circulaire.

    Deux coupes, comme la garde 7 : dans le plafond de percage les vis
    PLAFOND sont des trous nus et les vis PLATINE des logements d'ecrou ;
    a mi-hauteur c'est l'inverse."""
    import numpy as np
    m = V.trimesh.load(BUILD / "cale.stl")
    t, ep = V.TGT, float(m.bounds[1][2] - m.bounds[0][2])
    seat_t = float(V.echoes(sh(["openscad", "--export-format=stl", "-o", "/dev/null",
                                "-D", 'part="cale"', str(SRC)]).stderr)
                   .get("seat_t (plafond de percage)", "3").split()[0])

    fam, contre, r_out, cable = {}, {}, 0.0, None
    for nom, z in (("plafond", ep - seat_t / 2), ("platine", ep / 2)):
        _, holes, ro = V.holes_at(m, z)
        r_out = max(r_out, ro)
        cbl, vis, reste = V.triangle(holes)
        fam[nom], contre[nom], cable = vis, reste, cbl

    def rayon(vis):
        return float(np.mean([np.hypot(x, y) for x, y, *_ in vis]))

    def cap(vis):
        return sorted(float(np.degrees(np.arctan2(y, x))) % 360
                      for x, y, *_ in vis)[0]

    r_pl, r_pt = rayon(fam["plafond"]), rayon(fam["platine"])
    d = (cap(fam["platine"]) - cap(fam["plafond"])) % 120
    surplats = float(np.mean([2 * a for *_, a in contre["plafond"]]))
    d_vis = float(np.mean([2 * a for *_, a in fam["platine"]]))
    z = V.z_transition(m, fam["plafond"][0][:2], ep / 2, ep)
    seat = ep - z if z is not None else 0.0
    z = V.z_transition(m, fam["platine"][0][:2], ep - 1e-3, ep / 2)
    prof = ep - z if z is not None else 0.0
    angs = sorted(float(np.degrees(np.arctan2(y, x))) % 360
                  for x, y, *_ in fam["plafond"])

    return [
        ("Ø disque",             t["disc_d"],  2 * r_out, "mm"),
        ("Epaisseur",            t["disc_t"],  ep, "mm"),
        ("Ø passage cable",      t["cable_d"], 2 * cable[2], "mm"),
        ("Percages plafond",     t["n_holes"], len(fam["plafond"]), ""),
        ("Percages platine",     t["n_holes"], len(fam["platine"]), ""),
        ("Decalage des 2 triangles", t["offset_ang"], min(d, 120 - d), "deg"),
        ("Ecart angulaire",      120, float(np.mean(
            [(angs[(i + 1) % 3] - angs[i]) % 360 for i in range(3)])), "deg"),
        ("Ø utile percage (vis Ø%g)" % t["hole_d"], t["hole_d"], d_vis, "mm"),
        # La cote qui s'impose (relevee sur la platine) vs celle qui en
        # decoule (simple plancher). L'inverse de v1/v2 -- voir target.json.
        ("Cercle de percage R",  t["bolt_r"], (r_pl + r_pt) / 2, "mm"),
        ("Bord du trou -> bord (plancher %g)" % t["edge_margin_min"], None,
         r_out - (r_pl + r_pt) / 2 - t["hole_d"] / 2, "mm"),
        ("Logement d'ecrou, sur plats", t["ecrou_s"], surplats, "mm"),
        ("Profondeur du logement", None, prof, "mm"),
        ("Plafond de percage",   None, seat, "mm"),
        ("Ancrage rendu a une vis de %g" % t["vis_plafond_l"],
         None, t["vis_plafond_l"] - seat, "mm"),
        ("Entraxe d'un triangle", None, (r_pl + r_pt) / 2 * 3 ** 0.5, "mm"),
        ("Volume plein",         None, m.volume / 1000, "cm3"),
    ]


def rows_html(rows):
    out, tol = [], V.TGT["tol"]["longueur"]
    for lbl, cible, reel, unit in rows:
        if cible is None:
            out.append(f'<tr><td>{html.escape(lbl)}</td><td>—</td>'
                       f'<td>{reel:.2f} {unit}</td><td class="ok">mesure</td></tr>')
            continue
        d = reel - cible
        cls = "ok" if abs(d) <= tol else ("warn" if abs(d) <= 2 * tol else "bad")
        out.append(f'<tr><td>{html.escape(lbl)}</td><td>{cible:g}</td>'
                   f'<td>{reel:.2f} {unit}</td><td class="{cls}">{d:+.2f}</td></tr>')
    return "\n".join(out)


def git_stamp():
    r = sh(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"])
    sha = r.stdout.strip() if r.returncode == 0 else "non commite"
    dirty = sh(["git", "-C", str(ROOT), "status", "--porcelain", "."]).stdout.strip()
    d = sh(["git", "-C", str(ROOT), "log", "-1", "--format=%cd", "--date=short"])
    when = d.stdout.strip() if d.returncode == 0 else datetime.date.today().isoformat()
    return sha + (" +modifs" if dirty else ""), when


def b64(data):
    return base64.b64encode(data).decode("ascii")


def build_html():
    stls, warns = render_all()
    p = sh(["openscad", "--export-format=stl", "-o", "/dev/null",
            "-D", 'part="cale"', str(SRC)])
    raw = "\n".join(l.replace("ECHO: ", "").strip().strip('"')
                    for l in p.stderr.splitlines() if l.startswith("ECHO:"))
    sha, when = git_stamp()

    banner = ""
    if warns:
        items = "; ".join(f"{k}: {v[0][:80]}" for k, v in warns.items())
        banner = f'<div class="warn-banner">⚠ WARNING OpenSCAD — {html.escape(items)}</div>'

    doc = TEMPLATE.format(
        sha=html.escape(sha), when=html.escape(when), warn_banner=banner,
        rows=rows_html(measured()), echoes=html.escape(raw),
        three=(VENDOR / "three.min.js").read_text(),
        stll=(VENDOR / "STLLoader.js").read_text(),
        orbit=(VENDOR / "OrbitControls.js").read_text(),
        stl_data="{\n" + ",\n".join(f'  {json.dumps(k)}: "{b64(v)}"'
                                    for k, v in stls.items()) + "\n}",
        parts=json.dumps(list(stls.keys())),
    )
    out = BUILD / "index.html"
    out.write_text(doc)
    return out, list(stls.keys()), warns


TEMPLATE = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>cale-ventilateur — {sha}</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font:14px/1.45 system-ui,sans-serif; display:flex; height:100vh;
         overflow:hidden; background:#111; color:#eee; }}
  #view {{ flex:1; position:relative; background:radial-gradient(#222,#0c0c0c); }}
  #view canvas {{ display:block; }}
  #hud {{ position:absolute; top:10px; left:12px; font-size:12px; color:#9fb;
          background:rgba(0,0,0,.45); padding:5px 9px; border-radius:6px; }}
  aside {{ width:380px; max-width:46vw; background:#181818; border-left:1px solid #333;
           padding:14px 16px; overflow-y:auto; }}
  h1 {{ font-size:16px; margin:0 0 2px; }}
  .sub {{ color:#888; font-size:12px; margin-bottom:12px; }}
  .parts {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px; }}
  .parts button {{ background:#252525; color:#ddd; border:1px solid #3a3a3a;
      border-radius:6px; padding:5px 10px; cursor:pointer; font-size:12px; }}
  .parts button.active {{ background:#1D9E75; color:#04120c; border-color:#1D9E75;
      font-weight:600; }}
  table {{ width:100%; border-collapse:collapse; margin:6px 0 14px; font-size:12px; }}
  th,td {{ text-align:right; padding:3px 6px; border-bottom:1px solid #2a2a2a; }}
  th:first-child,td:first-child {{ text-align:left; }}
  td.ok {{ color:#54d19a; }} td.warn {{ color:#e7c34a; }} td.bad {{ color:#e8695b; }}
  pre {{ background:#0d0d0d; border:1px solid #2a2a2a; border-radius:6px; padding:9px;
         font-size:11px; overflow-x:auto; color:#bcd; white-space:pre-wrap; }}
  .warn-banner {{ background:#5a1d1d; color:#ffd7d0; padding:7px 12px; font-size:12px; }}
  .legend {{ font-size:11px; color:#888; margin:-6px 0 12px; }}
  h2 {{ font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#8fa;
        margin:16px 0 4px; }}
</style></head>
<body>
  <div id="view"><div id="hud">glisser = tourner · molette = zoom · clic-droit = pan</div></div>
  <aside>
    <h1>cale-ventilateur — Ø150 × 30</h1>
    <div class="sub">iteration {sha} · {when}</div>
    {warn_banner}
    <div class="parts" id="parts"></div>

    <h2>Cible (la demande) vs réel (mesuré sur le maillage)</h2>
    <table><thead><tr><th>cote</th><th>cible</th><th>réel</th><th>écart</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <div class="legend">La colonne « réel » est mesurée sur le STL par le même
      code que la garde 7 de <code>verify.py</code>, jamais lue dans le
      <code>.scad</code>. La cible vit dans <code>docs/target.json</code>.</div>

    <h2>Sortie OpenSCAD (echo)</h2>
    <pre>{echoes}</pre>
  </aside>

<script>{three}</script>
<script>{stll}</script>
<script>{orbit}</script>
<script>
const STL = {stl_data};
const PARTS = {parts};
const view = document.getElementById('view');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 5000);
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(devicePixelRatio);
view.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x223322, 0.9));
const key = new THREE.DirectionalLight(0xffffff, 0.8); key.position.set(1,1.5,1); scene.add(key);
const fill = new THREE.DirectionalLight(0xbcd4ff, 0.35); fill.position.set(-1,-0.5,-1); scene.add(fill);
const grid = new THREE.GridHelper(200, 20, 0x335544, 0x222c28); scene.add(grid);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
const loader = new THREE.STLLoader();
const mat = new THREE.MeshStandardMaterial({{color:0x1D9E75, metalness:0.1, roughness:0.65}});
let mesh = null;

function b64buf(b64){{
  const bin = atob(b64); const bytes = new Uint8Array(bin.length);
  for (let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
  return bytes.buffer;
}}
function resize(){{
  const w=view.clientWidth, h=view.clientHeight;
  renderer.setSize(w,h); camera.aspect=w/h; camera.updateProjectionMatrix();
}}
function show(part){{
  if (mesh){{ scene.remove(mesh); mesh.geometry.dispose(); }}
  const geo = loader.parse(b64buf(STL[part]));
  geo.computeVertexNormals(); geo.center();
  mesh = new THREE.Mesh(geo, mat);
  mesh.rotation.x = -Math.PI/2;          // OpenSCAD : Z = hauteur
  scene.add(mesh);
  geo.computeBoundingSphere();
  const r = geo.boundingSphere.radius;
  grid.scale.setScalar(Math.max(1, r/40));
  const d = r/Math.sin((camera.fov/2)*Math.PI/180)*1.25;
  camera.position.set(d*0.7, d*0.55, d*0.7);
  controls.target.set(0,0,0); controls.update();
  document.querySelectorAll('#parts button').forEach(b=>
    b.classList.toggle('active', b.dataset.p===part));
}}
const bar = document.getElementById('parts');
PARTS.forEach(p=>{{
  const b=document.createElement('button'); b.textContent=p; b.dataset.p=p;
  b.onclick=()=>show(p); bar.appendChild(b);
}});
addEventListener('resize', resize); resize();
show(PARTS.includes('cale') ? 'cale' : PARTS[0]);
(function loop(){{ requestAnimationFrame(loop); controls.update(); renderer.render(scene,camera); }})();
</script>
</body></html>
"""

if __name__ == "__main__":
    out, parts, warns = build_html()
    print(f"  -> {out}  ({out.stat().st_size/1024:.0f} Ko, "
          f"{len(parts)} pieces : {', '.join(parts)})")
    if warns:
        print("  ⚠ WARNING OpenSCAD :")
        for k, v in warns.items():
            print(f"      {k}: {v[0][:90]}")
    else:
        print("  0 WARNING.")
