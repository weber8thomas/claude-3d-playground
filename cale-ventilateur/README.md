# cale-ventilateur

Cale d'écartement imprimée 3D à intercaler entre le plafond et la platine de
fixation d'un ventilateur à pales, pour gagner **30 mm de dégagement**.

Disque Ø150 × 30 mm, passage central Ø25 pour le câble, trois perçages Ø6 en
triangle équilatéral (cercle de perçage R = 47 mm), bord du trou à 25 mm du
bord du disque.

## Démarrer

    make verify     # les 7 gardes, sur chaque pièce
    make params     # toutes les cotes dérivées
    make web        # viewer 3D autonome (build/index.html) : la pièce à l'œil
    make serve      # sert build/ en local (http://localhost:8000/index.html)
    make export     # STL versionnés dans stl/

Prérequis : `openscad`, `python3`, `trimesh`, `numpy`, `scipy`, `networkx`,
`shapely`, `rtree`. Le viewer emprunte three.js au projet voisin `cabas-velo`
(lu au build) : la page produite est autonome, elle marche hors-ligne.

## Ordre d'impression — le gabarit d'abord, toujours

| Job | Pièce | Durée | Matière | Ce qu'il valide |
|---|---|---|---|---|
| 1 | `gabarit` | ~20 min | ~11 g | **le triangle de perçage sur la platine réelle**, et que la vis passe |
| 2 | `cale` | ~10 h | ~190 g | la pièce |

**Ne lance jamais le job 2 avant le job 1.** Le gabarit est le même disque
Ø150 réduit à 2 mm : mêmes perçages, mêmes cotes. Il coûte vingt minutes et
onze grammes ; la cale coûte dix heures et deux cents grammes. Présente le
gabarit contre la platine du ventilateur — si le triangle ne tombe pas juste,
c'est une ligne à changer dans le `.scad`, pas une impression perdue.

Si le triangle ne correspond pas, mesure l'entraxe réel entre deux vis et
mets à jour `edge_margin` (ou passe `bolt_r` en cote directe). `make verify`
te dira si la matière restante est encore suffisante.

## Le remplissage se règle au trancheur, pas dans le modèle

Le modèle est un **cylindre plein**. Aucune structure interne n'est
modélisée, et c'est volontaire : 512 cm³ de volume plein, soit ~650 g de PETG
et une trentaine d'heures si on imprimait à 100 %. Pour rien.

La cale travaille en **compression pure** : le ventilateur pend, ce sont les
vis qui sont en traction, la cale est écrasée entre le plafond et la platine.
Un cylindre fermé en compression est tenu par ses périmètres et ses couches
pleines dessus/dessous, pas par son cœur.

**Réglages conseillés (PrusaSlicer / Cura) :**

| Réglage | Valeur | Pourquoi |
|---|---|---|
| Remplissage | **20 % gyroïde** | isotrope, suffisant hors des appuis |
| Périmètres | **4** | c'est là que passe l'effort |
| Couches pleines dessus/dessous | **5** | les deux faces d'appui |
| Matière | **PETG** | voir plus bas |
| Supports | **aucun** | `zmin = 0`, tous les perçages verticaux |

→ ~150 cm³, **~190 g, ~10 h** (à confirmer dans ton trancheur).

### `mod_hubs` : 100 % là où ça compte

Le seul endroit qui a besoin de matière pleine, c'est **sous les rondelles**.
`stl/mod_hubs.stl` contient trois cylindres Ø30 aux coordonnées exactes des
vis, dans le repère de la cale.

1. Charge `stl/cale.stl` dans PrusaSlicer.
2. Clic droit sur l'objet → **Ajouter un modificateur** → **Charger…** →
   `stl/mod_hubs.stl`.
3. Vérifie à l'œil qu'il tombe sur les trois perçages. S'il est décalé, saisis
   les positions à la main — `make params` donne `VIS_XY`.
4. Sur le modificateur : `fill_density = 100 %`.

C'est un confort, pas une obligation : un remplissage global à 40 % fait le
même travail pour ~60 g de plus.

## Matière : PETG, pas PLA

