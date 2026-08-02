# Buses 0,6 et 0,8 — ce que ça gagne vraiment

Complément à `cura_ender3v3se_petg.md`, qui reste la référence pour tout ce
qui ne dépend pas de la buse (température, plateau, refroidissement,
`hole_xy_offset`, `Maximum Resolution`, accélérations sous Klipper).

## Les temps sont mesurés, pas raisonnés — et mon raisonnement était faux

    make buses            # toutes les pièces
    make buses PART=cale  # une seule

J'avais prédit que le `gabarit` — un disque Ø150 de 2 mm, donc **que** des
couches pleines — serait limité par le débit, et qu'une grosse buse n'y
gagnerait presque rien. Faux : à 0,4 il ne passe que **40 %** de son temps au
plafond de débit. Les 60 % restants sont des accélérations, des changements
de direction et des couches. Une buse plus grosse les attaque tous.

| pièce | 0,4 / 0,20 | 0,6 / 0,30 | **0,6 + infill ×2** | 0,8 / 0,40 |
|---|---|---|---|---|
| `cale` | 11 h 02 · 186 g | 4 h 47 · 195 g | **3 h 44 · 184 g** | 3 h 09 · 208 g |
| `gabarit` | 49 min · 15,1 g | 28 min · 19,2 g | **26 min · 18,7 g** | 20 min · 22,9 g |
| `gabarit_fente` | 15 min · 4,0 g | 8 min · 4,8 g | **8 min · 4,7 g** | 6 min · 5,7 g |
| `essai` | 47 min · 12,3 g | 24 min · 12,8 g | **22 min · 12,4 g** | 17 min · 16,2 g |

## Verdict : **0,6 mm, couche 0,30, infill toutes les 2 couches**

**×2,95 sur la cale — 11 h 02 → 3 h 44 — et 2,6 g de matière en MOINS.**

La 0,8 ne rajoute que 18 % par-dessus, et les paie cher :

- **+25 g de matière** sur la cale (208 contre 184). Les lignes sont plus
  larges partout, y compris là où ça ne sert à rien.
- **80 % du temps déjà au plafond de débit** — et ce plafond est une
  *hypothèse*. Les 18 mm³/s de la table sont une estimation pour une hotend
  d'origine ; si la tienne n'en tient que 12, la 0,8 retombe à ~3 h 45 et le
  gain disparaît entièrement. À 0,6 le plancher est à 77 % : plus de marge,
  résultat plus robuste.
- **Les Ø6,4 sont la seule chose que cette pièce doit rendre juste.** Une
  ligne de 0,84 mm sur un cercle de 20 mm de circonférence, c'est là que le
  retrait de courbure et le retard de flux se voient le plus.

Garde la 0,8 pour une pièce qui n'a aucune cote à tenir.

## Réglages Cura par buse

Ce qui reste **constant**, c'est l'épaisseur, pas le comptage — sinon on
compare deux pièces différentes, pas deux buses.

| Champ Cura | 0,4 | **0,6** | 0,8 |
|---|---|---|---|
| Layer Height (`layer_height`) | 0,2 | **0,30** | 0,40 |
| Initial Layer Height (`layer_height_0`) | 0,2 | **0,30** | 0,40 |
| Line Width (`line_width`) | 0,42 | **0,62** | 0,84 |
| Wall Line Count (`wall_line_count`) | 3 | **2** | 2 |
| → épaisseur de paroi obtenue | 1,26 | **1,24** | 1,68 |
| Top / Bottom Layers | 5 / 5 | **4 / 4** | 3 / 3 |
| → épaisseur de peau obtenue | 1,0 | **1,2** | 1,2 |
| Infill Layer Thickness (`infill_sparse_thickness`) | 0,2 | **0,60** | 0,40 |
| Infill Density | 20 % | **20 %** | 20 % |
| Infill Speed (`speed_infill`) | 120 | **75** | 54 |
| Inner Wall Speed (`speed_wall_x`) | 100 | **75** | 54 |
| Outer Wall Speed (`speed_wall_0`) | 50 ou 90 | **40 ou 70** | 30 ou 50 |
| débit supposé de la hotend | 10 mm³/s | **14** | 18 |

**Les vitesses BAISSENT quand la buse grossit.** C'est le point que tout le
monde rate. Cura n'a pas de champ « débit volumétrique max » : la vitesse est
la seule façon de tenir le plafond, et il faut refaire le calcul à chaque
changement de buse ou de couche.

    vitesse_max = débit / (hauteur_de_couche × largeur_de_ligne)

    0,6 : 14 / (0,30 × 0,62) = 75 mm/s
    0,8 : 18 / (0,40 × 0,84) = 54 mm/s

