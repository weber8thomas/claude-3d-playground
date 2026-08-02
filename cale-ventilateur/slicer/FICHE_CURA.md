# Fiche Cura — à suivre de haut en bas, une seule fois

**Tu imprimes sous Cura. Reste sous Cura.** PrusaSlicer n'apparaît dans ce
dépôt que comme outil de mesure automatisable (`make slice`, `make buses`) :
c'est le seul trancheur pilotable en ligne de commande. Tu n'as rien à en
faire, rien à installer.

Cette fiche est le chemin court. Le détail et le pourquoi sont dans
`cura_ender3v3se_petg.md` (réglages) et `cura_buses.md` (choix de la buse).

---

## 1. Monte la buse de 0,6

Puis dis-le à Cura, sinon rien de la suite ne veut dire quoi que ce soit :

**Preferences → Printers → Ender 3 V3 SE → Machine Settings → Extruder 1 →
Nozzle Size = `0.6`**

## 2. Passe l'affichage des réglages en « Expert »

Sans ça, la moitié des champs ci-dessous sont invisibles.

**Roue dentée en haut du panneau de réglages → Expert.**

## 3. Les réglages

Tout ce qui n'est pas dans cette liste : laisse le défaut.

### Quality
| Champ | Valeur |
|---|---|
| Layer Height | `0.3` |
| Initial Layer Height | `0.3` |
| Line Width | `0.62` |

### Walls
| Champ | Valeur |
|---|---|
| Wall Line Count | `2` |
| **Hole Horizontal Expansion** | **`0`** ← n'y touche jamais |

### Top/Bottom
| Champ | Valeur |
|---|---|
| Top Layers | `4` |
| Bottom Layers | `4` |

### Infill
| Champ | Valeur |
|---|---|
| Infill Density | `20` % |
| Infill Pattern | Gyroid |
| **Infill Layer Thickness** | **`0.6`** ← ça seul enlève 1 h à la cale |

### Material
| Champ | Valeur |
|---|---|
| Printing Temperature | `235` |
| Printing Temperature Initial Layer | `240` |
| Build Plate Temperature | `70` |
| Build Plate Temperature Initial Layer | `70` |
| Retraction Distance | `1.0` |
| Retraction Speed | `40` |

### Speed
| Champ | Valeur |
|---|---|
| Infill Speed | `75` |
| Inner Wall Speed | `75` |
| Outer Wall Speed | `40` |
| Top/Bottom Speed | `60` |
| Travel Speed | `200` |
| Initial Layer Speed | `30` |
| Enable Acceleration Control | **décoché** |
| Enable Jerk Control | **décoché** |

Les accélérations sont gérées par Klipper (`printer.cfg`). Laisser Cura
écrire ses `M204` ne fait que se battre avec la machine.

### Cooling
| Champ | Valeur |
|---|---|
| Fan Speed | `40` % |
| Initial Fan Speed | `0` % |
| Regular Fan Speed at Layer | `2` |

### Support & Adhesion
| Champ | Valeur |
|---|---|
| Generate Support | **décoché** |
| Build Plate Adhesion Type | Skirt |

### Mesh Fixes
| Champ | Valeur |
|---|---|
| Maximum Resolution | `0.2` |
| Maximum Deviation | `0.01` |

Au défaut (0,5 mm), Cura polygonise les perçages Ø6 : tu testerais un trou
que la cale ne reproduirait pas.

## 4. Enregistre le profil

**Profile → Create profile from current settings** → `PETG 0.6 cale`.
Tu le rappelles pour chaque pièce, sans rien resaisir.

---

## 5. L'ordre d'impression

Ne lance **jamais** la cale en premier.

| | fichier | ~ | à quoi ça sert |
|---|---|---|---|
| 1 | `stl/gabarit_fente.stl` | 15 min | **mesurer le rayon du triangle de ta platine** |
| 2 | `stl/essai_buse06.stl` | 25 min | la M6 passe ? l'écrou entre ? la tête porte ? |
| 3 | `stl/gabarit.stl` | 45 min | le triangle tombe-t-il juste, plafond **et** platine |
| 4 | `stl/cale.stl` | ~4 h | la pièce |

Durées converties de PrusaSlicer vers ton estimation Cura ; Cura annonce
plutôt plus. Ce qui tient, ce sont les **rapports** : la cale passe de ~11 h
à ~4 h.

Pour la cale seulement, tu peux ajouter `stl/mod_hubs.stl` en *modifier
mesh* : **File → Open File(s)**, le sélectionner, **Per Model Settings →
Modify settings for infill of other models**, `Infill Density = 100 %` et
`Infill Layer Thickness = 0.3`. Six colonnes à 100 % là où passe l'effort.
C'est un confort, pas une obligation.

## Deux choses à ne pas rater

**`stl/essai_buse06.stl` n'est pas `stl/essai.stl`.** C'est la même pièce
avec `clr = 0,5` au lieu de 0,4 : une ligne de 0,62 se retire davantage en
virage qu'une de 0,42, le trou sort plus petit. Si la M6 passe trop juste,
réimprime avec 0,6 ; si elle flotte, reviens à 0,4.

**Plateau à 70 °C, pas 80, et bâton de colle en agent de démoulage.** Le PETG
colle assez à la tôle PC/PEI pour en arracher des morceaux. Laisse
redescendre sous 40 °C avant de décoller.
