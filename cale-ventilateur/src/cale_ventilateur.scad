// =====================================================================
//  CALE D'ECARTEMENT -- plafond <-> platine de ventilateur a pales  [v2]
//
//  FIXATION EN DEUX TEMPS. La cale se visse d'abord au plafond avec les
//    vis EXISTANTES ; la platine se visse ensuite sous la cale avec trois
//    M6 neuves. Deux triangles de percage identiques (R = bolt_r),
//    decales de 60 degres pour ne pas se rencontrer.
//
//  AUCUN PLASTIQUE EN TRACTION, NULLE PART.
//    Cote plafond : lamage profond, la tete de vis porte sur un plafond
//      de percage de seat_t mm juste sous le plafond reel. La vis ne
//      traverse que seat_t de cale au lieu de disc_t : elle retrouve
//      l'ancrage qu'elle avait, donc on GARDE les vis de 30 mm.
//    Cote platine : ecrous M6 noyes dans des empreintes hexagonales sur
//      la face plafond. Le serrage plaque l'ecrou au fond de son
//      logement et comprime la colonne de matiere sous lui. Chemin
//      d'effort tout metal ; le plastique n'est qu'une entretoise.
//      Les ecrous ne peuvent pas tomber : le plafond les bouche.
//
//  LE REMPLISSAGE N'EST PAS DANS LE MODELE, IL EST DANS LE TRANCHEUR.
//    Aucune structure interne. Ce qui porte, c'est la colonne de matiere
//    autour de chaque vis de platine (z = 0 -> fond du logement d'ecrou).
//    -> 20 % gyroide, et `mod_hubs` en *modifier mesh* pour forcer 100 %
//       sur ces six colonnes. Voir README.md.
//
//  IMPRESSION : posee a plat, face platine au plateau. zmin = 0, tous les
//    percages verticaux. Un seul pont : le plafond du lamage (annulaire,
//    3,8 mm de large). C'est un contre-percage ordinaire, aucun support.
//    Les logements d'ecrous sont ouverts vers le HAUT : imprimes en fin
//    de course, jamais en pont.
//
//  L'ORIENTATION SE LIT SUR LA PIECE. Les lamages Ø14 se voient au premier
//    coup d'oeil depuis la face platine ; les percages d'ecrou font Ø6.
//    Il n'y a pas moyen de monter la cale a 60 degres par erreur.
//
//  Les cotes derivees sortent par echo() -> `make params`. Elles ne sont
//  recopiees nulle part : verify.py et gallery.py relisent ces echos, et
//  confrontent le MAILLAGE MESURE a docs/target.json (verite externe).
// =====================================================================

$fa = 2;      // facettage adaptatif : fin sur les percages Ø6,
$fs = 0.6;    // raisonnable sur le disque Ø150.

part = "all";   // "cale" | "gabarit" | "essai" | "mod_hubs" | "all"

// --- DISQUE -----------------------------------------------------------
disc_d      = 150;    // diametre hors-tout                        [spec]
disc_t      = 30;     // epaisseur = l'ecartement gagne            [spec]

// --- TRIANGLE DE PERCAGE (le meme pour les deux faces) ----------------
hole_d      = 6;      // nominal : vis M6 / vis a bois Ø6          [spec]
clr         = 0.4;    // jeu de percage. Un trou vertical imprime sort
                      // sous-cote : sans jeu, la vis ne passe pas.
edge_margin = 25;     // du BORD DU TROU au bord du disque         [spec]
n_holes     = 3;      // triangle equilateral                      [spec]
offset_ang  = 60;     // decalage plafond -> platine. 60 deg place chaque
                      // percage de platine a mi-chemin entre deux lamages.

// --- COTE PLAFOND : vis existantes de 30 mm, reutilisees ---------------
cb_d        = 14;     // Ø du lamage : tete de vis + embout de vissage
seat_t      = 3;      // plafond de percage. C'est CA qui rend les vis de
                      // 30 mm suffisantes : elles ne traversent que 3 mm
                      // de cale et gardent ~27 mm d'ancrage.

// --- COTE PLATINE : 3 vis M6 neuves + 3 ecrous noyes ------------------
nut_s       = 10;     // six-pans sur plats, ecrou M6 DIN 934
nut_h       = 5;      // hauteur d'un ecrou M6 DIN 934
nut_clr     = 0.3;    // jeu du logement, sur plats
nut_depth   = 5.8;    // profondeur du logement. DOIT depasser nut_h :
                      // un ecrou qui affleure empeche la cale de porter.

// --- PASSAGE DU CABLE -------------------------------------------------
cable_d     = 25;     // traversant, centre

// --- FINITION ---------------------------------------------------------
cham        = 0.6;    // chanfrein des aretes : ebavurage, et la face
                      // plafond ne porte pas sur un elephant foot.
