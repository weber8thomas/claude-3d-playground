# cale-ventilateur — règles de travail

Cale d'écartement Ø150 × 30 entre le plafond et la platine d'un ventilateur à
pales, fixée en deux temps. Pièce simple, enjeu sérieux : elle est au-dessus
des têtes.

## Règle numéro un : le rendu, pas la relecture

Héritée de `cabas-velo`, et confirmée trois fois ici. Avant d'affirmer quoi
que ce soit sur la géométrie, rends-la — et avant d'affirmer quoi que ce soit
sur l'impression, tranche-la.

    make verify      # les sept gardes géométriques
    make slice       # la huitième : temps, poids et supports RÉELS
    make web         # viewer 3D autonome, chaque itération à l'œil

Ne conclus pas sans avoir vu passer la sortie.

## Les trois leçons de ce projet

Elles se ressemblent, et ce n'est pas un hasard : **à chaque fois, quelque
chose affirmait le faux sans que rien ne le signale.** Un vert n'est une
preuve que si la garde regarde ailleurs que le modèle, si elle mesure la
bonne chose, et si elle peut échouer.

### 1. Un modèle ne peut pas se vérifier lui-même

Le harnais a d'abord été écrit avec six gardes : WARNING fatal, maillage,
`zmin`, cotes hors-tout, volume, et comptage des perçages comparé à ce que le
modèle annonçait par `echo`.

Il déclarait **vert** une cale dont le cercle de perçage était à 40 mm au lieu
de 47. Rien ne pouvait l'attraper :

- le **volume** ne bouge pas — un trou déplacé occupe le même volume ;
- la **boîte englobante** ne bouge pas — le disque fait toujours Ø150 ;
- le **nombre de trous** ne bouge pas ;
- l'**echo** ne bouge pas non plus, parce qu'il dérive de `bolt_r`, comme la
  géométrie. Le modèle se trompait et se donnait raison.

D'où **`docs/target.json`** — la demande elle-même — et la **garde 7**, qui
mesure le maillage et le confronte à ce fichier. Même dispositif que
`docs/target_hook.json` dans `cabas-velo`.

### 2. Une garde peut mesurer faux

La garde 7 a ensuite déclaré **FAIL** sur une pièce parfaitement bonne :
« logement d'écrou, sur plats 9,78 pour un M6 de 10 ». Le logement mesure
exactement 10,300.

`ring()` renvoyait le rayon **moyen** des points du contour. Ça n'a de sens
que sur un cercle. Le contour hexagonal porte 12 points — 6 sommets à 5,947 et
6 nés de la triangulation STL des faces — et la moyenne tombe quelque part
entre le sommet et le plat, à une hauteur près.

La bonne mesure d'un emboîtement est l'**apothème** : la distance du centre au
*segment* le plus proche, c'est-à-dire le cercle inscrit. C'est lui que la vis
touche et que l'écrou doit franchir. Sur un hexagone, apothème et circonscrit
diffèrent de 13 % ; même sur les perçages Ø6,4 le rayon moyen dit 3,195 quand
la vis ne voit que 3,190.

`ring()` renvoie désormais les deux, et le choix est explicite à chaque
appel : **moyen pour les diamètres et les centres, apothème pour tout
emboîtement.**

Deux corollaires trouvés en creusant, l'un et l'autre du même genre — comparer
plus finement que ce que la mesure porte :

- Le centre d'un contour est le **barycentre de sa surface**, pas la moyenne
  de ses points. La triangulation en ajoute d'asymétriques, qui décalent la
  moyenne de 5·10⁻⁵ mm.
- L'**epsilon de comparaison** vaut 1 µm (`EPS`), pas 10⁻⁶ mm. Cent fois plus
  fin que ce qu'une imprimante FDM résout, vingt fois plus grossier que le
  bruit du maillage. Un epsilon à 10⁻⁶ sortait « hors plage » pour 50
  nanomètres d'écart à la borne.

### Corollaire : toute garde se teste en négatif

