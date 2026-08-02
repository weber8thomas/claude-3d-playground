# cale-ventilateur

Cale d'écartement imprimée 3D à intercaler entre le plafond et la platine de
fixation d'un ventilateur à pales, pour gagner **30 mm de dégagement**.

Disque Ø150 × 30 mm, passage central Ø25 pour le câble. **Fixation en deux
temps** : la cale se visse au plafond avec les vis existantes, la platine se
visse ensuite sous la cale.

**Tu veux juste imprimer ?** → **`slicer/FICHE_CURA.md`**. Une page, les
réglages Cura à saisir une fois, et l'ordre des quatre impressions. Le reste
de ce fichier explique le pourquoi.

## Démarrer

    make verify     # les 7 gardes géométriques, sur chaque pièce
    make slice      # garde 8 : tranche pour de vrai — temps, poids, supports
    make params     # toutes les cotes dérivées
    make web        # viewer 3D autonome (build/index.html) : la pièce à l'œil
    make serve      # sert build/ en local (http://localhost:8000/index.html)
    make export     # STL versionnés dans stl/

Prérequis : `openscad`, `prusa-slicer`, `python3`, `trimesh`, `numpy`,
`scipy`, `networkx`, `shapely`, `rtree`. Le viewer emprunte three.js au projet voisin `cabas-velo`
(lu au build) : la page produite est autonome, elle marche hors-ligne.

## Comment ça tient

Deux triangles de perçage de même rayon (**R = 51 mm**, entraxe 88,3 mm),
**décalés de 60°** pour ne pas se rencontrer.

**Côté plafond — 3 lamages Ø14.** Le lamage descend depuis la face platine
jusqu'à 3 mm du haut. La tête de vis porte sur ce plafond de perçage, juste
sous le plafond réel : la vis ne traverse que 3 mm de cale au lieu de 30 et
**retrouve ses 27 mm d'ancrage**. C'est pour ça que tes vis de 30 mm
suffisent.

**Côté platine — 3 écrous M6 noyés.** Empreintes hexagonales sur la face
plafond. La vis monte du bas, traverse la platine et la cale, et se serre
dans l'écrou. Le serrage plaque l'écrou au fond de son logement et comprime
la colonne de matière sous lui : **le chemin d'effort est tout métal, le
plastique ne travaille qu'en compression**. Les écrous ne peuvent pas
tomber — le plafond les bouche.

Nulle part la pièce ne travaille en traction. C'est le seul montage qui vaille
au-dessus des têtes.

## Ce qu'il faut acheter

| Pièce | Quantité | Note |
|---|---|---|
| Vis du plafond | **0** | tes vis de 30 mm sont réutilisées telles quelles |
| Vis M6 | 3 | longueur = épaisseur de la platine + 27 mm environ |
| Écrous M6 DIN 934 | 3 | six-pans sur plats 10 mm, hauteur 5 mm |

Il te faut aussi un **embout ou tournevis long** : la tête des vis du plafond
se trouve au fond d'un puits de 27 mm.

## Le cercle de perçage est une cote **relevée**, pas choisie

C'est la correction de la v3, et elle change le sens de lecture du modèle.

Jusqu'ici le rayon du triangle *découlait* des 25 mm de marge au bord
demandés au départ : `bolt_r = 75 − 25 − 3 = 47`. Les 25 mm étaient un
souhait ; la platine, elle, ne négocie pas. Résultat, des perçages **trop
centrés d'environ 4 mm**.

Le sens est inversé : **`bolt_r` est une entrée relevée sur la platine, et la
marge au bord en découle** (21 mm à R = 51, plancher admis 15 mm). Il reste
17 mm de matière entre un lamage Ø14 et le bord — largement de quoi
travailler.

### Régler `bolt_r` sur ta platine

Le plus rapide, si tu peux atteindre la platine au pied à coulisse : mesure
l'**entraxe** de deux trous, centre à centre, et divise.

    bolt_r = entraxe / 1,7321          (√3, pour un triangle équilatéral)

