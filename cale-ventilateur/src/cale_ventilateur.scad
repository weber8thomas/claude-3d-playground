// =====================================================================
//  CALE D'ECARTEMENT -- plafond <-> platine de ventilateur a pales  [v1]
//
//  LA CALE TRAVAILLE EN COMPRESSION, PAS EN FLEXION.
//    Le ventilateur pend. Ce sont les VIS qui sont en traction ; la cale
//    est ecrasee entre le plafond et la platine. C'est le cas de charge
//    le plus favorable pour une piece imprimee -- a condition qu'elle
//    porte sur toute sa surface, donc : deux faces planes, rien qui
//    depasse, aucune structure interne modelisee.
//
//  LE REMPLISSAGE N'EST PAS DANS LE MODELE, IL EST DANS LE TRANCHEUR.
//    512 cm3 de volume plein. A 100 % de remplissage : ~650 g et une
//    trentaine d'heures, pour rien. Un cylindre ferme en compression est
//    tenu par ses perimetres et ses couches pleines dessus/dessous.
//    -> 20 % gyroide, et la piece `mod_hubs` en *modifier mesh* pour
//       forcer 100 % la ou ca compte : sous les rondelles.
//    Voir README.md.
//
//  IMPRESSION : posee a plat. zmin = 0, tous les percages verticaux,
//    aucun porte-a-faux, aucun support.
//
//  LE GABARIT AVANT LA CALE. `gabarit` est le meme disque en 2 mm : il
//    coute 15 minutes et valide le triangle de percage sur la platine
//    REELLE avant de lancer 10 heures d'impression. Il n'existe que pour
//    ca. Ne lance jamais `cale` avant d'avoir presente le gabarit.
//
//  Les cotes derivees sortent par echo() -> `make params`. Rien ne se
//  recopie ailleurs : verify.py et gallery.py relisent ces echos.
// =====================================================================

$fa = 2;      // facettage adaptatif : fin sur les percages Ø6,
$fs = 0.6;    // raisonnable sur le disque Ø150.

part = "all";   // "cale" | "gabarit" | "mod_hubs" | "all"

// --- DISQUE -----------------------------------------------------------
disc_d      = 150;    // diametre hors-tout                        [spec]
disc_t      = 30;     // epaisseur = l'ecartement gagne            [spec]

// --- PERCAGES DE FIXATION ---------------------------------------------
hole_d      = 6;      // nominal : vis M6                          [spec]
clr         = 0.4;    // jeu de percage. Un trou vertical imprime sort
                      // sous-cote : sans jeu, la M6 ne passe pas.
                      // Mettre a 0 pour du Ø6 strict (et aleser).
edge_margin = 25;     // du BORD DU TROU au bord du disque         [spec]
n_holes     = 3;      // triangle equilateral                      [spec]

// --- PASSAGE DU CABLE -------------------------------------------------
cable_d     = 25;     // traversant, centre

// --- FINITION ---------------------------------------------------------
cham        = 0.6;    // chanfrein des aretes : ebavurage, et la face
                      // plafond ne porte pas sur un elephant foot.
gab_t       = 2;      // epaisseur du gabarit de percage
hub_d       = 30;     // Ø des bossages `mod_hubs` (modifier mesh)

// --- DERIVE -----------------------------------------------------------
eps    = 0.01;
disc_r = disc_d / 2;
hd     = hole_d + clr;                       // Ø reellement perce
bolt_r = disc_r - edge_margin - hole_d / 2;  // cercle de percage (nominal)
pitch  = bolt_r * sqrt(3);                   // entraxe du triangle
web_e  = disc_r - (bolt_r + hd / 2);         // matiere trou -> bord
web_i  = bolt_r - hd / 2 - cable_d / 2;      // matiere trou -> cable

// Le premier percage a 90 deg : pointe en haut, comme le gabarit qu'on
// presente sur la platine. Une seule definition, geometrie et echo.
function bolt_a(i)  = 90 + i * 360 / n_holes;
function bolt_xy(i) = [bolt_r * cos(bolt_a(i)), bolt_r * sin(bolt_a(i))];

