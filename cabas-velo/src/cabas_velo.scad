// =====================================================================
//  STRUCTURE DE CABAS VELO -- type BikeZac / Cobags            [v14]
//
//  LE CROCHET SE POSE, IL NE SE CLIPSE PAS.
//    Le tube du porte-bagages est ferme, soude au cadre : on ne l'enfile
//    pas dans une bouche etroite, on POSE le crochet dessus. Le v12
//    enroulait 230 deg avec une bouche de 8 mm -- impossible a engager.
//    Ce n'etait pas une cote fausse, c'etait la cinematique de montage.
//
//  FORME EN R (v14, d'apres le croquis cote).
//    Un dos plat (le collier qui enfile le jonc), un BRAS DU HAUT
//    horizontal, un VENTRE en arc qui epouse le tube, puis une LANGUETTE
//    droite qui descend : le pied du R, levier de decrochage. Le tube se
//    loge dans le ventre.
//    Le centre de l'arc EST le centre du tube : si le rayon interieur
//    vaut tube_d/2 + clr, l'arc epouse le flanc et le bras du haut touche
//    le sommet. Une seule cote (tube_d) gouverne les deux.
//
//  CE QUI TIENT LE SAC : le poids, qui plaque le bras du haut sur le tube,
//    et l'elastique en bas. Pas une barbe serree. La languette ne
//    "declipse" rien, elle fait pivoter le crochet a la main.
//
//  IMPRESSION : profil plan, extrude 15,05 mm en Z. Aucun porte-a-faux.
//    Dans un ruban qui flechit, la contrainte court LE LONG du ruban,
//    donc dans le plan des couches.
//
//  NB. Les cotes du croquis (dos 25, bras 15/10, ventre 21x17, languette
//  10) sont dans docs/target_hook.json. On ne les recopie pas ici : le
//  modele sort ses cotes REELLES par echo, l'outillage superpose la cible.
// =====================================================================

$fn = 96;
part = "all";   // "a"|"b"|"hook"|"hooks3"|"gauge"|"plate"|"hinge_test"|"all"

// --- JONC -------------------------------------------------------------
total_len   = 280;
bar_h       = 11;
bar_t       = 5;
hook_start  = 37.5;
tail_span   = 40;
tail_stem   = 14;

// --- COTES RELEVEES SUR LE CROCHET ORIGINAL ---------------------------
hook_len    = 15.05;  // largeur : axe d'extrusion
hook_depth  = 21.55;  // face du collier -> point le plus eloigne (croquis : 21)

// --- MESURE -----------------------------------------------------------
tube_d      = 12.23;  // tube du porte-bagages, au pied a coulisse
rib_t       = 2.5;    // epaisseur du ruban   (A CONFIRMER)
clr         = 0.4;    // jeu ruban / tube

// --- FORME DU R, ESTIME SUR PHOTO/CROQUIS, A CORRIGER -----------------
wrap_end    = -50;    //   0  = quart de cercle nu, rien ne retient
                      // -50  = le ruban passe sous le tube : levre legere
                      // plus negatif = levre plus fermee, pose plus dure
lang_l      = 10;     // longueur de la languette (le pied du R). Croquis : 10
lang_ang    = -90;    // cap absolu de la languette : -90 = tout droit vers le
                      // bas. Plus positif = languette rejetee vers le tube
                      // (referme la bouche) ; plus negatif = vers le dos.
bevel_a     = 35;     // biseau du bout de languette

// --- COLLIER ----------------------------------------------------------
col_wall    = 1.8;
col_clr     = 0.15;

// --- CHARNIERE --------------------------------------------------------
pin_d       = 2.5;    // 2.5 corde a piano | 4.0 vis sans tete M4
pin_gap     = 0.1;
kn_wall     = 1.25;
capture_t   = 0.3;
kn_clr      = 0.3;
hinge_clr   = 0.3;
tight_int   = 0.15;
free_clr    = 0.25;

