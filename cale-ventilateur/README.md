# cale-ventilateur

Cale d'écartement imprimée 3D à intercaler entre le plafond et la platine de
fixation d'un ventilateur à pales, pour gagner **30 mm de dégagement**.

Disque Ø150 × 30 mm, passage central Ø25 pour le câble. **Fixation en deux
temps** : la cale se visse au plafond avec les vis existantes, la platine se
visse ensuite sous la cale.

## Démarrer

    make verify     # les 7 gardes, sur chaque pièce
    make params     # toutes les cotes dérivées
    make web        # viewer 3D autonome (build/index.html) : la pièce à l'œil
    make serve      # sert build/ en local (http://localhost:8000/index.html)
    make export     # STL versionnés dans stl/

Prérequis : `openscad`, `python3`, `trimesh`, `numpy`, `scipy`, `networkx`,
`shapely`, `rtree`. Le viewer emprunte three.js au projet voisin `cabas-velo`
(lu au build) : la page produite est autonome, elle marche hors-ligne.

## Comment ça tient

Deux triangles de perçage de même rayon (R = 47 mm), **décalés de 60°** pour
ne pas se rencontrer.

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

## Ordre d'impression — jamais la cale en premier

| Job | Pièce | Durée | Matière | Ce qu'il valide |
|---|---|---|---|---|
| 1 | `essai` | ~45 min | ~7 g | la tête porte-t-elle au fond du lamage, l'embout atteint-il la vis, l'écrou entre-t-il, la M6 passe-t-elle |
| 2 | `gabarit` | ~25 min | ~13 g | **le triangle, sur le plafond ET sur la platine** |
| 3 | `cale` | ~10 h | ~190 g | la pièce |

`essai` est deux coupons à l'échelle 1 : un bloc de 30 mm avec un lamage
complet, et un plat avec un logement d'écrou. Il répond aux quatre questions
que le gabarit ne peut pas trancher.

`gabarit` est le même disque Ø150 réduit à 2 mm, avec les six perçages nus.
**Présente-le contre le plafond, puis contre la platine — les deux doivent
tomber juste.** C'est exactement l'hypothèse sur laquelle repose le décalage
de 60° : que la platine et le plafond partagent le même triangle. Si ce n'est
pas le cas, mesure l'entraxe réel et change `edge_margin` (ou `bolt_r`) ;
`make verify` te dira si la matière restante est encore suffisante.

Une heure et vingt grammes avant d'engager dix heures et deux cents.

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
| Périmètres | **4** | c'est là que passe l'effort |
| Couches pleines dessus/dessous | **5** | les deux faces d'appui |
| Matière | **PETG** | voir plus bas |
| Supports | **aucun** | `zmin = 0`, tous les perçages verticaux |

→ ~145 cm³, **~190 g, ~10 h** (à confirmer dans ton trancheur).

Un seul pont dans toute la pièce : le plafond du lamage, un anneau de 3,8 mm
de large. C'est un contre-perçage ordinaire, aucun slicer n'en fait un drame.
Les logements d'écrous sont ouverts vers le **haut** : imprimés en fin de
course, jamais en pont.

### `mod_hubs` : 100 % là où ça compte

`stl/mod_hubs.stl` contient six colonnes Ø22 aux coordonnées exactes des vis.

1. Charge `stl/cale.stl` dans PrusaSlicer.
2. Clic droit sur l'objet → **Ajouter un modificateur** → **Charger…** →
   `stl/mod_hubs.stl`.
3. Vérifie à l'œil qu'il tombe sur les six perçages. S'il est décalé, saisis
   les positions à la main — `make params` donne `VIS_PLAFOND_XY` et
   `VIS_PLATINE_XY`.
4. Sur le modificateur : `fill_density = 100 %`.

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
`hole_d` dans le `.scad` et réimprime `essai` — 45 minutes.

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

## Vérification

`make verify` rend chaque pièce et applique sept gardes. Voir `CLAUDE.md`
pour ce que chacune attrape et pourquoi elle existe — en particulier la
garde 7, et les deux fois où le harnais a déclaré vert quelque chose de faux.

Les cotes de la demande vivent dans `docs/target.json` (vérité externe). Elles
ne sont recopiées nulle part dans le `.scad` : `verify.py` mesure le maillage
et le confronte à ce fichier.
