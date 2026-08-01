// TEMOIN DE LA GARDE 8 -- cette piece DOIT echouer.
//
// Une etagere de 30 mm en porte-a-faux horizontal, a 20 mm du plateau :
// impossible a imprimer sans supports, et personne n'en doute.
//
// Elle existe parce qu'une garde qui n'a jamais echoue ne garde rien. Trois
// formulations de la garde 8 ont ete essayees avant celle-ci, et les trois
// laissaient passer cette etagere :
//
//   - "aucun support genere" : circulaire, le profil a support_material = 0 ;
//   - "l'auto-detecteur n'en reclame aucun" : trop severe en sens inverse ;
//   - "tout porte-a-faux est ponte" : PrusaSlicer ponte a peu pres tout.
//
// La formulation retenue -- la PART de support rapportee au poids de la
// piece -- la rejette a 31 %, quand la cale est a 1,7 %. C'est ce temoin qui
// a permis de le savoir, et c'est pour ca qu'il est versionne et rejoue a
// chaque `make slice` plutot que griffonne dans build/.
//
// La masse absolue ne discriminerait rien : ce temoin, minuscule, demande
// MOINS de support que la cale (1,9 g contre 3,2 g).

pied_x   = 10;
pied_y   = 10;
pied_h   = 20;
etagere  = 30;   // porte-a-faux horizontal pur
ep       = 3;

cube([pied_x, pied_y, pied_h]);
translate([0, 0, pied_h]) cube([pied_x + etagere, pied_y, ep]);
