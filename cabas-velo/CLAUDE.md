# Cabas velo — structure imprimee 3D

Reconstitution de l'armature rigide d'un cabas velo type BikeZac : un jonc de
280 mm cousu dans l'ourlet, pliable en son milieu, deux crochets pour le
porte-bagages, un lobe central pour l'elastique. Imprime sur Ender 3 V3 SE.

## Regle numero un : le rendu, pas la relecture

Sur ce projet, **six defauts sur sept ont ete trouves par OpenSCAD ou par un
trace, jamais par relecture du code**. Avant d'affirmer quoi que ce soit sur
la geometrie, rends-la.

    make verify      # toutes les gardes
    make profile     # trace le profil du crochet, tube en place, cotes cible
    make web         # viewer 3D autonome, chaque iteration a l'oeil

Ne conclus pas sans avoir vu passer la sortie.

## Les trois gardes, et pourquoi elles existent

**Le maillage : un seul corps, etanche, orientation coherente.** Mesure par
`trimesh` (`m.split()`, `m.is_watertight`). Un corps de trop = un corps
flottant. C'est ainsi qu'ont ete trouves le renfort de barbe orphelin,
l'eclat de chanfrein, les charnons detaches de leur barre, et le lobe de
queue qui pendait dans le vide.
*Historiquement on lisait `Volumes:` dans la sortie CGAL. trimesh est plus
sur : il compte aussi les pieces qui ne passent pas par CGAL (`hook`,
`gauge`), et il verifie l'etancheite -- qu'aucune garde ne verifiait.*

**Tout `WARNING` est fatal.** Et c'est la seule garde qu'aucun outil de
maillage ne peut remplacer. Une variable perdue (`k1`) produit un maillage
irreprochable de la MAUVAISE piece : etanche, un seul corps, meme genre,
meme boite englobante, 0,04 % d'ecart de volume. trimesh et admesh la
declarent parfaite. Seul OpenSCAD sait. C'est arrive deux fois, toujours
en recollant des morceaux de fichier.

**`zmin` doit valoir 0.** Sinon la piece est perchee sur des supports. C'est
ce critere qui a conduit a separer le crochet du jonc.
*Formulation forte, a cabler des que prusaslicer est dispo : trancher et
exiger qu'aucun support ne soit genere. Voir le TODO dans `verify.py`.*

## Ce que le code ne doit jamais faire

- **Recoller des morceaux de `.scad`.** Reecris le fichier entier. Les deux
  seules regressions silencieuses du projet viennent de la.
- **Reecrire une cote dans un script.** `tools/profile_plot.py` lit les
  parametres dans le `.scad`. Aucune valeur ne se recopie.
- **Ajouter un `assert` qui verifie le modele contre une mesure supposee.**
  `hook_out = 12` etait faux depuis le debut ; son `assert` l'a protege
  pendant onze versions au lieu de le denoncer. Un `assert` garde une
  **coherence interne** (une piece tient, une paroi n'est pas trop mince),
  jamais une mesure.

## Architecture

Quatre pieces, deux jobs d'impression independants **par dependance, pas par
geometrie** :

- `a`, `b` — les deux demi-joncs. Ne dependent d'aucune mesure. Imprimes a
  plat, face velo au plateau, gorges de charniere en l'air. Zero support.
- `hook` ×2 — les selles-crochets. Dependent de `tube_d` et `rib_t`. Profil
  plan extrude 15,05 mm : anneau a plat, aucun porte-a-faux. 3 g piece.

Le crochet est un **collier enfile par le bout du jonc**. Aucune entaille, le
jonc reste plein (W = 100,8 mm³). Ce qui bloque le collier en translation,
c'est la fenetre de 20 mm dans la gaine cousue. La couture fixe l'entraxe.

## Le crochet : il se pose, il ne se clipse pas

Le tube du porte-bagages est ferme, soude au cadre. On ne l'enfile pas dans
une bouche etroite. Le v12 enroulait 230° avec une bouche de 8 mm pour un
tube de 12,23 — il n'aurait jamais pu s'engager. Ce n'etait pas une cote
fausse, c'etait la cinematique de montage.

Forme (v15) : **un R.** Un dos plat (le collier), un BRAS DU HAUT, un VENTRE
en **arc a trois points** (bras_haut -> apex a la profondeur voulue ->
bras_bas), une LANGUETTE droite qui descend — le pied du R, levier de
decrochage. Le tube se loge dans le ventre. Cotes reglees dans l'editeur
`tools/web/designer.html` : `arm_top`, `depth`, `bowl_h`, `arm_bot`,
`back_h`, `leg_l`, `leg_ang`.

Le ventre n'epouse PLUS exactement le rayon du tube (c'etait le v14) : sa
forme suit le croquis, et une garde **verifie que le tube s'y loge**
(`assert` sur l'emboitement, pas sur une mesure). L'editeur montre
l'emboitement en direct pour arbitrer. Ce qui tient le sac, c'est son poids
et l'elastique du bas.

Cycle d'iteration : regler dans `designer.html` -> bouton **Copier** ->
couler les valeurs dans le `.scad` -> `make verify` + `make web`. Les cotes
du croquis vivent dans `docs/target_hook.json` (verite externe) ; on ne
recopie aucune cote dans le `.scad` et on n'en fait jamais un `assert`.

## Charniere

Charnons etages, gorges ouvertes vers la face tissu, axe corde a piano Ø2,5
enfonce **axialement** (le long de la hauteur du jonc), jamais radialement.
La levre ne flechit donc jamais : elle retient, c'est tout. Colle uniquement
le charnon central de B.

Passer a une vis sans tete M4 (DIN 913) : `pin_d = 4`. Tout se recalcule.
Coefficient 7,1 au lieu de 11,2, butee 1,55 au lieu de 2,30, mais demontable.
Le M3 est un piege : fond de filet 2,39 mm, plus faible que le fil de 2,5.
