#!/usr/bin/env python3
"""Genere build/index.html : un viewer web autonome, une iteration a la fois.

But : pouvoir juger d'un coup d'oeil si le crochet colle au croquis. La page
embarque un viewer three.js (on tourne, on zoome chaque piece) ET, a cote,
le profil 2D annote + une table CIBLE-vs-REEL. Tout est inline (STL en base64,
librairie vendorisee) : la page marche hors-ligne, meme ouverte en double-clic.

Deux sources, jamais melangees, comme partout dans ce projet :
  - REEL : cotes derivees des parametres du .scad (via profile_plot) ;
  - CIBLE : le croquis, dans docs/target_hook.json.
"""
import base64, datetime, html, json, pathlib, re, subprocess, sys
import profile_plot as pp   # meme dossier tools/

ROOT   = pathlib.Path(__file__).resolve().parent.parent
SRC    = ROOT / "src" / "cabas_velo.scad"
BUILD  = ROOT / "build"
VENDOR = ROOT / "tools" / "web" / "vendor"
PARTS  = ["hook", "hooks3", "a", "b", "gauge", "pin", "hinge_test", "plate"]

# quelles cotes CIBLE la piece "hook" doit-elle afficher, et depuis quel echo
ECHO_MAP = [
    ("arm_top", "Bras du haut", r"Bras du haut\s*=\s*(-?[\d.]+)"),
    ("depth",   "Profondeur",   r"Profondeur\s*=\s*(-?[\d.]+)"),
    ("bowl_h",  "Ventre",       r"Ventre\s*=\s*(-?[\d.]+)"),
    ("arm_bot", "Bras du bas",  r"Bras du bas\s*=\s*(-?[\d.]+)"),
    ("back_h",  "Dos",          r"Dos\s*=\s*(-?[\d.]+)"),
    ("leg_l",   "Languette",    r"Languette\s*=\s*(-?[\d.]+)"),
]

def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def render_all():
    BUILD.mkdir(exist_ok=True)
    stls, warns = {}, {}
    for part in PARTS:
        out = BUILD / f"{part}.stl"
        p = sh(["openscad", "-o", str(out), "-D", f'part="{part}"', str(SRC)])
        w = [l.strip() for l in p.stderr.splitlines() if l.startswith("WARNING") or "ERROR" in l]
        if w: warns[part] = w
        if out.exists(): stls[part] = out.read_bytes()
    return stls, warns

def hook_echoes():
    """Sortie ECHO brute du crochet + valeurs reelles parsees."""
    p = sh(["openscad", "-o", str(BUILD / "hook.stl"), "-D", 'part="hook"', str(SRC)])
    lines = [l.replace("ECHO: ", "").strip().strip('"')
             for l in p.stderr.splitlines() if l.startswith("ECHO:")]
    raw = "\n".join(lines)
    real = {}
    for key, _lbl, pat in ECHO_MAP:
        m = re.search(pat, p.stderr)
        if m: real[key] = float(m.group(1))
    return raw, real