Casse volontairement le modèle et vérifie qu'elle mord. Une garde qui n'a
jamais échoué ne garde rien — et une garde qui échoue à tort est pire, elle
apprend à ignorer les rouges. Les onze cas éprouvés : `bolt_r` décalé,
triangles superposés, décalage à 30°, lamage trop profond, lamage trop court,
écrou non noyé, logement trop serré, logement trop lâche, jeu de perçage
négatif, Ø disque faux, variable perdue. **11/11 détectés.** C'est le cas
« logement trop serré » qui passait silencieusement et qui a fait découvrir la
leçon n° 2.

### 3. Un temps d'impression et un « aucun support » se tranchent

J'ai écrit « ~25 min » pour le gabarit et « aucun support » dans le README
sans avoir jamais tranché. Le premier était faux du simple au double (50 min).
Le second était vrai, mais par chance : mis à l'épreuve, le plafond du lamage
était un annulaire de 3,8 mm au fond d'un puits borgne de 27 mm, dans lequel
PrusaSlicer voulait loger 3,2 g de support qu'on n'aurait jamais pu curer.
D'où le congé à 45° (`cb_relief`), qui ramène le porte-à-faux à 1,8 mm.

**Et la garde a dû être reformulée trois fois avant de mordre :**

- *« aucun support généré »* — la formulation que `cabas-velo` réclamait.
  **Circulaire** : le profil a `support_material = 0`, donc il n'en génère
  jamais, pour aucune pièce. Une étagère en porte-à-faux passe.
- *« l'auto-détecteur n'en réclame aucun »* — **trop sévère** en sens
  inverse : il signale toute face horizontale quelle que soit la portée.
- *« tout porte-à-faux est ponté »* — **ne mord pas** : PrusaSlicer ponte à
  peu près tout, y compris ce qui pendrait.
- *« la part de support rapportée au poids de la pièce »* — **mord.**
  Cale 1,7 %, gabarit 0 %, témoin en porte-à-faux 31,2 %. La masse absolue
  ne discriminerait rien : le témoin, minuscule, en demande moins que la cale.

Le témoin (`tools/temoin_porte_a_faux.scad`) fait partie de la garde autant
que le seuil. Il est versionné et **rejoué à chaque `make slice`** : si un
jour il passe, ce n'est pas lui qui est en cause, c'est la garde.

**Autre piège rencontré, même famille :** un `.ini` PrusaSlicer est **plat**.
Avec des en-têtes `[print]`/`[filament]`/`[printer]`, il est silencieusement
ignoré — le trancheur retombe sur ses défauts (couche 0,3, buse 200,
plateau 0) sans rien dire. La première mesure annonçait « 3h36 pour le
gabarit » et ne mesurait rien du tout. `slice_check.py` relit donc l'en-tête
du G-code avant de croire le moindre chiffre.

## Les huit gardes

1. **Tout `WARNING` OpenSCAD est fatal.** Une variable perdue produit un
   maillage irréprochable de la MAUVAISE pièce. Aucun outil de maillage ne
   remplace cette garde.
2. **Maillage** — un seul corps (2 pour `essai`, 6 pour `mod_hubs`), étanche,
   orientation des faces cohérente.
3. **`zmin` = 0** et encombrement dans le plateau.
4. **Cotes hors-tout** — bornes sur x, y, z.
5. **Volume annoncé vs mesuré** (1 %). Cohérence interne. Filet de sécurité,
   pas plus : voir la leçon n° 1.
6. **Perçages traversants** — coupe horizontale, nombre et positions.
7. **Cible vs réel** — le maillage mesuré, confronté à `docs/target.json` :
   les deux triangles, leur décalage, les jeux de perçage et d'écrou, la marge
   au bord, et deux profondeurs qu'aucune coupe unique ne montre — le plafond
   de perçage et le logement d'écrou, trouvés par dichotomie
   (`z_transition`). La seule garde dont la référence ne vient pas du `.scad`.
8. **Tranché pour de vrai** (`make slice`, `tools/slice_check.py`) — le profil
   arrive-t-il jusqu'au trancheur, la part de support réclamée reste-t-elle
   sous 10 %, et quels sont les temps et poids **mesurés**. Lent : hors de
   `make verify`.