// Volumes analytiques, chanfreins non deduits (~0,06 %). Ce ne sont pas
// des mesures supposees : c'est le modele qui dit ce qu'il croit produire,
// et verify.py confronte le maillage a cette affirmation.
function v_plate(h) = PI/4 * h * (disc_d*disc_d - cable_d*cable_d - n_holes*hd*hd);
v_full = v_plate(disc_t);

// -- Gardes de COHERENCE INTERNE uniquement. Aucune ne verifie le modele
//    contre une mesure supposee : ce sont des paroi-minimum et des
//    emboitements, pas des cotes relevees.
assert(web_e > 5,       "matiere trop mince entre le percage et le bord");
assert(web_i > 5,       "matiere trop mince entre le percage et le cable");
assert(2*cham < gab_t,  "chanfrein plus epais que le gabarit");
assert(2*cham < disc_t, "chanfrein plus epais que la cale");
assert(hub_d > hd + 8,  "bossage trop petit pour couvrir la rondelle");

echo(str("bolt_r (cercle de percage)  = ", bolt_r, " mm  -> Ø", 2*bolt_r));
echo(str("pitch (entraxe triangle)    = ", pitch, " mm"));
echo(str("hd (Ø reellement perce)     = ", hd, " mm"));
echo(str("web_e (trou -> bord)        = ", web_e, " mm"));
echo(str("web_i (trou -> cable)       = ", web_i, " mm"));
echo(str("VIS_XY = ", [for (i = [0:n_holes-1]) bolt_xy(i)]));
echo(str("V_CALE_MM3 = ", v_plate(disc_t)));
echo(str("V_GABARIT_MM3 = ", v_plate(gab_t)));
echo(str("V_HUBS_MM3 = ", n_holes * PI/4 * hub_d*hub_d * disc_t));

// =====================================================================
//  MODULES
// =====================================================================

// Disque chanfreine sur son pourtour, en un seul solide de revolution :
// pas de difference() sur le contour, donc pas de corps parasite.
module chamfered_disc(r, h, c) {
    rotate_extrude(convexity = 4)
        polygon([[0, 0], [r - c, 0], [r, c], [r, h - c], [r - c, h], [0, h]]);
}

// Outil de percage : trou de rayon r traversant h, chanfreine aux deux
// bouts. Depasse de eps en haut et en bas pour ne pas laisser de peau.
module bore(r, h, c) {
    rotate_extrude(convexity = 4)
        polygon([[0, -eps], [r + c, -eps], [r + c, 0], [r, c],
                 [r, h - c], [r + c, h], [r + c, h + eps], [0, h + eps]]);
}

// Les trois percages. Position prise dans bolt_xy() -- la meme fonction
// que celle echo-ee : le maillage et l'annonce ne peuvent pas diverger.
module bolt_pattern(h, c) {
    for (i = [0 : n_holes - 1])
        translate(bolt_xy(i)) bore(hd / 2, h, c);
}

module plate(h) {
    difference() {
        chamfered_disc(disc_r, h, cham);
        bore(cable_d / 2, h, cham);
        bolt_pattern(h, cham);
    }
}

// =====================================================================
//  PIECES
// =====================================================================

module cale()    { plate(disc_t); }   // la piece
module gabarit() { plate(gab_t);  }   // le meme disque en 2 mm

// Trois cylindres aux coordonnees EXACTES des vis, dans le repere de la
// cale. A charger dans le trancheur en *modifier mesh* -> 100 % de
// remplissage sous les rondelles. Ne s'imprime pas : 3 corps separes.
module mod_hubs() {
    for (i = [0 : n_holes - 1])
        translate(bolt_xy(i)) cylinder(d = hub_d, h = disc_t);
}

if      (part == "cale")     cale();
else if (part == "gabarit")  gabarit();
else if (part == "mod_hubs") mod_hubs();
else {
    cale();
    translate([disc_d + 10, 0, 0]) gabarit();
}
