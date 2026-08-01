// =====================================================================
//  CALE D'ECARTEMENT -- plafond <-> platine de ventilateur a pales  [v3]
//
//  FIXATION EN DEUX TEMPS. La cale se visse d'abord au plafond avec les
//    vis EXISTANTES ; la platine se visse ensuite sous la cale avec trois
//    M6 neuves. Deux triangles de percage identiques (R = bolt_r),
//    decales de 60 degres pour ne pas se rencontrer.
//
//  QUI COMMANDE LE CERCLE DE PERCAGE -- change en v3.
//    Jusqu'ici `bolt_r` DERIVAIT de `edge_margin` : on partait des 25 mm
//    de marge au bord demandes au depart, et le triangle tombait ou il
//    tombait. C'etait le mauvais sens. La platine existe, ses trous sont
//    la ou ils sont : `bolt_r` est une cote RELEVEE, et c'est `edge_margin`
//    qui en decoule. On ne negocie pas avec le materiel, on negocie avec
//    la marge -- tant qu'il reste de la matiere (assert plus bas).
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
//    percages verticaux, aucun support. Le seul porte-a-faux est le plafond
//    du lamage : un conge a 45 deg (cb_relief) le ramene a 1,8 mm
//    d'annulaire, que le trancheur ponte. TRANCHE, pas suppose --
//    `make slice` mesure 1,7 % de support reclame sur la cale, contre 31 %
//    pour un temoin en porte-a-faux.
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

// "cale" | "gabarit" | "gabarit_fente" | "essai" | "mod_hubs" | "all"
part = "all";

// --- DISQUE -----------------------------------------------------------
disc_d      = 150;    // diametre hors-tout                        [spec]
disc_t      = 30;     // epaisseur = l'ecartement gagne            [spec]

// --- TRIANGLE DE PERCAGE (le meme pour les deux faces) ----------------
hole_d      = 6;      // nominal : vis M6 / vis a bois Ø6          [spec]
clr         = 0.4;    // jeu de percage. Un trou vertical imprime sort
                      // sous-cote : sans jeu, la vis ne passe pas.
n_holes     = 3;      // triangle equilateral                      [spec]
offset_ang  = 60;     // decalage plafond -> platine. 60 deg place chaque
                      // percage de platine a mi-chemin entre deux lamages.

// LE CERCLE DE PERCAGE, cote RELEVEE sur la platine existante.  [releve]
// C'est la seule cote de ce fichier qui ne se choisit pas : elle se
// mesure. Elle etait a 47 en v1/v2 -- valeur DEDUITE des 25 mm de marge
// au bord, jamais relevee -- et les trous sortaient trop centres d'environ
// 4 mm. D'ou 51. Le "environ" n'est pas leve : `gabarit_fente` le tranche
// en 15 minutes, et `edge_margin` ci-dessous dit ce que ca coute.
//   entraxe d'un triangle equilateral = bolt_r * sqrt(3)
//   -> si tu mesures l'entraxe au pied a coulisse : bolt_r = entraxe / 1,7321
bolt_r      = 51;

// --- COTE PLAFOND : vis existantes de 30 mm, reutilisees ---------------
cb_d        = 14;     // Ø du lamage : tete de vis + embout de vissage
seat_t      = 3;      // plafond de percage. C'est CA qui rend les vis de
                      // 30 mm suffisantes : elles ne traversent que 3 mm
                      // de cale et gardent ~27 mm d'ancrage.
cb_relief   = 2;      // CONGE A 45 DEG SOUS LE PLAFOND DU LAMAGE.
                      // Sans lui, le plafond est un annulaire de 3,8 mm en
                      // porte-a-faux au fond d'un puits borgne de 27 mm :
                      // PrusaSlicer y pose 3,35 g de support qu'on ne peut
                      // pas aller chercher. Le conge ramene le porte-a-faux
                      // a 1,8 mm et laisse une portee plate de 1,8 mm de
                      // large -- assez pour une tete M6. Verifie par
                      // `make slice` (garde 8), pas suppose.

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
gab_t       = 2;      // epaisseur des deux gabarits
hub_d       = 22;     // Ø des bossages `mod_hubs` (modifier mesh)

// --- GABARIT A FENTES : l'instrument qui MESURE bolt_r ----------------
gab_slot    = 6;      // demi-course radiale des fentes : bolt_r +/- 6
gab_arm_w   = 20;     // largeur d'un bras
gab_hub_r   = 18;     // rayon du moyeu central
gab_arm_m   = 8;      // matiere au-dela du bout de fente
wit_d       = 2;      // Ø des deux temoins qui marquent bolt_r nominal
wit_off     = 6.2;    // leur decalage tangentiel, de part et d'autre

