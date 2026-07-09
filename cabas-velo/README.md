# cabas-velo

Armature imprimee 3D pour cabas velo type BikeZac : jonc de 280 mm pliable,
deux crochets de porte-bagages, lobe central pour l'elastique.

## Demarrer

    make verify     # rend chaque piece et passe les gardes
    make profile    # trace le profil du crochet, tube en place, cotes cible
    make web        # viewer 3D autonome (build/index.html) : chaque iteration a l'oeil
    make serve      # sert build/ en local (http://localhost:8000/index.html)
    make stl        # tous les STL dans build/
    make params     # toutes les cotes derivees

Prerequis : `openscad`, `python3`, `matplotlib`, `trimesh` (+ `scipy` ou
`networkx`, requis par `trimesh.split`). Le viewer (`make web`) embarque
three.js vendorise dans `tools/web/vendor/` : rien a telecharger, la page
marche hors-ligne, meme ouverte en double-clic.

## Ordre d'impression

| Job | Piece | Duree | Ce qu'il valide |
|---|---|---|---|
| 1 | `gauge` + `hinge_test` | ~20 min | le jeu du collier, l'alesage serre |
| 2 | `hook` seul | ~10 min | `tube_d`, `rib_t`, `wrap_end` — pose-le sur le tube |
| 3 | `a` + `b` | ~1 h 30 | 6 perimetres, 20 % de gyroide, couture Z au bout libre |
| 4 | `hooks3` | ~50 min | temps de couche mini 15 s |

PETG. Rien a tourner dans le trancheur : `zmin = 0` partout, aucun support.

**Ne lance jamais le job 3 avant le job 1.** Le jauge coute 1,7 g et huit
minutes ; les deux joncs coutent 21 g et une heure et demie.

## Ou vit la resistance du jonc

Le moment de 1250 N·mm flechit le jonc autour de Z : les fibres extremes sont
les **deux aretes longues de la bande**, donc les perimetres. I total = 554,6 mm⁴ ;
le coeur non-perimetrique n'en porte que 23,6 %. Reduire les perimetres serait
une faute ; reduire le remplissage ne coute rien.

Voir `CLAUDE.md` pour les regles de travail, `docs/DECISIONS.md` pour l'historique.