gab_t       = 2;      // epaisseur du gabarit de percage
hub_d       = 22;     // Ø des bossages `mod_hubs` (modifier mesh)

// --- DERIVE -----------------------------------------------------------
eps    = 0.01;
disc_r = disc_d / 2;
hd     = hole_d + clr;                       // Ø reellement perce
bolt_r = disc_r - edge_margin - hole_d / 2;  // cercle de percage (nominal)
pitch  = bolt_r * sqrt(3);                   // entraxe d'un triangle
hex_d  = (nut_s + nut_clr) / cos(30);        // Ø circonscrit du logement
chord  = 2 * bolt_r * sin(offset_ang / 2);   // lamage <-> logement voisin

// Une seule definition des positions : la geometrie et l'echo ne peuvent
// pas diverger. Plafond a 90 deg (pointe en haut), platine decalee.
function ceil_a(i)   = 90 + i * 360 / n_holes;
function brkt_a(i)   = 90 + offset_ang + i * 360 / n_holes;
function ceil_xy(i)  = bolt_r * [cos(ceil_a(i)), sin(ceil_a(i))];
function brkt_xy(i)  = bolt_r * [cos(brkt_a(i)), sin(brkt_a(i))];

// Matiere restante. web_cb / web_nut : jusqu'au bord du disque.
web_cb  = disc_r - bolt_r - cb_d / 2;
web_nut = disc_r - bolt_r - hex_d / 2;
web_mid = chord - cb_d / 2 - hex_d / 2;      // entre les deux familles
web_cbl = bolt_r - cb_d / 2 - cable_d / 2;   // lamage -> passage cable

// Volumes analytiques, chanfreins non deduits (~0,1 %). Ce n'est pas une
// mesure supposee : c'est le modele qui dit ce qu'il croit produire, et
// verify.py confronte le maillage a cette affirmation.
function a_hex(d)   = 3 * sqrt(3) / 2 * pow(d / 2, 2);
function v_plate(h) =
      PI/4 * h * (disc_d*disc_d - cable_d*cable_d)
    - n_holes * (PI/4 * hd*hd * min(h, seat_t)
                 + PI/4 * cb_d*cb_d * max(0, h - seat_t))
    - n_holes * (PI/4 * hd*hd * max(0, h - nut_depth)
                 + a_hex(hex_d) * min(h, nut_depth));

// -- Gardes de COHERENCE INTERNE uniquement. Aucune ne verifie le modele
//    contre une mesure relevee sur le ventilateur : ces cotes-la vivent
//    dans docs/target.json, ou elles restent discutables.
assert(web_cb  > 5, "matiere trop mince entre le lamage et le bord");
assert(web_nut > 5, "matiere trop mince entre le logement d'ecrou et le bord");
assert(web_mid > 5, "lamage et logement d'ecrou trop proches");
assert(web_cbl > 5, "lamage trop proche du passage de cable");
assert(seat_t >= 2, "plafond de percage trop mince pour porter une tete");
assert(nut_depth > nut_h,
       "logement moins profond que l'ecrou : la cale ne porterait plus a plat");
assert(nut_depth + seat_t < disc_t, "logement et lamage se rejoignent");
assert(cb_d > hd + 4, "lamage trop etroit pour une tete de vis");
assert(2 * cham < gab_t,  "chanfrein plus epais que le gabarit");
assert(2 * cham < disc_t, "chanfrein plus epais que la cale");

echo(str("bolt_r (cercle de percage)  = ", bolt_r, " mm  -> Ø", 2*bolt_r));
echo(str("pitch (entraxe d'un triangle) = ", pitch, " mm"));
echo(str("chord (lamage <-> ecrou)    = ", chord, " mm"));
echo(str("hd (Ø reellement perce)     = ", hd, " mm"));
echo(str("hex_d (Ø circonscrit logement) = ", hex_d, " mm"));
echo(str("seat_t (plafond de percage) = ", seat_t, " mm"));
echo(str("ancrage rendu a une vis de 30 = ", 30 - seat_t, " mm"));
echo(str("web_cb (lamage -> bord)     = ", web_cb, " mm"));
echo(str("web_nut (ecrou -> bord)     = ", web_nut, " mm"));
echo(str("web_mid (lamage -> ecrou)   = ", web_mid, " mm"));
echo(str("web_cbl (lamage -> cable)   = ", web_cbl, " mm"));
echo(str("VIS_PLAFOND_XY = ", [for (i = [0:n_holes-1]) ceil_xy(i)]));
echo(str("VIS_PLATINE_XY = ", [for (i = [0:n_holes-1]) brkt_xy(i)]));
echo(str("V_CALE_MM3 = ", v_plate(disc_t)));
echo(str("V_GABARIT_MM3 = ", PI/4 * gab_t * (disc_d*disc_d - cable_d*cable_d)
                             - 2 * n_holes * PI/4 * hd*hd * gab_t));