// --- DERIVE -----------------------------------------------------------
eps    = 0.01;
disc_r = disc_d / 2;
hd     = hole_d + clr;                       // Ø reellement perce
pitch  = bolt_r * sqrt(3);                   // entraxe d'un triangle
hex_d  = (nut_s + nut_clr) / cos(30);        // Ø circonscrit du logement
chord  = 2 * bolt_r * sin(offset_ang / 2);   // lamage <-> logement voisin

// CONSEQUENCE, plus une entree : c'est le cercle de percage qui commande.
edge_margin = disc_r - bolt_r - hole_d / 2;  // du BORD DU TROU au bord
edge_min    = 15;                            // plancher admis (voir assert)

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
//
// Aucun de ces volumes ne depend de bolt_r -- c'est precisement pourquoi
// la garde 5 ne peut PAS attraper un cercle de percage faux. Voir CLAUDE.md.
function a_hex(d)   = 3 * sqrt(3) / 2 * pow(d / 2, 2);
// Tronc de cone : hauteur th, rayons r1 et r2.
function v_cone(th, r1, r2) = PI/3 * th * (r1*r1 + r1*r2 + r2*r2);
// Le lamage : puits droit + conge a 45 deg + percage a travers la portee.
function v_ceil(h) = h <= seat_t ? PI/4 * hd*hd * h :
      PI/4 * cb_d*cb_d * (h - seat_t - cb_relief)
    + v_cone(cb_relief, cb_d/2, max(hd/2, cb_d/2 - cb_relief))
    + PI/4 * hd*hd * seat_t;
function v_plate(h) =
      PI/4 * h * (disc_d*disc_d - cable_d*cable_d)
    - n_holes * v_ceil(h)
    - n_holes * (PI/4 * hd*hd * max(0, h - nut_depth)
                 + a_hex(hex_d) * min(h, nut_depth));

// -- Gardes de COHERENCE INTERNE uniquement. Aucune ne verifie le modele
//    contre une mesure relevee sur le ventilateur : ces cotes-la vivent
//    dans docs/target.json, ou elles restent discutables.
//
//    `edge_margin` a change de camp en v3 : ce n'est plus une cote de la
//    demande a respecter, c'est une consequence a SURVEILLER. D'ou un
//    plancher ici, et non plus une valeur dans target.json.
assert(edge_margin >= edge_min,
       "cercle de percage trop grand : il ne reste plus assez de bord");
assert(web_cb  > 5, "matiere trop mince entre le lamage et le bord");
assert(web_nut > 5, "matiere trop mince entre le logement d'ecrou et le bord");
assert(web_mid > 5, "lamage et logement d'ecrou trop proches");
assert(web_cbl > 5, "lamage trop proche du passage de cable");
assert(seat_t >= 2, "plafond de percage trop mince pour porter une tete");
assert(nut_depth > nut_h,
       "logement moins profond que l'ecrou : la cale ne porterait plus a plat");
assert(nut_depth + seat_t < disc_t, "logement et lamage se rejoignent");
assert(cb_d > hd + 4, "lamage trop etroit pour une tete de vis");
assert(cb_d/2 - cb_relief > hd/2 + 1,
       "conge trop grand : il ne reste plus de portee plate sous la tete");
assert(seat_t + cb_relief < disc_t, "conge et puits depassent l'epaisseur");
assert(2 * cham < gab_t,  "chanfrein plus epais que le gabarit");
assert(2 * cham < disc_t, "chanfrein plus epais que la cale");
// Le gabarit a fentes doit rester un instrument valide : la fente ne doit
// ni sortir du bras, ni mordre le moyeu, ni toucher les temoins.
assert(bolt_r - gab_slot > gab_hub_r + hd/2,
       "la fente du gabarit mord le moyeu");
assert(wit_off + wit_d/2 < gab_arm_w/2 - 1,
       "les temoins du gabarit debordent du bras");
assert(wit_off - wit_d/2 > hd/2 + 1,
       "les temoins du gabarit touchent la fente");

echo(str("bolt_r (cercle de percage)  = ", bolt_r, " mm  -> Ø", 2*bolt_r));
echo(str("pitch (entraxe d'un triangle) = ", pitch, " mm"));
echo(str("edge_margin (bord du trou -> bord) = ", edge_margin,
         " mm  (plancher ", edge_min, ")"));