Charge permanente, au-dessus des têtes, contre un plafond qui peut monter à
35-40 °C l'été. Le PLA flue sous charge constante et ramollit vers 55 °C.
Le PETG tient jusque vers 80 °C. **N'imprime pas cette pièce en PLA.**

## Les vis — ce que tu dois vérifier avant de monter

Descendre le ventilateur de 30 mm ne change pas seulement la longueur des
vis : ça allonge le bras de levier des vibrations sur la fixation du plafond.
Trois points, dans l'ordre d'importance.

### 1. Longueur : la pénétration dans le plafond doit rester identique

La règle est simple et il n'y a pas de marge à grappiller :

> **nouvelle longueur = longueur actuelle + épaisseur de la cale**

Avec des vis de 30 mm et une cale de 30 mm : **60 mm minimum**, et 70 mm si
tu veux de la marge. Une vis de 60 mm te rend exactement l'ancrage que tu
avais ; toute longueur inférieure te le retire, millimètre pour millimètre.

### 2. Nature : un pas de 2 mm, ce n'est pas une vis métrique

Un pas de 2 mm mesuré de filet à filet **exclut une M6** : une M6 a un pas de
1,00 mm, une M8 de 1,25 mm, une M10 de 1,50 mm. Il faudrait une M14 pour un
pas de 2 mm — impossible dans un perçage de 6.

Un pas aussi ouvert sur un diamètre aussi faible, c'est la signature d'une
**vis à bois** (ou d'un tire-fond) : filet en dents de scie, largement espacé,
destiné à mordre dans une cheville ou dans une solive. Ça se confirme en trois
secondes :

| Indice | Vis à bois | Vis métrique |
|---|---|---|
| Bout de la vis | **pointu** | plat |
| Filet | **jusqu'à la pointe, très ouvert** | serré, régulier |
| Tige sous la tête | souvent **lisse** sur une partie | filetée partout |
| Tête | fraisée conique, ou hexagonale (tire-fond) | cylindrique |

Si c'est une vis à bois : rachète le **même diamètre**, en 60 ou 70 mm. Le
diamètre annoncé (4×60, 5×70…) est le diamètre du filet, celui qui doit
retrouver le même trou dans la cheville. Ne monte pas en diamètre pour
« faire plus solide » : une vis plus grosse dans la même cheville la fait
éclater.

**Mesure à faire au pied à coulisse : le diamètre du filet, crête à crête.**
C'est lui qui décide si Ø6,4 suffit. S'il vaut 5 ou 5,5 → le perçage actuel
convient. S'il dépasse 6,4 → change `hole_d` dans le `.scad` et réimprime le
gabarit (vingt minutes).

Les têtes n'ont pas besoin d'être noyées dans la cale : elles portent sous la
**platine**, pas sur la cale. La cale ne voit que la tige. C'est pour ça que
les perçages sont de simples trous lisses.

### 3. Le vrai point faible n'est pas la vis, c'est ce qu'il y a derrière

Une vis de 70 mm n'a aucun intérêt si elle mord dans une cheville plastique
de 30 mm posée dans du plâtre. En abaissant le ventilateur de 30 mm, tu
augmentes le porte-à-faux et donc l'effort d'arrachement en tête de cheville,
alors même que le balourd du ventilateur travaille en fatigue.

Avant de monter, regarde dans quoi les vis mordent :

- **Solive / bois massif** — vis à bois de 70 mm, rien d'autre à faire.
- **Béton** — chevilles à frapper ou goujons métalliques ; une cheville
  plastique d'origine mérite d'être remplacée pendant que c'est démonté.
- **Placo seul** — à ne pas faire, avec ou sans cale. Il faut reprendre la
  charge sur une solive ou sur un boîtier de plafond dédié.

Ce point sort du périmètre de la pièce, mais c'est lui qui décide si le
montage tient.

## Vérification

`make verify` rend chaque pièce et applique sept gardes. Voir `CLAUDE.md`
pour ce que chacune attrape et pourquoi elle existe — en particulier la
garde 7, sans laquelle un cercle de perçage faux passait inaperçu.

Les cotes de la demande vivent dans `docs/target.json` (vérité externe). Elles
ne sont recopiées nulle part dans le `.scad` : `verify.py` mesure le maillage
et le confronte à ce fichier.
