# Cura — Ender 3 V3 SE sous Klipper — PETG

Noms de champs Cura 5.x, interface anglaise (le nom interne est entre
parenthèses : c'est lui qu'on retrouve dans un `.curaprofile`).

**Ce fichier ne couvre que ce qui se règle dans Cura.** La `pressure_advance`
et l'input shaper vivent dans `printer.cfg` — voir `klipper_petg.cfg`. Aucun
profil de trancheur ne peut les rattraper.

## Le plafond n'est pas la vitesse, c'est le débit

La V3 SE annonce 250 mm/s, et sous Klipper la partie mouvement peut
effectivement suivre. Mais la hotend d'origine plafonne autour de
**10 mm³/s en PETG**, et **Cura n'a pas de champ « débit volumétrique max »**
(contrairement à PrusaSlicer ou Orca). À toi de faire la conversion :

    vitesse_max (mm/s) = 10 / (hauteur_de_couche × largeur_de_ligne)

À 0,2 × 0,42 → **120 mm/s**. Monter à 150 ne fait pas gagner de temps : ça
sous-extrude. Si tu changes de hauteur de couche, refais le calcul.

## Réglages

### Quality
| Champ | Valeur |
|---|---|
| Layer Height (`layer_height`) | **0,2** |
| Initial Layer Height (`layer_height_0`) | 0,2 |
| Line Width (`line_width`) | 0,42 |

### Walls
| Champ | Valeur | |
|---|---|---|
| Wall Line Count (`wall_line_count`) | **3** | |
| **Hole Horizontal Expansion (`hole_xy_offset`)** | **0** | ← **n'y touche jamais** |
| Horizontal Expansion (`xy_offset`) | 0 | |

`hole_xy_offset` est une compensation de diamètre de trou. Si tu l'actives, le
gabarit ment exactement sur ce qu'il est censé mesurer, et la cale sortira
différente. Le but du gabarit est de mesurer ce que **ta** machine produit
réellement — pas de le corriger d'avance.

### Top/Bottom & Infill
| Champ | `cale` | `gabarit` / `essai` |
|---|---|---|
| Top Layers (`top_layers`) | 5 | 1 |
| Bottom Layers (`bottom_layers`) | 5 | 1 |
| Infill Density (`infill_sparse_density`) | **20 %** | 15 % |
| Infill Pattern (`infill_pattern`) | Gyroid | Grid |

### Material
| Champ | Valeur |
|---|---|
| Printing Temperature (`material_print_temperature`) | **235** |
| Printing Temperature Initial Layer (`material_print_temperature_layer_0`) | 240 |
| Build Plate Temperature (`material_bed_temperature`) | **70** |
| Build Plate Temperature Initial Layer | 70 |
| Retraction Distance (`retraction_amount`) | **1,0** |
| Retraction Speed (`retraction_speed`) | 40 |

**70 °C, pas 80.** Le PETG crée une liaison chimique avec la tôle PC/PEI de
la V3 SE, assez forte pour en arracher des morceaux au démoulage. Passe un
**bâton de colle** — pas pour faire tenir, comme **agent de démoulage** — et
laisse le plateau redescendre sous 40 °C avant de décoller. C'est
contre-intuitif et c'est ce qui sauve la tôle.

### Speed
| Champ | Valeur | |
|---|---|---|
| Outer Wall Speed (`speed_wall_0`) | **50** ou **90** | voir le tableau input shaper |
| Inner Wall Speed (`speed_wall_x`) | 100 | |
| Infill Speed (`speed_infill`) | **120** | = 10 mm³/s, le plafond |
| Top/Bottom Speed (`speed_topbottom`) | 100 | |
| Travel Speed (`speed_travel`) | 200 | |
| Initial Layer Speed (`speed_layer_0`) | **50** | |

### Acceleration — à DÉSACTIVER dans Cura
| Champ | Valeur |
|---|---|
| Enable Acceleration Control (`acceleration_enabled`) | **off** |
| Enable Jerk Control (`jerk_enabled`) | **off** |

Sous Klipper, les accélérations se règlent dans `printer.cfg` (`max_accel`,
`square_corner_velocity`) et l'input shaper corrige le ringing à la source.
Laisser Cura écrire ses `M204`/`M205` ne fait que se battre avec la config
machine. Une seule autorité sur les accélérations, et c'est Klipper.

### Cooling
| Champ | Valeur |
|---|---|
| Enable Print Cooling (`cool_fan_enabled`) | on |
| Fan Speed (`cool_fan_speed`) | **40 %** |
| Initial Fan Speed (`cool_fan_speed_0`) | 0 % |
| Regular Fan Speed at Layer (`cool_fan_full_layer`) | 2 |

100 % de ventilation tue la cohésion inter-couches du PETG. Sur une pièce qui
porte un ventilateur au plafond, ce n'est pas un détail.

### Support & Adhesion
| Champ | Valeur |
|---|---|
| Generate Support (`support_enable`) | **off** |
| Build Plate Adhesion Type (`adhesion_type`) | **Skirt** |

`zmin = 0` sur toutes les pièces, tous les perçages verticaux : aucun support
n'est nécessaire. Le seul pont est le plafond du lamage (anneau de 3,8 mm),
qu'un contre-perçage ordinaire franchit sans aide. Pas de brim : Ø150 de
contact au plateau, aucun risque de warp en PETG à 70 °C.

### Mesh Fixes — le piège silencieux
| Champ | Défaut | Mettre |
|---|---|---|
| Maximum Resolution (`meshfix_maximum_resolution`) | 0,5 mm | **0,2 mm** |
| Maximum Deviation (`meshfix_maximum_deviation`) | 0,025 mm | 0,01 mm |

Au défaut, Cura simplifie les contours par segments de 0,5 mm. Sur un perçage
Ø6,4 — 20 mm de circonférence — ça le réduit à une quarantaine de segments au
mieux, souvent bien moins après filtrage : le trou imprimé est un polygone,
pas le cercle du modèle. Le gabarit testerait alors un trou que la cale ne
reproduirait pas. C'est le réglage qui compte le plus dans tout ce fichier
après `hole_xy_offset`.

## Ce qu'il ne faut PAS accélérer entre le gabarit et la cale

Le gabarit ne prédit la cale que si **le diamètre réel des trous** est le
même dans les deux impressions. Trois réglages le décident :

- la **température de buse**,
- la **vitesse de périmètre externe**,
- le **débit** (Flow, et donc la largeur de ligne).

Garde-les identiques. Tout le reste — remplissage, couches pleines, hauteur
de couche des couches intermédiaires — peut différer librement.

Si tu changes l'un des trois pour aller plus vite sur le gabarit, il ne
mesure plus rien d'utile : il te donne le diamètre d'un trou que tu
n'imprimeras jamais.

## Aller plus vite sur le gabarit

Le temps du gabarit est dominé par la **première couche** : un disque Ø150
plein, c'est ~40 m d'extrusion, soit ~13 min à 50 mm/s quoi qu'il arrive.
C'est un plancher, la géométrie ne permet pas mieux.

Le seul vrai levier est l'épaisseur :

    openscad -o gabarit_1mm.stl -D 'part="gabarit"' -D gab_t=1 \
             src/cale_ventilateur.scad

1 mm au lieu de 2 : cinq couches au lieu de dix, ~10 min de gagnées. Un
gabarit qu'on presse contre un plafond n'a pas besoin de 2 mm.
