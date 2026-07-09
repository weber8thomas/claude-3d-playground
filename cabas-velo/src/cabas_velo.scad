// =====================================================================
//  STRUCTURE DE CABAS VELO -- type BikeZac / Cobags            [v15]
//
//  LE CROCHET SE POSE, IL NE SE CLIPSE PAS.
//    Le tube du porte-bagages est ferme, soude au cadre : on ne l'enfile
//    pas dans une bouche etroite, on POSE le crochet dessus.
//
//  FORME EN R (v15, cotes reglees dans l'editeur web tools/web/designer.html).
//    Un DOS plat (le collier qui enfile le jonc), un BRAS DU HAUT, un
//    VENTRE en arc (arc a trois points : bras_haut -> apex a la profondeur
//    voulue -> bras_bas), puis une LANGUETTE droite : le pied du R, levier
//    de decrochage. Le tube se loge dans le ventre.
//
//    Le ventre n'est plus force a epouser exactement le rayon du tube : sa
//    forme suit le croquis (profondeur + hauteur), et on VERIFIE que le tube
//    s'y loge (assert + trace). L'editeur montre l'emboitement en direct.
//
//  IMPRESSION : profil plan, extrude 15,05 mm en Z. Aucun porte-a-faux.
//
//  COTES DU CROQUIS -> docs/target_hook.json (verite externe). Le modele
//  sort ses cotes reelles par echo ; profile_plot et le viewer superposent
//  cible-vs-reel. On ne recopie aucune cote ici et on n'en fait pas d'assert.
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

// --- CROCHET : cotes reglees dans l'editeur (designer.html) ------------
hook_len    = 15.05;  // largeur : axe d'extrusion
arm_top     = 15;     // bras du haut (dos -> depart du ventre)
depth       = 21.5;   // profondeur du ventre (dos -> apex)
bowl_h      = 17;     // hauteur du ventre
arm_bot     = 10;     // bras du bas (dos -> bas du ventre)
back_h      = 25;     // dos : hauteur totale du profil
leg_l       = 10;     // languette : longueur (pied du R)
leg_ang     = -45;    // languette : cap absolu (deg). -90 = tout droit vers le bas
bevel_a     = 35;     // biseau du bout de languette

// --- MESURE -----------------------------------------------------------
tube_d      = 12.23;  // tube du porte-bagages, au pied a coulisse
rib_t       = 2.5;    // epaisseur du ruban   (A CONFIRMER)
clr         = 0.4;    // jeu ruban / tube

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

// =====================  GEOMETRIE DERIVEE (JONC/CHARNIERE)  ===========
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

// =====================  GEOMETRIE DU CROCHET  ========================
// Collier : anneau ferme derriere le dos, il enfile le jonc (bar_t x bar_h).
co_u1 =  rib_t/2;                                   // face avant, au ras du dos
co_u0 =  co_u1 - (bar_t + 2*col_clr + 2*col_wall);  // face arriere
co_v1 =  0;                                         // haut, au ras du bras du haut
co_v0 =  co_v1 - (bar_h + 2*col_clr + 2*col_wall);  // bas du collier
ci_u0 =  co_u0 + col_wall;  ci_u1 = co_u1 - col_wall;   // alesage du jonc
ci_v0 =  co_v0 + col_wall;  ci_v1 = co_v1 - col_wall;

// Ligne moyenne du ruban : dos -> bras du haut -> ventre (arc 3 pts) -> languette
function n360(x)   = x - 360*floor(x/360);
function circ3(A,Q,B) =
    let(d = 2*(A[0]*(Q[1]-B[1]) + Q[0]*(B[1]-A[1]) + B[0]*(A[1]-Q[1])))
    [ ((A[0]*A[0]+A[1]*A[1])*(Q[1]-B[1]) + (Q[0]*Q[0]+Q[1]*Q[1])*(B[1]-A[1]) + (B[0]*B[0]+B[1]*B[1])*(A[1]-Q[1]))/d,
      ((A[0]*A[0]+A[1]*A[1])*(B[0]-Q[0]) + (Q[0]*Q[0]+Q[1]*Q[1])*(A[0]-B[0]) + (B[0]*B[0]+B[1]*B[1])*(Q[0]-A[0]))/d ];

spineTop = [0, 0];
spineBot = [0, -back_h];
armEnd   = [arm_top, 0];
bowlBot  = [arm_bot, -bowl_h];
apex     = [depth,   -bowl_h/2];

cc   = circ3(armEnd, apex, bowlBot);
rr   = norm(armEnd - cc);
a0   = atan2(armEnd[1]-cc[1],  armEnd[0]-cc[0]);
a1   = atan2(bowlBot[1]-cc[1], bowlBot[0]-cc[0]);
am   = atan2(apex[1]-cc[1],    apex[0]-cc[0]);
sweepP = n360(a1 - a0);
span   = (n360(am - a0) <= sweepP) ? sweepP : sweepP - 360;
Nbowl  = 48;
bowl   = [ for (i=[0:Nbowl]) let(a = a0 + span*i/Nbowl) [cc[0]+rr*cos(a), cc[1]+rr*sin(a)] ];