// =====================  GEOMETRIE DERIVEE  ============================
half_len   = total_len / 2;
pin_y      = -(bar_t + pin_gap);
knuckle    = pin_d/2 + kn_wall;
bore_tight = pin_d - tight_int;
bore_free  = pin_d + free_clr;
rc         = knuckle + hinge_clr;
butee      = abs(pin_y) - rc;
tail_root  = rc + 0.1;
hinge_lip  = sqrt(pow(bore_free/2,2) - pow((pin_d - capture_t)/2,2));
debord     = pin_gap + hinge_lip;
axe_out    = pin_gap + pin_d/2;
capture    = pin_d - 2*sqrt(pow(bore_free/2,2) - pow(hinge_lip,2));
k1 = bar_h/3;
k2 = 2*bar_h/3;

ci_u0 = -bar_t - col_clr;  ci_u1 =  col_clr;
ci_v0 = -col_clr;          ci_v1 =  bar_h + col_clr;
co_u0 = ci_u0 - col_wall;  co_u1 = ci_u1 + col_wall;
co_v0 = ci_v0 - col_wall;  co_v1 = ci_v1 + col_wall;

Rc    = tube_d/2 + clr + rib_t/2;            // ligne moyenne de l'arc du ventre
cu    = co_u1 + hook_depth - rib_t/2 - Rc;   // centre du tube, profondeur
v_top = co_v1 - rib_t/2;                     // bras du haut, arase au collier
cv    = v_top - Rc;                          // centre du tube, hauteur

// -- languette droite : levier a cap fixe (v14), plus force tangente a l'arc
lipe   = [cu + Rc*cos(wrap_end), cv + Rc*sin(wrap_end)];   // sortie de l'arc
u_tip  = lipe[0] + lang_l*cos(lang_ang);
v_tip  = lipe[1] + lang_l*sin(lang_ang);
mouth  = (u_tip - rib_t/2) - co_u1;          // passage horizontal libre pour poser

// -- cotes REELLES, a comparer a docs/target_hook.json (cible-vs-reel)
depth_r  = cu + Rc + rib_t/2 - co_u1;                    // ventre : profondeur
height_r = (v_top + rib_t/2) - (v_tip - rib_t/2);        // dos : hauteur totale
armtop_r = cu - co_u1;                                   // bras du haut
arc_low  = min(cv - Rc, cv + Rc*sin(wrap_end));          // bas de l'arc trace
bowl_r   = (cv + Rc) - arc_low + rib_t;                  // ventre : hauteur
lipsous  = cv - lipe[1];                                 // levre sous le tube

echo(str("Tube Phi", tube_d, " centre [", cu, ", ", cv, "]  R_moy ", Rc));
echo(str("Profondeur = ", depth_r, "  (cible ", hook_depth, ")"));
echo(str("Hauteur totale = ", height_r, "  (dos ; croquis 25)"));
echo(str("Ventre = ", bowl_r, "  (croquis 17)"));
echo(str("Bras du haut = ", armtop_r, "  (croquis 15)"));
echo(str("Languette = ", lang_l, " mm a ", lang_ang, " deg  (croquis 10)"));
echo(str("Enroulement = ", 90 - wrap_end, " deg ; levre sous le tube = ", lipsous, " mm"));
echo(str("Bouche de pose = ", mouth, " mm   (tube ", tube_d, ")"));
echo(str("Jeu tube / jonc = ", (cu - tube_d/2) - co_u1, " mm"));
echo(str("Entraxe = ", total_len - 2*(hook_start + hook_len/2), " mm"));
echo(str("Butee charniere = ", butee, " ; debord axe = ", axe_out, " ; capture = ", capture));

// -- gardes : COHERENCE INTERNE uniquement, jamais une mesure supposee.
assert(cu - tube_d/2 > co_u1,    "Le tube traverse le jonc.");
assert(wrap_end <= 0,            "L'enroulement doit atteindre le quart de cercle.");
assert(wrap_end > -80,           "Trop enroule : le crochet ne se posera plus.");
assert(mouth > tube_d * 0.75,    "Bouche trop etroite : impossible de poser le crochet.");
assert(v_tip < cv - tube_d/2,    "La languette ne descend pas sous le tube.");
assert(lang_l > 0,               "Languette de longueur nulle.");
assert(rib_t >= 2.0,             "Ruban trop mince.");
assert(butee >= 1.5,             "Butee trop mince.");
assert(hinge_lip < bore_tight/2, "Levre de charniere trop profonde.");
assert(capture >= 0.2,           "Levre de charniere trop courte.");
assert(kn_wall >= 1.2,           "Paroi de charnon trop mince.");
assert(tail_root >= rc,          "La racine du lobe empiete sur le degagement.");