echo(str("chord (lamage <-> ecrou)    = ", chord, " mm"));
echo(str("hd (Ø reellement perce)     = ", hd, " mm"));
echo(str("hex_d (Ø circonscrit logement) = ", hex_d, " mm"));
echo(str("seat_t (plafond de percage) = ", seat_t, " mm"));
echo(str("portee plate sous la tete = ", (cb_d - 2*cb_relief - hd)/2, " mm de large"));
echo(str("porte-a-faux du plafond   = ", (cb_d - 2*cb_relief - hd)/2, " mm"));
echo(str("ancrage rendu a une vis de 30 = ", 30 - seat_t, " mm"));
echo(str("course de mesure du gabarit a fentes = R", bolt_r - gab_slot,
         " a R", bolt_r + gab_slot, " (entraxe ", (bolt_r-gab_slot)*sqrt(3),
         " a ", (bolt_r+gab_slot)*sqrt(3), ")"));
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
//
// Un seul solide de revolution : le puits, le conge a 45 deg, la portee
// plate et le percage. Pas d'union de primitives, donc pas d'arete parasite
// au raccord -- et le profil se lit d'un coup.
module ceiling_cut(h) {
    if (h <= seat_t) bore(hd / 2, h, cham);
    else {
        rc = max(hd / 2, cb_d / 2 - cb_relief);   // rayon de la portee plate
        rotate_extrude(convexity = 6)
            polygon([[0, -eps], [cb_d/2, -eps],
                     [cb_d/2, h - seat_t - cb_relief],   // puits droit
                     [rc,     h - seat_t],               // conge a 45 deg
                     [hd/2,   h - seat_t],               // portee plate
                     [hd/2,   h - cham],
                     [hd/2 + cham, h], [hd/2 + cham, h + eps], [0, h + eps]]);
    }
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

// Fente radiale de r0 a r1, largeur hd. Pas de chanfrein : hull() de deux
// `bore` remplirait le chanfrein et elargirait la fente de 2*cham -- la
// coque convexe d'un profil rentrant, c'est le profil enveloppe. Sur un
// instrument de mesure, une fente Ø7,6 au lieu de Ø6,4 fausserait tout.
module fente(r0, r1) {
    hull() {
        translate([r0, 0, -eps]) cylinder(d = hd, h = gab_t + 2*eps);
        translate([r1, 0, -eps]) cylinder(d = hd, h = gab_t + 2*eps);
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

// L'INSTRUMENT DE MESURE. Trois bras, trois fentes radiales de bolt_r-6 a
// bolt_r+6, larges de hd.
//
// Il se centre TOUT SEUL : trois vis dans trois fentes radiales a 120 deg,
// c'est trois contraintes tangentielles pour trois degres de liberte
// (x, y, rotation). Une fois pose sur la platine et les vis engagees, il
// n'a plus qu'une position -- et les vis s'y trouvent au rayon REEL.
//
// Deux temoins Ø2 de part et d'autre de chaque fente marquent le bolt_r
// nominal : d'un coup d'oeil on voit si la vis tombe en dedans ou en
// dehors. Pour le chiffre exact, trace au crayon au travers des trois
// fentes, retire le gabarit et mesure l'entraxe des trois marques au pied
// a coulisse -- c'est plus fin que n'importe quelle graduation imprimee.
//   bolt_r = entraxe / sqrt(3)
//
// Trois bras au lieu d'un disque plein : ~4 fois moins de matiere et de
// temps que `gabarit`. C'est ce qui le rend utilisable AVANT de decider.
module gabarit_fente() {
    r_out = bolt_r + gab_slot + gab_arm_m;
    difference() {
        union() {
            chamfered_disc(gab_hub_r, gab_t, cham);
            for (i = [0 : n_holes - 1])
                rotate([0, 0, ceil_a(i)])
                    translate([0, -gab_arm_w/2, 0])
                        cube([r_out, gab_arm_w, gab_t]);
        }
        bore(cable_d / 2, gab_t, cham);
        for (i = [0 : n_holes - 1]) rotate([0, 0, ceil_a(i)]) {
            fente(bolt_r - gab_slot, bolt_r + gab_slot);
            translate([bolt_r,  wit_off, 0]) bore(wit_d/2, gab_t, cham);
            translate([bolt_r, -wit_off, 0]) bore(wit_d/2, gab_t, cham);
        }
    }
}

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

if      (part == "cale")          cale();
else if (part == "gabarit")       gabarit();
else if (part == "gabarit_fente") gabarit_fente();
else if (part == "essai")         essai();
else if (part == "mod_hubs")      mod_hubs();
else {
    cale();
    translate([disc_d + 10, 0, 0]) gabarit();
    translate([0, disc_d + 10, 0]) gabarit_fente();
}
