# Ce qui reste ouvert

## 1. `rib_t` — l'epaisseur du ruban  (bloquant)

Estimee a 2,5 mm a l'oeil sur photo. **Aucune des trois cotes d'encombrement
relevees ne la contraint.** L'effort pour asseoir le crochet varie comme son
cube : 2,2 au lieu de 2,5, et c'est deux fois plus souple.

Mesure : au pied a coulisse, sur la branche horizontale, loin des conges.

## 2. `wrap_end` — l'enroulement sous le tube

| `wrap_end` | Bouche | vs tube 12,23 |
|---|---|---|
| 0° | 19,05 | +6,82 — rien ne retient |
| −25° | 15,18 | +2,95 — se pose et se leve librement |
| −50° (actuel) | 11,43 | −0,80 — levre legere |

Si le crochet d'origine se pose sans aucune resistance : `wrap_end = -25`.

## 3. L'origine des 20,28 mm de hauteur

Le biseau ampute 0,66 mm au bout du levier. La boite englobante rendue fait
19,62. Si tes 20,28 s'arretent a l'angle vif du biseau, il faut decaler `v_tip`.

## 4. `col_clr = 0.15` — le jeu du collier sur le jonc

Tres serre. L'ecrasement de premiere couche le mange en bas du collier.
Imprime `gauge` (25 × 11 × 5 nominal, 1,7 g, huit minutes) et mesure-le avant
tout le reste. S'il sort a 24,6 × 10,7 × 4,6, regle la compensation
« pied d'elephant » a 0,15–0,20 mm.

## 5. La gaine

Fentes : 20 × 15 mm par crochet, 46 × 6 mm pour la queue.
Entraxe des fenetres : 190 mm. C'est la couture qui le fixe, pas le jonc.

## 6. La forme en R (v14) — cotes du croquis a arbitrer

Le crochet est passe du J au R d'apres le croquis cote. `make web` superpose
cible-vs-reel. Trois points restent ouverts (iteration 1) :

- **Bras du haut : croquis 15, reel 12,5.** L'ecart n'est pas librement
  reductible : sous l'invariant « centre de l'arc = centre du tube », la
  profondeur (21) et le bras (12,5) sont lies par le rayon du tube. Pour
  gagner du bras il faudrait relire la cote (mesuree jusqu'ou ?) ou accepter
  un ventre non centre sur le tube.
- **Sens du pied.** `lang_ang = -90` (tout droit vers le bas). Le croquis
  suggere une diagonale vers le bas-droite. A confirmer : cap et longueur.
- **Ventre vs posabilite.** Un ventre plus ferme (`wrap_end` plus negatif)
  retient mieux mais ferme la bouche. Iteration 1 laisse la bouche tres
  ouverte (16,3 mm) : facile a poser, peu de retenue laterale — la retenue
  vient de l'arc sous le tube (levre 5,9 mm) et de l'elastique. Si le sac
  saute, fermer le ventre ; si la pose accroche, l'ouvrir.