def git_stamp():
    r = sh(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"])
    sha = r.stdout.strip() if r.returncode == 0 else "non commite"
    d = sh(["git", "-C", str(ROOT), "log", "-1", "--format=%cd", "--date=short"])
    when = d.stdout.strip() if d.returncode == 0 else datetime.date.today().isoformat()
    dirty = sh(["git", "-C", str(ROOT), "status", "--porcelain"]).stdout.strip()
    return sha + (" +modifs" if dirty else ""), when

def b64(data): return base64.b64encode(data).decode("ascii")

def rows_html(tgt, real):
    out = []
    for key, lbl, _ in ECHO_MAP:
        c = tgt.get(key); v = real.get(key)
        if c is None or v is None: continue
        d = v - c
        cls = "ok" if abs(d) <= 1.0 else ("warn" if abs(d) <= 2.5 else "bad")
        out.append(
            f'<tr><td>{html.escape(lbl)}</td><td>{c:g}</td>'
            f'<td>{v:.2f}</td><td class="{cls}">{d:+.2f}</td></tr>')
    # tube pour reference
    if "tube_d" in tgt:
        out.append(f'<tr><td>tube Ø</td><td>{tgt["tube_d"]:g}</td>'
                   f'<td>{tgt["tube_d"]:g}</td><td class="ok">mesure</td></tr>')
    return "\n".join(out)

def build_html():
    stls, warns = render_all()
    pp_params = pp.scad_params()
    tgt = pp.targets()
    g = pp.build(pp_params)
    real = g["real"]
    raw, echo_real = hook_echoes()
    # profil 2D (genere par profile_plot lance a part, on lit l'image)
    sh([sys.executable, str(ROOT / "tools" / "profile_plot.py")])
    profil = (BUILD / "profil.png")
    profil_b64 = b64(profil.read_bytes()) if profil.exists() else ""
    sha, when = git_stamp()

    stl_js = "{\n" + ",\n".join(
        f'  {json.dumps(k)}: "{b64(v)}"' for k, v in stls.items()) + "\n}"
    parts_js = json.dumps(list(stls.keys()))
    warn_banner = ""
    if warns:
        items = "; ".join(f"{k}: {v[0][:80]}" for k, v in warns.items())
        warn_banner = f'<div class="warn-banner">⚠ WARNING OpenSCAD — {html.escape(items)}</div>'

    three  = (VENDOR / "three.min.js").read_text()
    stll   = (VENDOR / "STLLoader.js").read_text()
    orbit  = (VENDOR / "OrbitControls.js").read_text()

    doc = TEMPLATE.format(
        sha=html.escape(sha), when=html.escape(when),
        warn_banner=warn_banner,
        rows=rows_html(tgt, {**real, **echo_real}),
        arm_top=pp_params["arm_top"], arm_bot=pp_params["arm_bot"],
        depth=pp_params["depth"], bowl_h=pp_params["bowl_h"],
        leg_l=pp_params["leg_l"], leg_ang=pp_params["leg_ang"],
        tube=pp_params["tube_d"], fits=("oui" if g["fits"] else "NON"),
        echoes=html.escape(raw),
        profil_b64=profil_b64,
        three=three, stll=stll, orbit=orbit,
        stl_data=stl_js, parts=parts_js,
    )
    out = BUILD / "index.html"
    out.write_text(doc)
    return out, list(stls.keys()), warns

TEMPLATE = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>cabas-velo — crochet R — {sha}</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font:14px/1.45 system-ui,sans-serif; display:flex; height:100vh;
         overflow:hidden; background:#111; color:#eee; }}
  #view {{ flex:1; position:relative; background:radial-gradient(#222,#0c0c0c); }}
  #view canvas {{ display:block; }}
  #hud {{ position:absolute; top:10px; left:12px; font-size:12px; color:#9fb;
          background:rgba(0,0,0,.45); padding:5px 9px; border-radius:6px; }}
  aside {{ width:360px; max-width:44vw; background:#181818; border-left:1px solid #333;
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
  img.profil {{ width:100%; border-radius:8px; background:#fff; margin-bottom:12px; }}
  pre {{ background:#0d0d0d; border:1px solid #2a2a2a; border-radius:6px; padding:9px;
         font-size:11px; overflow-x:auto; color:#bcd; white-space:pre-wrap; }}
  .warn-banner {{ background:#5a1d1d; color:#ffd7d0; padding:7px 12px; font-size:12px; }}
  .legend {{ font-size:11px; color:#888; margin:-6px 0 12px; }}
  h2 {{ font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:#8fa;
        margin:16px 0 4px; }}
  a.dl {{ color:#7cf; font-size:11px; }}
</style></head>
<body>
  <div id="view"><div id="hud">glisser = tourner · molette = zoom · clic-droit = pan</div></div>
  <aside>
    <h1>cabas-velo — crochet en <b>R</b></h1>
    <div class="sub">iteration {sha} · {when}</div>
    {warn_banner}
    <div class="parts" id="parts"></div>

    <h2>Cible (croquis) vs réel</h2>
    <table><thead><tr><th>cote</th><th>cible</th><th>réel</th><th>écart</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <div class="legend">bras {arm_top}/{arm_bot} · ventre {depth}×{bowl_h} ·
      languette {leg_l}mm@{leg_ang}° · tube Ø{tube:.2f} logé : {fits}</div>

    <h2>Profil 2D — tube en place</h2>
    <img class="profil" src="data:image/png;base64,{profil_b64}" alt="profil">

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
const mat = new THREE.MeshStandardMaterial({{color:0x1D9E75, metalness:0.1, roughness:0.65,
   flatShading:false}});
let mesh = null;

function b64buf(b64){{
  const bin = atob(b64); const len = bin.length; const bytes = new Uint8Array(len);
  for (let i=0;i<len;i++) bytes[i]=bin.charCodeAt(i);
  return bytes.buffer;
}}
function resize(){{
  const w=view.clientWidth, h=view.clientHeight;
  renderer.setSize(w,h); camera.aspect=w/h; camera.updateProjectionMatrix();
}}
function show(part){{
  if (mesh){{ scene.remove(mesh); mesh.geometry.dispose(); }}
  const geo = loader.parse(b64buf(STL[part]));
  geo.computeVertexNormals();
  geo.center();               // recentre pour l'orbite
  mesh = new THREE.Mesh(geo, mat);
  // OpenSCAD : Z = hauteur ; on met Z en haut dans la vue
  mesh.rotation.x = -Math.PI/2;
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
show(PARTS.includes('hook') ? 'hook' : PARTS[0]);
(function loop(){{ requestAnimationFrame(loop); controls.update(); renderer.render(scene,camera); }})();
</script>
</body></html>
"""

if __name__ == "__main__":
    out, parts, warns = build_html()
    kb = out.stat().st_size / 1024
    print(f"  -> {out}  ({kb:.0f} Ko, {len(parts)} pieces : {', '.join(parts)})")
    if warns:
        print("  ⚠ WARNING OpenSCAD :")
        for k, v in warns.items():
            print(f"      {k}: {v[0][:90]}")
    else:
        print("  0 WARNING.")