| entraxe mesuré | `bolt_r` |
|---|---|
| 81,4 mm | 47 (l'ancienne valeur, trop centrée) |
| 84,9 mm | 49 |
| **88,3 mm** | **51 — la valeur actuelle** |
| 91,8 mm | 53 |
| 95,3 mm | 55 |

Puis `bolt_r` dans `src/cale_ventilateur.scad` **et** dans
`docs/target.json` — les deux séparément, c'est voulu : `make verify` les
confronte au maillage mesuré et gueule si l'un des deux a été oublié.

Si tu ne peux pas mesurer directement, c'est le rôle de `gabarit_fente`.

## Ordre d'impression — jamais la cale en premier

| Job | Pièce | Buse 0,4 | **Buse 0,6** | Ce qu'il valide |
|---|---|---|---|---|
| 0 | `gabarit_fente` | 15 min · 4,0 g | **8 min · 4,7 g** | **le rayon réel du triangle** — il le mesure |
| 1 | `essai` | 47 min · 12,3 g | **22 min · 12,4 g** | la tête porte-t-elle au fond du lamage, l'embout atteint-il la vis, l'écrou entre-t-il, la M6 passe-t-elle |
| 2 | `gabarit` | 49 min · 15,1 g | **26 min · 18,7 g** | **le triangle, sur le plafond ET sur la platine** |
| 3 | `cale` | 11 h 02 · 186 g | **3 h 44 · 184 g** | la pièce |

Colonne 0,6 : couche 0,30, deux parois, remplissage une couche sur deux.
**×2,95 sur la cale pour moins de matière** — voir `slicer/cura_buses.md`,
et `make buses` pour régénérer la comparaison des trois buses.

Ces chiffres sortent de `make slice` et `make buses`, ils ne sont plus
estimés. J'avais annoncé ~25 min pour le gabarit : c'était faux du simple au
double. Attention quand même : ce sont des temps **PrusaSlicer**, et tu
imprimes sous Cura + Klipper — prends-les comme un ordre de grandeur, et
surtout comme des **rapports** entre configurations, qui eux tiennent.

### `gabarit_fente` — l'instrument, 15 minutes et 4 grammes

Trois bras, chacun portant une **fente radiale** de R−6 à R+6 (donc R = 45 à
57, entraxe 78 à 99). Deux petits témoins Ø2 encadrent chaque fente au
`bolt_r` **nominal**.

Il se centre tout seul : trois fentes radiales à 120°, c'est trois
contraintes tangentielles pour trois degrés de liberté (x, y, rotation). Une
fois posé sur la platine et les vis engagées, il n'a plus qu'une position —
et les vis s'y trouvent au **rayon réel**.

1. Pose-le sur la platine, engage les trois vis dans les fentes, laisse-le se
   placer.
2. **Coup d'œil** : les vis tombent-elles entre les témoins, en dedans, ou en
   dehors ? Tu sais déjà si 51 est bon.
3. **Chiffre exact** : trace au crayon au travers des trois fentes, retire le
   gabarit, et mesure l'entraxe des trois marques au pied à coulisse. Plus fin
   que n'importe quelle graduation imprimée.

`essai` est deux coupons à l'échelle 1 : un bloc de 30 mm avec un lamage
complet, et un plat avec un logement d'écrou. Il répond aux quatre questions
que ni l'un ni l'autre gabarit ne peut trancher.

`gabarit` est le même disque Ø150 réduit à 2 mm, avec les six perçages nus.
**Présente-le contre le plafond, puis contre la platine — les deux doivent
tomber juste.** C'est exactement l'hypothèse sur laquelle repose le décalage
de 60° : que la platine et le plafond partagent le même triangle. Il
*confirme* un rayon, il ne le mesure pas — si ça ne tombe pas juste, retourne
au `gabarit_fente` et change `bolt_r` ; `make verify` te dira si la matière
restante est encore suffisante.

Une heure trois quarts et trente et un grammes avant d'en engager onze et
cent quatre-vingt-six.

## Montage

1. Poser les 3 écrous M6 dans leurs logements, **face plafond**.
2. Passer le câble par le trou central.
3. Plaquer la cale au plafond, écrous vers le haut, **lamages en face des
   trous existants** — les grands trous Ø14 vont sur les vis du plafond.
4. Visser les 3 vis d'origine au fond des lamages (embout long).
5. Présenter la platine sous la cale, la faire tourner de 60° par rapport aux
   lamages : ses trous tombent sur les perçages d'écrou.
6. Serrer les 3 vis M6 dans les écrous. Elles ne peuvent pas tourner à vide,
   le six-pans les bloque.

## Le remplissage se règle au trancheur, pas dans le modèle

Le modèle est un **cylindre plein**, sans aucune structure interne, et c'est
volontaire : 498 cm³, soit ~630 g de PETG et une trentaine d'heures si on
imprimait à 100 %. Pour rien.

Ce qui porte, c'est la colonne de matière autour de chaque vis de platine, en
compression. Le cœur du disque ne fait rien.

| Réglage | Valeur | Pourquoi |
|---|---|---|
| Remplissage | **20 % gyroïde** | isotrope, suffisant hors des appuis |
| Périmètres | **3** | c'est là que passe l'effort |
| Couches pleines dessus/dessous | **5** | les deux faces d'appui |
| Matière | **PETG** | voir plus bas |
| Supports | **aucun** | mesuré, pas supposé — voir ci-dessous |

→ **186 g, 11 h** en buse 0,4 ; **184 g, 3 h 44** en buse 0,6 avec le
remplissage une couche sur deux (mesuré par `make slice` et `make buses`).

La hauteur de couche est **globale** dans Cura : impossible d'affiner
seulement les logements d'écrous. Elle se choisit donc sur la plus petite
cote verticale qui compte — le logement d'écrou, 5,8 mm pour un écrou de 5 —
et la vitesse se récupère sur la buse et le remplissage. Détail dans
`slicer/cura_buses.md`.

### Pourquoi aucun support, et comment on le sait

Le seul porte-à-faux de la pièce est le plafond du lamage. Il est au fond
d'un puits borgne Ø14 profond de 27 mm — donc si un support s'y logeait, tu
ne pourrais jamais aller le curer.

Un **congé à 45°** (`cb_relief`) ramène le porte-à-faux de 3,8 à **1,8 mm**
d'annulaire, et laisse une portée plate de 1,8 mm de large sous la tête de
vis. Le trancheur le franchit en pont.

Ce n'est pas une affirmation, c'est une mesure. `make slice` tranche chaque
pièce **avec les supports en auto** et compare ce que la géométrie
réclamerait au poids de la pièce :

| | support réclamé |
|---|---|
| `cale` | **1,8 %** |
| `gabarit` | **0 %** |
| `gabarit_fente` | **0 %** |
| `essai` | 8,1 % |
| *témoin en porte-à-faux* | *31,2 %* ← doit échouer, et échoue |

`essai` frôle le seuil de 10 % : c'est le même lamage dans un coupon bien
plus petit, il pèse donc proportionnellement plus. Normal, mais à surveiller
si tu réduis encore les coupons.

Les logements d'écrous, eux, sont ouverts vers le **haut** : imprimés en fin
de course, jamais en pont.

### `mod_hubs` : 100 % là où ça compte

`stl/mod_hubs.stl` contient six colonnes Ø22 aux coordonnées exactes des vis.

Dans **Cura** : charge `stl/cale.stl`, puis **File → Open File(s)** →
`stl/mod_hubs.stl`. Sélectionne les colonnes, clique **Per Model Settings**
(icône à gauche) → **Modify settings for infill of other models**, et mets
`Infill Density = 100 %`. Vérifie à l'œil qu'elles tombent sur les six
perçages ; si elles sont décalées, saisis les positions à la main —
`make params` donne `VIS_PLAFOND_XY` et `VIS_PLATINE_XY`.

C'est un confort, pas une obligation : un remplissage global à 40 % fait le
même travail pour ~60 g de plus.

## Matière : PETG, pas PLA

Charge permanente, au-dessus des têtes, contre un plafond qui peut monter à
35-40 °C l'été. Le PLA flue sous charge constante et ramollit vers 55 °C.
Le PETG tient jusque vers 80 °C. **N'imprime pas cette pièce en PLA.**

## Tes vis du plafond — ce qu'elles sont

Un pas de 2 mm mesuré de filet à filet **exclut une vis métrique** : une M6 a
un pas de 1,00 mm, une M8 de 1,25 mm, une M10 de 1,50 mm. Il faudrait une M14
pour un pas de 2 mm, impossible dans un perçage de 6.

Un filet aussi ouvert sur un si petit diamètre, c'est la signature d'une
**vis à bois** (ou d'un tire-fond), faite pour mordre dans une cheville ou
dans une solive. Ça se confirme en trois secondes :

| Indice | Vis à bois | Vis métrique |
|---|---|---|
| Bout de la vis | **pointu** | plat |
| Filet | jusqu'à la pointe, très ouvert | serré, régulier |
| Tige sous la tête | souvent **lisse** sur une partie | filetée partout |
| Tête | fraisée conique, ou hexagonale | cylindrique |

**La seule mesure qui reste à faire : le diamètre du filet, crête à crête, au
pied à coulisse.** C'est lui qui décide si le perçage convient. Le trou fait
Ø6,38 utile. S'il mesure 5 ou 5,5, tout va bien. S'il dépasse 6,38, change
`hole_d` dans le `.scad` et réimprime `essai` — 47 minutes.

Si ta tête de vis est **fraisée conique**, mets une rondelle M6 (Ø12, elle
entre dans le lamage Ø14) : un cône serré directement dans un trou
cylindrique travaille comme un coin et fend le plastique.

## Le vrai point faible n'est pas la pièce

En abaissant le ventilateur de 30 mm, tu allonges le porte-à-faux et donc
l'effort d'arrachement en tête de cheville — alors que le balourd du
ventilateur travaille en fatigue. Regarde dans quoi les vis mordent :

- **Solive / bois massif** — rien à faire.
- **Béton** — chevilles à frapper ou goujons métalliques ; une cheville
  plastique d'origine mérite d'être remplacée pendant que c'est démonté.
- **Placo seul** — à ne pas faire, avec ou sans cale. Il faut reprendre la
  charge sur une solive ou sur un boîtier de plafond dédié.

Ce point sort du périmètre de la pièce, mais c'est lui qui décide si le
montage tient.

## Profil Ender 3 V3 SE / PETG — Cura + Klipper

Les réglages complets sont dans **`slicer/`** :

- **`cura_ender3v3se_petg.md`** — noms de champs Cura exacts. Trois pièges y
  sont détaillés, dont deux qui feraient mentir le gabarit :
  `Hole Horizontal Expansion` doit rester à **0**, et `Maximum Resolution`
  doit descendre à **0,2 mm** (au défaut de 0,5, Cura polygonise les Ø6).
- **`klipper_petg.cfg`** — ce qu'aucun profil Cura ne peut rattraper : la
  `pressure_advance` (~0,04 en direct drive, à calibrer), et les deux cas
  d'accélération selon que ton input shaper est calibré ou non.
- **`ender3v3se_petg.ini`** — PrusaSlicer, uniquement pour `make slice`. Ce
  n'est pas un profil d'impression.

Deux points qui comptent plus que la table de réglages :

**Le plafond n'est pas la vitesse, c'est le débit.** La hotend d'origine
plafonne vers **10 mm³/s** en PETG, et Cura n'a pas de champ « débit
volumétrique max ». Fais la conversion toi-même :
`vitesse_max = 10 / (hauteur × largeur)` → 120 mm/s à 0,2 × 0,42. Monter à
150 ne fait que sous-extruder.

**Le PETG et la tôle PC/PEI s'aiment trop.** Assez pour en arracher des
morceaux. Bâton de colle en **agent de démoulage**, plateau à **70 °C** et
pas 80, et refroidissement complet avant de décoller.

## Vérification

`make verify` rend chaque pièce et applique sept gardes géométriques ;
`make slice` ajoute la huitième, qui tranche pour de vrai. Voir `CLAUDE.md`
pour ce que chacune attrape et pourquoi elle existe — en particulier la
garde 7, et les deux fois où le harnais a déclaré vert quelque chose de faux.

Les cotes de la demande vivent dans `docs/target.json` (vérité externe). Elles
ne sont recopiées nulle part dans le `.scad` : `verify.py` mesure le maillage
et le confronte à ce fichier.

Ça n'a pas suffi : la v2 est sortie verte avec les perçages trop centrés de
4 mm, parce que `target.json` portait la marge au bord — un souhait — au lieu
du cercle de perçage — une cote imposée. **Une garde ne vaut que ce que vaut
sa référence.** C'est la leçon n° 4 de `CLAUDE.md`, et le balayage de
`make verify` montre maintenant la garde mordre sur la bonne grandeur :

    hors plage  bolt_r=47   CIBLE cercle de percage (plafond) : 47.00 vs 51 demande
    ok          bolt_r=51   edge_margin = 21 mm  (plancher 15)
    hors plage  bolt_r=55   CIBLE cercle de percage (plafond) : 55.00 vs 51 demande
