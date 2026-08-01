# cale-ventilateur — règles de travail

Cale d'écartement Ø150 × 30 entre le plafond et la platine d'un ventilateur à
pales. Pièce simple, enjeu sérieux : elle est au-dessus des têtes.

## Règle numéro un : le rendu, pas la relecture

Héritée de `cabas-velo`, et déjà confirmée ici. Avant d'affirmer quoi que ce
soit sur la géométrie, rends-la.

    make verify      # les sept gardes
    make web         # viewer 3D autonome, chaque itération à l'œil

Ne conclus pas sans avoir vu passer la sortie.

## La leçon de ce projet : un modèle ne peut pas se vérifier lui-même

Le harnais a d'abord été écrit avec six gardes : WARNING fatal, maillage,
`zmin`, cotes hors-tout, volume, et comptage des perçages traversants comparé
à ce que le modèle annonçait par `echo`.

Il déclarait **vert** une cale dont le cercle de perçage était à 40 mm au lieu
de 47.

Rien ne pouvait l'attraper, et c'est logique :

- le **volume** ne bouge pas — un trou déplacé occupe le même volume ;
- la **boîte englobante** ne bouge pas — le disque fait toujours Ø150 ;
- le **nombre de trous** ne bouge pas ;
- l'**echo** ne bouge pas non plus, parce qu'il dérive de `bolt_r`, comme la
  géométrie. Le modèle se trompait et se donnait raison.

Comparer un modèle à ce qu'il affirme de lui-même ne prouve rien. Il faut une
source qui ne vienne pas du `.scad` : c'est **`docs/target.json`**, la demande
elle-même, et la **garde 7** qui mesure le maillage et le confronte à ce
fichier. Même dispositif que `docs/target_hook.json` dans `cabas-velo`.

**Corollaire : toute nouvelle garde doit être testée en négatif.** Casse
volontairement le modèle et vérifie qu'elle mord. Une garde qui n'a jamais
échoué ne garde rien. Les cas déjà éprouvés : `bolt_r` décalé, `n_holes=4`,
`clr` négatif, `disc_d` faux, `cable_d` faux, variable perdue, hors plateau.

## Les sept gardes

1. **Tout `WARNING` OpenSCAD est fatal.** Une variable perdue produit un
   maillage irréprochable de la MAUVAISE pièce. Aucun outil de maillage ne
   remplace cette garde.
2. **Maillage** — un seul corps (trois pour `mod_hubs`), étanche, orientation
   des faces cohérente.
3. **`zmin` = 0** et encombrement dans le plateau. Sinon la pièce est perchée
   sur des supports.
4. **Cotes hors-tout** — bornes sur x, y, z.
5. **Volume annoncé vs mesuré** (0,5 %). Cohérence interne entre ce que le
   modèle dit produire et ce qu'il produit. Filet de sécurité, pas plus : voir
   plus haut pourquoi ça ne suffit pas.
6. **Perçages traversants** — coupe à mi-hauteur, nombre et positions.
7. **Cible vs réel** — le maillage mesuré, confronté à `docs/target.json`.
   La seule garde dont la référence ne vient pas du `.scad`.

## Ce que le code ne doit jamais faire

- **Recoller des morceaux de `.scad`.** Réécris le fichier entier.
- **Recopier une cote de `docs/target.json` dans le `.scad`.** Ça ferait
  disparaître la seule garde indépendante du projet. Les cotes du `.scad`
  sont des paramètres de conception ; celles de `target.json` sont la demande.
  Les deux doivent rester séparées pour pouvoir être confrontées.
- **Dupliquer une position.** `bolt_xy(i)` sert à la fois à la géométrie et à
  l'echo. Une seule définition, pas deux qui peuvent diverger.
- **Ajouter un `assert` qui verrouille une mesure supposée.** Les `assert` du
  `.scad` gardent une **cohérence interne** — une paroi n'est pas trop mince,
  un chanfrein tient dans son épaisseur — jamais une cote relevée sur le
  ventilateur. Ces cotes-là vont dans `target.json`, où elles restent
  discutables.

## Architecture

Trois pièces, un seul `part=` :

- **`cale`** — la pièce. Cylindre plein Ø150 × 30, passage central Ø25,
  trois perçages Ø6+jeu à R = 47. Chanfreins 0,6 mm.
- **`gabarit`** — le même disque en 2 mm. Il n'existe que pour être présenté
  sur la platine réelle avant de lancer dix heures d'impression.
- **`mod_hubs`** — trois cylindres Ø30 aux coordonnées des vis, pour le
  *modifier mesh* du trancheur. Ne s'imprime pas.

## Le remplissage n'est pas dans le modèle

Aucune structure interne n'est modélisée, et il ne faut pas en ajouter. La
cale travaille en compression pure ; un cylindre fermé est tenu par ses
périmètres et ses couches pleines d'appui. Le remplissage se règle au
trancheur (20 % gyroïde), et `mod_hubs` force 100 % sous les rondelles.
Modéliser des nervures coûterait de la complexité pour un gain nul.

## Ce qui reste ouvert

- **Le diamètre réel des vis** n'est pas confirmé. Le pas mesuré (2 mm) exclut
  une métrique et désigne une vis à bois. `hole_d = 6` et `clr = 0,4` sont
  des hypothèses raisonnables ; le gabarit tranche en vingt minutes.
- **L'entraxe du triangle** vient de la demande, pas d'une mesure sur la
  platine. Même remarque : le gabarit tranche.
- **La tenue de la fixation au plafond** (cheville, solive, boîtier) est le
  vrai point faible du montage et sort du périmètre de la pièce. Voir
  `README.md`.