echo(str("V_HUBS_MM3 = ", 2 * n_holes * PI/4 * hub_d*hub_d * disc_t));

// =====================================================================
//  MODULES
// =====================================================================

// Disque chanfreine sur son pourtour, en un seul solide de revolution :
// pas de difference() sur le contour, donc pas de corps parasite.
module chamfered_disc(r, h, c) {
    rotate_extrude(convexity = 4)
        polygon([[0, 0], [r - c, 0], [r, c], [r, h - c], [r - c, h], [0, h]]);
}

// Percage traversant de rayon r, chanfreine aux deux bouts. Depasse de eps
// en haut et en bas pour ne laisser aucune peau.
module bore(r, h, c) {
    rotate_extrude(convexity = 4)
        polygon([[0, -eps], [r + c, -eps], [r + c, 0], [r, c],
                 [r, h - c], [r + c, h], [r + c, h + eps], [0, h + eps]]);
}

// COTE PLAFOND : lamage Ø cb_d depuis la face platine (z = 0) jusqu'a
// seat_t du haut, puis Ø hd traversant. La tete porte sur ce plafond.
module ceiling_cut(h) {
    bore(hd / 2, h, cham);
    if (h > seat_t)
        translate([0, 0, -eps])
            cylinder(d = cb_d, h = h - seat_t + eps);
}

// COTE PLATINE : Ø hd traversant, plus le logement d'ecrou ouvert vers le
// HAUT (face plafond). Ouvert vers le haut = imprime en fin de course,
// jamais en pont, et l'ecrou ne peut pas tomber une fois au plafond.
module bracket_cut(h) {
    bore(hd / 2, h, cham);
    if (h > nut_depth)
        translate([0, 0, h - nut_depth])
            cylinder(d = hex_d, h = nut_depth + eps, $fn = 6);
}

// Plateau perce : le disque, le passage du cable, les deux triangles.
// `pierced` = percages nus, pour le gabarit : c'est le TRIANGLE qu'on
// verifie sur la platine, pas les lamages.
module plate(h, pierced = false) {
    difference() {
        chamfered_disc(disc_r, h, cham);
        bore(cable_d / 2, h, cham);
        for (i = [0 : n_holes - 1]) {
            translate(ceil_xy(i)) if (pierced) bore(hd/2, h, cham);
                                  else         ceiling_cut(h);
            translate(brkt_xy(i)) if (pierced) bore(hd/2, h, cham);
                                  else         bracket_cut(h);
        }
    }
}

// =====================================================================
//  PIECES
// =====================================================================

module cale() { plate(disc_t); }

// Le meme TRIANGLE, en 2 mm. Les deux familles y sont des trous nus et
// identiques -- c'est voulu : on presente le gabarit contre le plafond,
// puis contre la platine. Les deux doivent tomber juste. C'est
// exactement l'hypothese sur laquelle repose le decalage de 60 degres.
module gabarit() { plate(gab_t, pierced = true); }

// Deux coupons, la vraie geometrie a l'echelle 1, ~45 min et ~9 g.
// A imprimer AVANT la cale. Ils repondent aux quatre questions que le
// gabarit ne peut pas trancher : la tete porte-t-elle au fond du lamage,
// l'embout atteint-il la vis, l'ecrou entre-t-il dans son logement, la
// M6 passe-t-elle.
module essai() {
    ct = 24;
    translate([-ct - 3, 0, 0]) difference() {
        translate([-ct/2, -ct/2, 0]) cube([ct, ct, disc_t]);
        ceiling_cut(disc_t);
    }
    translate([ct + 3, 0, 0]) difference() {
        translate([-ct/2, -ct/2, 0]) cube([ct, ct, nut_depth + 3]);
        bracket_cut(nut_depth + 3);
    }
}

// Six colonnes aux coordonnees EXACTES des vis, dans le repere de la
// cale. A charger dans le trancheur en *modifier mesh* -> 100 % de
// remplissage la ou passe l'effort. Ne s'imprime pas : 6 corps separes.
module mod_hubs() {
    for (i = [0 : n_holes - 1]) {
        translate(ceil_xy(i)) cylinder(d = hub_d, h = disc_t);
        translate(brkt_xy(i)) cylinder(d = hub_d, h = disc_t);
    }
}

if      (part == "cale")     cale();
else if (part == "gabarit")  gabarit();
else if (part == "essai")    essai();
else if (part == "mod_hubs") mod_hubs();
else {
    cale();
    translate([disc_d + 10, 0, 0]) gabarit();
}