Le gain ne vient pas d'aller plus vite, il vient de **poser 2,3 fois plus de
matière à chaque passage** et d'avoir **deux fois moins de couches**.

### `Infill Layer Thickness` — le levier gratuit

`infill_sparse_thickness` fait imprimer le remplissage **une couche sur
deux**, en double épaisseur. Sur la cale : **4 h 47 → 3 h 44**, sans toucher
à une seule surface visible ni à une seule cote. Doit être un multiple exact
de `layer_height` (0,60 pour une couche de 0,30), sinon Cura arrondit en
silence.

À 0,8 / 0,40, laisse-le à 0,40 : 0,80 mm de remplissage d'un coup, ça
commence à faire des ponts internes discutables pour une pièce porteuse.

## « Du détail seulement là où ça compte » — ce qui est possible, et ce qui ne l'est pas

**La hauteur de couche est GLOBALE dans Cura. Point.** Elle n'est pas
disponible en *Per Model Settings* : impossible de donner 0,15 aux logements
d'écrous et 0,4 au reste. C'est une limite du trancheur, pas un réglage à
trouver.

Conséquence : **la hauteur de couche se choisit sur la plus petite cote
verticale qui compte**, et la vitesse se récupère ailleurs.

Les trois cotes verticales qui comptent ici, et ce qu'une couche épaisse leur
fait :

| cote | valeur | à 0,40 de couche |
|---|---|---|
| logement d'écrou | 5,8 mm pour un écrou de 5 | quantifié à 5,6 ou 6,0 — **reste > 5** ✔ |
| plafond de perçage | 3,0 mm | 2,8 ou 3,2 — sans effet sur l'ancrage ✔ |
| congé du lamage | 2,0 mm à 45° | escalier de 5 marches de 0,4 — se ponte ✔ |

Les 0,8 mm de marge du logement d'écrou ne sont pas un hasard : le `.scad`
porte maintenant `assert(nut_depth - layer_max > nut_h)` avec
`layer_max = 0.4`. Si tu descends `nut_depth`, la garde parle.

Ce que tu **peux** localiser, par *modifier mesh* (`stl/mod_hubs.stl`, six
colonnes Ø22 sur les vis) — **Per Model Settings → Modify settings for
infill of other models** :

| Réglage | Valeur dans les colonnes |
|---|---|
| Infill Density (`infill_sparse_density`) | **100 %** |
| Infill Layer Thickness | remets **= layer_height** |
| Wall Line Count | +1 |

C'est exactement la bonne division du travail : le cœur du disque ne fait
rien, les six colonnes portent tout.

**Adaptive Layers : laisse-le off.** Il fait varier la couche selon la
*pente* de la surface. Nos cotes critiques sont des trous verticaux — il
n'irait rien affiner d'utile et ralentirait le congé du lamage.

## Ce qu'il faut re-tester après un changement de buse

Le jeu de perçage `clr = 0,4` a été choisi pour une **0,4**. Une ligne plus
large se retire davantage en virage : le trou sort plus petit.

| buse | `clr` à essayer |
|---|---|
| 0,4 | 0,4 *(la valeur du dépôt)* |
| **0,6** | **0,5** |
| 0,8 | 0,6 à 0,7 |

    openscad -o essai.stl -D 'part="essai"' -D clr=0.5 src/cale_ventilateur.scad

**Ce sont des points de départ, pas des mesures.** `essai` tranche en
**22 minutes** à 0,6 — et il faut le réimprimer **avec la buse et la couche
de la cale**, sinon il valide une pièce que tu n'imprimeras pas. Il répond
aux quatre questions d'un coup : la M6 passe-t-elle, l'écrou entre-t-il, la
tête porte-t-elle, l'embout atteint-il la vis.

Bonne nouvelle sur le logement d'écrou : une buse large arrondit les angles
internes de l'hexagone d'environ un rayon de buse, mais sur un angle de 120°
ça ne coûte que **0,06 mm** dans les coins, pour 0,34 de jeu disponible. Le
six-pans est la partie la plus tolérante de la pièce.

## Avant de croire la ligne « 0,8 »

Le débit maximal est une propriété de ta hotend, pas de ta géométrie, et
c'est la seule valeur de ce fichier qui n'ait pas été vérifiée ici. Le test
prend dix minutes : extrude en l'air à débit croissant (Klipper :
`M83` puis des `G1 E… F…` calculés) et note où la sous-extrusion commence.

Tant que ce chiffre n'est pas connu, **0,6 est le choix sûr** : il gagne
l'essentiel (×2,95) avec la plus grande marge sous le plafond.