legEnd = [ bowlBot[0] + leg_l*cos(leg_ang), bowlBot[1] + leg_l*sin(leg_ang) ];
path   = concat([spineBot, spineTop], bowl, [legEnd]);

// Tube niche dans le ventre (comme l'editeur) : centre, et test d'emboitement.
maxx    = max([ for (q = path) q[0] ]);
tube_cu = maxx - rib_t/2 - clr - tube_d/2;
tube_cv = -bowl_h/2;

// Encombrement du profil (avec l'epaisseur du ruban et le collier).
prof_x0 = min(min([for(q=path) q[0]]) - rib_t/2, co_u0);
prof_x1 = max([for(q=path) q[0]]) + rib_t/2;
prof_y0 = min(min([for(q=path) q[1]]) - rib_t/2, co_v0);
prof_y1 = max([for(q=path) q[1]]) + rib_t/2;

echo(str("Bras du haut = ", arm_top, "  (croquis 15)"));
echo(str("Profondeur = ", depth, "  (croquis 21)"));
echo(str("Ventre = ", bowl_h, "  (croquis 17)"));
echo(str("Bras du bas = ", arm_bot, "  (croquis 10)"));
echo(str("Dos = ", back_h, "  (croquis 25)"));
echo(str("Languette = ", leg_l, " a ", leg_ang, " deg  (croquis 10)"));
echo(str("Tube Phi", tube_d, " centre [", tube_cu, ", ", tube_cv, "]"));
echo(str("Jeu tube / dos = ", (tube_cu - tube_d/2) - co_u1, " mm"));
echo(str("Encombrement = ", prof_x1-prof_x0, " x ", prof_y1-prof_y0, " mm"));
echo(str("Entraxe = ", total_len - 2*(hook_start + hook_len/2), " mm"));
echo(str("Butee charniere = ", butee, " ; debord axe = ", axe_out, " ; capture = ", capture));

// -- gardes : COHERENCE INTERNE uniquement, jamais une mesure supposee.
assert(is_num(cc[0]) && is_num(cc[1]), "Ventre degenere : les trois points sont alignes.");
assert(tube_cu - tube_d/2 > co_u1,  "Le tube touche le dos/jonc : ventre trop peu profond.");
assert(maxx - tube_cu >= rib_t/2 + tube_d/2 + clr - 0.35, "Le tube ne se loge pas dans le ventre.");
assert(back_h >= (bar_h + 2*col_clr + 2*col_wall), "Dos trop court pour loger le collier.");
assert(leg_l > 0,               "Languette de longueur nulle.");
assert(bowl_h > rib_t,          "Ventre trop plat.");
assert(rib_t >= 2.0,            "Ruban trop mince.");
assert(butee >= 1.5,            "Butee trop mince.");
assert(hinge_lip < bore_tight/2, "Levre de charniere trop profonde.");
assert(capture >= 0.2,          "Levre de charniere trop courte.");
assert(kn_wall >= 1.2,          "Paroi de charnon trop mince.");
assert(tail_root >= rc,         "La racine du lobe empiete sur le degagement.");

// ======================  CROCHET  =====================================
module chain(pts, t) {
    for (i = [0 : len(pts)-2])
        hull() {
            translate(pts[i])   circle(d = t, $fn = 24);
            translate(pts[i+1]) circle(d = t, $fn = 24);
        }
}
module hook2d() {
    difference() {
        union() {
            chain(path, rib_t);
            translate([co_u0, co_v0]) square([co_u1-co_u0, co_v1-co_v0]);
        }
        translate([ci_u0, ci_v0]) square([ci_u1-ci_u0, ci_v1-ci_v0]);
        // biseau du bout de languette : bande etroite au-dela de la pointe,
        // le long de l'axe du levier (jamais assez large pour toucher le ventre).
        translate(legEnd) rotate(leg_ang + bevel_a) translate([0, -rib_t]) square([12, 2*rib_t]);
    }
}
module hook()   { linear_extrude(height = hook_len) hook2d(); }
module hooks3() { hook(); translate([40,0,0]) hook(); translate([80,0,0]) hook(); }
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
    translate([0,115,0]) hooks3();   // ecarte : le crochet v15 (27,5 mm) degage le lobe de B
}

if      (part=="a")          bar_flat() bar_a();
else if (part=="b")          bar_flat() bar_b();
else if (part=="hook")       hook();
else if (part=="hooks3")     hooks3();
else if (part=="gauge")      gauge();
else if (part=="plate")      build_plate();
else if (part=="hinge_test") bar_flat() hinge_test();
else { bar_b(); color("DimGray") mirror([1,0,0]) bar_a(); }