## Ce que le code ne doit jamais faire

- **Recoller des morceaux de `.scad`.** Réécris le fichier entier.
- **Recopier une cote de `docs/target.json` dans le `.scad`.** Ça ferait
  disparaître la seule garde indépendante du projet. Les cotes du `.scad` sont
  des paramètres de conception ; celles de `target.json` sont la demande. Les
  deux doivent rester séparées pour pouvoir être confrontées.
- **Dupliquer une position.** `ceil_xy(i)` et `brkt_xy(i)` servent à la fois à
  la géométrie et aux echos. Une seule définition, pas deux qui peuvent
  diverger.
- **Utiliser un rayon moyen pour un emboîtement.** Voir la leçon n° 2.
- **Annoncer un temps d'impression ou une absence de support sans avoir
  tranché.** Voir la leçon n° 3. `make slice` est là pour ça.
- **Ajouter un `assert` qui verrouille une mesure supposée.** Les `assert` du
  `.scad` gardent une **cohérence interne** — une paroi n'est pas trop mince,
  un écrou est bien noyé, un lamage ne rejoint pas son voisin — jamais une
  cote relevée sur le ventilateur. Ces cotes-là vont dans `target.json`, où
  elles restent discutables.

## Architecture

Quatre pièces, un seul `part=` :

- **`cale`** — la pièce. Cylindre plein Ø150 × 30, passage central Ø25, deux
  triangles à R = 47 décalés de 60° : trois lamages Ø14 (plafond) et trois
  logements d'écrou M6 ouverts vers le haut (platine).
- **`gabarit`** — le même disque en 2 mm, six perçages nus. Il n'existe que
  pour être présenté sur le plafond **et** sur la platine : c'est la seule
  chose qui valide l'hypothèse « les deux triangles sont le même ».
- **`essai`** — deux coupons à l'échelle 1 (~45 min). Portée de tête, accès de
  l'embout, entrée de l'écrou, passage de la M6. À imprimer en premier.
- **`mod_hubs`** — six colonnes Ø22 aux coordonnées des vis, pour le
  *modifier mesh* du trancheur. Ne s'imprime pas.

## Le remplissage n'est pas dans le modèle

Aucune structure interne, et il ne faut pas en ajouter. Ce qui porte, c'est la
colonne de matière autour de chaque vis de platine, en compression. Le
remplissage se règle au trancheur (20 % gyroïde), et `mod_hubs` force 100 %
sur les six colonnes. Modéliser des nervures coûterait de la complexité pour
un gain nul.

## La chaîne d'impression

L'utilisateur imprime sous **Cura + Klipper**, sur Ender 3 V3 SE, en PETG.
Les profils vivent dans `slicer/` : Cura et Klipper sont les vrais, le
`.ini` PrusaSlicer n'existe que pour la garde 8 (seul trancheur pilotable en
CLI ; `CuraEngine` n'est pas empaquetable). **Un temps sorti de PrusaSlicer
n'est pas un temps Cura**, et sous Klipper le temps réel dépend surtout de
`max_accel` et de l'input shaper — le dire chaque fois qu'on cite un chiffre.

Deux réglages échappent structurellement au trancheur et vivent dans
`printer.cfg` : la `pressure_advance` (rondeur des Ø6 à vitesse) et l'input
shaper. Aucun profil Cura ne peut les rattraper.

## Ce qui reste ouvert

- **Le diamètre réel des vis du plafond** n'est pas confirmé. Le pas mesuré
  (2 mm) exclut une métrique et désigne une vis à bois. `hole_d = 6` et
  `clr = 0,4` sont des hypothèses ; `essai` tranche en 45 minutes.
- **Le type de tête** non plus. Une tête fraisée dans un trou cylindrique
  travaille comme un coin : rondelle obligatoire, ou fraisure à modéliser.
- **L'entraxe de la platine** vient de la demande, pas d'une mesure. Le
  gabarit tranche — et c'est lui qui valide le décalage de 60°.
- **La tenue de la fixation au plafond** (cheville, solive, boîtier) est le
  vrai point faible du montage et sort du périmètre de la pièce. Voir
  `README.md`.