// ======================  CROCHET  =====================================
function pol(c, r, a) = [c[0] + r*cos(a), c[1] + r*sin(a)];

module chain(pts, t) {
    for (i = [0 : len(pts)-2])
        hull() {
            translate(pts[i])   circle(d = t, $fn = 24);
            translate(pts[i+1]) circle(d = t, $fn = 24);
        }
}

arc  = [ for (a = [90 : -5 : wrap_end]) pol([cu, cv], Rc, a) ];
path = concat([[0, v_top]], arc, [[u_tip, v_tip]]);

module hook2d() {
    difference() {
        union() {
            translate([co_u0, co_v0]) square([co_u1-co_u0, co_v1-co_v0]);
            chain(path, rib_t);
        }
        translate([ci_u0, ci_v0]) square([ci_u1-ci_u0, ci_v1-ci_v0]);
        translate([u_tip, v_tip]) rotate(lang_ang + bevel_a)
            translate([0, -20]) square([40, 40]);
    }
}
module hook()   { linear_extrude(height = hook_len) hook2d(); }
module hooks3() { hook(); translate([36,0,0]) hook(); translate([72,0,0]) hook(); }
module gauge()  { cube([25, bar_h, bar_t]); }

// ======================  JONC  ========================================
module half_tail2d() {
    sh = tail_stem;
    st = tail_root + 3.0;
    intersection() {
        polygon([[-st,0],[-st,sh-3],[-tail_span/2,sh+2],[-tail_span/2+5,sh+9],
                 [0,sh+5],[tail_span/2-5,sh+9],[tail_span/2,sh+2],[st,sh-3],[st,0]]);
        translate([tail_root,-1]) square([tail_span, sh+12]);
    }
}
module knuckle_at(z0,z1,bore) {
    difference() {
        translate([0,pin_y,z0]) cylinder(r=knuckle, h=z1-z0);
        translate([0,pin_y,z0-1]) cylinder(d=bore, h=z1-z0+2);
        translate([-20,-60+pin_y-hinge_lip,z0-1]) cube([40,60,z1-z0+2]);
    }
}
module relief_at(z0,z1) {
    intersection() {
        translate([0,pin_y,z0]) cylinder(r=rc, h=z1-z0);
        translate([-20,pin_y-hinge_lip,z0]) cube([40,60,z1-z0]);
    }
}
module collar_bore(bore) {
    translate([0,pin_y,-1]) cylinder(d=bore, h=bar_h+2);
    translate([-20,-60+pin_y-hinge_lip,-1]) cube([40,60,bar_h+2]);
}
module bar_body() {
    union() {
        translate([0,-bar_t,0]) cube([half_len, bar_t, bar_h]);
        translate([0,0,bar_h]) rotate([90,0,0]) linear_extrude(height=bar_t) half_tail2d();
    }
}
module bar_a() {
    difference() {
        union() { bar_body(); knuckle_at(0,k1-kn_clr,bore_free); knuckle_at(k2+kn_clr,bar_h,bore_free); }
        relief_at(k1,k2); collar_bore(bore_free);
    }
}
module bar_b() {
    difference() {
        union() { bar_body(); knuckle_at(k1+kn_clr,k2-kn_clr,bore_tight); }
        relief_at(-1,k1); relief_at(k2,bar_h+1); collar_bore(bore_tight);
    }
}
module hinge_test() {
    intersection() {
        union() { bar_b(); translate([-0.2,0,0]) mirror([1,0,0]) bar_a(); }
        translate([-15,-30,-5]) cube([30,45,bar_h+35]);
    }
}
module bar_flat() { rotate([-90,0,0]) children(); }
module build_plate() {
    bar_flat() bar_a();
    translate([0,40,0]) bar_flat() bar_b();
    translate([0,90,0]) hooks3();
}

if      (part=="a")          bar_flat() bar_a();
else if (part=="b")          bar_flat() bar_b();
else if (part=="hook")       hook();
else if (part=="hooks3")     hooks3();
else if (part=="gauge")      gauge();
else if (part=="plate")      build_plate();
else if (part=="hinge_test") bar_flat() hinge_test();
else { bar_b(); color("DimGray") mirror([1,0,0]) bar_a(); }
