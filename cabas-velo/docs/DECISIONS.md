# Journal des decisions

Chaque entree dit ce qui a change **et ce qui l'a revele**. La colonne
« revele par » est la plus utile : elle dit ou regarder la prochaine fois.

| # | Decision | Revele par |
|---|---|---|
| v5 | Deux joncs bout a bout, tissu comme charniere | condamne : le jonc flotte libre dans une gaine cousue, il faut un axe |
| v7 | Crochet remonte au ras du bord bas du jonc | impression debout impossible autrement (barillets 2,9 mm sous le plateau) |
| v8 | Barillets fermes -> gorges ouvertes clipsables | debord ramene de 2,9 a 0,7 mm |
| v9 | Renfort de barbe orphelin supprime (flottait depuis le v2) | `Volumes: 3` |
| v9 | Chanfreins reconstruits (eclat de 1×5×1 isole) | `Volumes: 3` |
| v9 | Degagement de charnon reduit sous le rayon du charnon | `Volumes: 3` — les charnons etaient detaches de leur barre |
| v9 | Axe sorti de l'epaisseur du jonc | recouvrement de 1,6 mm au pliage |
| v10 | **Crochet separe du jonc** | le jonc portait deux excroissances sur des faces opposees. Separe, il s'imprime a plat, sans support, et le crochet devient une extrusion 2D pure |
| v10 | Aucun blocage axial du crochet | la fenetre de la gaine bloque le collier. Le jonc reste plein : W = 100,8 mm³ au lieu de 27,5 avec une M4 traversante mal placee |
| v11 | Levre de charniere rendue dependante de `pin_d` | en Ø4 la capture tombait a 0,063 mm |
| v11 | Pied du lobe de queue : 0,5 → 3 mm | present depuis le v8. `Volumes: 2` ne l'a jamais vu : la piece tenait, par un fil. Le passage en Ø4 l'a fait flotter |
| v12 | Anneau massif -> **ruban d'epaisseur constante** | photo. `ri`/`ro`/`hook_wall` decrivaient une couronne percee ; la piece est une lame pliee |
| v12 | `hook_out = 12` supprime, avec son `assert` | l'assert verifiait la fidelite du modele a une mesure fausse. Cote reelle : 21,55 |
| v13 | **Le crochet se pose, il ne se clipse pas** | le tube du porte-bagages est ferme. Bouche de 8 mm pour un tube de 12,23 : jamais engageable. Defaut de cinematique, pas de cote |
| v13 | Horizontale + quart de cercle. Centre de l'arc = centre du tube | une seule cote (`tube_d`) gouverne l'epousage du flanc et le contact du sommet |
| v14 | **Forme en R** : dos + bras du haut + ventre + languette droite | croquis cote de l'utilisateur. Le ventre epouse toujours le tube (centre de l'arc = centre du tube, inchange) |
| v14 | `hook_height` remplace par `lang_l` + `lang_ang` | la languette devient un levier droit a cap fixe, plus une tangente forcee. Sa longueur (croquis : 10) et son cap pilotent le pied du R et la hauteur totale |
| v14 | Cotes du croquis sorties dans `docs/target_hook.json` | verite EXTERNE. Le modele sort ses cotes reelles par echo ; `profile_plot` et le viewer superposent cible-vs-reel. Jamais dans un `assert` (regle : un assert garde une coherence interne, pas une mesure) |
| v14 | Viewer web autonome (`make web`) | juger chaque iteration a l'oeil : three.js embarque + STL en base64 + profil 2D + table cible-vs-reel, dans un seul `index.html` hors-ligne |

## Deux regressions silencieuses, meme cause

Les v12 et v13 ont chacun perdu des variables (`k1`/`k2`, puis `lip` ecrase par
la levre du crochet) en **recollant** des morceaux de `.scad`. Dans les deux
cas OpenSCAD a rendu une geometrie fausse en annoncant `Volumes: 2`.

D'ou la garde « tout WARNING est fatal », et la regle : on reecrit le fichier,
on ne le rapiece pas.

## Emprunts a `claude-3d-playground`

Ce depot fait la meme chose en plus general : generer, compiler, valider le
maillage, trancher. Trois choses en sont tirees.

**`trimesh` remplace la regle `Volumes:`.** Plus portable (il compte les corps
sur n'importe quel STL, pas seulement ceux passes par CGAL), et il ajoute
l'etancheite, qu'aucune garde ne verifiait.

**Trancher pour verifier, pas pour produire.** `prusaslicer --info` puis
assertion : aucun support genere. C'est `zmin = 0` dit fort. Cable en TODO.

**CadQuery : ecarte.** Le crochet est une extrusion 2D d'une ligne moyenne
balayee. OpenSCAD le fait en douze lignes.

Et une chose qu'ils n'ont pas, qu'il ne faut pas perdre : **tout `WARNING` est
fatal**. Verifie sur le bug `k1` : maillage etanche, un corps, meme bbox,
0,04 % d'ecart de volume. Aucun validateur de maillage ne le voit. 14 WARNING.
